"""Stage 2 — Semantic skill matching.

TF-IDF vectors over skill text with cosine similarity. Character n-grams on
top of word tokens let related terms ("Data Analysis" / "Data Analytics",
"Machine Learning" / "ML Engineering") score as similar without exact
keyword overlap. Production path: sentence-transformer embeddings stored in
pgvector, queried with the same cosine metric.
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _skill_text(skills: list[str]) -> str:
    return " ".join(skills) if skills else ""


def skill_similarity_matrix(students: list[dict], internships: list[dict]) -> np.ndarray:
    """Rows = students, columns = internships; values in [0, 1]."""
    student_docs = [_skill_text(s["skills"]) for s in students]
    internship_docs = [_skill_text(j["skills_required"]) for j in internships]

    vectorizer = TfidfVectorizer(
        analyzer="char_wb", ngram_range=(3, 5), lowercase=True, min_df=1
    )
    matrix = vectorizer.fit_transform(student_docs + internship_docs)
    s_vecs = matrix[: len(student_docs)]
    j_vecs = matrix[len(student_docs):]
    return np.clip(cosine_similarity(s_vecs, j_vecs), 0.0, 1.0)
