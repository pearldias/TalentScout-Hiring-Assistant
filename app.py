
import os
import re
import json
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


# Gemini API Setup
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL = "gemini-2.5-flash-lite"

tools = [types.Tool(googleSearch=types.GoogleSearch())]

generate_content_config = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_budget=-1),
    safety_settings=[
        types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_ONLY_HIGH"),
        types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_ONLY_HIGH"),
        types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_ONLY_HIGH"),
        types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH"),
    ],
    tools=tools,
)


# Streamlit UI Config

st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🤖")

st.markdown("""
    <style>
        .stApp { background-color: grey; }
        div[data-testid="stChatMessage"] {
            border-radius: 12px;
            padding: 12px;
            margin: 6px 0px;
        }
        div[data-testid="stChatMessage"][data-testid="user"] {
            background-color: #e8f5e9 !important;
        }
        div[data-testid="stChatMessage"][data-testid="assistant"] {
            background-color: #f1f8e9 !important;
        }
        .stButton > button {
            background-color: #4caf50;
            color: white;
            border-radius: 8px;
            padding: 0.5em 1em;
            border: none;
        }
        .stButton > button:hover {
            background-color: #45a049;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 TalentScout - AI Hiring Assistant")


# Session State

if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = """You are "TalentScout," an intelligent Hiring Assistant chatbot.

🎯 OBJECTIVES:
1. Greet candidates warmly and explain your purpose as an AI Hiring Assistant.
2. Collect key candidate details:
   - Full Name
   - Email Address
   - Phone Number
   - Years of Experience
   - Desired Position(s)
   - Current Location
   - Tech Stack (programming languages, frameworks, databases, tools).  
3. For each tech, generate **3–5 MCQs** in STRICT JSON format:
   {
     "technology": "Python",
     "questions": [
       {
         "question": "Which keyword defines a function in Python?",
         "options": ["A) function", "B) def", "C) func", "D) lambda"],
         "correct_option": "B",
         "difficulty": "beginner"
       }
     ]
   }
4. Do NOT show JSON to candidate, only ask interactively.
5. After each answer: ✅ or ❌ with correct answer.Evaluate responses:
   - If correct, acknowledge positively.  
   - If wrong, politely show the correct answer.  
6. Handle unexpected inputs (ask them to choose A/B/C/D).
7. End gracefully on quit/exit/stop.
"""

    st.session_state.messages.append({
        "role": "model",
        "content": "Hello! 👋 I'm TalentScout, your AI Hiring Assistant. Let's get started! Could you please tell me your full name?"
    })

if "pending_mcqs" not in st.session_state:
    st.session_state.pending_mcqs = []
if "current_q" not in st.session_state:
    st.session_state.current_q = None
if "awaiting_answer" not in st.session_state:
    st.session_state.awaiting_answer = False


for msg in st.session_state.messages:
    with st.chat_message("assistant" if msg["role"] == "model" else "user"):
        st.markdown(msg["content"])


# Handle MCQ Rendering
if st.session_state.current_q:
    q = st.session_state.current_q
    st.markdown(f"**{q['question']}**")
    choice = st.radio("Choose an option:", q["options"], key=f"mcq_{q['question']}")

    if st.button("Submit Answer"):
        correct_letter = q["correct_option"]
        chosen_letter = choice.split(")")[0]  # Extract "A", "B", etc.
        if chosen_letter == correct_letter:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect. The correct answer was **{correct_letter})**")
        # Move to next question
        if st.session_state.pending_mcqs:
            st.session_state.current_q = st.session_state.pending_mcqs.pop(0)
        else:
            st.session_state.current_q = None
            st.session_state.awaiting_answer = False
            st.session_state.messages.append({
                "role": "model",
                "content": "That completes this round of questions! 🎉"
            })
        st.experimental_rerun()


elif not st.session_state.awaiting_answer:
    if prompt := st.chat_input("Type your response..."):
        # Store user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        response_text = ""
        with st.chat_message("assistant"):
            response_container = st.empty()
            chunks = client.models.generate_content(
                model=MODEL,
                contents=[
                    types.Content(role="user", parts=[types.Part.from_text(text=st.session_state.system_prompt)])
                ] + [
                    types.Content(role=m["role"], parts=[types.Part.from_text(text=m["content"])])
                    for m in st.session_state.messages
                ],
                config=generate_content_config,
            )
            response_text = chunks.text
            response_container.markdown(response_text)

        
        # Parse JSON MCQs (via regex extraction)
        
        try:
            json_match = re.search(r"\{[\s\S]*\}", response_text)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)

                if isinstance(parsed, dict) and "questions" in parsed:
                    st.session_state.pending_mcqs.extend(parsed["questions"])
                elif isinstance(parsed, list):
                    for tech in parsed:
                        if "questions" in tech:
                            st.session_state.pending_mcqs.extend(tech["questions"])

                if st.session_state.pending_mcqs:
                    st.session_state.current_q = st.session_state.pending_mcqs.pop(0)
                    st.session_state.awaiting_answer = True
                    st.experimental_rerun()
            else:
                st.session_state.messages.append({"role": "model", "content": response_text})
        except Exception:
            st.session_state.messages.append({"role": "model", "content": response_text})
