import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import process
import re

def normalize_title(title):
    # Move trailing ', The', ', An', ', A' to the front
    match = re.match(r'^(.*?)(?:,\s(The|An|A))?(\s*\(\d{4}\))?$', title)
    if match:
        main, article, year = match.groups()
        if article:
            main = main.rstrip()
            if year:
                return f"{article} {main}{year}"
            else:
                return f"{article} {main}"
    return title

def recommend_movies(input_title, top_n=6):
    # Load movies.csv only when needed
    movies = pd.read_csv("data/ml-latest-small/movies.csv")

    # Basic TF-IDF setup
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(movies['title'])

    # Use fuzzy matching to find closest match
    match = process.extractOne(input_title, movies['title'])
    if not match:
        return pd.DataFrame({'title': []})

    matched_title = match[0]
    matched_idx = movies[movies['title'] == matched_title].index[0]

    # Compute similarity scores
    cosine_sim = cosine_similarity(tfidf_matrix[matched_idx], tfidf_matrix).flatten()
    similar_indices = cosine_sim.argsort()[-(top_n + 1):][::-1]

    recommendations = movies.iloc[similar_indices]
    recommendations = recommendations[recommendations['title'] != matched_title]  # remove self

    # Normalize titles for display
    recommendations = recommendations.copy()
    recommendations['title'] = recommendations['title'].apply(normalize_title)
    return recommendations
