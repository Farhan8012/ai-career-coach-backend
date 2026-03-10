import os
import google.generativeai as genai

# Use the API key from the environment
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_dsa_question(resume_text: str):
    """Reads the resume and generates a custom DSA question."""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        Act as a Senior FAANG Interviewer.
        Read this candidate's resume and generate ONE Data Structures and Algorithms (DSA) question tailored to their experience level.
        Resume: {resume_text[:2000]}
        
        Format your response EXACTLY like this (do not use markdown blocks for the format words):
        QUESTION:
        [Write the problem statement here]
        
        BOILERPLATE:
        [Write the starting Python def function here]
        """
        response = model.generate_content(prompt)
        text = response.text
        
        # Split the response into the question and the starting code
        if "BOILERPLATE:" in text:
            parts = text.split("BOILERPLATE:")
            question = parts[0].replace("QUESTION:", "").strip()
            boilerplate = parts[1].strip()
        else:
            question = text.replace("QUESTION:", "").strip()
            boilerplate = "def solve():\n    # Write your code here\n    pass"
            
        return {"question": question, "boilerplate": boilerplate}
    except Exception as e:
        return {"error": str(e)}

def evaluate_dsa_answer(question: str, user_code: str):
    """Evaluates the candidate's Python code."""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        Act as a Senior FAANG Interviewer. 
        Here is the DSA question you asked the candidate: {question}
        
        Here is the candidate's Python code:
        {user_code}
        
        Provide strict but encouraging feedback. Include:
        1. Is it functionally correct?
        2. Time and Space Complexity.
        3. Any edge cases they missed.
        Keep it under 150 words.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return str(e)