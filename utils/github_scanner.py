import os
import requests
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def analyze_github_profile(username: str):
    """Fetches a user's GitHub profile, repos, and calculates language stats."""
    
    # We use the token so GitHub doesn't block us for making too many requests
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    
    try:
        # 1. Fetch Basic Profile Info
        user_url = f"https://api.github.com/users/{username}"
        user_response = requests.get(user_url, headers=headers)
        
        if user_response.status_code != 200:
            return {"status": "error", "message": f"Could not find GitHub user: {username}"}
            
        user_data = user_response.json()
        
        # 2. Fetch User's Repositories
        repos_url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"
        repos_response = requests.get(repos_url, headers=headers)
        repos_data = repos_response.json() if repos_response.status_code == 200 else []
        
        # 3. Calculate Stats (Stars and Languages)
        languages = {}
        total_stars = 0
        
        for repo in repos_data:
            # Add up the stars
            total_stars += repo.get("stargazers_count", 0)
            
            # Count the programming languages used
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
                
        return {
            "status": "success",
            "data": {
                "username": username,
                "name": user_data.get("name") or username,
                "bio": user_data.get("bio"),
                "public_repos": user_data.get("public_repos"),
                "total_stars": total_stars,
                "top_languages": languages
            }
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
    


def generate_dev_scorecard(github_stats: dict):
    """Passes GitHub stats to Gemini to generate a developer evaluation."""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        You are an expert Technical Recruiter evaluating a candidate's GitHub profile.
        Here is the raw data:
        - Username: {github_stats.get('username')}
        - Total Repos: {github_stats.get('public_repos')}
        - Total Stars Earned: {github_stats.get('total_stars')}
        - Top Languages Used: {github_stats.get('top_languages')}
        
        Task: Write a short, punchy, 3-sentence "Developer Score Card" summary. 
        Highlight their primary tech stack and overall open-source activity. Keep it professional and encouraging.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Could not generate AI scorecard: {str(e)}"