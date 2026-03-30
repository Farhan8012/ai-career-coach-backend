import os
from google import genai

def setup_gemini():
    # Changed this line to match your .env file!
    api_key = os.getenv("GOOGLE_API_KEY") 
    if not api_key:
        print("Warning: GOOGLE_API_KEY not found in environment variables.")
        return None
    # Initialize the new Client instead of configuring the old module
    return genai.Client(api_key=api_key)

def generate_dsa_question(resume_text: str):
    client = setup_gemini()
    if not client:
        return "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.\n\nExample:\nInput: nums = [2,7,11,15], target = 9\nOutput: [0,1]"
        
    prompt = f"""
    Based on the following candidate resume, generate a single Data Structures and Algorithms (DSA) interview question appropriate for their skill level.
    Just output the question text and an example. Do not output the solution.
    
    Resume:
    {resume_text}
    """
    try:
        # New SDK syntax
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error generating question: {str(e)}"

def evaluate_dsa_answer(question: str, user_code: str):
    client = setup_gemini()
    if not client:
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
        # New SDK syntax
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error evaluating code: {str(e)}"

# BRAND NEW: The Senior Dev Hint Generator
def get_dsa_hint(question: str):
    client = setup_gemini() 
    if not client:
        return "Error: Gemini API key not configured."
        
    prompt = f"""
    You are an empathetic Senior Software Engineer mentoring a junior developer. 
    They are stuck on this DSA question:
    {question}
    
    Provide ONE actionable, concrete hint (max 2 sentences). 
    Suggest a specific data structure (e.g., "Try using a Hash Map to track complements") or a specific algorithmic pattern (e.g., "A two-pointer approach starting from both ends might work here").
    
    STRICT RULE: Do NOT write the actual code. Do NOT ask cryptic, philosophical questions. Be direct, technical, and helpful.
    """
    try:
        # New SDK syntax
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error generating hint: {str(e)}"