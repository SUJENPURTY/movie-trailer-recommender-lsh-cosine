"""Utilities to compare cosine similarity and LSH recommendation methods."""

from __future__ import annotations

from time import perf_counter
from typing import Any, Dict

import pandas as pd
from datasketch import MinHash, MinHashLSH
from scipy.sparse import csr_matrix

from .lsh_recommender import recommend_lsh
from .vectorization import recommend_cosine


def compare_recommenders(
    movie_name: str,
    movies_df: pd.DataFrame,
    tfidf_matrix: csr_matrix,
    lsh_index: MinHashLSH,
    minhash_store: Dict[str, MinHash],
    top_n: int = 5,
) -> Dict[str, Any]:
    """Compare runtime and recommendation overlap for cosine vs LSH."""
    cosine_start = perf_counter()
    cosine_df = recommend_cosine(movie_name, movies_df, tfidf_matrix, top_n=top_n)
    cosine_time = perf_counter() - cosine_start

    lsh_start = perf_counter()
    lsh_df = recommend_lsh(movie_name, movies_df, lsh_index, minhash_store, top_n=top_n)
    lsh_time = perf_counter() - lsh_start

    cosine_titles = set(cosine_df["title"].tolist())
    lsh_titles = set(lsh_df["title"].tolist())
    overlap_titles = sorted(cosine_titles.intersection(lsh_titles))

    return {
        "movie_name": movie_name,
        "cosine_time_seconds": cosine_time,
        "lsh_time_seconds": lsh_time,
        "cosine_recommendations": cosine_df,
        "lsh_recommendations": lsh_df,
        "top_k_overlap_count": len(overlap_titles),
        "top_k_overlap_titles": overlap_titles,
    }


def print_comparison_report(comparison: Dict[str, Any]) -> None:
    """Print a human-readable comparison summary."""
    print("\n===== Recommendation Method Comparison =====")
    print(f"Query movie: {comparison['movie_name']}")
    print(f"Cosine time: {comparison['cosine_time_seconds']:.6f} seconds")
    print(f"LSH time:    {comparison['lsh_time_seconds']:.6f} seconds")

    print("\nCosine top recommendations:")
    for title in comparison["cosine_recommendations"]["title"].tolist():
        print(f"- {title}")

    print("\nLSH top recommendations:")
    for title in comparison["lsh_recommendations"]["title"].tolist():
        print(f"- {title}")

    overlap_count = comparison["top_k_overlap_count"]
    overlap_titles = comparison["top_k_overlap_titles"]
    print(f"\nTop-5 overlap count: {overlap_count}")
    print("Overlap titles:")
    if overlap_titles:
        for title in overlap_titles:
            print(f"- {title}")
    else:
        print("- None")
