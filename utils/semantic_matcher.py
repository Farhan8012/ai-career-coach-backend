import re

def calculate_semantic_match(resume_text: str, job_description: str) -> int:
    """
    A lightweight, pure-Python Jaccard Similarity algorithm to replace scikit-learn.
    """
    def get_words(text):
        words = re.findall(r'\w+', str(text).lower())
        return set(words)

    resume_words = get_words(resume_text)
    job_words = get_words(job_description)

    if not job_words:
        return 0

    intersection = resume_words.intersection(job_words)
    union = resume_words.union(job_words)

    score = (len(intersection) / len(union)) * 100 if union else 0
    adjusted_score = min(int(score * 1.5), 100)
    
    return adjusted_score