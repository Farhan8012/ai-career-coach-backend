#  AI Career Coach (Backend API)

A powerful, headless REST API built with **FastAPI**, **Google Gemini**, and **Supabase**. This API serves as the "brain" for an AI Career Coach application, automating candidate evaluation, resume analysis, and technical profiling.

## ✨ Features

* **📄 AI Resume Parsing & ATS Scoring:** Extracts text from PDF resumes and compares it against Job Descriptions using semantic matching.
* **🐙 GitHub Profile Analyzer:** Fetches live repository data and generates an AI-written "Developer Scorecard" highlighting the candidate's tech stack and open-source activity.
* **🧠 Generative AI Endpoints:** Uses Google Gemini to automatically generate Cover Letters, 5-Day Study Plans for missing skills, and custom Interview Prep questions.
* **🗄️ Cloud Database Integration:** Automatically saves generated candidate evaluations to a Supabase PostgreSQL database.
* **🔐 User Authentication:** Secure signup, login, and JWT-based route protection using Supabase Auth.

## 🛠️ Tech Stack

* **Framework:** FastAPI (Python)
* **AI Engine:** Google Gemini (`gemini-2.5-flash`)
* **Database & Auth:** Supabase (PostgreSQL)
* **External APIs:** GitHub API
* **PDF Processing:** `pdfplumber`

##  Getting Started

### Prerequisites
* Python 3.10+
* A Supabase account and Google Gemini API key.

### Installation
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your API keys (`GOOGLE_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`, `GITHUB_TOKEN`).
4. Run the server: `uvicorn api:app --reload`
5. Visit `http://127.0.0.1:8000/docs` to interact with the API Swagger UI.