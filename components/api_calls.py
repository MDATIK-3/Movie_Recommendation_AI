import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
from typing import List, Dict, Optional

# Get API key from environment variable for security
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "9ef5ae6fc8b8f484e9295dc97d8d32ea")
if not TMDB_API_KEY:
    st.error("❌ TMDB_API_KEY environment variable not set. Please set it to use movie features.")
    TMDB_API_KEY = "demo_key"  # Fallback for demo purposes


def create_session():
    """Create a requests session with retry logic."""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session


@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_popular_movies(limit: int = 20) -> List[Dict]:
    """Fetch popular movies from TMDB API with improved error handling."""
    if TMDB_API_KEY == "demo_key":
        return get_demo_movies(limit)
    
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page=1"
    
    try:
        session = create_session()
        response = session.get(url, timeout=10)
        
        if response.status_code == 401:
            return get_demo_movies(limit)
        elif response.status_code != 200:
            return get_demo_movies(limit)
        
        data = response.json()
        if not isinstance(data, dict) or "results" not in data:
            return get_demo_movies(limit)
        
        movies_list = []
        for movie in data.get("results", [])[:limit]:
            movies_list.append({
                "id": movie.get("id", 0),
                "title": movie.get("title", "Unknown"),
                "rating": movie.get("vote_average", 0.0),
                "description": movie.get("overview", "No description available"),
                "poster": f"https://image.tmdb.org/t/p/w500/{movie.get('poster_path')}"
                if movie.get("poster_path")
                else "https://via.placeholder.com/300x450?text=No+Poster",
                "runtime": movie.get("runtime", 120),
                "release_date": movie.get("release_date", "2000-01-01"),
                "genres": movie.get("genre_ids", []),
            })
        
        return movies_list
        
    except requests.exceptions.Timeout:
        return get_demo_movies(limit)
    except requests.exceptions.ConnectionError:
        return get_demo_movies(limit)
    except Exception as e:
        return get_demo_movies(limit)


def get_demo_movies(limit: int = 20) -> List[Dict]:
    """Return demo movie data when API is unavailable."""
    demo_movies = [
        {
            "id": 1,
            "title": "The Shawshank Redemption",
            "rating": 9.3,
            "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
            "poster": "https://via.placeholder.com/300x450?text=Shawshank+Redemption",
            "runtime": 142,
            "release_date": "1994-09-22",
            "genres": [18, 80]
        },
        {
            "id": 2,
            "title": "The Godfather",
            "rating": 9.2,
            "description": "The aging patriarch of an organized crime dynasty transfers control to his reluctant son.",
            "poster": "https://via.placeholder.com/300x450?text=The+Godfather",
            "runtime": 175,
            "release_date": "1972-03-14",
            "genres": [18, 80]
        },
        {
            "id": 3,
            "title": "Pulp Fiction",
            "rating": 8.9,
            "description": "The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.",
            "poster": "https://via.placeholder.com/300x450?text=Pulp+Fiction",
            "runtime": 154,
            "release_date": "1994-10-14",
            "genres": [18, 80]
        }
    ]
    return demo_movies[:limit]


@st.cache_data(ttl=3600)
def fetch_genres() -> Dict[int, str]:
    """Fetch movie genres from TMDB API."""
    if TMDB_API_KEY == "demo_key":
        return get_demo_genres()
    
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US"
    
    try:
        session = create_session()
        response = session.get(url, timeout=10)
        
        if response.status_code != 200:
            st.warning(f"⚠️ Failed to fetch genres: HTTP {response.status_code}")
            return get_demo_genres()
        
        data = response.json()
        if not isinstance(data, dict) or "genres" not in data:
            st.warning("⚠️ Invalid genres response")
            return get_demo_genres()
        
        return {genre["id"]: genre["name"] for genre in data.get("genres", [])}
        
    except Exception as e:
        st.warning(f"⚠️ Error fetching genres: {e}")
        return get_demo_genres()


