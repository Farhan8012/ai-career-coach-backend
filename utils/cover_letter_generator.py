import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_cover_letter(resume_text, jd_text, company_name="Hiring Manager"):
    """
    Generates a personalized cover letter connecting resume projects to JD requirements.
    """
    try:
        prompt = f"""
        You are an expert Career Coach and Professional Copywriter.
        Write a convincing Cover Letter for a candidate applying to this job.
        
        RESUME:
        {resume_text[:3000]}
        
        JOB DESCRIPTION:
        {jd_text[:2000]}
        
        RULES:
        1. Tone: Professional, confident, but NOT robotic. Sound human.
        2. Structure:
           - Opening: State excitement for the role.
           - Body Paragraph 1: Connect a SPECIFIC project from the resume to a KEY requirement in the JD.
           - Body Paragraph 2: Mention soft skills or culture fit based on the resume.
           - Closing: Call to action (request interview).
        3. Do not use placeholders like [Insert Name]. Use "{company_name}" as the recipient.
        4. Keep it concise (under 300 words).
        
        Output only the body of the letter.
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text

    except Exception as e:
        return f"Error generating cover letter: {str(e)}"