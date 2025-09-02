🤖 TalentScout – AI Hiring Assistant

TalentScout is an AI-powered hiring assistant built with Streamlit and Google Gemini 2.5 Flash Lite.
It helps recruiters and companies interactively assess candidates by collecting their details and generating customized multiple-choice technical questions (MCQs) for each declared technology stack.

✨ Features

📝 Candidate Info Collection

Full Name, Email, Phone, Experience, Desired Position, Location, Tech Stack

🎯 Adaptive Technical Questions

3–5 MCQs generated dynamically for each declared technology

Difficulty levels: beginner, intermediate, advanced

✅ Automatic Evaluation

Instant feedback: Correct ✅ or Incorrect ❌

Shows correct answers when candidate is wrong

🔒 Safe AI Responses

Built-in safety filters (harassment, hate speech, explicit, dangerous content)

🎨 Custom UI with Streamlit

Styled chat interface with distinct colors for user & assistant messages

Interactive MCQ answering via radio buttons

☁️ Deployable to Streamlit Cloud

Uses Streamlit Secrets instead of .env for API keys

🛠️ Tech Stack

Python 3.9+

Streamlit
 – UI framework

Google Gemini API
 – LLM backend

dotenv
 – local development

Regex-based JSON parsing – ensures Gemini’s MCQ JSON is parsed internally without leaking raw JSON

📂 Project Structure
talentscout-hiring-assistant/
│
├── app.py              # Main Streamlit app
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
└── .streamlit/
    └── secrets.toml    # API key storage (for Streamlit Cloud)

⚙️ Setup Instructions
1. Clone Repository
git clone https://github.com/pearldias/TalentScout-Hiring-Assistant.git
cd TalentScout-Hiring-Assistant

2. Create Virtual Environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

3. Install Dependencies
pip install -r requirements.txt

4. Configure Environment Variables
🔹 Local Development (.env)

Create a .env file:

GEMINI_API_KEY=your_api_key_here

🔹 Streamlit Cloud (secrets.toml)

Streamlit Cloud does not use .env. Instead, create a file:

.streamlit/secrets.toml

GEMINI_API_KEY = "your_api_key_here"


On Streamlit Cloud
:

Go to Manage app → Settings → Secrets

Paste the same config there

5. Run Locally
streamlit run app.py

🚀 Deploy on Streamlit Cloud

Push code to GitHub

Go to Streamlit Cloud
 → New App

Select repo + branch (main)

Set Python version & requirements.txt

Add Secrets (see above)

Click Deploy 🎉

📊 How It Works

Start Conversation

Assistant greets and asks for candidate details

Tech Stack Declaration

Candidate lists skills (e.g., Python, React, SQL)

Dynamic Questioning

Gemini generates MCQs in JSON → parsed silently → shown one at a time

Answer Evaluation

Candidate selects option → instant feedback

Completion

Ends session gracefully with results summary

🧑‍💻 Example Interaction

Assistant: Hi! I’m TalentScout 🤖 Please tell me your full name.
User: John Doe

Assistant: Thanks John! What’s your email?
...
Assistant: Great! You mentioned Python. Here’s your first question:

Which keyword defines a function in Python?

A) function

B) def

C) func

D) lambda

User: B) def
Assistant: ✅ Correct!

🔮 Future Enhancements

📊 Scorecard & summary at the end

📤 Export candidate results to CSV/Google Sheets

🎥 Video-based proctoring integration

🔗 ATS integration (Greenhouse, Lever, etc.)

🤝 Contributing

Pull requests are welcome! For major changes:

Open an issue first

Discuss what you’d like to change
