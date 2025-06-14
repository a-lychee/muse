import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Step 1: Build path relative to this script
BASE_DIR = Path(__file__).resolve().parent.parent  # go up to the project root
DATA_PATH = BASE_DIR / 'data' / 'ml-latest-small' / 'movies.csv'

# Step 2: Load the dataset
movies_df = pd.read_csv(DATA_PATH)

# Clean genres
movies_df['genres'] = movies_df['genres'].replace("(no genres listed)", "")

# TF-IDF and similarity
tfidf = TfidfVectorizer(token_pattern=r'[^|]+')
tfidf_matrix = tfidf.fit_transform(movies_df['genres'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Recommendation function
def recommend_movies(title, num_recommendations=5):
    idx = movies_df[movies_df['title'].str.lower() == title.lower()].index
    if len(idx) == 0:
        return f"Movie '{title}' not found in dataset."

    idx = idx[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:num_recommendations+1]
    
    movie_indices = [i[0] for i in sim_scores]
    return movies_df.iloc[movie_indices][['title', 'genres']]

# Run test
if __name__ == "__main__":
    recommendations = recommend_movies("Toy Story (1995)", 5)
    print(recommendations)