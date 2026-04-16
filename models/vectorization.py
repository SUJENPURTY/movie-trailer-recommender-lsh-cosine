"""TF-IDF vectorization and cosine recommendation logic."""

from __future__ import annotations

from typing import Tuple

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel

from .config import TFIDF_MAX_FEATURES
from .utils import resolve_movie_index


def build_tfidf_vectors(
    movies_df: pd.DataFrame,
    max_features: int = TFIDF_MAX_FEATURES,
) -> Tuple[TfidfVectorizer, csr_matrix]:
    """Build TF-IDF vectors from the `tags` column."""
    if "tags" not in movies_df.columns:
        raise ValueError("Input dataframe must contain a 'tags' column.")

    vectorizer = TfidfVectorizer(max_features=max_features, stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(movies_df["tags"].fillna(""))
    return vectorizer, tfidf_matrix


def compute_similarity_matrix(tfidf_matrix: csr_matrix) -> np.ndarray:
    """Compute full cosine similarity matrix."""
    return cosine_similarity(tfidf_matrix).astype("float32")


def recommend_cosine(
    movie_name: str,
    movies_df: pd.DataFrame,
    tfidf_matrix: csr_matrix,
    top_n: int = 5,
) -> pd.DataFrame:
    """Recommend movies based on cosine similarity over TF-IDF vectors."""
    movie_index = resolve_movie_index(movie_name, movies_df)

    # Using linear_kernel here avoids materializing the full NxN matrix for inference.
    scores = linear_kernel(tfidf_matrix[movie_index : movie_index + 1], tfidf_matrix).flatten()
    scores[movie_index] = -1.0

    top_indices = np.argsort(scores)[::-1][:top_n]

    result_df = movies_df.iloc[top_indices][["tmdb_id", "title", "poster_path"]].copy()
    result_df["score"] = scores[top_indices]
    result_df["method"] = "cosine"
    return result_df.reset_index(drop=True)
