import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import process

# Set up file paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / 'data' / 'ml-latest-small' / 'movies.csv'

# Load the movie data
movies_df = pd.read_csv(DATA_PATH)
movies_df['genres'] = movies_df['genres'].replace("(no genres listed)", "")

# Prepare the TF-IDF matrix of genres
tfidf = TfidfVectorizer(token_pattern=r'[^|]+')
tfidf_matrix = tfidf.fit_transform(movies_df['genres'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

def recommend_movies(title, num_recommendations=5):
    """
    Recommend movies based on genre similarity using fuzzy matching for input.
    
    Args:
        title (str): Movie title input by user (can be approximate)
        num_recommendations (int): Number of movies to recommend
        
    Returns:
        pandas.DataFrame: Recommended movies with titles and genres
    """
    # Fuzzy match the input to find the closest movie title in the dataset
    titles = movies_df['title'].tolist()
    match, score, index = process.extractOne(title, list(enumerate(titles)), scorer=process.fuzz.WRatio)

    matched_title = match[1]
    matched_index = match[0]

    print(f"\n🔎 Closest match found: '{matched_title}' (Score: {score})\n")

    # Get similarity scores for all movies with respect to the matched movie
    sim_scores = list(enumerate(cosine_sim[matched_index]))

    # Sort by similarity score in descending order and exclude the movie itself
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = [s for s in sim_scores if s[0] != matched_index]

    # Take the top 'num_recommendations' similar movies
    sim_scores = sim_scores[:num_recommendations]
    movie_indices = [i[0] for i in sim_scores]

    return movies_df.iloc[movie_indices][['title', 'genres']]
