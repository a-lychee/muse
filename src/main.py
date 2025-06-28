from fastapi import FastAPI, Query
from typing import List
from .recommend import recommend_movies
# from .generate_collab_recs import recommend_unseen_movies  # Disabled for now

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to your AI Movie Recommender!"}

@app.get("/recommend/content", response_model=List[str])
def recommend_by_content(title: str = Query(..., description="Movie title to base recommendations on")):
    recs = recommend_movies(title)
    return recs['title'].tolist()

# Collaborative filtering temporarily disabled due to memory limits on Render's free tier
# @app.get("/recommend/collab", response_model=List[str])
# def recommend_by_collab(n: int = 5):
#     # Reuse the core logic but return titles only
#     import pandas as pd
#     from surprise import SVD, Dataset, Reader

#     ratings_df = pd.read_csv("data/ratings.csv")
#     ratings_df['user_id'] = 1

#     reader = Reader(rating_scale=(1, 5))
#     data = Dataset.load_from_df(ratings_df[['user_id', 'title', 'rating']], reader)
#     trainset = data.build_full_trainset()
#     model = SVD()
#     model.fit(trainset)

#     movies_df = pd.read_csv("data/ml-latest-small/movies.csv")
#     rated = set(ratings_df['title'])
#     unseen = movies_df[~movies_df['title'].isin(rated)]

#     predictions = []
#     for title in unseen['title']:
#         pred = model.predict(uid=1, iid=title)
#         predictions.append((title, pred.est))

#     top_recs = sorted(predictions, key=lambda x: x[1], reverse=True)[:n]
#     return [title for title, _ in top_recs]
