import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from supabase import create_client, Client
from pydantic import BaseModel
from typing import List
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse 
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber

from utils.text_cleaner import clean_text
from utils.ats_matcher import extract_skills_from_text, match_skills
from utils.semantic_matcher import calculate_semantic_match
from utils.resume_rewriter import optimize_bullet_point
from utils.learning_roadmap import generate_study_plan
from utils.cover_letter_generator import generate_cover_letter  
from utils.interview_prep import generate_interview_questions 
from utils.github_scanner import analyze_github_profile, generate_dev_scorecard
from utils.pdf_generator import create_pdf_report
from utils.dsa_interviewer import generate_dsa_question, evaluate_dsa_answer

# 1. Load environment variables
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# 2. Initialize App
app = FastAPI(
    title="AI Career Coach API",
    description="The backend engine for the v2.0 Resume Analyzer",
    version="2.0.0"
)

# --- CORS SETUP ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "https://ai-career-coach-frontend-peach.vercel.app"
    ], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# --- DATA MODELS ---
class UserCredentials(BaseModel):
    email: str
    password: str

# BRAND NEW: Sign Up model includes Profile Data
class UserSignUp(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    target_role: str

class DSAEvalRequest(BaseModel):
    question: str
    user_code: str

class HistoryCreate(BaseModel):
    user_email: str
    match_score: float
    semantic_score: float
    missing_skills: List[str]

class RewriteRequest(BaseModel):
    bullet_point: str

class CoverLetterRequest(BaseModel):
    resume_text: str
    job_description: str

class StudyPlanRequest(BaseModel):
    missing_skills: List[str]

class InterviewPrepRequest(BaseModel):
    resume_text: str
    job_role: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Career Coach API v2.0! 🚀", "status": "Online"}

@app.get("/test-db")
def test_database_connection():
    try:
        if supabase:
            return {"status": "Success", "message": "Successfully connected to Supabase PostgreSQL! 🎉"}
    except Exception as e:
        return {"status": "Error", "message": str(e)}

# --- ROUTES ---

@app.post("/api/history")
def save_history(data: HistoryCreate):
    try:
        response = supabase.table("resume_history").insert({
            "user_email": data.user_email,
            "match_score": data.match_score,
            "semantic_score": data.semantic_score,
            "missing_skills": data.missing_skills
        }).execute()
        return {"status": "success", "data": response.data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/history/{email}")
def get_history(email: str):
    try:
        response = supabase.table("resume_history").select("*").eq("user_email", email).execute()
        return {"status": "success", "data": response.data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    try:
        if resume.content_type != "application/pdf":
            return {"status": "error", "message": "Please upload a valid PDF file."}

        text = ""
        with pdfplumber.open(resume.file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        
        if not text.strip():
            return {"status": "error", "message": "Could not extract text. The PDF might be an image."}

        cleaned_text = clean_text(text)
        resume_skills = extract_skills_from_text(cleaned_text)
        
        jd_clean = job_description.lower()
        jd_skills = extract_skills_from_text(jd_clean)
        
        match_pct, matched, missing = match_skills(resume_skills, jd_skills)
        sem_score = calculate_semantic_match(cleaned_text, jd_clean)

        return {
            "status": "success",
            "data": {
                "ats_score": match_pct,
                "semantic_score": sem_score,
                "matched_skills": list(matched), 
                "missing_skills": list(missing)
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/rewrite")
def api_rewrite_bullet(data: RewriteRequest):
    try:
        improved_text = optimize_bullet_point(data.bullet_point)
        return {
            "status": "success",
            "original": data.bullet_point,
            "improved": improved_text
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/study-plan")
def api_study_plan(data: StudyPlanRequest):
    try:
        plan = generate_study_plan(data.missing_skills)
        return {"status": "success", "study_plan": plan}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/cover-letter")
async def api_cover_letter(
    job_description: str = Form(...),
    resume: UploadFile = File(...)
):
    try:
        if resume.content_type != "application/pdf":
            return {"status": "error", "message": "Please upload a valid PDF file."}

        text = ""
        with pdfplumber.open(resume.file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

        cover_letter = generate_cover_letter(text, job_description)
        return {"status": "success", "cover_letter": cover_letter}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- THE MASTER ENDPOINT ---

@app.post("/api/evaluate-candidate")
async def evaluate_candidate(
    github_username: str = Form(...),
    job_description: str = Form(...),
    resume: UploadFile = File(...)
):
    try:
        if resume.content_type != "application/pdf":
            return {"status": "error", "message": "Please upload a valid PDF file."}

        text = ""
        with pdfplumber.open(resume.file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

        cleaned_text = clean_text(text)
        resume_skills = extract_skills_from_text(cleaned_text)
        jd_clean = job_description.lower()
        jd_skills = extract_skills_from_text(jd_clean)
        
        match_pct, matched, missing = match_skills(resume_skills, jd_skills)
        sem_score = calculate_semantic_match(cleaned_text, jd_clean)

        github_data = analyze_github_profile(github_username)
        
        if github_data and isinstance(github_data, dict) and "public_repos" in github_data:
            github_data["ai_scorecard"] = generate_dev_scorecard(github_data)
        else:
            github_data = {"public_repos": 0, "total_stars": 0, "total_forks": 0, "top_languages": {}, "ai_scorecard": "No GitHub data found."}

        try:
            db_record = {
                "github_username": github_username,
                "ats_score": float(match_pct),
                "semantic_score": float(sem_score),
                "ai_scorecard": github_data.get("ai_scorecard", ""),
                "matched_skills": list(matched),
                "missing_skills": list(missing)
            }
            supabase.table("evaluations").insert(db_record).execute()
        except Exception as db_error:
            print(f"Database warning: Could not save record. {db_error}")

        return {
            "status": "success",
            "candidate_evaluation": {
                "resume_metrics": {
                    "ats_score": match_pct,
                    "semantic_score": sem_score,
                    "matched_skills": list(matched),
                    "missing_skills": list(missing)
                },
                "github_metrics": github_data
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/github/{username}")
def api_get_github_profile(username: str):
    try:
        result = analyze_github_profile(username)
        
        if result and isinstance(result, dict) and "public_repos" in result:
            ai_summary = generate_dev_scorecard(result)
            result["ai_scorecard"] = ai_summary
            return {"status": "success", "data": result}
        
        return {"status": "error", "message": "Could not fetch GitHub data."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- AUTHENTICATION & PROFILE FLOW ---

@app.post("/api/signup")
async def sign_up(credentials: UserSignUp):
    try:
        # 1. Create the secure user in Supabase Auth
        response = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password
        })
        
        # 2. If successful, save their profile data to the table we just upgraded!
        if response.user:
            supabase.table("profiles").upsert({
                "id": response.user.id,
                "first_name": credentials.first_name,
                "last_name": credentials.last_name,
                "target_role": credentials.target_role
            }).execute()
            
        return {
            "status": "success", 
            "message": f"Welcome aboard, {credentials.first_name}! 🎉"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/login")
async def log_in(credentials: UserCredentials):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        
        session = response.session
        if session:
            return {
                "status": "success",
                "message": "Login successful!",
                "access_token": session.access_token
            }
        else:
            return {"status": "error", "message": "Could not log in. Please check your credentials."}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- SECURITY CHECKPOINT ---
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return user_response.user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

@app.get("/api/me")
async def get_my_profile(user = Depends(get_current_user)):
    try:
        # 1. Fetch the user's custom profile data from our table
        profile_response = supabase.table("profiles").select("*").eq("id", user.id).execute()
        profile_data = profile_response.data[0] if profile_response.data else {}

        # 2. Return everything to the frontend
        return {
            "status": "success",
            "user_email": user.email,
            "first_name": profile_data.get("first_name", "Developer"),
            "last_name": profile_data.get("last_name", ""),
            "target_role": profile_data.get("target_role", "Software Engineer")
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- PDF GENERATION ---
@app.post("/api/generate-pdf")
async def generate_pdf(eval_data: dict):
    try:
        temp_filename = "candidate_report.pdf"
        create_pdf_report(eval_data, temp_filename)
        return FileResponse(
            path=temp_filename, 
            filename="AI_Developer_Scorecard.pdf", 
            media_type="application/pdf"
        )
    except Exception as e:
        return {"status": "error", "message": f"Could not generate PDF: {str(e)}"}

# --- DSA INTERVIEW ENDPOINTS ---
@app.post("/api/dsa-question")
async def api_dsa_question(resume: UploadFile = File(...)):
    try:
        if resume.content_type != "application/pdf":
            return {"status": "error", "message": "Please upload a valid PDF."}

        text = ""
        with pdfplumber.open(resume.file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        
        result = generate_dsa_question(text)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/dsa-evaluate")
def api_dsa_evaluate(data: DSAEvalRequest):
    try:
        feedback = evaluate_dsa_answer(data.question, data.user_code)
        return {"status": "success", "feedback": feedback}
    except Exception as e:
        return {"status": "error", "message": str(e)}