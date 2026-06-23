
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def match_resumes(job_desc_text, resume_data):
    """
    Matches a job description with a list of resumes and ranks them by similarity.

    Args:
        job_desc_text (str): The text content of the job description.
        resume_data (list of tuple): A list where each tuple contains (resume_filename, resume_text_content).

    Returns:
        list of tuple: A list of (resume_filename, similarity_score) ranked in descending order of score.
    """

    if not resume_data:
        return []

    # Combine job description and resumes for vectorization
    documents = [job_desc_text] + [resume_text for _, resume_text in resume_data]

    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Compute cosine similarity between job description and resumes
    # tfidf_matrix[0:1] is the job description vector
    # tfidf_matrix[1:] are the resume vectors
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Rank resumes
    ranked_resumes = sorted(zip([filename for filename, _ in resume_data], cosine_similarities),
                            key=lambda x: x[1], reverse=True)

    return ranked_resumes
