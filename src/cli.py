from recommend import recommend_movies

def main():
    print("🎬 Welcome to Muse 🎬\n")

    while True:
        title = input("Enter a movie title (or 'exit' to quit): ").strip()
        if title.lower() == 'exit':
            print("Goodbye! 🍿")
            break

        recommendations = recommend_movies(title, 5)
        print("\nHere are your recommendations:\n")
        print(recommendations)

if __name__ == "__main__":
    main()
