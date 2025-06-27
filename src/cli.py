import pandas as pd
from datetime import datetime
from recommend import recommend_movies

def main():
    while True:
        title = input("Enter a movie title (or 'exit' to quit): ").strip()
        if title.lower() == 'exit':
            break

        recommendations = recommend_movies(title)
        print("\n🎬 Here are your recommendations:\n")
        print(recommendations)

        # Ask for feedback
        rate_title = input("\nWhich of these movies did you watch? (Enter exact title or 'skip'): ").strip()
        if rate_title.lower() == 'skip':
            continue

        try:
            rating = int(input(f"Rate '{rate_title}' from 1 to 5: "))
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5.")
        except ValueError as e:
            print(f"❗ Invalid input: {e}")
            continue

        # Save the feedback to CSV (append, no header, no index)
        feedback = pd.DataFrame([{
            "title": rate_title,
            "rating": rating,
            "date": datetime.now().isoformat()
        }])

        feedback.to_csv("data/ratings.csv", mode='a', header=False, index=False, encoding='utf-8')
        print(f"✅ Rating saved for '{rate_title}'.")

if __name__ == "__main__":
    main()