def get_demo_genres() -> Dict[int, str]:
    """Return demo genre data."""
    return {
        28: "Action",
        12: "Adventure",
        16: "Animation",
        35: "Comedy",
        80: "Crime",
        99: "Documentary",
        18: "Drama",
        10751: "Family",
        14: "Fantasy",
        36: "History",
        27: "Horror",
        10402: "Music",
        9648: "Mystery",
        10749: "Romance",
        878: "Science Fiction",
        10770: "TV Movie",
        53: "Thriller",
        10752: "War",
        37: "Western"
    }


@st.cache_data(ttl=1800)  # Cache for 30 minutes
def fetch_movies_by_genre(genre_id: int, limit: int = 20) -> List[Dict]:
    """Fetch movies by genre from TMDB API."""
    if TMDB_API_KEY == "demo_key":
        return get_demo_movies(limit)
    
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}&language=en-US&page=1&sort_by=popularity.desc"
    
    try:
        session = create_session()
        response = session.get(url, timeout=10)
        
        if response.status_code != 200:
            st.warning(f"⚠️ Failed to fetch movies for genre: HTTP {response.status_code}")
            return get_demo_movies(limit)
        
        data = response.json()
        if not isinstance(data, dict) or "results" not in data:
            st.warning("⚠️ Invalid genre movies response")
            return get_demo_movies(limit)
        
        movies_list = []
        for movie in data.get("results", [])[:limit]:
            movies_list.append({
                "id": movie.get("id", 0),
                "title": movie.get("title", "Unknown"),
                "rating": movie.get("vote_average", 0.0),
                "description": movie.get("overview", "No description available"),
                "poster": f"https://image.tmdb.org/t/p/w500/{movie.get('poster_path')}"
                if movie.get("poster_path")
                else "https://via.placeholder.com/300x450?text=No+Poster",
                "runtime": movie.get("runtime", 120),
                "release_date": movie.get("release_date", "2000-01-01"),
                "genres": movie.get("genre_ids", []),
            })
        
        return movies_list
        
    except Exception as e:
        st.warning(f"⚠️ Error fetching movies for genre: {e}")
        return get_demo_movies(limit)


@st.cache_data(ttl=3600)
def fetch_poster(movie_id: int) -> str:
    """Fetch movie poster URL from TMDB API."""
    if TMDB_API_KEY == "demo_key":
        return "https://via.placeholder.com/300x450?text=Demo+Poster"
    
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    
    try:
        session = create_session()
        response = session.get(url, timeout=10)
        
        if response.status_code == 404:
            return "https://via.placeholder.com/300x450?text=Movie+Not+Found"
        elif response.status_code != 200:
            return "https://via.placeholder.com/300x450?text=Error+Loading+Poster"
        
        data = response.json()
        if not isinstance(data, dict):
            return "https://via.placeholder.com/300x450?text=Invalid+Response"
        
        poster_path = data.get("poster_path")
        return (
            f"https://image.tmdb.org/t/p/w500/{poster_path}"
            if poster_path
            else "https://via.placeholder.com/300x450?text=No+Poster"
        )
        
    except Exception:
        return "https://via.placeholder.com/300x450?text=Network+Error"


