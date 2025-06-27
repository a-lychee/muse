import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise import train_test_split
from surprise import accuracy

def train_collab_filter(ratings_file="data/ratings.csv"):
    # Load ratings
    ratings_df = pd.read_csv(ratings_file)
    
    # Surprise requires columns: user_id, item_id, rating — make sure these exist
    # If user_id missing, add dummy user_id=1 (yourself)
    if 'user_id' not in ratings_df.columns:
        ratings_df['user_id'] = 1
    
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(ratings_df[['user_id', 'title', 'rating']], reader)
    
    # Split into train and test
    trainset, testset = train_test_split(data, test_size=0.2, random_state=42)
    
    # Use SVD algorithm (matrix factorization)
    algo = SVD()
    algo.fit(trainset)
    
    # Predict on test set
    predictions = algo.test(testset)
    rmse = accuracy.rmse(predictions)
    print(f"Test RMSE: {rmse:.4f}")
    
    return algo

if __name__ == "__main__":
    model = train_collab_filter()
