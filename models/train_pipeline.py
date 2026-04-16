"""Training entrypoint for preprocessing, vectorization, LSH indexing, and artifact saving."""

from __future__ import annotations

import argparse

from .config import (
    ARTIFACTS_DIR,
    CREDITS_CSV_PATH,
    DEFAULT_TOP_N,
    LSH_INDEX_PATH,
    MINHASH_STORE_PATH,
    MOVIES_CSV_PATH,
    PROCESSED_CSV_PATH,
    PROCESSED_PICKLE_PATH,
    TFIDF_MATRIX_PATH,
    TFIDF_VECTORIZER_PATH,
)
from .lsh_recommender import build_lsh_index
from .preprocessing import preprocess_movies, save_processed_dataset
from .utils import save_pickle


def train_pipeline(
    query_movie: str,
    top_n: int = DEFAULT_TOP_N,
    analysis_compare: bool = False,
    skip_full_similarity: bool = False,
) -> None:
    """Train LSH production artifacts and optionally run cosine analysis."""
    print("[1/3] Preprocessing TMDB datasets...")
    processed_df = preprocess_movies(MOVIES_CSV_PATH, CREDITS_CSV_PATH)
    save_processed_dataset(processed_df, PROCESSED_CSV_PATH)
    print(f"Processed dataset saved to: {PROCESSED_CSV_PATH}")

    print("\n[2/3] Building LSH index...")
    lsh_index, minhash_store = build_lsh_index(processed_df)
    print(f"Indexed {len(minhash_store)} movie signatures with LSH.")

    print("\n[3/3] Saving production artifacts...")
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    save_pickle(processed_df, ARTIFACTS_DIR / PROCESSED_PICKLE_PATH.name)
    save_pickle(lsh_index, ARTIFACTS_DIR / LSH_INDEX_PATH.name)
    save_pickle(minhash_store, ARTIFACTS_DIR / MINHASH_STORE_PATH.name)
    print(f"Artifacts saved to: {ARTIFACTS_DIR}")

    if not analysis_compare:
        print("\nSkipped cosine comparison (LSH production mode).")
        return

    from .compare_models import compare_recommenders, print_comparison_report
    from .vectorization import build_tfidf_vectors, compute_similarity_matrix

    print("\n[analysis] Building TF-IDF vectors for cosine-vs-LSH comparison...")
    vectorizer, tfidf_matrix = build_tfidf_vectors(processed_df)
    print(f"TF-IDF shape: {tfidf_matrix.shape}")
    save_pickle(vectorizer, ARTIFACTS_DIR / TFIDF_VECTORIZER_PATH.name)
    save_pickle(tfidf_matrix, ARTIFACTS_DIR / TFIDF_MATRIX_PATH.name)

    if skip_full_similarity:
        print("Skipping full cosine similarity matrix computation.")
    else:
        print("[analysis] Computing full cosine similarity matrix...")
        similarity_matrix = compute_similarity_matrix(tfidf_matrix)
        print(f"Similarity matrix shape: {similarity_matrix.shape}")

    print("\n[analysis] Running cosine vs LSH comparison report...")
    comparison = compare_recommenders(
        movie_name=query_movie,
        movies_df=processed_df,
        tfidf_matrix=tfidf_matrix,
        lsh_index=lsh_index,
        minhash_store=minhash_store,
        top_n=top_n,
    )
    print_comparison_report(comparison)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Train LSH movie recommendation artifacts."
    )
    parser.add_argument(
        "--movie",
        default="Avatar",
        help="Movie title used if analysis comparison is enabled.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=DEFAULT_TOP_N,
        help="Number of recommendations used in analysis comparison.",
    )
    parser.add_argument(
        "--analysis-compare",
        action="store_true",
        help="Run cosine-vs-LSH analysis flow and save TF-IDF artifacts.",
    )
    parser.add_argument(
        "--skip-full-similarity",
        action="store_true",
        help="With --analysis-compare, skip full NxN cosine similarity matrix computation.",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    train_pipeline(
        query_movie=args.movie,
        top_n=args.top_n,
        analysis_compare=args.analysis_compare,
        skip_full_similarity=args.skip_full_similarity,
    )


if __name__ == "__main__":
    main()
