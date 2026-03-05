import re

def calculate_semantic_match(resume_text: str, job_description: str) -> int:
    """
    A lightweight, pure-Python Jaccard Similarity algorithm to replace scikit-learn.
    Compares the overlap of words between the resume and the job description.
    """
    def get_words(text):
        # Convert to lowercase and extract only alphanumeric words
        words = re.findall(r'\w+', str(text).lower())
        return set(words)

    resume_words = get_words(resume_text)
    job_words = get_words(job_description)

    if not job_words:
        return 0

    # Calculate Jaccard Similarity: (Intersection / Union) * 100
    intersection = resume_words.intersection(job_words)
    union = resume_words.union(job_words)

    score = (len(intersection) / len(union)) * 100 if union else 0
    
    # Boost the score slightly since strict word-matching is tough
    adjusted_score = min(int(score * 1.5), 100)
    
    return adjusted_score