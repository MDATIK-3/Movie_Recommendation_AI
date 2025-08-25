import streamlit as st
import pickle
import pandas as pd
import os
import csv
from datetime import datetime


@st.cache_resource
def load_pickles():
    # defaults
    movies = pd.DataFrame()
    similarity = None
    svd_model = None

    # movie list
    try:
        movies = pickle.load(open("movie_list.pkl", "rb"))
    except FileNotFoundError:
        st.warning(
            "Could not find 'movie_list.pkl'. Content-based features will be limited."
        )
    except Exception as e:
        st.warning(f"Error loading 'movie_list.pkl': {e}")

    # similarity matrix
    try:
        similarity = pickle.load(open("similarity.pkl", "rb"))
    except FileNotFoundError:
        st.info(
            "No 'similarity.pkl' found. Content-based recommendations will be limited."
        )
    except Exception as e:
        st.warning(f"Error loading 'similarity.pkl': {e}")

    # collaborative model (may require 'surprise' package)
    try:
        svd_model = pickle.load(open("svd_model.pkl", "rb"))
    except FileNotFoundError:
        st.info(
            "No 'svd_model.pkl' found. Collaborative recommendations will be disabled."
        )
        svd_model = None
    except ModuleNotFoundError as e:
        st.warning(
            f"Missing module when loading 'svd_model.pkl': {e}. Using fallback average-rating predictor."
        )
        # lightweight fallback predictor that mimics Surprise .predict(...).est
        class FallbackPredictor:
            class Pred:
                def __init__(self, est):
                    self.est = est

            def __init__(self, ratings_csv="user_reviews.csv", default=3.0):
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

        svd_model = FallbackPredictor()
    except Exception as e:
        st.warning(
            f"Error loading 'svd_model.pkl': {e}. Collaborative recommendations disabled."
        )
        svd_model = None

    return movies, similarity, svd_model


def save_user_activity(user_id, action, movie_title, movie_id, rating=None):
    try:
        file_exists = os.path.exists("user_activity.csv")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
    except Exception as e:
        st.warning(f"Error saving user activity: {e}")


def save_watchlist_to_csv(user_id, movie_title, movie_id):
    filename = f"watchlist_{user_id}.csv"
    file_exists = os.path.exists(filename)
    try:
        movie_id = int(movie_id)
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
    except Exception as e:
        st.error(f"Error saving watchlist for user {user_id}: {e}")


def load_watchlist_from_csv(user_id):
    filename = f"watchlist_{user_id}.csv"
    if os.path.exists(filename):
        try:
            watchlist_df = pd.read_csv(
                filename,
                names=["title", "movie_id"],
                skiprows=1 if os.path.getsize(filename) > 0 else 0,
                on_bad_lines="skip",
                quoting=csv.QUOTE_NONNUMERIC,
            )
            watchlist_df = watchlist_df.dropna(subset=["title", "movie_id"])
            watchlist_df["movie_id"] = pd.to_numeric(
                watchlist_df["movie_id"], errors="coerce", downcast="integer"
            )
            watchlist_df = watchlist_df.dropna(subset=["movie_id"])
            return watchlist_df[["title", "movie_id"]].to_dict("records")
        except Exception as e:
            st.warning(f"Error loading watchlist for user {user_id}: {e}")
            try:
                corrupted_filename = f"watchlist_{user_id}_corrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                os.rename(filename, corrupted_filename)
                st.info(
                    f"Corrupted watchlist file renamed to {corrupted_filename}. Starting with an empty watchlist."
                )
            except Exception as rename_e:
                st.error(f"Failed to rename corrupted watchlist file: {rename_e}")
            return []
    return []
