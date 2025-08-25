import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "9ef5ae6fc8b8f484e9295dc97d8d32ea")


@st.cache_data
def fetch_popular_movies():
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page=1"
    try:
        session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=1, status_forcelist=[204, 429, 500, 502, 503, 504]
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        response = session.get(url, timeout=5)
        if response.status_code != 200:
            st.warning(f"Failed to fetch popular movies: HTTP {response.status_code}")
            return []
        data = response.json()
        if not isinstance(data, dict) or "results" not in data:
            st.warning("Invalid popular movies response")
            return []
        movies_list = []
        for movie in data.get("results", []):
            movies_list.append(
                {
                    "id": movie.get("id", 0),
                    "title": movie.get("title", "Unknown"),
                    "rating": movie.get("vote_average", 0.0),
                    "description": movie.get("overview", "No description available"),
                    "poster": f"https://image.tmdb.org/t/p/w500/{movie.get('poster_path')}"
                    if movie.get("poster_path")
                    else "https://via.placeholder.com/200x300?text=No+Poster",
                    "runtime": movie.get("runtime", 120),
                    "release_date": movie.get("release_date", "2000-01-01"),
                    "genres": movie.get("genre_ids", []),
                }
            )
        return movies_list
    except requests.exceptions.RequestException as e:
        st.warning(f"Network error fetching popular movies: {e}")
        return []
    except Exception as e:
        st.warning(f"Error fetching popular movies: {e}")
        return []


@st.cache_data
def fetch_genres():
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US"
    try:
        session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=1, status_forcelist=[204, 429, 500, 502, 503, 504]
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        response = session.get(url, timeout=5)
        if response.status_code != 200:
            st.warning(f"Failed to fetch genres: HTTP {response.status_code}")
            return {}
        data = response.json()
        if not isinstance(data, dict) or "genres" not in data:
            st.warning("Invalid genres response")
            return {}
        return {genre["id"]: genre["name"] for genre in data.get("genres", [])}
    except Exception as e:
        st.warning(f"Error fetching genres: {e}")
        return {}


@st.cache_data
def fetch_movies_by_genre(genre_id):
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}&language=en-US&page=1"
    try:
        session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=1, status_forcelist=[204, 429, 500, 502, 503, 504]
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        response = session.get(url, timeout=5)
        if response.status_code != 200:
            st.warning(
                f"Failed to fetch movies for genre: HTTP {response.status_code}"
            )
            return []
        data = response.json()
        if not isinstance(data, dict) or "results" not in data:
            st.warning("Invalid genre movies response")
            return []
        movies_list = []
        for movie in data.get("results", []):
            movies_list.append(
                {
                    "id": movie.get("id", 0),
                    "title": movie.get("title", "Unknown"),
                    "rating": movie.get("vote_average", 0.0),
                    "description": movie.get("overview", "No description available"),
                    "poster": f"https://image.tmdb.org/t/p/w500/{movie.get('poster_path')}"
                    if movie.get("poster_path")
                    else "https://via.placeholder.com/200x300?text=No+Poster",
                    "runtime": movie.get("runtime", 120),
                    "release_date": movie.get("release_date", "2000-01-01"),
                    "genres": movie.get("genre_ids", []),
                }
            )
        return movies_list
    except Exception as e:
        st.warning(f"Error fetching movies for genre: {e}")
        return []


@st.cache_data
def fetch_poster(movie_id):
    try:
        session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=1, status_forcelist=[204, 429, 500, 502, 503, 504]
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        response = session.get(url, timeout=5)

        if response.status_code == 204:
            st.warning(f"No poster available for movie ID {movie_id} (HTTP 204)")
            return "https://via.placeholder.com/200x300?text=No+Poster"
        elif response.status_code != 200:
            st.warning(
                f"Failed to fetch poster for movie ID {movie_id}: HTTP {response.status_code}"
            )
            return "https://via.placeholder.com/200x300?text=Error"

        data = response.json()
        if not isinstance(data, dict):
            st.warning(f"Invalid poster response for movie ID {movie_id}")
            return "https://via.placeholder.com/200x300?text=Error"

        poster_path = data.get("poster_path")
        return (
            f"https://image.tmdb.org/t/p/w500/{poster_path}"
            if poster_path
            else "https://via.placeholder.com/200x300?text=No+Poster"
        )
    except requests.exceptions.ConnectionError as e:
        st.warning(f"Network error fetching poster for movie ID {movie_id}: {e}")
        return "https://via.placeholder.com/200x300?text=Network+Error"
    except requests.exceptions.Timeout:
        st.warning(f"Request timed out fetching poster for movie ID {movie_id}")
        return "https://via.placeholder.com/200x300?text=Timeout"
    except requests.exceptions.RequestException as e:
        st.warning(f"Error fetching poster for movie ID {movie_id}: {e}")
        return "https://via.placeholder.com/200x300?text=Error"
    except Exception as e:
        st.warning(f"Unexpected error fetching poster for movie ID {movie_id}: {e}")
        return "https://via.placeholder.com/200x300?text=Error"


