import os
from dotenv import load_dotenv
from fastapi import FastAPI
from supabase import create_client, Client
from pydantic import BaseModel
from typing import List
from fastapi import FastAPI, UploadFile, File, Form
import pdfplumber
from utils.text_cleaner import clean_text
from utils.ats_matcher import extract_skills_from_text, match_skills
from utils.semantic_matcher import calculate_semantic_match
from utils.resume_rewriter import optimize_bullet_point

# 1. Load environment variables from your .env file
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 2. Initialize the Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 3. Initialize the FastAPI App
app = FastAPI(
    title="AI Career Coach API",
    description="The backend engine for the v2.0 Resume Analyzer",
    version="2.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Career Coach API v2.0! 🚀", "status": "Online"}

# 4. Create a test endpoint for the database
@app.get("/test-db")
def test_database_connection():
    try:
        # If the client initialized successfully with your keys, this will work
        if supabase:
            return {"status": "Success", "message": "Successfully connected to Supabase PostgreSQL! 🎉"}
    except Exception as e:
        return {"status": "Error", "message": str(e)}
    

# --- DATA MODELS ---
class HistoryCreate(BaseModel):
    user_email: str
    match_score: float
    semantic_score: float
    missing_skills: List[str]

# --- ROUTES ---

# 1. Save Analysis to Database
@app.post("/api/history")
def save_history(data: HistoryCreate):
    try:
        # Insert data into the Supabase table we just created
        response = supabase.table("resume_history").insert({
            "user_email": data.user_email,
            "match_score": data.match_score,
            "semantic_score": data.semantic_score,
            "missing_skills": data.missing_skills
        }).execute()
        return {"status": "success", "data": response.data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 2. Get User History from Database
@app.get("/api/history/{email}")
def get_history(email: str):
    try:
        # Fetch all rows where the email matches
        response = supabase.table("resume_history").select("*").eq("user_email", email).execute()
        return {"status": "success", "data": response.data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    

        # 3. Main Analysis Endpoint
@app.post("/api/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    try:
        # 1. Validate File Type
        if resume.content_type != "application/pdf":
            return {"status": "error", "message": "Please upload a valid PDF file."}

        # 2. Extract Text using pdfplumber
        text = ""
        with pdfplumber.open(resume.file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        
        if not text.strip():
            return {"status": "error", "message": "Could not extract text. The PDF might be an image."}

        # 3. The "Brain" - Clean text and calculate scores
        cleaned_text = clean_text(text)
        resume_skills = extract_skills_from_text(cleaned_text)
        
        jd_clean = job_description.lower()
        jd_skills = extract_skills_from_text(jd_clean)
        
        match_pct, matched, missing = match_skills(resume_skills, jd_skills)
        sem_score = calculate_semantic_match(cleaned_text, jd_clean)

        # 4. Return the Final JSON Response
        return {
            "status": "success",
            "data": {
                "ats_score": match_pct,
                "semantic_score": sem_score,
                # Convert 'sets' to 'lists' so FastAPI can send them as JSON
                "matched_skills": list(matched), 
                "missing_skills": list(missing)
            }
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
    


class RewriteRequest(BaseModel):
    bullet_point: str

@app.post("/api/rewrite")
def api_rewrite_bullet(data: RewriteRequest):
    try:
        # Call your function from the utils folder
        improved_text = optimize_bullet_point(data.bullet_point)

        return {
            "status": "success",
            "original": data.bullet_point,
            "improved": improved_text
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}