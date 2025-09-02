
import os
import json
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


# Gemini API Setup

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL = "gemini-2.5-flash-lite"



# Config & Safety Settings
tools = [types.Tool(googleSearch=types.GoogleSearch())]

generate_content_config = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_budget=-1),
    safety_settings=[
        types.SafetySetting(
            category="HARM_CATEGORY_HARASSMENT",
            threshold="BLOCK_ONLY_HIGH",
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_HATE_SPEECH",
            threshold="BLOCK_ONLY_HIGH",
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
            threshold="BLOCK_ONLY_HIGH",
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT",
            threshold="BLOCK_ONLY_HIGH",
        ),
    ],
    tools=tools,
)


# Streamlit UI Config

st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🤖")

#  CSS
st.markdown("""
    <style>
        /* Whole app background */
        .stApp {
            background-color: grey;
        }

        /* Chat message container */
        div[data-testid="stChatMessage"] {
            border-radius: 12px;
            padding: 12px;
            margin: 6px 0px;
        }

        /* User messages */
        div[data-testid="stChatMessage"][data-testid="user"] {
            background-color: #e8f5e9 !important;
        }

        /* Assistant messages */
        div[data-testid="stChatMessage"][data-testid="assistant"] {
            background-color: #f1f8e9 !important;
        }

        /* Buttons */
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

    ====================
    🎯 OBJECTIVES
    ====================
    1. Greet candidates warmly and explain your purpose as an AI Hiring Assistant.  
    2. Collect key candidate details:
   - Full Name
   - Email Address
   - Phone Number
   - Years of Experience
   - Desired Position(s)
   - Current Location
   - Tech Stack (programming languages, frameworks, databases, tools).  
    3. Ask candidates to declare their tech stack clearly.  
    4. For EACH declared technology, generate **3–5 multiple-choice technical questions (MCQs)**.  
   - Each MCQ must contain:
        - "question": the actual technical question
        - "options": an array of 4 possible answers
        - "correct_option": the correct answer (A/B/C/D)
        - "difficulty": beginner, intermediate, or advanced
   - The chatbot MUST NOT reveal the correct answer before the candidate responds.  
    5. Evaluate responses:
   - If correct, acknowledge positively.  
   - If wrong, politely show the correct answer.  
    6. Handle unexpected inputs (ask them to choose A/B/C/D).  
    7. End gracefully if candidate says "quit", "exit", or "stop".  

====================
📋 OUTPUT RULES
====================
-Do not display the JSON block to the candidate. Use it internally only. Instead, ask the questions one by one interactively.
- When generating technical questions, return them in STRICT JSON format only.
- In conversation mode (greeting, info collection, thanking), use natural human-like responses.

    - Collect candidate info (name, email, phone, experience, desired position, location, tech stack).
    - For EACH declared technology, generate **3–5 MCQs** in STRICT JSON format. Do not display the JSON block to the candidate. Use it internally only. Instead, ask the questions one by one interactively.:
        {
          "technology": "Python",
          "questions": [
            {
              "question": "Which keyword is used to define a function in Python?",
              "options": ["A) function", "B) def", "C) func", "D) lambda"],
              "correct_option": "B",
              "difficulty": "beginner"
            }
          ]
        }
    - DO NOT reveal correct answers before the candidate answers.
    - After each response, say Correct ✅ or Incorrect ❌ (and show correct).
    - Do not display raw JSON to user. Use it internally only.
    """

    st.session_state.messages.append({
        "role": "model",
        "content": "Hello! 👋 I'm TalentScout, your AI Hiring Assistant. Let's get started! Could you please tell me your full name?"
    })

if "pending_mcqs" not in st.session_state:
    st.session_state.pending_mcqs = []  # store current batch of MCQs
if "current_q" not in st.session_state:
    st.session_state.current_q = None
if "awaiting_answer" not in st.session_state:
    st.session_state.awaiting_answer = False


# Chat History

for msg in st.session_state.messages:
    with st.chat_message("assistant" if msg["role"] == "model" else "user"):
        st.markdown(msg["content"])


if st.session_state.current_q:
    q = st.session_state.current_q
    st.markdown(f"**{q['question']}**")
    choice = st.radio("Choose an option:", q["options"], key=f"mcq_{q['question']}")

    if st.button("Submit Answer"):
        correct_letter = q["correct_option"]
        chosen_letter = choice.split(")")[0]  # extract "A", "B", etc.
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
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=st.session_state.system_prompt)]
                    )
                ] + [
                    types.Content(
                        role=m["role"],
                        parts=[types.Part.from_text(text=m["content"])]
                    )
                    for m in st.session_state.messages
                ],
                config=generate_content_config,
            )
            response_text = chunks.text
            response_container.markdown(response_text)

        #  parse JSON MCQs
        try:
            parsed = json.loads(response_text)
            if isinstance(parsed, list):
                # Store questions
                for tech in parsed:
                    for q in tech["questions"]:
                        st.session_state.pending_mcqs.append(q)
                if st.session_state.pending_mcqs:
                    st.session_state.current_q = st.session_state.pending_mcqs.pop(0)
                    st.session_state.awaiting_answer = True
                    st.experimental_rerun()
            else:
                st.session_state.messages.append({"role": "model", "content": response_text})
        except Exception:
            # Normal text (non-MCQ)
            st.session_state.messages.append({"role": "model", "content": response_text})
