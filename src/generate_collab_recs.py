import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split

def train_model(ratings_df):
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(ratings_df[['user_id', 'title', 'rating']], reader)
    trainset = data.build_full_trainset()
    algo = SVD()
    algo.fit(trainset)
    return algo

def recommend_unseen_movies(ratings_file="data/ratings.csv", movies_file="data/ml-latest-small/movies.csv", num_recs=5):
    # Load your personal ratings
    ratings_df = pd.read_csv(ratings_file)
    ratings_df['user_id'] = 1  # Only one user

    # Load movie metadata
    movies_df = pd.read_csv(movies_file)

    # Movies you've already rated
    rated_titles = set(ratings_df['title'])

    # Movies you haven't rated yet
    unseen_movies = movies_df[~movies_df['title'].isin(rated_titles)]

    # Train the model
    model = train_model(ratings_df)

    # Predict ratings for unseen movies
    predictions = []
    for title in unseen_movies['title']:
        pred = model.predict(uid=1, iid=title)
        predictions.append((title, pred.est))

    # Sort and return top N
    top_recs = sorted(predictions, key=lambda x: x[1], reverse=True)[:num_recs]
    print("\n🎯 Top Recommended Movies Based on Your Ratings:\n")
    for i, (title, score) in enumerate(top_recs, 1):
        print(f"{i}. {title} (Predicted rating: {score:.2f})")

if __name__ == "__main__":
    recommend_unseen_movies()