@st.cache_data(ttl=1800)
def fetch_trailer(movie_id: int) -> Optional[str]:
    """Fetch movie trailer URL from TMDB API."""
    if TMDB_API_KEY == "demo_key" or not movie_id:
        return None
    
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}&language=en-US"
    
    try:
        session = create_session()
        response = session.get(url, timeout=10)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        if not isinstance(data, dict) or "results" not in data:
            return None
        
        videos = data.get("results", [])
        if not videos:
            return None
        
        # Priority 1: Official YouTube trailer
        for video in videos:
            if (video.get("type") == "Trailer" and 
                video.get("site") == "YouTube" and 
                video.get("official", False) and
                video.get("key")):
                return f"https://www.youtube.com/watch?v={video['key']}"
        
        # Priority 2: Any YouTube trailer
        for video in videos:
            if (video.get("type") == "Trailer" and 
                video.get("site") == "YouTube" and
                video.get("key")):
                return f"https://www.youtube.com/watch?v={video['key']}"
        
        # Priority 3: Any trailer (Vimeo, etc.)
        for video in videos:
            if video.get("type") == "Trailer" and video.get("key"):
                if video.get("site") == "Vimeo":
                    return f"https://vimeo.com/{video['key']}"
                elif video.get("site") == "YouTube":
                    return f"https://www.youtube.com/watch?v={video['key']}"
        
        return None
        
    except Exception:
        return None


@st.cache_data(ttl=1800)
def fetch_movie_details(movie_id: int) -> Dict:
    """Fetch detailed movie information from TMDB API."""
    if TMDB_API_KEY == "demo_key":
        return {"rating": 7.5, "description": "Demo movie description"}
    
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    
    try:
        session = create_session()
        response = session.get(url, timeout=10)
        
        if response.status_code != 200:
            return {"rating": 0.0, "description": "No description available"}
        
        data = response.json()
        if not isinstance(data, dict):
            return {"rating": 0.0, "description": "No description available"}
        
        return {
            "rating": data.get("vote_average", 0.0),
            "description": data.get("overview", "No description available"),
            "runtime": data.get("runtime", 0),
            "release_date": data.get("release_date", ""),
            "genres": [g["name"] for g in data.get("genres", [])]
        }
        
    except Exception:
        return {"rating": 0.0, "description": "No description available"}


@st.cache_data(ttl=1800)
def fetch_movie_metadata(movie_id: int) -> Dict:
    """Fetch movie metadata including genres and keywords."""
    if TMDB_API_KEY == "demo_key":
        return {
            "genres": [28, 12, 18],
            "keywords": [1, 2, 3],
            "title": "Demo Movie",
            "rating": 7.5,
            "description": "Demo movie description"
        }
    
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=keywords"
    
    try:
        session = create_session()
        response = session.get(url, timeout=10)
        
        if response.status_code != 200:
            return {
                "genres": [],
                "keywords": [],
                "title": "Unknown",
                "rating": 0.0,
                "description": "No description available"
            }
        
        data = response.json()
        return {
            "genres": [g["id"] for g in data.get("genres", [])],
            "keywords": [k["id"] for k in data.get("keywords", {}).get("keywords", [])[:5]],
            "title": data.get("title", "Unknown"),
            "rating": data.get("vote_average", 0.0),
            "description": data.get("overview", "No description available"),
        }
        
    except Exception:
        return {
            "genres": [],
            "keywords": [],
            "title": "Unknown",
            "rating": 0.0,
            "description": "No description available"
        }


def search_movies(query: str, limit: int = 20) -> List[Dict]:
    """Search for movies by title."""
    if TMDB_API_KEY == "demo_key":
        return get_demo_movies(limit)
    
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}&language=en-US&page=1"
    
    try:
        session = create_session()
        response = session.get(url, timeout=10)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        if not isinstance(data, dict) or "results" not in data:
            return []
        
        movies_list = []
        for movie in data.get("results", [])[:limit]:
            movies_list.append({
                "id": movie.get("id", 0),
                "title": movie.get("title", "Unknown"),
                "rating": movie.get("vote_average", 0.0),
                "description": movie.get("overview", "No description available"),
                "poster": f"https://image.tmdb.org/t/p/w500/{movie.get('poster_path')}"
                if movie.get("poster_path")
                else "https://via.placeholder.com/300x450?text=No+Poster",
                "runtime": movie.get("runtime", 120),
                "release_date": movie.get("release_date", "2000-01-01"),
                "genres": movie.get("genre_ids", []),
            })
        
        return movies_list
        
    except Exception:
        return []
