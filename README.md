# Advanced Movie Recommendation with LSH

End-to-end movie recommendation system using the TMDB 5000 dataset, with:

- preprocessing and feature engineering
- MinHash + LSH recommendations for production serving
- optional cosine-vs-LSH analysis workflow (notebooks/analysis mode)
- Flask web app with TMDB trailer integration

## Project Structure

```
advanced-movie-recommendation-lsh/
├── app/
│   ├── app.py
│   ├── static/
│   │   └── styles.css
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── result.html
│       └── movie.html
├── data/
│   ├── tmdb_5000_movies.csv
│   ├── tmdb_5000_credits.csv
│   └── processed_movies.csv
├── models/
│   ├── artifacts/
│   ├── preprocessing.py
│   ├── vectorization.py
│   ├── lsh_recommender.py
│   ├── compare_models.py
│   ├── recommender.py
│   └── train_pipeline.py
├── notebooks/
└── requirements.txt
```

## Features

1. Preprocessing
- Merges movies and credits datasets.
- Parses JSON-like columns with `ast.literal_eval`.
- Extracts genres, keywords, top 3 cast members, and director.
- Normalizes tokens (remove spaces, lowercase).
- Builds combined `tags` column.
- Saves `data/processed_movies.csv`.

2. Vectorization
- Uses `TfidfVectorizer(max_features=5000, stop_words='english')`.
- Converts `tags` into vectors.

3. Recommendation Models
- LSH recommender using `datasketch` MinHash + MinHashLSH: `recommend_lsh(movie_name)`.
- Production Flask endpoint serves LSH recommendations.

4. Comparison
- Optional analysis mode measures runtime of cosine vs LSH.
- Computes overlap in top recommendations when analysis mode is enabled.
- Intended for notebooks/experimentation, not production serving.

5. Model Persistence
- Saves processed dataframe and model artifacts as pickle files in `models/artifacts/`.

6. Flask App
- `/` home/search page.
- `/recommend` recommendation endpoint (HTML and optional JSON), served with LSH by default.
- `/movie/<id>` detail page with trailer embedding.

## Setup (Python 3.10)

1. Create and activate a virtual environment.

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Train and save artifacts:
```bash
python -m models.train_pipeline
```

Optional analysis comparison run:
```bash
python -m models.train_pipeline --analysis-compare --movie "Avatar"
```

4. Run Flask locally:
```bash
python app/app.py
```

App URL: `http://127.0.0.1:5000`

## TMDB Trailer Integration

Set TMDB API key before starting Flask:

- Windows PowerShell:
```powershell
$env:TMDB_API_KEY="your_tmdb_api_key"
```

- Linux/macOS:
```bash
export TMDB_API_KEY="your_tmdb_api_key"
```

If no API key is configured, the detail page still works but trailer playback is disabled.

## Deployment (Render)

- Build command:
```bash
pip install -r requirements.txt
```

- Start command:
```bash
gunicorn app.app:app
```

- Environment variables:
  - `TMDB_API_KEY` (optional, for trailer support)

## API Mode

You can request JSON output from `/recommend` and `/movie/<id>` by adding `?format=json`.
