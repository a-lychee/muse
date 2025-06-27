import pandas as pd
import matplotlib.pyplot as plt

# === 1️⃣ Load Ratings === #
ratings_path = "data/ratings.csv"
ratings_df = pd.read_csv(ratings_path)

print("\n📋 Loaded Ratings:")
print(ratings_df.head())

# === 2️⃣ Clean the Ratings === #
ratings_df = ratings_df.drop_duplicates()
ratings_df = ratings_df.dropna()

print("\n✅ Cleaned Ratings:")
print(ratings_df.head())

# === 3️⃣ Summarize the Ratings === #
summary = ratings_df.groupby('title')['rating'].agg(['count', 'mean']).reset_index()
summary = summary.rename(columns={'count': 'num_ratings', 'mean': 'avg_rating'})

print("\n🎯 Ratings Summary (Number of Ratings + Average Rating per Movie):")
print(summary.sort_values(by='num_ratings', ascending=False))

# === 4️⃣ Create a Ratings Matrix (for Collaborative Filtering later) === #
ratings_df['user_id'] = 1  # Dummy user ID for now since it's just you
ratings_matrix = ratings_df.pivot_table(index='user_id', columns='title', values='rating')

print("\n🎬 Ratings Matrix:")
print(ratings_matrix)

# === 5️⃣ Visualize the Ratings === #
summary.plot(x='title', y='avg_rating', kind='barh', legend=False)
plt.xlabel("Average Rating (1-5)")
plt.title("Your Movie Ratings by Average Score")
plt.tight_layout()
plt.show()
