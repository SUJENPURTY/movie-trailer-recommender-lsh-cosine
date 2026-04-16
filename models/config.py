"""Shared project paths and constants."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
ARTIFACTS_DIR = MODELS_DIR / "artifacts"

MOVIES_CSV_PATH = DATA_DIR / "tmdb_5000_movies.csv"
CREDITS_CSV_PATH = DATA_DIR / "tmdb_5000_credits.csv"
PROCESSED_CSV_PATH = DATA_DIR / "processed_movies.csv"

PROCESSED_PICKLE_PATH = ARTIFACTS_DIR / "processed_movies.pkl"
TFIDF_VECTORIZER_PATH = ARTIFACTS_DIR / "tfidf_vectorizer.pkl"
TFIDF_MATRIX_PATH = ARTIFACTS_DIR / "tfidf_matrix.pkl"
LSH_INDEX_PATH = ARTIFACTS_DIR / "lsh_index.pkl"
MINHASH_STORE_PATH = ARTIFACTS_DIR / "minhash_store.pkl"

DEFAULT_TOP_N = 5
TFIDF_MAX_FEATURES = 5000
MINHASH_NUM_PERM = 96
LSH_THRESHOLD = 0.2
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_API_BASE_URL = "https://api.themoviedb.org/3"
