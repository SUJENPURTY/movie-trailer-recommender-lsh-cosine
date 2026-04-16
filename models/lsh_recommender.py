"""Locality Sensitive Hashing recommendation logic using datasketch."""

from __future__ import annotations

from typing import Dict, Iterable, Tuple

import pandas as pd
from datasketch import MinHash, MinHashLSH

from .config import LSH_THRESHOLD, MINHASH_NUM_PERM
from .utils import resolve_movie_index


def create_minhash(tokens: Iterable[str], num_perm: int = MINHASH_NUM_PERM) -> MinHash:
    """Create a MinHash signature for a set of tokens."""
    signature = MinHash(num_perm=num_perm)
    for token in sorted(set(tokens)):
        signature.update(token.encode("utf8"))
    return signature


def build_lsh_index(
    movies_df: pd.DataFrame,
    num_perm: int = MINHASH_NUM_PERM,
    threshold: float = LSH_THRESHOLD,
) -> Tuple[MinHashLSH, Dict[str, MinHash]]:
    """Build MinHash signatures and LSH index for all movies."""
    if "tags" not in movies_df.columns:
        raise ValueError("Input dataframe must contain a 'tags' column.")

    lsh_index = MinHashLSH(threshold=threshold, num_perm=num_perm)
    minhash_store: Dict[str, MinHash] = {}

    for row_index, tags_text in enumerate(movies_df["tags"].fillna("")):
        movie_key = str(row_index)
        tokens = str(tags_text).split()
        signature = create_minhash(tokens, num_perm=num_perm)
        lsh_index.insert(movie_key, signature)
        minhash_store[movie_key] = signature

    return lsh_index, minhash_store


def recommend_lsh(
    movie_name: str,
    movies_df: pd.DataFrame,
    lsh_index: MinHashLSH,
    minhash_store: Dict[str, MinHash],
    top_n: int = 5,
) -> pd.DataFrame:
    """Recommend movies by querying MinHashLSH and ranking by Jaccard estimate."""
    movie_index = resolve_movie_index(movie_name, movies_df)
    query_key = str(movie_index)

    if query_key not in minhash_store:
        raise ValueError(f"MinHash signature missing for movie index {movie_index}.")

    query_signature = minhash_store[query_key]
    candidate_keys = lsh_index.query(query_signature)
    candidate_indices = []
    for key in candidate_keys:
        try:
            candidate_index = int(str(key))
        except (TypeError, ValueError):
            continue

        if candidate_index != movie_index:
            candidate_indices.append(candidate_index)

    if len(candidate_indices) < top_n:
        # Fallback to global candidate scan so we still return top_n results.
        candidate_indices = [idx for idx in range(len(movies_df)) if idx != movie_index]

    scored_candidates = []
    for candidate_index in candidate_indices:
        candidate_key = str(candidate_index)
        candidate_signature = minhash_store.get(candidate_key)
        if candidate_signature is None:
            continue
        score = query_signature.jaccard(candidate_signature)
        scored_candidates.append((candidate_index, score))

    scored_candidates.sort(key=lambda item: item[1], reverse=True)
    top_matches = scored_candidates[:top_n]

    result_indices = [idx for idx, _ in top_matches]
    result_scores = [score for _, score in top_matches]

    result_df = movies_df.iloc[result_indices][
        ["tmdb_id", "title", "poster_path"]
    ].copy()
    result_df["score"] = result_scores
    result_df["method"] = "lsh"
    return result_df.reset_index(drop=True)
