import pandas as pd
from pathlib import Path

# Dynamically get the directory of THIS script (agnostic of where you run it)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data' / 'ml-latest-small'

def load_movies():
    return pd.read_csv(DATA_DIR / 'movies.csv')

def load_ratings():
    return pd.read_csv(DATA_DIR / 'ratings.csv')

if __name__ == "__main__":
    movies_df = load_movies()
    ratings_df = load_ratings()
    
    print("Movies dataset:")
    print(movies_df.head(), "\n")
    
    print("Ratings dataset:")
    print(ratings_df.head(), "\n")

print(f"Number of movies: {len(movies_df)}")
print(f"Number of ratings: {len(ratings_df)}")

print("\nMovies columns:", movies_df.columns.tolist())
print("Ratings columns:", ratings_df.columns.tolist())

print("\nExample genres values:")
print(movies_df['genres'].unique()[:10])

print("\nRatings summary:")
print(ratings_df['rating'].describe())

ratings_per_user = ratings_df.groupby('userId').size()
active_users = ratings_per_user[ratings_per_user > 20]
print(f"Number of active users (20+ ratings): {len(active_users)}")