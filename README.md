# muse
A personalized movie recommendation engine using TMDb data

## Features
- Modern web interface with responsive design
- Movie recommendations based on rich metadata:
  - Plot/overview (weighted heavily)
  - Genres (weighted moderately)
  - Actors and directors
- Movie cards showing:
  - Movie posters
  - Titles and ratings
  - Brief overview/plot
  - Genre tags
  - Director and cast information
- Autocomplete for movie search

## Technology Stack
- **Backend**: FastAPI (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Data Source**: TMDb (The Movie Database) API
- **ML/AI**: TF-IDF for content-based filtering
- **Data Processing**: Pandas, scikit-learn

## How It Works
1. The application loads movie data from TMDb, including titles, plots, genres, actors, directors, etc.
2. When a user searches for a movie, the system uses TF-IDF and cosine similarity to find movies with similar attributes.
3. Results are weighted to prioritize plot/overview, then genres, then actors/directors.
4. The top recommendations are displayed with visually appealing movie cards.

## Getting Started

### Prerequisites
- Python 3.8+
- TMDb API key (stored in .env file)

### Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your TMDb API key:
   ```
   TMDB_API_KEY=your_api_key_here
   ```
4. Run the data fetcher: `python src/fetch_tmdb_data.py`
5. Start the server: `uvicorn src.main:app --reload`
6. Visit `http://localhost:8000` in your browser

## Future Improvements
- User accounts and personalized recommendations
- Rating system to incorporate collaborative filtering
- Additional filters by genre, year, etc.
- Expanded movie database
