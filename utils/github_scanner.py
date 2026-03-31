import os
import requests
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def get_github_metrics(username: str):
    """Fetches advanced GitHub metrics AND detailed repository data for the UI."""
    headers = {}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    try:
        # Fetch up to 100 public repositories
        response = requests.get(f"https://api.github.com/users/{username}/repos?per_page=100", headers=headers)
        
        if response.status_code != 200:
            return {"public_repos": 0, "total_stars": 0, "total_forks": 0, "top_languages": {}, "repositories": []}
            
        repos = response.json()
        
        # Calculate the aggregate metrics
        total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
        total_forks = sum(repo.get("forks_count", 0) for repo in repos)
        
        languages = {}
        repo_names = []
        detailed_repos = []
        
        for repo in repos:
            repo_names.append(repo.get("name", ""))
            
            # Tally up the languages
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
            
            # Grab the specific details for the Frontend UI Grid
            detailed_repos.append({
                "name": repo.get("name", "Unnamed Repo"),
                "description": repo.get("description") or "No description provided.",
                "url": repo.get("html_url", "#"),
                "stars": repo.get("stargazers_count", 0),
                "language": lang or "Mixed"
            })
                
        # Sort the detailed repos by Stars (highest first), so the best ones show up in the UI
        detailed_repos = sorted(detailed_repos, key=lambda x: x['stars'], reverse=True)
                
        return {
            "public_repos": len(repos),
            "total_stars": total_stars,
            "total_forks": total_forks,
            "top_languages": languages,
            "repo_names": repo_names[:15], # Keep top 15 names for the Gemini AI Prompt
            "repositories": detailed_repos[:6] # Send the top 6 fully-detailed repos to the Frontend UI
        }
        
    except Exception as e:
        print(f"GitHub Fetch Error: {e}")
        return {"public_repos": 0, "total_stars": 0, "total_forks": 0, "top_languages": {}, "repositories": []}
    

def generate_dev_scorecard(github_stats: dict):
    """Uses advanced GitHub stats to ask Gemini to generate a developer evaluation."""
    try:
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Format languages nicely for the AI
        langs = github_stats.get("top_languages", {})
        lang_str = ", ".join([f"{k} ({v})" for k, v in langs.items()]) if langs else "None"
        repos_str = ", ".join(github_stats.get("repo_names", []))
        
        prompt = f"""
        Act as an expert Senior Engineering Manager. 
        Write a 2-sentence "Developer Persona" summary for this candidate based on their GitHub data.
        Make it sound highly professional, impressive, and tailored exactly to their tech stack.
        
        GitHub Stats:
        - Public Repos: {github_stats.get("public_repos")}
        - Total Stars: {github_stats.get("total_stars")}
        - Total Forks: {github_stats.get("total_forks")}
        - Top Languages: {lang_str}
        - Key Repositories: {repos_str}
        
        Do not use formatting like bolding or bullet points. Just write the short paragraph.
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "An active developer consistently building projects and contributing to the open-source community."
    

def analyze_github_profile(username: str):
    """Wrapper function to connect the old api.py to our new upgraded metrics."""
    return get_github_metrics(username)