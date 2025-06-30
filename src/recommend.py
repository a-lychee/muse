import pandas as pd
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import process
import re

def normalize_title(title):
    # No need to handle articless like with MovieLens, TMDb titles are already normalized
    return title

def load_tmdb_data():
    """Load movie data from TMDb JSON file"""
    with open("data/tmdb_movies.json", "r", encoding="utf-8") as f:
        movies = json.load(f)
    return pd.DataFrame(movies)

def recommend_movies(input_title, top_n=6):
    """Content-based recommendation using movie metadata"""
    # Load TMDb movies
    movies_df = load_tmdb_data()
    
    # Create a rich feature set combining overview, genres, actors, directors
    movies_df["features"] = (
        movies_df["overview"].fillna("") + " " + 
        movies_df["genres"].apply(lambda g: " ".join(g)) + " " +
        movies_df["actors"].apply(lambda a: " ".join(a)) + " " +
        movies_df["directors"].apply(lambda d: " ".join(d))
    )
    
    # Basic TF-IDF setup on combined features (not just title)
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(movies_df['features'])
    
    # Use fuzzy matching to find closest title match
    movie_titles = movies_df['title'].tolist()
    match = process.extractOne(input_title, movie_titles)
    if not match:
        return pd.DataFrame({'title': [], 'overview': []})
    
    matched_title = match[0]
    matched_idx = movies_df[movies_df['title'] == matched_title].index[0]
    
    # Compute similarity scores
    cosine_sim = cosine_similarity(tfidf_matrix[matched_idx], tfidf_matrix).flatten()
    similar_indices = cosine_sim.argsort()[-(top_n + 1):][::-1]
    
    # Get recommendations
    recommendations = movies_df.iloc[similar_indices]
    recommendations = recommendations[recommendations['title'] != matched_title]  # remove self
    
    # Select columns to return, including poster_url and vote_average
    return recommendations[['title', 'overview', 'genres', 'actors', 'directors', 'poster_url', 'vote_average']][:top_n]

def hybrid_recommend_movies(input_title, top_n=6):
    """
    Hybrid recommendation combining content-based filtering
    This is a simplified version as we no longer have user ratings
    We weight different features instead of using collaborative filtering
    """
    movies_df = load_tmdb_data()
    
    # Weight different features differently
    movies_df["weighted_features"] = (
        # Give plot/overview higher weight (x3)
        movies_df["overview"].fillna("") + " " + 
        movies_df["overview"].fillna("") + " " + 
        movies_df["overview"].fillna("") + " " + 
        # Give genre good weight (x2)
        movies_df["genres"].apply(lambda g: " ".join(g)) + " " +
        movies_df["genres"].apply(lambda g: " ".join(g)) + " " +
        # Actors and directors get normal weight
        movies_df["actors"].apply(lambda a: " ".join(a)) + " " +
        movies_df["directors"].apply(lambda d: " ".join(d))
    )
    
    # TF-IDF on weighted features
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(movies_df['weighted_features'])
    
    # Use fuzzy matching to find closest title match
    movie_titles = movies_df['title'].tolist()
    match = process.extractOne(input_title, movie_titles)
    if not match:
        return pd.DataFrame({'title': [], 'overview': []})
    
    matched_title = match[0]
    matched_idx = movies_df[movies_df['title'] == matched_title].index[0]
    
    # Compute similarity scores
    cosine_sim = cosine_similarity(tfidf_matrix[matched_idx], tfidf_matrix).flatten()
    similar_indices = cosine_sim.argsort()[-(top_n + 1):][::-1]
    
    # Get recommendations
    recommendations = movies_df.iloc[similar_indices]
    recommendations = recommendations[recommendations['title'] != matched_title]  # remove self
    
    # Select columns to return, including poster_url and vote_average
    return recommendations[['title', 'overview', 'genres', 'actors', 'directors', 'poster_url', 'vote_average']][:top_n]
