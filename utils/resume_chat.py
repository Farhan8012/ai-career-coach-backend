from google import genai
import streamlit as st

def ask_resume_question(resume_text, question):
    """
    Answers a specific question about the resume text.
    """
    try:
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

        prompt = f"""
        You are an intelligent assistant helping a recruiter analyze a resume.
        
        RESUME TEXT:
        {resume_text}
        
        USER QUESTION:
        {question}
        
        INSTRUCTIONS:
        1. Answer the question based ONLY on the resume text provided.
        2. If the information is not in the resume, say "I cannot find that information in the resume."
        3. Be concise and professional.
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text

    except Exception as e:
        return f"Error processing question: {str(e)}"