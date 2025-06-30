from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List, Dict, Any
import json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")

def load_tmdb_data():
    """Load movie data from TMDb JSON file"""
    with open("data/tmdb_movies.json", "r", encoding="utf-8") as f:
        movies = json.load(f)
    return movies

@app.get("/recommend/content", response_model=List[Dict[str, Any]])
def recommend_by_content(title: str = Query(..., description="Movie title to base recommendations on")):
    from .recommend import hybrid_recommend_movies
    recs = hybrid_recommend_movies(title)
    # Convert DataFrame to list of dicts for response
    return recs.to_dict(orient="records")

@app.get("/suggest", response_model=List[str])
def suggest_titles(q: str = Query(..., description="Partial movie title for suggestions")):
    movies = load_tmdb_data()
    # Filter movies where title contains query (case insensitive)
    suggestions = []
    for movie in movies:
        if q.lower() in movie['title'].lower():
            suggestions.append(movie['title'])
        if len(suggestions) >= 10:
            break
    return suggestions

# TMDb data already has detailed information, so we can add a new endpoint
@app.get("/movie/{movie_id}", response_model=Dict[str, Any])
def get_movie_details(movie_id: int):
    movies = load_tmdb_data()
    for movie in movies:
        if movie['id'] == movie_id:
            return movie
    return {"error": "Movie not found"}
