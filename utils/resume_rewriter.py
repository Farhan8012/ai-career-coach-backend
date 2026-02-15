import os
from dotenv import load_dotenv
import google.generativeai as genai

# 1. Load environment variables from .env
load_dotenv()

# 2. Configure Gemini using the key from .env (Do this globally, outside the function)
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def optimize_bullet_point(bullet_text):
    """Rewrites a resume bullet point to follow the XYZ formula."""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        You are a Professional Resume Editor.
        I will give you a "Weak" resume bullet point.
        
        Your Goal: Rewrite it into 3 different "Strong" versions using active voice and metrics.
        
        WEAK BULLET: "{bullet_text}"
        
        RULES:
        1. Use "Action Verbs" (e.g., Engineered, Spearheaded, Optimized).
        2. If no numbers are provided, add placeholders like [X%] or [Y hours] for the user to fill in.
        3. Make it sound professional but realistic.
        4. Output format: Just the 3 options, numbered.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error optimizing text: {str(e)}"