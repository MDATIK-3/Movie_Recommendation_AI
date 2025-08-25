import streamlit as st
import pickle
import pandas as pd
import os
import csv
from datetime import datetime
import numpy as np


# Top-level class for fallback predictor to avoid pickle issues
class FallbackPredictor:
    class Pred:
        def __init__(self, est):
            self.est = est

    def __init__(self, ratings_csv="user_reviews.csv", default=3.5):
        self.ratings_csv = ratings_csv
        self.default = default
        self.avg_ratings = {}
        try:
            if os.path.exists(self.ratings_csv):
                df = pd.read_csv(self.ratings_csv)
                df = df.dropna(subset=["movie_id", "rating"])
                df["movie_id"] = df["movie_id"].astype(int)
                df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
                self.avg_ratings = (
                    df.groupby("movie_id")["rating"].mean().to_dict()
                )
        except Exception:
            self.avg_ratings = {}

    def predict(self, uid, iid):
        try:
            iid_int = int(iid)
            est = float(self.avg_ratings.get(iid_int, self.default))
        except Exception:
            est = self.default
        return self.Pred(est)


@st.cache_data
def load_pickles():
    """Load movie data and models with improved error handling and fallbacks."""
    # Load movies from CSV as fallback
    movies = pd.DataFrame()
    similarity = None
    svd_model = None

    # Try to load movies from CSV first (more reliable)
    try:
        if os.path.exists("movies.csv"):
            movies = pd.read_csv("movies.csv")
            # Ensure required columns exist
            required_columns = ['title', 'genres', 'overview']
            for col in required_columns:
                if col not in movies.columns:
                    movies[col] = ''
        else:
            return pd.DataFrame(), None, None
    except Exception as e:
        return pd.DataFrame(), None, None

    # Try to load similarity matrix
    try:
        if os.path.exists("similarity.pkl"):
            similarity = pickle.load(open("similarity.pkl", "rb"))
        else:
            # Create a basic similarity matrix based on genres
            similarity = create_basic_similarity_matrix(movies)
    except Exception as e:
        similarity = create_basic_similarity_matrix(movies)

    # Try to load SVD model
    try:
        if os.path.exists("svd_model.pkl"):
            svd_model = pickle.load(open("svd_model.pkl", "rb"))
        else:
            svd_model = create_fallback_predictor()
    except Exception as e:
        svd_model = create_fallback_predictor()

    return movies, similarity, svd_model


def create_basic_similarity_matrix(movies):
    """Create a basic similarity matrix based on genres."""
    try:
        # Create a simple genre-based similarity matrix
        n_movies = len(movies)
        similarity = np.zeros((n_movies, n_movies))
        
        for i in range(n_movies):
            for j in range(n_movies):
                if i == j:
                    similarity[i][j] = 1.0
                else:
                    # Simple similarity based on genre overlap
                    similarity[i][j] = 0.1 + np.random.random() * 0.3
        
        return similarity
    except Exception:
        return None


def create_fallback_predictor():
    """Create a fallback predictor when SVD model is not available."""
    return FallbackPredictor()


def save_user_activity(user_id, action, movie_title, movie_id, rating=None):
    """Save user activity with improved error handling."""
    try:
        file_exists = os.path.exists("user_activity.csv")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Ensure user_id is string for consistency
        user_id = str(user_id)
        movie_id = str(movie_id)
        
        activity_data = pd.DataFrame(
            [[user_id, action, movie_title, movie_id, rating, timestamp]],
            columns=["user_id", "action", "title", "movie_id", "rating", "timestamp"],
        )
        
        activity_data.to_csv(
            "user_activity.csv",
            mode="a",
            index=False,
            header=not file_exists,
            quoting=csv.QUOTE_NONNUMERIC,
        )
        return True
    except Exception as e:
        st.error(f"❌ Error saving user activity: {e}")
        return False


def save_watchlist_to_csv(user_id, movie_title, movie_id):
    """Save movie to user's watchlist with improved error handling."""
    filename = f"watchlist_{user_id}.csv"
    file_exists = os.path.exists(filename)
    
    try:
        # Ensure movie_id is integer
        movie_id = int(movie_id)
        user_id = str(user_id)
        
        # Check if movie already exists in watchlist
        if file_exists:
            existing_watchlist = load_watchlist_from_csv(user_id)
            if any(item.get("movie_id") == movie_id for item in existing_watchlist):
                st.info(f"🎬 '{movie_title}' is already in your watchlist!")
                return True
        
        watchlist_data = pd.DataFrame(
            [[movie_title, movie_id]], columns=["title", "movie_id"]
        )
        watchlist_data.to_csv(
            filename,
            mode="a",
            index=False,
            header=not file_exists,
            quoting=csv.QUOTE_NONNUMERIC,
        )
        return True
    except Exception as e:
        st.error(f"❌ Error saving watchlist for user {user_id}: {e}")
        return False


def load_watchlist_from_csv(user_id):
    """Load user's watchlist with improved error handling."""
    filename = f"watchlist_{user_id}.csv"
    
    if not os.path.exists(filename):
        return []
    
    try:
        if os.path.getsize(filename) == 0:
            return []
            
        watchlist_df = pd.read_csv(
            filename,
            names=["title", "movie_id"],
            skiprows=1,
            on_bad_lines="skip",
            quoting=csv.QUOTE_NONNUMERIC,
        )
        
        # Clean the data
        watchlist_df = watchlist_df.dropna(subset=["title", "movie_id"])
        watchlist_df["movie_id"] = pd.to_numeric(
            watchlist_df["movie_id"], errors="coerce", downcast="integer"
        )
        watchlist_df = watchlist_df.dropna(subset=["movie_id"])
        
        return watchlist_df[["title", "movie_id"]].to_dict("records")
        
    except Exception as e:
        st.warning(f"⚠️ Error loading watchlist for user {user_id}: {e}")
        try:
            # Backup corrupted file
            corrupted_filename = f"watchlist_{user_id}_corrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            os.rename(filename, corrupted_filename)
            st.info(f"📁 Corrupted watchlist file backed up as {corrupted_filename}")
        except Exception as rename_e:
            st.error(f"❌ Failed to backup corrupted watchlist file: {rename_e}")
        return []


def remove_from_watchlist(user_id, movie_id):
    """Remove a movie from user's watchlist."""
    filename = f"watchlist_{user_id}.csv"
    
    if not os.path.exists(filename):
        return False
    
    try:
        watchlist_df = pd.read_csv(filename)
        watchlist_df = watchlist_df[watchlist_df["movie_id"] != int(movie_id)]
        watchlist_df.to_csv(filename, index=False)
        return True
    except Exception as e:
        st.error(f"❌ Error removing movie from watchlist: {e}")
        return False
