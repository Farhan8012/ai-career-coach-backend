from fpdf import FPDF

def create_pdf_report(eval_data: dict, filename="candidate_report.pdf"):
    # 1. Create a blank PDF document
    pdf = FPDF()
    pdf.add_page()
    
    # 2. Add the Main Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "AI Candidate Evaluation Report", ln=True, align='C')
    pdf.ln(10) # Add a blank line for spacing
    
    # 3. Add Candidate Info & Scores
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, f"Candidate GitHub: {eval_data.get('github_username', 'N/A')}", ln=True)
    
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"ATS Match Score: {eval_data.get('ats_score', 0)}%", ln=True)
    pdf.cell(0, 8, f"Semantic Score: {eval_data.get('semantic_score', 0)}", ln=True)
    pdf.ln(5)
    
    # 4. Add Skills Section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Matched Skills:", ln=True)
    pdf.set_font("Arial", '', 11)
    matched = ", ".join(eval_data.get('matched_skills', []))
    # We use multi_cell here so the text wraps to the next line if it gets too long!
    pdf.multi_cell(0, 6, matched if matched else "None found")
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Missing Skills:", ln=True)
    pdf.set_font("Arial", '', 11)
    missing = ", ".join(eval_data.get('missing_skills', []))
    pdf.multi_cell(0, 6, missing if missing else "None found")
    pdf.ln(5)
    
    # 5. Add the AI Scorecard
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "AI Developer Scorecard:", ln=True)
    pdf.set_font("Arial", '', 11)
    
    # The AI text is usually a whole paragraph, so multi_cell is required here
    # We also encode/decode to 'latin-1' and 'replace' to handle any weird emojis or symbols Gemini might output
    ai_text = eval_data.get('ai_scorecard', 'No scorecard generated.')
    clean_text = ai_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 6, clean_text)
    
    # 6. Save the actual file!
    pdf.output(filename)
    return filename