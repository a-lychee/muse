import requests
import os
import json
import time
import logging
from dotenv import load_dotenv
from pathlib import Path
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tmdb_fetch.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
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

def save_progress(all_movies, filename="data/tmdb_movies.json"):
    """Save current progress to file"""
    os.makedirs("data", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {len(all_movies)} movies to {filename}")

def load_existing_data(filename="data/tmdb_movies.json"):
    """Load existing data if available"""
    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
            logger.info(f"Loaded {len(existing_data)} movies from existing file")
            return existing_data, {movie["id"] for movie in existing_data}
    except Exception as e:
        logger.error(f"Error loading existing data: {e}")
    return [], set()

# Fetch movies from a specific year range
def fetch_movies_by_year(start_year, end_year, page=1):
    params = {
        "api_key": API_KEY, 
        "language": "en-US", 
        "page": page,
        "primary_release_date.gte": f"{start_year}-01-01",
        "primary_release_date.lte": f"{end_year}-12-31",
        "sort_by": "popularity.desc"
    }
    r = requests.get(f"{BASE_URL}/discover/movie", params=params)
    r.raise_for_status()
    return r.json()["results"]

def main():
    # Try to load existing data first
    all_movies, movie_ids = load_existing_data()
    
    # Set target to 10,000 movies
    target_count = 10000  # Target number of movies to fetch
    
    logger.info(f"Starting to fetch {target_count} movies from TMDb (already have {len(all_movies)})...")
    
    # New - First specifically target 2024-2025 movies
    logger.info("\nPrioritizing movies from 2024-2025...")
    
    # Get 2024-2025 movies first (prioritize recent content)
    max_pages_recent = 50  # Fetch many pages of recent content
    recent_movie_count = 0  # Track how many 2024-2025 movies we've found
    target_recent_movies = 1000  # Try to get at least 1000 recent movies if available
    
    for page in tqdm(range(1, max_pages_recent + 1), desc="2024-2025 movies"):
        if recent_movie_count >= target_recent_movies:
            logger.info(f"Reached target of {target_recent_movies} movies from 2024-2025!")
            break
            
        try:
            recent_movies = fetch_movies_by_year(2024, 2025, page)
            if not recent_movies:
                logger.info("No more 2024-2025 movies found.")
                break
                
            for movie in recent_movies:
                if movie["id"] not in movie_ids:
                    movie_ids.add(movie["id"])
                    try:
                        meta = extract_metadata(movie)
                        all_movies.append(meta)
                        recent_movie_count += 1
                        
                        # Save progress more frequently for recent movies
                        if len(all_movies) % 25 == 0:
                            logger.info(f"Progress: {len(all_movies)}/{target_count} movies (Recent: {recent_movie_count})")
                            save_progress(all_movies)
                    except Exception as e:
                        logger.error(f"Error fetching {movie.get('title', 'unknown')}: {e}")
            
            time.sleep(0.25)  # Rate limiting
        except Exception as e:
            logger.error(f"Error fetching 2024-2025 movies page {page}: {e}")
            time.sleep(1)  # Wait a bit longer after an error
            
    logger.info(f"Found {recent_movie_count} movies from 2024-2025")
    
    # Continue with the regular fetch process
    # 1. Start with Popular movies (up to 500 pages)
    max_pages_popular = 500
    
    logger.info("\nFetching popular movies...")
    for page in tqdm(range(1, max_pages_popular + 1), desc="Popular movies"):
        if len(movie_ids) >= target_count:
            break
            
        try:
            popular = fetch_popular_movies(page)
            if not popular:  # If we get an empty response, we've reached the end
                break
                
            for movie in popular:
                if movie["id"] not in movie_ids and len(movie_ids) < target_count:
                    movie_ids.add(movie["id"])
                    try:
                        meta = extract_metadata(movie)
                        all_movies.append(meta)
                        
                        # Save progress every 50 movies
                        if len(all_movies) % 50 == 0:
                            logger.info(f"Progress: {len(all_movies)}/{target_count} movies")
                            save_progress(all_movies)
                    except Exception as e:
                        logger.error(f"Error fetching {movie.get('title', 'unknown')}: {e}")
            
            time.sleep(0.25)  # Rate limiting
        except Exception as e:
            logger.error(f"Error fetching popular movies page {page}: {e}")
            time.sleep(1)  # Wait a bit longer after an error
    
    # 2. If we still need more, add top-rated movies
    if len(movie_ids) < target_count:
        logger.info("\nFetching top-rated movies...")
        max_pages_top = 500
        
        for page in tqdm(range(1, max_pages_top + 1), desc="Top-rated movies"):
            if len(movie_ids) >= target_count:
                break
                
            try:
                top_rated = fetch_top_rated_movies(page)
                if not top_rated:
                    break
                    
                for movie in top_rated:
                    if movie["id"] not in movie_ids and len(movie_ids) < target_count:
                        movie_ids.add(movie["id"])
                        try:
                            meta = extract_metadata(movie)
                            all_movies.append(meta)
                            
                            # Save progress every 50 movies
                            if len(all_movies) % 50 == 0:
                                logger.info(f"Progress: {len(all_movies)}/{target_count} movies")
                                save_progress(all_movies)
                        except Exception as e:
                            logger.error(f"Error fetching {movie.get('title', 'unknown')}: {e}")
                
                time.sleep(0.25)  # Rate limiting
            except Exception as e:
                logger.error(f"Error fetching top-rated movies page {page}: {e}")
                time.sleep(1)  # Wait longer after an error
    
    # 3. If we still need more, add trending movies
    if len(movie_ids) < target_count:
        logger.info("\nFetching trending movies (weekly)...")
        max_pages_trending = 100
        
        for page in tqdm(range(1, max_pages_trending + 1), desc="Trending movies"):
            if len(movie_ids) >= target_count:
                break
                
            try:
                trending = fetch_trending_movies("week", page)
                if not trending:
                    break
                    
                for movie in trending:
                    if movie["id"] not in movie_ids and len(movie_ids) < target_count:
                        movie_ids.add(movie["id"])
                        try:
                            meta = extract_metadata(movie)
                            all_movies.append(meta)
                            
                            # Save progress every 50 movies
                            if len(all_movies) % 50 == 0:
                                logger.info(f"Progress: {len(all_movies)}/{target_count} movies")
                                save_progress(all_movies)
                        except Exception as e:
                            logger.error(f"Error fetching {movie.get('title', 'unknown')}: {e}")
                
                time.sleep(0.25)  # Rate limiting
            except Exception as e:
                logger.error(f"Error fetching trending movies page {page}: {e}")
                time.sleep(1)  # Wait longer after an error
    
    # 4. If we still need more, add upcoming movies
    if len(movie_ids) < target_count:
        logger.info("\nFetching upcoming movies...")
        max_pages_upcoming = 50
        
        for page in tqdm(range(1, max_pages_upcoming + 1), desc="Upcoming movies"):
            if len(movie_ids) >= target_count:
                break
                
            try:
                upcoming = fetch_upcoming_movies(page)
                if not upcoming:
                    break
                    
                for movie in upcoming:
                    if movie["id"] not in movie_ids and len(movie_ids) < target_count:
                        movie_ids.add(movie["id"])
                        try:
                            meta = extract_metadata(movie)
                            all_movies.append(meta)
                            
                            # Save progress every 50 movies
                            if len(all_movies) % 50 == 0:
                                logger.info(f"Progress: {len(all_movies)}/{target_count} movies")
                                save_progress(all_movies)
                        except Exception as e:
                            logger.error(f"Error fetching {movie.get('title', 'unknown')}: {e}")
                
                time.sleep(0.25)  # Rate limiting
            except Exception as e:
                logger.error(f"Error fetching upcoming movies page {page}: {e}")
                time.sleep(1)  # Wait longer after an error
    
    # 5. Add movies by decade to ensure a good historical range
    decades = [
        (2024, 2025, "2024-2025"),  # Latest movies first
        (2020, 2023, "2020-2023"),
        (2010, 2019, "2010s"),
        (2000, 2009, "2000s"),
        (1990, 1999, "1990s"),
        (1980, 1989, "1980s"),
        (1970, 1979, "1970s"),
        (1960, 1969, "1960s"),
        (1950, 1959, "1950s"),
        (1940, 1949, "1940s"),
        (1930, 1939, "1930s"),
        (1920, 1929, "1920s"),
        (1900, 1919, "Pre-1920s")
    ]
    
    if len(movie_ids) < target_count:
        logger.info("\nFetching movies by decade...")
        
        for start_year, end_year, decade_name in decades:
            if len(movie_ids) >= target_count:
                break
                
            logger.info(f"Fetching {decade_name} movies...")
            
            # Special handling for recent years - fetch more pages to prioritize newest movies
            if decade_name == "2024-2025":
                max_pages_decade = 100  # More pages for newest movies
            else:
                max_pages_decade = 30  # Regular amount for other decades
            
            for page in tqdm(range(1, max_pages_decade + 1), desc=f"{decade_name} movies"):
                if len(movie_ids) >= target_count:
                    break
                    
                try:
                    decade_movies = fetch_movies_by_year(start_year, end_year, page)
                    if not decade_movies:
                        break
                        
                    for movie in decade_movies:
                        if movie["id"] not in movie_ids and len(movie_ids) < target_count:
                            movie_ids.add(movie["id"])
                            try:
                                meta = extract_metadata(movie)
                                all_movies.append(meta)
                                
                                # Save progress every 50 movies
                                if len(all_movies) % 50 == 0:
                                    logger.info(f"Progress: {len(all_movies)}/{target_count} movies")
                                    save_progress(all_movies)
                            except Exception as e:
                                logger.error(f"Error fetching {movie.get('title', 'unknown')}: {e}")
                    
                    time.sleep(0.25)  # Rate limiting
                except Exception as e:
                    logger.error(f"Error fetching {decade_name} movies page {page}: {e}")
                    time.sleep(1)  # Wait longer after an error
    
    # 6. If we still need more, fetch by major genres
    if len(movie_ids) < target_count:
        logger.info("\nFetching movies from major genres...")
        # Common genre IDs: Action=28, Comedy=35, Drama=18, Sci-Fi=878, Thriller=53
        genres = [(28, "Action"), (35, "Comedy"), (18, "Drama"), (878, "Sci-Fi"), (53, "Thriller"),
                 (27, "Horror"), (10749, "Romance"), (16, "Animation"), (12, "Adventure"), (80, "Crime"),
                 (14, "Fantasy"), (36, "History"), (10402, "Music"), (9648, "Mystery"), 
                 (10752, "War"), (37, "Western")]
        
        max_pages_per_genre = 50  # 50 pages per genre (increased from 5)
        
        for genre_id, genre_name in genres:
            if len(movie_ids) >= target_count:
                break
                
            logger.info(f"Fetching {genre_name} movies...")
            
            for page in tqdm(range(1, max_pages_per_genre + 1), desc=f"{genre_name} movies"):
                if len(movie_ids) >= target_count:
                    break
                    
                try:
                    genre_movies = fetch_movies_by_genre(genre_id, page)
                    if not genre_movies:
                        break
                        
                    for movie in genre_movies:
                        if movie["id"] not in movie_ids and len(movie_ids) < target_count:
                            movie_ids.add(movie["id"])
                            try:
                                meta = extract_metadata(movie)
                                all_movies.append(meta)
                                
                                # Save progress every 50 movies
                                if len(all_movies) % 50 == 0:
                                    logger.info(f"Progress: {len(all_movies)}/{target_count} movies")
                                    save_progress(all_movies)
                            except Exception as e:
                                logger.error(f"Error fetching {movie.get('title', 'unknown')}: {e}")
                    
                    time.sleep(0.25)  # Rate limiting
                except Exception as e:
                    logger.error(f"Error fetching {genre_name} movies page {page}: {e}")
                    time.sleep(1)  # Wait longer after an error
    
    # Final save
    logger.info(f"\nTotal unique movies fetched: {len(all_movies)}")
    save_progress(all_movies)
    logger.info("Data collection complete!")

if __name__ == "__main__":
    try:
        # Try to import tqdm, install if not available
        try:
            from tqdm import tqdm
        except ImportError:
            print("Installing tqdm package for progress bars...")
            import subprocess
            subprocess.check_call(["pip", "install", "tqdm"])
            from tqdm import tqdm
            
        print(f"Starting fetch of up to 10,000 movies from TMDb...")
        print("This process may take several hours. You can stop it at any time with Ctrl+C.")
        print("Progress will be saved periodically and can be resumed later.")
        
        main()
        
        print("\nMovie fetching complete! Check data/tmdb_movies.json for results.")
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user. Progress has been saved and can be resumed later.")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nAn error occurred: {e}")
        print("Check tmdb_fetch.log for details.")
