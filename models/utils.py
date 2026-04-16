"""Helper utilities shared across recommendation modules."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import pandas as pd


def normalize_title(title: str) -> str:
    """Normalize movie titles for case-insensitive lookup."""
    return str(title).strip().lower()


def resolve_movie_index(movie_name: str, movies_df: pd.DataFrame) -> int:
    """Resolve a movie title to dataframe index using exact then contains matching."""
    if movies_df.empty:
        raise ValueError("Movie dataset is empty.")

    target = normalize_title(movie_name)
    if not target:
        raise ValueError("Movie name cannot be empty.")

    title_series = movies_df["title"].fillna("").astype(str).str.strip().str.lower()

    exact_matches = movies_df.index[title_series == target]
    if len(exact_matches) > 0:
        return int(exact_matches[0])

    contains_matches = movies_df.index[title_series.str.contains(target, regex=False)]
    if len(contains_matches) > 0:
        return int(contains_matches[0])

    raise ValueError(f"Movie '{movie_name}' not found in dataset.")


def ensure_directory(path: Path) -> None:
    """Ensure a directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def save_pickle(obj: Any, path: Path) -> None:
    """Save an object to a pickle file."""
    ensure_directory(path.parent)
    with path.open("wb") as file:
        pickle.dump(obj, file)


def load_pickle(path: Path) -> Any:
    """Load an object from a pickle file."""
    with path.open("rb") as file:
        return pickle.load(file)
