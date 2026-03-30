import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Initialize the new client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_study_plan(missing_skills):
    """
    Generates a 5-day crash course for the identified missing skills.
    """
    try:
        skills_text = ", ".join(missing_skills)

        prompt = f"""
        You are a Senior Technical Mentor.
        The candidate is missing the following skills: {skills_text}.
        
        Create a customized "5-Day Crash Course" to help them learn the basics of these skills efficiently.
        
        STRUCTURE:
        - **Day 1-2: Concepts & Basics** (What is it? Why use it?)
        - **Day 3-4: Hands-on Practice** (Simple exercises or commands)
        - **Day 5: Mini Project Idea** (How to apply it to a resume project)
        - **Recommended Resources:** (Suggest specific official docs, YouTube channels, or free courses).
        
        Keep it concise, actionable, and encouraging.
        """

        # New SDK syntax for generating content
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text

    except Exception as e:
        return f"Error generating roadmap: {str(e)}"