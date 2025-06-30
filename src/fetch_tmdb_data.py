import requests
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

# Fetch popular movies 
def fetch_popular_movies(page=1):
    params = {"api_key": API_KEY, "language": "en-US", "page": page}
    r = requests.get(f"{BASE_URL}/movie/popular", params=params)
    r.raise_for_status()
    return r.json()["results"]

# Fetch top rated movies
def fetch_top_rated_movies(page=1):
    params = {"api_key": API_KEY, "language": "en-US", "page": page}
    r = requests.get(f"{BASE_URL}/movie/top_rated", params=params)
    r.raise_for_status()
    return r.json()["results"]

# Fetch movies by genre
def fetch_movies_by_genre(genre_id, page=1):
    params = {"api_key": API_KEY, "language": "en-US", "page": page, "with_genres": genre_id}
    r = requests.get(f"{BASE_URL}/discover/movie", params=params)
    r.raise_for_status()
    return r.json()["results"]

# Get list of genres
def get_genres():
    params = {"api_key": API_KEY, "language": "en-US"}
    r = requests.get(f"{BASE_URL}/genre/movie/list", params=params)
    r.raise_for_status()
    return r.json()["genres"]

def get_movie_details(movie_id):
    params = {"api_key": API_KEY, "append_to_response": "credits"}
    r = requests.get(f"{BASE_URL}/movie/{movie_id}", params=params)
    r.raise_for_status()
    return r.json()

def extract_metadata(movie):
    # Extracts title, overview, genres, actors, directors, release year
    details = get_movie_details(movie["id"])
    genres = [g["name"] for g in details.get("genres", [])]
    actors = [c["name"] for c in details.get("credits", {}).get("cast", [])[:5]]
    directors = [c["name"] for c in details.get("credits", {}).get("crew", []) if c["job"] == "Director"]
    
    # Add poster path
    poster_path = details.get("poster_path")
    if poster_path:
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
    else:
        poster_url = ""
        
    return {
        "id": details["id"],
        "title": details["title"],
        "overview": details.get("overview", ""),
        "genres": genres,
        "actors": actors,
        "directors": directors,
        "release_date": details.get("release_date", ""),
        "poster_url": poster_url,
        "vote_average": details.get("vote_average", 0)
    }

def main():
    all_movies = []
    movie_ids = set()  # To track unique movies
    
    # 1. Fetch popular movies (5 pages)
    print("Fetching popular movies...")
    for page in range(1, 6):
        print(f"Popular movies page {page}...")
        popular = fetch_popular_movies(page)
        for movie in popular:
            if movie["id"] not in movie_ids:
                movie_ids.add(movie["id"])
                try:
                    meta = extract_metadata(movie)
                    all_movies.append(meta)
                except Exception as e:
                    print(f"Error fetching {movie.get('title', 'unknown')}: {e}")
        time.sleep(0.5)  # Avoid rate limiting
    
    # 2. Fetch top rated movies (5 pages)
    print("\nFetching top rated movies...")
    for page in range(1, 6):
        print(f"Top rated movies page {page}...")
        top_rated = fetch_top_rated_movies(page)
        for movie in top_rated:
            if movie["id"] not in movie_ids:
                movie_ids.add(movie["id"])
                try:
                    meta = extract_metadata(movie)
                    all_movies.append(meta)
                except Exception as e:
                    print(f"Error fetching {movie.get('title', 'unknown')}: {e}")
        time.sleep(0.5)  # Avoid rate limiting
    
    # 3. Fetch movies from popular genres
    print("\nFetching movies from major genres...")
    # Common genre IDs: Action=28, Comedy=35, Drama=18, Sci-Fi=878, Thriller=53
    genres = [(28, "Action"), (35, "Comedy"), (18, "Drama"), (878, "Sci-Fi"), (53, "Thriller")]
    
    for genre_id, genre_name in genres:
        print(f"Fetching {genre_name} movies...")
        for page in range(1, 3):  # 2 pages per genre
            print(f"{genre_name} movies page {page}...")
            genre_movies = fetch_movies_by_genre(genre_id, page)
            for movie in genre_movies:
                if movie["id"] not in movie_ids:
                    movie_ids.add(movie["id"])
                    try:
                        meta = extract_metadata(movie)
                        all_movies.append(meta)
                    except Exception as e:
                        print(f"Error fetching {movie.get('title', 'unknown')}: {e}")
            time.sleep(0.5)  # Avoid rate limiting
    
    print(f"\nTotal unique movies fetched: {len(all_movies)}")
    with open("data/tmdb_movies.json", "w", encoding="utf-8") as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(all_movies)} movies to data/tmdb_movies.json")

if __name__ == "__main__":
    main()
