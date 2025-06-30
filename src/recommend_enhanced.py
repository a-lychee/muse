import pandas as pd
import json
import numpy as np
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
    
    # Add similarity scores with enhanced scaling for better differentiation
    similarity_scores = cosine_sim[similar_indices]
    
    # Apply improved scaling for better differentiation between recommendations
    
    # First normalize to [0,1] range
    normalized_scores = similarity_scores / similarity_scores[0]  # Divide by self-similarity
    
    # Debug the raw scores - should print during API calls
    print(f"Raw normalized scores: {normalized_scores}")
    
    # Apply a more balanced transformation with better spread:
    # This helps create greater differences between similar items while
    # still giving reasonable scores to less similar items
    
    # First apply square root to raise low values (less aggressive than power)
    balanced_scores = np.sqrt(normalized_scores)
    
    # Then apply rank-based scaling to ensure distribution across percentage range
    ranks = np.arange(len(balanced_scores))
    rank_factor = 1.0 - (ranks / (len(ranks) - 1)) * 0.5  # Scale from 1.0 to 0.5
    
    # Apply rank factor to further separate scores
    adjusted_scores = balanced_scores * rank_factor
    
    # Map to percentage range with more meaningful spread
    min_display = 55  # Minimum percentage
    max_display = 98  # Maximum percentage
    
    # Scale to display range
    scaled_scores = min_display + adjusted_scores * (max_display - min_display)
    
    # Round to integers
    scaled_scores = np.round(scaled_scores).astype(int)
    
    # Debug the final scores
    print(f"Final scaled scores: {scaled_scores}")
    
    # Assign to recommendations dataframe
    recommendations['similarity'] = scaled_scores
    
    # Remove the input movie itself
    recommendations = recommendations[recommendations['title'] != matched_title]
    
    # Select columns to return, including poster_url, vote_average, and similarity
    return recommendations[['title', 'overview', 'genres', 'actors', 'directors', 'poster_url', 'vote_average', 'similarity']][:top_n]

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
    
    # Add extra weight to title similarities to boost franchise matches
    # Extract the franchise name from the title (like "Alien" or "Star Wars")
    def extract_franchise_name(title):
        # Split on common franchise separators and get the first part
        separators = [":", " - ", " – ", ",", ".", "Part", "Chapter", "Volume"]
        base_title = title
        for sep in separators:
            if sep in title:
                base_title = title.split(sep)[0].strip()
                break
                
        # Handle numbered sequels (e.g., "Alien 3", "Terminator 2")
        base_title = re.sub(r'\s+\d+$', '', base_title).strip()
        
        # Return the first 1-3 words which often indicate the franchise
        words = base_title.split()
        franchise = " ".join(words[:min(3, len(words))])
        return franchise
    
    # Add franchise name with very high weight to boost franchise matches (increased from 3x to 5x)
    movies_df["weighted_features"] = movies_df["weighted_features"] + " " + \
                                     movies_df["title"].apply(extract_franchise_name) + " " + \
                                     movies_df["title"].apply(extract_franchise_name) + " " + \
                                     movies_df["title"].apply(extract_franchise_name) + " " + \
                                     movies_df["title"].apply(extract_franchise_name) + " " + \
                                     movies_df["title"].apply(extract_franchise_name)
    
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
    
    # Add similarity scores with enhanced scaling for better differentiation
    similarity_scores = cosine_sim[similar_indices]
    
    # Apply improved scaling for better differentiation between recommendations
    
    # First normalize to [0,1] range
    normalized_scores = similarity_scores / similarity_scores[0]  # Divide by self-similarity
    
    # Debug the raw scores - should print during API calls
    print(f"Raw normalized scores: {normalized_scores}")
    
    # Apply a more balanced transformation with better spread:
    # This helps create greater differences between similar items while
    # still giving reasonable scores to less similar items
    
    # First apply square root to raise low values (less aggressive than power)
    balanced_scores = np.sqrt(normalized_scores)
    
    # Then apply rank-based scaling to ensure distribution across percentage range
    ranks = np.arange(len(balanced_scores))
    rank_factor = 1.0 - (ranks / (len(ranks) - 1)) * 0.5  # Scale from 1.0 to 0.5
    
    # Apply rank factor to further separate scores
    adjusted_scores = balanced_scores * rank_factor
    
    # Boost franchise match detection by checking titles
    for i in range(1, len(similar_indices)):
        rec_title = movies_df.iloc[similar_indices[i]]['title']
        input_title = movies_df.iloc[similar_indices[0]]['title']
        
        # Check if these titles are likely from the same franchise
        rec_franchise = extract_franchise_name(rec_title).lower()
        input_franchise = extract_franchise_name(input_title).lower()
        
        # If franchise names match, give a boost
        if rec_franchise == input_franchise and len(rec_franchise) > 2:
            adjusted_scores[i] = min(adjusted_scores[i] * 1.2, 0.95)  # Boost but don't exceed 0.95
            print(f"Franchise match detected: {rec_title} - boosting score")
    
    # Map to percentage range with more meaningful spread
    min_display = 55  # Minimum percentage
    max_display = 98  # Maximum percentage
    
    # Scale to display range
    scaled_scores = min_display + adjusted_scores * (max_display - min_display)
    
    # Round to integers
    scaled_scores = np.round(scaled_scores).astype(int)
    
    # Debug the final scores
    print(f"Final scaled scores: {scaled_scores}")
    
    # Assign to recommendations dataframe
    recommendations['similarity'] = scaled_scores
    
    # Remove the input movie itself
    recommendations = recommendations[recommendations['title'] != matched_title]
    
    # Select columns to return, including poster_url, vote_average, and similarity
    return recommendations[['title', 'overview', 'genres', 'actors', 'directors', 'poster_url', 'vote_average', 'similarity']][:top_n]
