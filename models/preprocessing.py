"""Data preprocessing for TMDB movie recommendation workflows."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable, List

import pandas as pd


MOVIES_REQUIRED_COLUMNS = {
    "id",
    "title",
    "overview",
    "genres",
    "keywords",
    "release_date",
    "vote_average",
    "vote_count",
}

CREDITS_REQUIRED_COLUMNS = {"movie_id", "title", "cast", "crew"}


def _safe_literal_eval(value: str | list | float) -> list:
    """Safely parse list-like JSON strings in TMDB CSV columns."""
    if isinstance(value, list):
        return value
    if pd.isna(value):
        return []

    if not isinstance(value, str):
        return []

    try:
        parsed = ast.literal_eval(value)
        return parsed if isinstance(parsed, list) else []
    except (SyntaxError, ValueError):
        return []


def _extract_names(entries: Iterable[dict], max_items: int | None = None) -> List[str]:
    """Extract "name" fields from list of dictionaries."""
    names = [entry.get("name", "") for entry in entries if isinstance(entry, dict)]
    filtered = [name for name in names if name]
    if max_items is not None:
        filtered = filtered[:max_items]
    return filtered


def _extract_director(entries: Iterable[dict]) -> List[str]:
    """Extract the director name from crew entries."""
    directors = [
        entry.get("name", "")
        for entry in entries
        if isinstance(entry, dict) and entry.get("job") == "Director"
    ]
    return [name for name in directors if name]


def _clean_tokens(tokens: Iterable[str]) -> List[str]:
    """Normalize tokens: remove spaces and lowercase text."""
    return [
        str(token).replace(" ", "").lower() for token in tokens if str(token).strip()
    ]


def validate_input_frames(movies_df: pd.DataFrame, credits_df: pd.DataFrame) -> None:
    """Validate required columns before preprocessing."""
    missing_movies = MOVIES_REQUIRED_COLUMNS.difference(movies_df.columns)
    missing_credits = CREDITS_REQUIRED_COLUMNS.difference(credits_df.columns)

    if missing_movies:
        missing = ", ".join(sorted(missing_movies))
        raise ValueError(f"Missing required columns in movies dataset: {missing}")

    if missing_credits:
        missing = ", ".join(sorted(missing_credits))
        raise ValueError(f"Missing required columns in credits dataset: {missing}")


def preprocess_movies(movies_path: Path, credits_path: Path) -> pd.DataFrame:
    """
    Build a processed dataset with normalized `tags` for recommendation.

    Steps:
    1. Merge movies and credits datasets.
    2. Parse JSON-like columns with ast.literal_eval.
    3. Extract genres, keywords, top 3 cast, and director.
    4. Lowercase and normalize feature tokens.
    5. Combine into a single tags column.
    """
    movies_df = pd.read_csv(movies_path)
    credits_df = pd.read_csv(credits_path)
    validate_input_frames(movies_df, credits_df)

    merged_df = movies_df.merge(
        credits_df, on="title", how="inner", suffixes=("", "_credits")
    )

    if "poster_path" not in merged_df.columns:
        merged_df["poster_path"] = None

    selected_df = merged_df[
        [
            "id",
            "title",
            "overview",
            "genres",
            "keywords",
            "cast",
            "crew",
            "poster_path",
            "release_date",
            "vote_average",
            "vote_count",
        ]
    ].copy()

    selected_df = selected_df.dropna(subset=["overview"]).reset_index(drop=True)
    selected_df = selected_df.rename(columns={"id": "tmdb_id"})

    selected_df["overview_raw"] = selected_df["overview"].astype(str)
    selected_df["overview"] = selected_df["overview_raw"].str.lower().str.split()

    selected_df["genres"] = (
        selected_df["genres"].apply(_safe_literal_eval).apply(_extract_names)
    )
    selected_df["keywords"] = (
        selected_df["keywords"].apply(_safe_literal_eval).apply(_extract_names)
    )
    selected_df["cast"] = (
        selected_df["cast"]
        .apply(_safe_literal_eval)
        .apply(lambda items: _extract_names(items, max_items=3))
    )
    selected_df["director"] = (
        selected_df["crew"].apply(_safe_literal_eval).apply(_extract_director)
    )

    for feature in ["genres", "keywords", "cast", "director"]:
        selected_df[feature] = selected_df[feature].apply(_clean_tokens)

    selected_df["tags"] = selected_df.apply(
        lambda row: " ".join(
            row["overview"]
            + row["genres"]
            + row["keywords"]
            + row["cast"]
            + row["director"]
        ),
        axis=1,
    )
    selected_df["tags"] = (
        selected_df["tags"].str.replace(r"\s+", " ", regex=True).str.strip().str.lower()
    )

    processed_df = selected_df[
        [
            "tmdb_id",
            "title",
            "overview_raw",
            "tags",
            "poster_path",
            "release_date",
            "vote_average",
            "vote_count",
        ]
    ].rename(columns={"overview_raw": "overview"})

    processed_df = processed_df.drop_duplicates(subset=["tmdb_id"]).reset_index(
        drop=True
    )
    return processed_df


def save_processed_dataset(processed_df: pd.DataFrame, output_path: Path) -> None:
    """Persist processed movies dataset to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    processed_df.to_csv(output_path, index=False)
