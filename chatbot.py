# from dotenv import load_dotenv
# import os
# from google import genai
# from prompts import TECH_QUESTION_PROMPT, FALLBACK_RESPONSE

# # Load environment variables
# load_dotenv()
# api_key = os.getenv("GEMINI_API_KEY")
# if not api_key:
#     raise ValueError("Gemini API key not found! Make sure it is set in the .env file.")

# # Initialize client
# client = genai.Client(api_key=api_key)

# def generate_response(prompt, model="gemini-2.5-flash"):
#     try:
#         response = client.models.generate_content(
#             model=model,
#             contents=prompt
#         )
#         return response.text.strip()
#     except Exception as e:
#         return f"Sorry, I didn’t understand that. Could you rephrase? (Error: {e})"

# def generate_tech_questions(tech_stack):
#     prompt = f"Generate 3 technical interview questions for a {tech_stack} developer."
#     return generate_response(prompt)
        

import os
import re
import json
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ----------------------------
# Helper: clean & parse JSON
# ----------------------------
def clean_and_parse(raw_output: str):
    """
    Cleans Gemini's output by stripping markdown fences and parses it into JSON.
    """
    # Remove ```json or ``` fences
    cleaned = re.sub(r"```(json)?", "", raw_output).strip("` \n")
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON", "raw_output": raw_output}

# ----------------------------
# Prompt builder
# ----------------------------
def build_prompt(tech_stack: list):
    return f"""
You are a hiring assistant chatbot for a recruitment agency.

The candidate has declared expertise in the following tech stack: {", ".join(tech_stack)}.

For EACH technology, generate 3–5 technical questions in the following JSON format:

{{
  "Technology": [
    {{
      "question": "string",
      "answer_outline": "string",
      "difficulty": "beginner|intermediate|advanced"
    }}
  ]
}}

⚠️ IMPORTANT:
- Return ONLY valid JSON (no markdown, no explanations).
- Ensure it is strictly parseable by Python json.loads().
"""

# ----------------------------
# Ask Gemini
# ----------------------------
def generate_questions(tech_stack):
    prompt = build_prompt(tech_stack)
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(prompt)
    return response.text

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="TalentScout - AI Hiring Assistant", page_icon="🤖")

st.title("🤖 TalentScout Hiring Assistant")
st.write("Welcome! I will ask for your details and generate relevant technical questions.")

# Input fields
with st.form("candidate_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    phone = st.text_input("Phone Number")
    experience = st.number_input("Years of Experience", min_value=0, max_value=50, step=1)
    desired_position = st.text_input("Desired Position(s)")
    location = st.text_input("Current Location")
    tech_stack = st.text_area("Tech Stack (comma separated, e.g. Python, Django, React)").split(",")

    submitted = st.form_submit_button("Start Screening")

# When submitted
if submitted:
    st.success(f"Hello {name}, generating technical questions for your stack...")

    raw_output = generate_questions([t.strip() for t in tech_stack if t.strip()])
    parsed = clean_and_parse(raw_output)

    if "error" in parsed:
        st.error("❌ Could not parse Gemini output. Showing raw response:")
        st.code(parsed["raw_output"])
    else:
        # Nicely render the questions
        for tech, questions in parsed.items():
            st.header(f"📌 {tech} Questions")
            for idx, q in enumerate(questions, 1):
                with st.expander(f"Q{idx}: {q['question']}"):
                    st.markdown(f"**Answer Outline:** {q['answer_outline']}")
                    st.markdown(f"**Difficulty:** {q['difficulty'].capitalize()}")

# Conversation end
st.write("---")
st.write("🙏 Thank you for using TalentScout. Our team will review your responses shortly.")