@st.cache_data
def fetch_trailer(movie_id):
    try:
        session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=1, status_forcelist=[204, 429, 500, 502, 503, 504]
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}&language=en-US"
        response = session.get(url, timeout=5)

        if response.status_code == 204:
            st.warning(f"No trailer available for movie ID {movie_id} (HTTP 204)")
            return None
        elif response.status_code != 200:
            st.warning(
                f"Failed to fetch trailer for movie ID {movie_id}: HTTP {response.status_code}"
            )
            return None

        data = response.json()
        if not isinstance(data, dict) or "results" not in data:
            st.warning(f"Invalid trailer response for movie ID {movie_id}")
            return None

        for video in data.get("results", []):
            if video.get("type") == "Trailer" and video.get("site") == "YouTube":
                return f"https://www.youtube.com/watch?v={video['key']}"
        return None
    except requests.exceptions.ConnectionError as e:
        st.warning(
            f"Network error fetching trailer for movie ID {movie_id}. Please check internet connection."
        )
        return None
    except requests.exceptions.Timeout:
        st.warning(
            f"Request timed out fetching trailer for movie ID {movie_id}. Please try again later."
        )
        return None
    except requests.exceptions.RequestException as e:
        st.warning(f"Error fetching trailer for movie ID {movie_id}: {e}")
        return None
    except Exception as e:
        st.warning(f"Unexpected error fetching trailer for movie ID {movie_id}: {e}")
        return None


@st.cache_data
def fetch_movie_details(movie_id):
    try:
        session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=1, status_forcelist=[204, 429, 500, 502, 503, 504]
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        response = session.get(url, timeout=5)

        if response.status_code == 204:
            st.warning(f"No details available for movie ID {movie_id} (HTTP 204)")
            return {"rating": 0.0, "description": "No description available"}
        elif response.status_code != 200:
            st.warning(
                f"Failed to fetch details for movie ID {movie_id}: HTTP {response.status_code}"
            )
            return {"rating": 0.0, "description": "No description available"}

        data = response.json()
        if not isinstance(data, dict):
            st.warning(f"Invalid details response for movie ID {movie_id}")
            return {"rating": 0.0, "description": "No description available"}

        return {
            "rating": data.get("vote_average", 0.0),
            "description": data.get("overview", "No description available"),
        }
    except Exception as e:
        st.warning(f"Error fetching movie details for movie ID {movie_id}: {e}")
        return {"rating": 0.0, "description": "No description available"}


@st.cache_data
def fetch_movie_metadata(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=keywords"
    try:
        session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=1, status_forcelist=[204, 429, 500, 502, 503, 504]
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        response = session.get(url, timeout=5)
        if response.status_code != 200:
            st.warning(
                f"Failed to fetch metadata for movie ID {movie_id}: HTTP {response.status_code}"
            )
            return {"genres": [], "keywords": [], "title": "Unknown"}
        data = response.json()
        return {
            "genres": [g["id"] for g in data.get("genres", [])],
            "keywords": [
                k["id"] for k in data.get("keywords", {}).get("keywords", [])[:5]
            ],
            "title": data.get("title", "Unknown"),
            "rating": data.get("vote_average", 0.0),
            "description": data.get("overview", "No description available"),
        }
    except Exception as e:
        st.warning(f"Error fetching metadata for movie ID {movie_id}: {e}")
        return {
            "genres": [],
            "keywords": [],
            "title": "Unknown",
            "rating": 0.0,
            "description": "No description available",
        }
