"""Model loading, recommendation serving, and TMDB trailer helpers."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from requests import RequestException

from .config import (
    ARTIFACTS_DIR,
    DEFAULT_TOP_N,
    LSH_INDEX_PATH,
    MINHASH_STORE_PATH,
    POSTER_BASE_URL,
    PROCESSED_PICKLE_PATH,
    TFIDF_MATRIX_PATH,
    TMDB_API_BASE_URL,
)
from .lsh_recommender import recommend_lsh
from .utils import load_pickle
from .vectorization import recommend_cosine


class MovieRecommender:
    """Load trained artifacts and serve movie recommendations."""

    def __init__(
        self,
        movies_df: pd.DataFrame,
        lsh_index: Any,
        minhash_store: Dict[str, Any],
        tfidf_matrix: Any | None = None,
    ) -> None:
        self.movies_df = movies_df.reset_index(drop=True)
        self.lsh_index = lsh_index
        self.minhash_store = minhash_store
        self.tfidf_matrix = tfidf_matrix

    @classmethod
    def from_artifacts(cls, artifacts_dir: Path = ARTIFACTS_DIR) -> "MovieRecommender":
        """Construct recommender from saved pickle artifacts."""
        required_paths = [
            artifacts_dir / PROCESSED_PICKLE_PATH.name,
            artifacts_dir / LSH_INDEX_PATH.name,
            artifacts_dir / MINHASH_STORE_PATH.name,
        ]

        missing_paths = [str(path) for path in required_paths if not path.exists()]
        if missing_paths:
            missing_summary = "\n".join(missing_paths)
            raise FileNotFoundError(
                "Missing artifact files. Run `python -m models.train_pipeline` first.\n"
                f"Missing files:\n{missing_summary}"
            )

        movies_df = load_pickle(artifacts_dir / PROCESSED_PICKLE_PATH.name)
        lsh_index = load_pickle(artifacts_dir / LSH_INDEX_PATH.name)
        minhash_store = load_pickle(artifacts_dir / MINHASH_STORE_PATH.name)
        tfidf_matrix_path = artifacts_dir / TFIDF_MATRIX_PATH.name
        tfidf_matrix = (
            load_pickle(tfidf_matrix_path) if tfidf_matrix_path.exists() else None
        )

        return cls(
            movies_df=movies_df,
            lsh_index=lsh_index,
            minhash_store=minhash_store,
            tfidf_matrix=tfidf_matrix,
        )

    @staticmethod
    def build_poster_url(poster_path: Optional[str]) -> Optional[str]:
        """Build full TMDB poster URL from poster path."""
        if poster_path is None or pd.isna(poster_path):
            return None

        poster_path = str(poster_path).strip()
        if not poster_path:
            return None

        return f"{POSTER_BASE_URL}{poster_path}"

    def list_titles(self, limit: int = 300) -> List[str]:
        """Return a list of movie titles for autocomplete use."""
        titles = self.movies_df["title"].dropna().astype(str).drop_duplicates().tolist()
        return sorted(titles)[:limit]

    def browse_movies(
        self,
        limit: int = 36,
        api_key: str | None = None,
    ) -> List[Dict[str, Any]]:
        """Return a default movie gallery for the home page."""
        browse_df = self.movies_df.copy()
        browse_df["poster_url"] = browse_df["poster_path"].apply(self.build_poster_url)

        # Prefer more popular titles in the default gallery.
        browse_df = browse_df.sort_values(
            by=["vote_count", "vote_average"],
            ascending=[False, False],
            kind="mergesort",
        )

        records: List[Dict[str, Any]] = []
        for row in browse_df.head(limit).to_dict(orient="records"):
            tmdb_id = int(row["tmdb_id"])
            poster_url = row.get("poster_url")
            if not poster_url:
                poster_url = fetch_tmdb_poster_url(tmdb_id, api_key)

            vote_average_raw = row.get("vote_average", 0.0)
            vote_average = (
                float(vote_average_raw) if pd.notna(vote_average_raw) else 0.0
            )
            records.append(
                {
                    "tmdb_id": tmdb_id,
                    "title": str(row["title"]),
                    "poster_url": poster_url,
                    "release_date": str(row.get("release_date", "")),
                    "vote_average": vote_average,
                }
            )

        return records

    def recommend(
        self,
        movie_name: str,
        top_n: int = DEFAULT_TOP_N,
        method: str = "lsh",
        api_key: str | None = None,
    ) -> List[Dict[str, Any]]:
        """Return top movie recommendations using the selected method."""
        method_name = str(method).strip().lower()

        if method_name == "cosine":
            if self.tfidf_matrix is None:
                raise ValueError(
                    "Cosine artifacts are not available. "
                    "Run `python -m models.train_pipeline --analysis-compare`."
                )
            recommendation_df = recommend_cosine(
                movie_name=movie_name,
                movies_df=self.movies_df,
                tfidf_matrix=self.tfidf_matrix,
                top_n=top_n,
            )
        elif method_name == "lsh":
            recommendation_df = recommend_lsh(
                movie_name=movie_name,
                movies_df=self.movies_df,
                lsh_index=self.lsh_index,
                minhash_store=self.minhash_store,
                top_n=top_n,
            )
        else:
            raise ValueError(f"Unsupported recommendation method: {method}")

        recommendation_df = recommendation_df.copy()
        recommendation_df["poster_url"] = recommendation_df["poster_path"].apply(
            self.build_poster_url
        )

        records: List[Dict[str, Any]] = []
        for row in recommendation_df.to_dict(orient="records"):
            tmdb_id = int(row["tmdb_id"])
            poster_url = row.get("poster_url")
            if not poster_url:
                poster_url = fetch_tmdb_poster_url(tmdb_id, api_key)

            records.append(
                {
                    "tmdb_id": tmdb_id,
                    "title": str(row["title"]),
                    "poster_path": row.get("poster_path"),
                    "poster_url": poster_url,
                    "score": float(row["score"]),
                    "method": method_name,
                }
            )

        return records

    def get_movie(self, tmdb_id: int) -> Optional[Dict[str, Any]]:
        """Fetch movie metadata by TMDB movie id."""
        matches = self.movies_df[self.movies_df["tmdb_id"] == tmdb_id]
        if matches.empty:
            return None

        row = matches.iloc[0]
        vote_average_raw = row.get("vote_average", 0.0)
        vote_count_raw = row.get("vote_count", 0)

        vote_average = float(vote_average_raw) if pd.notna(vote_average_raw) else 0.0
        vote_count = int(vote_count_raw) if pd.notna(vote_count_raw) else 0

        return {
            "tmdb_id": int(row["tmdb_id"]),
            "title": str(row["title"]),
            "overview": str(row.get("overview", "")),
            "release_date": str(row.get("release_date", "")),
            "vote_average": vote_average,
            "vote_count": vote_count,
            "poster_url": self.build_poster_url(row.get("poster_path")),
        }


def fetch_tmdb_trailer_key(tmdb_movie_id: int, api_key: str | None) -> Optional[str]:
    """Fetch first available YouTube trailer key from TMDB."""
    if not api_key:
        return None

    endpoint = f"{TMDB_API_BASE_URL}/movie/{tmdb_movie_id}/videos"

    try:
        response = requests.get(endpoint, params={"api_key": api_key}, timeout=10)
        response.raise_for_status()
    except RequestException:
        return None

    payload = response.json()
    videos = payload.get("results", [])

    # Prefer official trailers first.
    for video in videos:
        if (
            video.get("site") == "YouTube"
            and video.get("type") == "Trailer"
            and video.get("official") is True
            and video.get("key")
        ):
            return str(video["key"])

    # Fallback to any YouTube trailer or teaser.
    for video in videos:
        if (
            video.get("site") == "YouTube"
            and video.get("type") in {"Trailer", "Teaser"}
            and video.get("key")
        ):
            return str(video["key"])

    return None


def fetch_tmdb_poster_url(tmdb_movie_id: int, api_key: str | None) -> Optional[str]:
    """Fetch movie poster URL from TMDB when local poster data is missing."""
    if not api_key:
        return None

    try:
        poster_path = _fetch_tmdb_poster_path_cached(tmdb_movie_id, api_key)
    except RequestException:
        return None

    return MovieRecommender.build_poster_url(poster_path)


@lru_cache(maxsize=2048)
def _fetch_tmdb_poster_path_cached(tmdb_movie_id: int, api_key: str) -> Optional[str]:
    """Fetch and cache TMDB poster path by movie id and API key."""
    endpoint = f"{TMDB_API_BASE_URL}/movie/{tmdb_movie_id}"

    response = requests.get(endpoint, params={"api_key": api_key}, timeout=10)
    response.raise_for_status()

    payload = response.json()
    poster_path = payload.get("poster_path")
    if poster_path is None:
        return None

    poster_path = str(poster_path).strip()
    if not poster_path:
        return None

    return poster_path
