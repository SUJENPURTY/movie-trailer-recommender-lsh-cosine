"""Flask application for movie recommendations and trailer viewing."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from time import perf_counter
from typing import Any

from flask import Flask, jsonify, render_template, request

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.recommender import (
    MovieRecommender,
    fetch_tmdb_poster_url,
    fetch_tmdb_trailer_key,
)


def request_wants_json() -> bool:
    """Return True when the client explicitly asks for JSON output."""
    if request.args.get("format", "").lower() == "json":
        return True
    return request.accept_mimetypes.best == "application/json"


def create_app() -> Flask:
    """Application factory for local and production deployment."""
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["TMDB_API_KEY"] = os.getenv(
        "TMDB_API_KEY", "8bd059d480488cc9277fe087665fddc6"
    )

    recommender: MovieRecommender | None = None
    startup_error: str | None = None

    try:
        recommender = MovieRecommender.from_artifacts()
    except Exception as exc:  # pragma: no cover - startup guard
        startup_error = str(exc)

    @app.route("/", methods=["GET"])
    def home() -> str:
        runtime_movies = [
            "Avatar",
            "Dark Knight",
            "Inception",
            "Titanic",
            "Interstellar",
            "Avengers",
        ]
        runtime_cosine_times = [7.4, 13.7, 9.2, 5.1, 6.3, 8.0]
        runtime_lsh_times = [11.5, 9.7, 7.5, 2.8, 3.2, 6.5]

        movie_titles = recommender.list_titles(limit=500) if recommender else []
        browse_movies = (
            recommender.browse_movies(
                limit=36,
                api_key=app.config.get("TMDB_API_KEY"),
            )
            if recommender
            else []
        )
        return render_template(
            "index.html",
            movie_titles=movie_titles,
            browse_movies=browse_movies,
            runtime_movies=runtime_movies,
            runtime_cosine_times=runtime_cosine_times,
            runtime_lsh_times=runtime_lsh_times,
            startup_error=startup_error,
        )

    @app.route("/recommend", methods=["GET", "POST"])
    def recommend() -> Any:
        movie_name = request.values.get("movie_name", "").strip()
        method = request.values.get("method", "lsh").strip().lower() or "lsh"

        if method not in {"lsh", "cosine"}:
            error_message = "Unsupported method. Choose 'lsh' or 'cosine'."
            if request_wants_json():
                return jsonify({"error": error_message}), 400
            return (
                render_template(
                    "result.html",
                    query=movie_name,
                    method=method,
                    recommendations=[],
                    runtime_ms=None,
                    error=error_message,
                ),
                400,
            )

        if recommender is None:
            error_message = startup_error or "Model artifacts are not available."
            if request_wants_json():
                return jsonify({"error": error_message}), 503
            return (
                render_template(
                    "result.html",
                    query=movie_name,
                    method=method,
                    recommendations=[],
                    runtime_ms=None,
                    error=error_message,
                ),
                503,
            )

        if not movie_name:
            error_message = "Please enter a movie title."
            if request_wants_json():
                return jsonify({"error": error_message}), 400
            return (
                render_template(
                    "result.html",
                    query=movie_name,
                    method=method,
                    recommendations=[],
                    runtime_ms=None,
                    error=error_message,
                ),
                400,
            )

        try:
            start_time = perf_counter()
            recommendations = recommender.recommend(
                movie_name=movie_name,
                top_n=5,
                method=method,
                api_key=app.config.get("TMDB_API_KEY"),
            )
            runtime_ms = (perf_counter() - start_time) * 1000
        except ValueError as exc:
            error_message = str(exc)
            lower_error = error_message.lower()
            status_code = 404
            if "not available" in lower_error:
                status_code = 503
            elif (
                "unsupported method" in lower_error
                or "unsupported recommendation method" in lower_error
            ):
                status_code = 400

            if request_wants_json():
                return jsonify({"error": error_message}), status_code
            return (
                render_template(
                    "result.html",
                    query=movie_name,
                    method=method,
                    recommendations=[],
                    runtime_ms=None,
                    error=error_message,
                ),
                status_code,
            )

        if request_wants_json():
            return jsonify(
                {
                    "query": movie_name,
                    "method": method,
                    "runtime_ms": round(runtime_ms, 3),
                    "count": len(recommendations),
                    "results": recommendations,
                }
            )

        return render_template(
            "result.html",
            query=movie_name,
            method=method,
            recommendations=recommendations,
            runtime_ms=runtime_ms,
            error=None,
        )

    @app.route("/movie/<int:tmdb_id>", methods=["GET"])
    def movie_detail(tmdb_id: int) -> Any:
        if recommender is None:
            error_message = startup_error or "Model artifacts are not available."
            if request_wants_json():
                return jsonify({"error": error_message}), 503
            return (
                render_template(
                    "movie.html", movie=None, trailer_key=None, error=error_message
                ),
                503,
            )

        movie = recommender.get_movie(tmdb_id)
        if movie is None:
            error_message = (
                f"Movie with TMDB ID {tmdb_id} was not found in the dataset."
            )
            if request_wants_json():
                return jsonify({"error": error_message}), 404
            return (
                render_template(
                    "movie.html", movie=None, trailer_key=None, error=error_message
                ),
                404,
            )

        tmdb_api_key = app.config.get("TMDB_API_KEY")
        trailer_key = fetch_tmdb_trailer_key(tmdb_id, tmdb_api_key)
        if not movie.get("poster_url"):
            movie["poster_url"] = fetch_tmdb_poster_url(tmdb_id, tmdb_api_key)

        if request_wants_json():
            return jsonify(
                {
                    "movie": movie,
                    "trailer_key": trailer_key,
                    "youtube_url": (
                        f"https://www.youtube.com/watch?v={trailer_key}"
                        if trailer_key
                        else None
                    ),
                }
            )

        return render_template(
            "movie.html",
            movie=movie,
            trailer_key=trailer_key,
            tmdb_api_configured=bool(app.config.get("TMDB_API_KEY")),
            error=None,
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
