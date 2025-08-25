import streamlit as st
import numpy as np
import pandas as pd
import os
from typing import List, Tuple, Optional, Dict, Any
from .api_calls import (
    fetch_movie_metadata,
    fetch_poster,
    fetch_popular_movies,
    fetch_genres,
    fetch_movies_by_genre,
)


class RecommendationEngine:
    def __init__(self, movies: pd.DataFrame, similarity: np.ndarray = None, svd_model = None):
        self.movies = movies
        self.similarity = similarity
        self.svd_model = svd_model
        self.mood_genres = {
            "happy": [35, 10751, 16, 10402],
            "sad": [18, 10749, 10402, 99],
            "excited": [28, 12, 878, 53],
            "relaxed": [99, 36, 14, 10751],
            "scared": [27, 53, 9648, 28],
            "romantic": [10749, 18, 35, 10402],
            "adventurous": [12, 28, 14, 878],
            "thoughtful": [18, 99, 36, 80]
        }

    def _validate_data(self, required_data: List[str]) -> bool:
        validations = {
            "movies": not self.movies.empty,
            "similarity": self.similarity is not None,
            "svd_model": self.svd_model is not None
        }
        return all(validations.get(data, True) for data in required_data)

    def _get_movie_index(self, movie_title: str) -> Optional[int]:
        indices = self.movies[self.movies["title"].str.lower() == movie_title.lower()].index
        return indices[0] if len(indices) > 0 else None

    def _get_user_rated_movies(self, user_id: int) -> set:
        try:
            if not os.path.exists("user_reviews.csv"):
                return set()
            
            reviews_df = pd.read_csv("user_reviews.csv")
            user_reviews = reviews_df[reviews_df["user"].astype(str) == str(user_id)]
            return set(user_reviews["movie_id"].astype(int))
        except Exception:
            return set()

    def content_based_similarity(self, movie_title: str, num_recommendations: int = 5) -> Tuple[List[str], List[str]]:
        if not self._validate_data(["movies", "similarity"]):
            return self._fallback_recommendations()
        
        try:
            index = self._get_movie_index(movie_title)
            if index is None or index >= len(self.similarity):
                st.error(f"Movie '{movie_title}' not found")
                return self._fallback_recommendations()
            
            similarity_scores = list(enumerate(self.similarity[index]))
            similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
            
            recommendations = []
            posters = []
            
            for idx, score in similarity_scores[1:num_recommendations + 1]:
                if idx < len(self.movies):
                    movie = self.movies.iloc[idx]
                    recommendations.append(movie.get('title', 'Unknown'))
                    posters.append(fetch_poster(movie.get('id', 0)))
            
            return recommendations, posters
            
        except Exception as e:
            st.error(f"Content-based recommendation error: {e}")
            return self._fallback_recommendations()

    def content_based_tmdb(self, movie_title: str, num_recommendations: int = 5) -> Tuple[List[str], List[str]]:
        if not self._validate_data(["movies"]):
            return self._fallback_recommendations()

        try:
            movie_data = self.movies[self.movies["title"].str.lower() == movie_title.lower()]
            if movie_data.empty:
                return self._fallback_recommendations()
            
            target_id = movie_data["id"].iloc[0]
            target_metadata = fetch_movie_metadata(target_id)
            target_genres = set(target_metadata.get("genres", []))
            
            similarities = []
            for _, movie in self.movies.iterrows():
                if movie["title"].lower() == movie_title.lower():
                    continue
                
                try:
                    metadata = fetch_movie_metadata(movie["id"])
                    genres = set(metadata.get("genres", []))
                    
                    jaccard_sim = self._calculate_jaccard_similarity(target_genres, genres)
                    similarities.append((movie["id"], movie["title"], jaccard_sim))
                except Exception:
                    continue

            similarities.sort(key=lambda x: x[2], reverse=True)
            top_similarities = similarities[:num_recommendations]
            
            names = [title for _, title, _ in top_similarities]
            posters = [fetch_poster(movie_id) for movie_id, _, _ in top_similarities]
            
            return names, posters

        except Exception as e:
            st.error(f"TMDB content-based error: {e}")
            return self._fallback_recommendations()

    def collaborative_filtering(self, user_id: int, num_recommendations: int = 5) -> Tuple[List[str], List[str]]:
        if not self._validate_data(["movies", "svd_model"]):
            return self._fallback_recommendations()
        
        try:
            rated_movies = self._get_user_rated_movies(user_id)
            predictions = []
            
            for _, movie in self.movies.iterrows():
                movie_id = movie["id"]
                if movie_id not in rated_movies:
                    try:
                        prediction = self.svd_model.predict(user_id, movie_id)
                        predictions.append((movie_id, movie["title"], prediction.est))
                    except Exception:
                        continue

            predictions.sort(key=lambda x: x[2], reverse=True)
            top_predictions = predictions[:num_recommendations]
            
            names = [title for _, title, _ in top_predictions]
            posters = [fetch_poster(movie_id) for movie_id, _, _ in top_predictions]
            
            return names, posters
            
        except Exception as e:
            st.error(f"Collaborative filtering error: {e}")
            return self._fallback_recommendations()

    def hybrid_recommendations(self, movie_title: str, user_id: int, 
                              content_weight: float = 0.6, collab_weight: float = 0.4) -> Tuple[List[str], List[str]]:
        if not self._validate_data(["movies"]):
            return self._fallback_recommendations()
        
        try:
            content_names, content_posters = self.content_based_similarity(movie_title)
            collab_names, collab_posters = self.collaborative_filtering(user_id)
            
            hybrid_movies = {}
            
            for i, name in enumerate(content_names):
                score = content_weight * (len(content_names) - i) / len(content_names)
                hybrid_movies[name] = {
                    'score': score, 
                    'poster': content_posters[i]
                }
            
            for i, name in enumerate(collab_names):
                score = collab_weight * (len(collab_names) - i) / len(collab_names)
                if name in hybrid_movies:
                    hybrid_movies[name]['score'] += score
                else:
                    hybrid_movies[name] = {
                        'score': score, 
                        'poster': collab_posters[i]
                    }
            
            sorted_movies = sorted(hybrid_movies.items(), key=lambda x: x[1]['score'], reverse=True)[:5]
            
            names = [movie[0] for movie in sorted_movies]
            posters = [movie[1]['poster'] for movie in sorted_movies]
            
            return names, posters
            
        except Exception as e:
            st.error(f"Hybrid recommendation error: {e}")
            return self._fallback_recommendations()

    def mood_based_recommendations(self, mood_answers: Dict[str, Any]) -> Tuple[List[Dict], List[str]]:
        try:
            primary_mood = mood_answers.get("mood", "thoughtful")
            time_available = mood_answers.get("time_available", "medium")
            genre_preference = mood_answers.get("genre_preference", "")
            avoid_content = mood_answers.get("avoid_content", [])
            watching_with = mood_answers.get("watching_with", "alone")
            energy = mood_answers.get("energy", "medium")
            
            # Determine target runtime based on time available
            if "short" in time_available.lower():
                target_runtime = (60, 90)
            elif "long" in time_available.lower():
                target_runtime = (120, 200)
            else:  # medium
                target_runtime = (90, 120)
            
            # Get genre IDs based on preference or mood
            if genre_preference:
                # Find genre ID by name
                all_genres = fetch_genres()
                genre_id = None
                for gid, gname in all_genres.items():
                    if gname.lower() == genre_preference.lower():
                        genre_id = gid
                        break
                if genre_id:
                    genre_ids = [genre_id]
                else:
                    genre_ids = self.mood_genres.get(primary_mood, [18])
            else:
                genre_ids = self.mood_genres.get(primary_mood, [18])
            
            # Adjust genres based on watching company
            if watching_with == "kids":
                # Filter out adult content genres
                family_genres = [16, 10751]  # Animation, Family
                genre_ids = [g for g in genre_ids if g in family_genres] or family_genres
            elif watching_with == "family":
                # Avoid very violent or scary content
                avoid_genres = [27, 53, 80]  # Horror, Thriller, Crime
                genre_ids = [g for g in genre_ids if g not in avoid_genres]
            
            recommendations = []
            posters = []
            movies_per_genre = max(1, 5 // len(genre_ids))
            
            for genre_id in genre_ids:
                if len(recommendations) >= 5:
                    break
                    
                try:
                    genre_movies = fetch_movies_by_genre(genre_id, limit=movies_per_genre + 5)
                    for movie in genre_movies:
                        if len(recommendations) >= 5:
                            break
                            
                        # Check if movie title is already recommended
                        if any(movie["title"] == rec["title"] for rec in recommendations):
                            continue
                        
                        # Check runtime constraints
                        movie_runtime = movie.get("runtime", 120)
                        if not (target_runtime[0] <= movie_runtime <= target_runtime[1]):
                            continue
                        
                        # Check avoid content (basic filtering)
                        movie_overview = movie.get("overview", "").lower()
                        should_avoid = False
                        for avoid in avoid_content:
                            if avoid.lower() in movie_overview:
                                should_avoid = True
                                break
                        
                        if should_avoid:
                            continue
                        
                        # Create movie object with all required fields
                        movie_obj = {
                            "id": movie.get("id", len(recommendations) + 1000),
                            "title": movie["title"],
                            "poster": movie["poster"],
                            "rating": movie.get("rating", 7.5),
                            "description": movie.get("overview", f"A great {primary_mood} movie!"),
                            "runtime": movie_runtime,
                            "release_date": movie.get("release_date", "2020-01-01"),
                            "genres": movie.get("genres", [])
                        }
                        
                        recommendations.append(movie_obj)
                        posters.append(movie["poster"])
                        
                except Exception:
                    continue
            
            # Always return a proper tuple
            if recommendations:
                return recommendations, posters
            else:
                fallback_names, fallback_posters = self._fallback_recommendations()
                # Create fallback movie objects
                fallback_movies = []
                for i, (name, poster) in enumerate(zip(fallback_names, fallback_posters)):
                    fallback_movies.append({
                        "id": i + 1000,
                        "title": name,
                        "poster": poster,
                        "rating": 7.5,
                        "description": f"A great {primary_mood} movie for your mood!",
                        "runtime": 120,
                        "release_date": "2020-01-01",
                        "genres": []
                    })
                return fallback_movies, fallback_posters
            
        except Exception as e:
            fallback_names, fallback_posters = self._fallback_recommendations()
            # Create fallback movie objects
            fallback_movies = []
            for i, (name, poster) in enumerate(zip(fallback_names, fallback_posters)):
                fallback_movies.append({
                    "id": i + 1000,
                    "title": name,
                    "poster": poster,
                    "rating": 7.5,
                    "description": "A great movie for your mood!",
                    "runtime": 120,
                    "release_date": "2020-01-01",
                    "genres": []
                })
            return fallback_movies, fallback_posters

    def genre_based_recommendations(self, genre_id: int, limit: int = 5) -> Tuple[List[str], List[str]]:
        try:
            genre_movies = fetch_movies_by_genre(genre_id, limit=limit * 2)
            
            if genre_movies:
                movies_sample = genre_movies[:limit]
                names = [movie["title"] for movie in movies_sample]
                posters = [movie["poster"] for movie in movies_sample]
                return names, posters
            
            return self._fallback_recommendations()
            
        except Exception:
            return self._fallback_recommendations()

    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        try:
            if not os.path.exists("user_reviews.csv"):
                return {}
            
            reviews_df = pd.read_csv("user_reviews.csv")
            user_reviews = reviews_df[reviews_df["user"].astype(str) == str(user_id)]
            
            if user_reviews.empty:
                return {}
            
            profile = {
                "total_reviews": len(user_reviews),
                "average_rating": user_reviews["rating"].mean(),
                "top_rated_movies": user_reviews.nlargest(5, "rating")["title"].tolist(),
                "most_recent_movies": user_reviews.nlargest(5, "timestamp")["title"].tolist() 
                if "timestamp" in user_reviews.columns else [],
                "rating_distribution": user_reviews["rating"].value_counts().to_dict()
            }
            
            return profile
            
        except Exception:
            return {}

    def _calculate_jaccard_similarity(self, set1: set, set2: set) -> float:
        if not set1 and not set2:
            return 0.0
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0.0

    def _fallback_recommendations(self) -> Tuple[List[str], List[str]]:
        try:
            popular_movies = fetch_popular_movies(limit=5)
            if popular_movies:
                names = [movie["title"] for movie in popular_movies]
                posters = [movie["poster"] for movie in popular_movies]
                return names, posters
            return [], []
        except Exception:
            return [], []


def recommend_content_based(movie_title: str, movies: pd.DataFrame, similarity: np.ndarray) -> Tuple[List[str], List[str]]:
    engine = RecommendationEngine(movies, similarity)
    return engine.content_based_similarity(movie_title)

def recommend_content_based_tmdb(movie_title: str, movies: pd.DataFrame, num_recommendations: int = 5) -> Tuple[List[str], List[str]]:
    engine = RecommendationEngine(movies)
    return engine.content_based_tmdb(movie_title, num_recommendations)

def recommend_collaborative(user_id: int, movies: pd.DataFrame, svd_model) -> Tuple[List[str], List[str]]:
    engine = RecommendationEngine(movies, svd_model=svd_model)
    return engine.collaborative_filtering(user_id)

def recommend_hybrid(movie_title: str, user_id: int, movies: pd.DataFrame, similarity: np.ndarray, svd_model) -> Tuple[List[str], List[str]]:
    engine = RecommendationEngine(movies, similarity, svd_model)
    return engine.hybrid_recommendations(movie_title, user_id)

def recommend_by_mood(mood_answers: dict) -> Tuple[List[Dict], List[str]]:
    engine = RecommendationEngine(pd.DataFrame())
    return engine.mood_based_recommendations(mood_answers)

def get_fallback_recommendations() -> Tuple[List[str], List[str]]:
    engine = RecommendationEngine(pd.DataFrame())
    return engine._fallback_recommendations()

def get_user_top_rated_movies(user_id: int, limit: int = 5) -> List[str]:
    engine = RecommendationEngine(pd.DataFrame())
    profile = engine.get_user_profile(user_id)
    return profile.get("top_rated_movies", [])[:limit]

def get_similar_movies_by_genre(genre_id: int, limit: int = 5) -> Tuple[List[str], List[str]]:
    engine = RecommendationEngine(pd.DataFrame())
    return engine.genre_based_recommendations(genre_id, limit)