from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List
from .recommend import recommend_movies
from .load_data import load_movies

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")

@app.get("/recommend/content", response_model=List[str])
def recommend_by_content(title: str = Query(..., description="Movie title to base recommendations on")):
    recs = recommend_movies(title)
    return recs['title'].tolist()

@app.get("/suggest", response_model=List[str])
def suggest_titles(q: str = Query(..., description="Partial movie title for suggestions")):
    movies_df = load_movies()
    suggestions = movies_df[movies_df['title'].str.contains(q, case=False, na=False)]['title'].head(10).tolist()
    return suggestions

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
