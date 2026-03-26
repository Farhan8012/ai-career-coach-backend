import os
import google.generativeai as genai

def setup_gemini():
    # Changed this line to match your .env file!
    api_key = os.getenv("GOOGLE_API_KEY") 
    if not api_key:
        print("Warning: GOOGLE_API_KEY not found in environment variables.")
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

def generate_dsa_question(resume_text: str):
    model = setup_gemini()
    if not model:
        return "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.\n\nExample:\nInput: nums = [2,7,11,15], target = 9\nOutput: [0,1]"
        
    prompt = f"""
    Based on the following candidate resume, generate a single Data Structures and Algorithms (DSA) interview question appropriate for their skill level.
    Just output the question text and an example. Do not output the solution.
    
    Resume:
    {resume_text}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating question: {str(e)}"

def evaluate_dsa_answer(question: str, user_code: str):
    model = setup_gemini()
    if not model:
        return "Error: Gemini API key not configured."
        
    prompt = f"""
    You are an expert technical interviewer. The candidate was asked this question:
    {question}
    
    Here is the code they submitted:
    {user_code}
    
    TASK:
    1. Give a VERY brief 1-2 sentence feedback (Is it correct? What is the Time/Space complexity?).
    2. Provide the optimal solution in a clean code block.
    
    STRICT RULE: Do NOT write long paragraphs or essays. Keep it punchy, professional, and short.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error evaluating code: {str(e)}"

# BRAND NEW: The Hint Generator
def get_dsa_hint(question: str):
    model = setup_gemini()
    if not model:
        return "Error: Gemini API key not configured."
        
    prompt = f"""
    The candidate is struggling with this DSA question:
    {question}
    
    Provide a single, short conceptual hint (max 2 sentences) to point them in the right direction. 
    STRICT RULE: Do NOT write any code. Do NOT give away the exact solution.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating hint: {str(e)}"