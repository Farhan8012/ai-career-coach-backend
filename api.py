import os
from dotenv import load_dotenv
from fastapi import FastAPI
from supabase import create_client, Client
from pydantic import BaseModel
from typing import List

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