import pandas as pd
import os

def load_movies():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, '..', 'data', 'ml-latest-small', 'movies.csv')
    movies = pd.read_csv(path)
    return movies

if __name__ == "__main__":
    movies_df = load_movies()
    print("Sample movies data:")
    print(movies_df.head())
