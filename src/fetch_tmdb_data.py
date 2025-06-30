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

# Fetch trending movies
def fetch_trending_movies(time_window="week", page=1):
    params = {"api_key": API_KEY, "language": "en-US", "page": page}
    r = requests.get(f"{BASE_URL}/trending/movie/{time_window}", params=params)
    r.raise_for_status()
    return r.json()["results"]

# Fetch upcoming movies
def fetch_upcoming_movies(page=1):
    params = {"api_key": API_KEY, "language": "en-US", "page": page}
    r = requests.get(f"{BASE_URL}/movie/upcoming", params=params)
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
    target_count = 1000  # Target number of movies to fetch
    
    print(f"Starting to fetch {target_count} movies from TMDb...")
    
    # Strategy: Fetch from different sources until we reach our target count
    # 1. Start with Popular movies (up to 50 pages)
    page = 1
    max_pages = 50  # TMDb usually limits to 1000 results (50 pages)
    
    print("\nFetching popular movies...")
    while len(movie_ids) < target_count and page <= max_pages:
        try:
            print(f"Popular movies page {page}...")
            popular = fetch_popular_movies(page)
            if not popular:  # If we get an empty response, we've reached the end
                break
                
            for movie in popular:
                if movie["id"] not in movie_ids and len(movie_ids) < target_count:
                    movie_ids.add(movie["id"])
                    try:
                        meta = extract_metadata(movie)
                        all_movies.append(meta)
                        print(f"Added: {meta['title']} ({len(all_movies)}/{target_count})")
                    except Exception as e:
                        print(f"Error fetching {movie.get('title', 'unknown')}: {e}")
            
            page += 1
            time.sleep(0.5)  # Rate limiting
        except Exception as e:
            print(f"Error fetching popular movies page {page}: {e}")
            break
    
    # 2. If we still need more, add top-rated movies
    if len(movie_ids) < target_count:
        print("\nFetching top-rated movies...")
        page = 1
        while len(movie_ids) < target_count and page <= max_pages:
            try:
                print(f"Top-rated movies page {page}...")
                top_rated = fetch_top_rated_movies(page)
                if not top_rated:
                    break
                    
                for movie in top_rated:
                    if movie["id"] not in movie_ids and len(movie_ids) < target_count:
                        movie_ids.add(movie["id"])
                        try:
                            meta = extract_metadata(movie)
                            all_movies.append(meta)
                            print(f"Added: {meta['title']} ({len(all_movies)}/{target_count})")
                        except Exception as e:
                            print(f"Error fetching {movie.get('title', 'unknown')}: {e}")
                
                page += 1
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"Error fetching top-rated movies page {page}: {e}")
                break
    
    # 3. If we still need more, add trending movies
    if len(movie_ids) < target_count:
        print("\nFetching trending movies (weekly)...")
        page = 1
        while len(movie_ids) < target_count and page <= max_pages:
            try:
                print(f"Trending movies page {page}...")
                trending = fetch_trending_movies("week", page)
                if not trending:
                    break
                    
                for movie in trending:
                    if movie["id"] not in movie_ids and len(movie_ids) < target_count:
                        movie_ids.add(movie["id"])
                        try:
                            meta = extract_metadata(movie)
                            all_movies.append(meta)
                            print(f"Added: {meta['title']} ({len(all_movies)}/{target_count})")
                        except Exception as e:
                            print(f"Error fetching {movie.get('title', 'unknown')}: {e}")
                
                page += 1
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"Error fetching trending movies page {page}: {e}")
                break
    
    # 4. If we still need more, add upcoming movies
    if len(movie_ids) < target_count:
        print("\nFetching upcoming movies...")
        page = 1
        while len(movie_ids) < target_count and page <= max_pages:
            try:
                print(f"Upcoming movies page {page}...")
                upcoming = fetch_upcoming_movies(page)
                if not upcoming:
                    break
                    
                for movie in upcoming:
                    if movie["id"] not in movie_ids and len(movie_ids) < target_count:
                        movie_ids.add(movie["id"])
                        try:
                            meta = extract_metadata(movie)
                            all_movies.append(meta)
                            print(f"Added: {meta['title']} ({len(all_movies)}/{target_count})")
                        except Exception as e:
                            print(f"Error fetching {movie.get('title', 'unknown')}: {e}")
                
                page += 1
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"Error fetching upcoming movies page {page}: {e}")
                break
    
    # 5. If we still need more, fetch by major genres
    if len(movie_ids) < target_count:
        print("\nFetching movies from major genres...")
        # Common genre IDs: Action=28, Comedy=35, Drama=18, Sci-Fi=878, Thriller=53
        genres = [(28, "Action"), (35, "Comedy"), (18, "Drama"), (878, "Sci-Fi"), (53, "Thriller"),
                 (27, "Horror"), (10749, "Romance"), (16, "Animation"), (12, "Adventure"), (80, "Crime")]
        
        for genre_id, genre_name in genres:
            if len(movie_ids) >= target_count:
                break
                
            print(f"Fetching {genre_name} movies...")
            page = 1
            while len(movie_ids) < target_count and page <= 5:  # Limit to 5 pages per genre
                print(f"{genre_name} movies page {page}...")
                genre_movies = fetch_movies_by_genre(genre_id, page)
                if not genre_movies:
                    break
                    
                for movie in genre_movies:
                    if movie["id"] not in movie_ids and len(movie_ids) < target_count:
                        movie_ids.add(movie["id"])
                        try:
                            meta = extract_metadata(movie)
                            all_movies.append(meta)
                            print(f"Added: {meta['title']} ({len(all_movies)}/{target_count})")
                        except Exception as e:
                            print(f"Error fetching {movie.get('title', 'unknown')}: {e}")
                
                page += 1
                time.sleep(0.5)  # Rate limiting
    
    print(f"\nTotal unique movies fetched: {len(all_movies)}")
    with open("data/tmdb_movies.json", "w", encoding="utf-8") as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(all_movies)} movies to data/tmdb_movies.json")

if __name__ == "__main__":
    main()
