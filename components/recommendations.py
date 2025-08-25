import streamlit as st
import numpy as np
import pandas as pd
import os
import uuid
from .api_calls import (
    fetch_movie_metadata,
    fetch_poster,
    fetch_popular_movies,
    fetch_genres,
)


def recommend_content_based(movie_title, movies, similarity):
    if similarity is None or movies.empty:
        st.error("Content-based recommendations unavailable due to missing data.")
        return [], []
    try:
        index = movies[movies["title"] == movie_title].index[0]
        distances = sorted(
            list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1]
        )
        recommended_names = []
        recommended_posters = []
        for i in distances[1:6]:
            movie_id = movies.iloc[i[0]].id
            recommended_names.append(movies.iloc[i[0]].title)
            recommended_posters.append(fetch_poster(movie_id))
        return recommended_names, recommended_posters
    except IndexError:
        st.error(f"Movie '{movie_title}' not found in the database.")
        return [], []
    except Exception as e:
        st.error(f"Error generating content-based recommendations: {e}")
        return [], []


def recommend_content_based_tmdb(movie_title, movies, num_recommendations=5):
    if movies.empty:
        st.error("Content-based recommendations unavailable due to missing movie data.")
        return [], []

    try:
        movie_id = (
            movies[movies["title"] == movie_title]["id"].iloc[0]
            if movie_title in movies["title"].values
            else None
        )
        if not movie_id:
            st.error(f"Movie '{movie_title}' not found.")
            return [], []

        # Fetch metadata for the target movie
        target_metadata = fetch_movie_metadata(movie_id)
        target_genres = set(target_metadata["genres"])

        # Compute similarities with other movies
        similarities = []
        for movie in movies.itertuples():
            if movie.title == movie_title:
                continue
            metadata = fetch_movie_metadata(movie.id)
            genres = set(metadata["genres"])
            # Jaccard similarity for genres
            intersection = len(target_genres & genres)
            union = len(target_genres | genres)
            sim = intersection / union if union > 0 else 0
            similarities.append((movie.id, movie.title, sim))

        # Sort by similarity and select top recommendations
        similarities = sorted(similarities, key=lambda x: x[2], reverse=True)[
            :num_recommendations
        ]
        recommended_names = [title for _, title, _ in similarities]
        recommended_posters = [
            fetch_poster(movie_id) for movie_id, _, _ in similarities
        ]
        return recommended_names, recommended_posters

    except IndexError:
        st.error(f"Movie '{movie_title}' not found in the database.")
        return [], []
    except Exception as e:
        st.error(f"Error generating TMDB-based content recommendations: {e}")
        return [], []


def recommend_collaborative(user_id, movies, svd_model):
    if svd_model is None or movies.empty:
        st.error("Collaborative recommendations unavailable due to missing data.")
        return [], []
    try:
        # Get movies already rated by the user
        rated_movie_ids = set()
        if os.path.exists("user_reviews.csv"):
            reviews_df = pd.read_csv("user_reviews.csv", header=0)
            reviews_df["user"] = reviews_df["user"].astype(str)
            uid = str(user_id)
            rated_movie_ids = set(
                reviews_df[reviews_df["user"] == uid]["movie_id"].astype(int).tolist()
            )

        # Predict ratings for movies not yet rated
        predictions = [
            (movie_id, svd_model.predict(user_id, movie_id).est)
            for movie_id in movies["id"]
            if movie_id not in rated_movie_ids
        ]
        predictions = sorted(predictions, key=lambda x: x[1], reverse=True)
        recommended_names = []
        recommended_posters = []
        for movie_id, _ in predictions[:3]:
            movie_title = movies[movies["id"] == movie_id]["title"].iloc[0]
            recommended_names.append(movie_title)
            recommended_posters.append(fetch_poster(movie_id))
        return recommended_names, recommended_posters
    except Exception as e:
        st.error(f"Error generating collaborative recommendations: {e}")
        return [], []


def recommend_hybrid(
    movie_title, user_id, movies, similarity, svd_model, num_recommendations=3, content_weight=0.5
):
    if movies.empty:
        st.error("Hybrid recommendations unavailable due to missing movie data.")
        return [], []

    try:
        # Get content-based recommendations
        if similarity is not None:
            content_names, content_posters = recommend_content_based(
                movie_title, movies, similarity
            )
        else:
            content_names, content_posters = recommend_content_based_tmdb(
                movie_title, movies, num_recommendations * 2
            )
        content_scores = {
            name: score
            for name, score in zip(
                content_names, np.linspace(1.0, 0.5, len(content_names))
            )
        }

        # Get collaborative recommendations (SVD-based)
        collab_names, collab_posters = recommend_collaborative(
            user_id, movies, svd_model
        )
        collab_scores = {
            name: score
            for name, score in zip(
                collab_names, np.linspace(1.0, 0.5, len(collab_names))
            )
        }

        # Combine scores
        combined_scores = {}
        all_names = set(content_names) | set(collab_names)

        for name in all_names:
            content_score = content_scores.get(name, 0.0) * content_weight
            collab_score = collab_scores.get(name, 0.0) * (1.0 - content_weight)
            combined_scores[name] = content_score + collab_score

        # Sort by combined score and exclude the input movie
        filtered_scores = [
            (name, score) for name, score in combined_scores.items() if name != movie_title
        ]
        top_movies = sorted(filtered_scores, key=lambda x: x[1], reverse=True)[
            :num_recommendations
        ]
        recommended_names = []
        recommended_posters = []
        for name, _ in top_movies:
            if name in content_names:
                idx = content_names.index(name)
                recommended_names.append(name)
                recommended_posters.append(content_posters[idx])
            elif name in collab_names:
                idx = collab_names.index(name)
                recommended_names.append(name)
                recommended_posters.append(collab_posters[idx])
            else:
                movie_id = (
                    movies[movies["title"] == name]["id"].iloc[0]
                    if name in movies["title"].values
                    else None
                )
                if movie_id:
                    recommended_names.append(name)
                    recommended_posters.append(fetch_poster(movie_id))

        if not recommended_names:
            st.warning(
                "No hybrid recommendations found. Falling back to mood-based or popular movies."
            )
            if st.session_state.mood_answers:
                movies_list = recommend_mood_based(
                    st.session_state.mood_answers, fetch_genres()
                )
                return (
                    [m["title"] for m in movies_list[:num_recommendations]],
                    [m["poster"] for m in movies_list[:num_recommendations]],
                )
            popular_movies = fetch_popular_movies()
            return (
                [m["title"] for m in popular_movies[:num_recommendations]],
                [m["poster"] for m in popular_movies[:num_recommendations]],
            )

        return recommended_names, recommended_posters

    except IndexError:
        st.error(f"Movie '{movie_title}' not found in the database.")
        popular_movies = fetch_popular_movies()
        return (
            [m["title"] for m in popular_movies[:num_recommendations]],
            [m["poster"] for m in popular_movies[:num_recommendations]],
        )
    except Exception as e:
        st.error(f"Error generating hybrid recommendations: {e}")
        popular_movies = fetch_popular_movies()
        return (
            [m["title"] for m in popular_movies[:num_recommendations]],
            [m["poster"] for m in popular_movies[:num_recommendations]],
        )


def recommend_mood_based(answers, genre_map):
    genre_ids = []
    max_runtime = None
    min_year = None
    max_year = None
    keywords = None
    adult = False

    mood_genres = {
        "Happy": [35, 16, 12],  # Comedy, Animation, Adventure
        "Sad": [18, 10749, 99],  # Drama, Romance, Documentary
        "Stressed": [35, 10749, 10751],  # Comedy, Romance, Family
        "Excited": [28, 53, 878],  # Action, Thriller, Sci-Fi
        "Relaxed": [18, 10749, 99],  # Drama, Romance, Documentary
        "Bored": [28, 35, 12],  # Action, Comedy, Adventure
        "Angry": [53, 28, 18],  # Thriller, Action, Drama
    }
    secondary_genres = {
        "Happy": [10751],  # Family
        "Sad": [36],  # History
        "Stressed": [16],  # Animation
        "Excited": [12],  # Adventure
        "Relaxed": [35],  # Comedy
        "Bored": [878],  # Sci-Fi
        "Angry": [80],  # Crime
    }

    if answers.get("mood"):
        genre_ids.extend(mood_genres.get(answers["mood"], []))
        genre_ids.extend(secondary_genres.get(answers["mood"], []))

    if answers.get("motivation") == "Yes":
        genre_ids.extend([18, 99])  # Drama, Documentary
        keywords = "inspirational,motivational"

    if (
        answers.get("watching_with") in ["Kids", "Family"]
        or answers.get("occasion") == "Family Night"
    ):
        genre_ids.extend([16, 10751])  # Animation, Family
        adult = False
    elif (
        answers.get("occasion") == "Date Night" or answers.get("romantic") == "Yes"
    ):
        genre_ids.extend([10749, 35])  # Romance, Comedy

    if answers.get("time"):
        if answers["time"] == "Less than 1 hour":
            max_runtime = 90
        elif answers["time"] == "1-2 hours":
            max_runtime = 120
        elif answers["time"] == "2+ hours":
            max_runtime = 180

    if answers.get("genre"):
        genre_id = [k for k, v in genre_map.items() if v == answers["genre"]]
        if genre_id:
            genre_ids.append(genre_id[0])

    tone_genres = {
        "Light-hearted": [35, 10749],  # Comedy, Romance
        "Serious": [18, 36],  # Drama, History
        "Emotional": [18, 10749],  # Drama, Romance
        "Fun": [35, 12],  # Comedy, Adventure
        "Epic": [12, 28],  # Adventure, Action
        "Thought-provoking": [18, 99],  # Drama, Documentary
    }
    if answers.get("tone"):
        genre_ids.extend(tone_genres.get(answers["tone"], []))

    if answers.get("release"):
        if answers["release"] == "New (post-2010)":
            min_year = 2010
        elif answers["release"] == "Classics (pre-2010)":
            max_year = 2010

    if answers.get("mature") == "No":
        adult = False
    elif answers.get("mature") == "Yes":
        adult = True

    # Remove duplicates and limit genres
    genre_ids = list(set(genre_ids))[:3]

    # Fallback genres if none selected
    if not genre_ids:
        genre_ids = [35, 18]  # Comedy, Drama

    # Unique cache key for diversity
    cache_key = str(uuid.uuid4()) + str(answers)

    return fetch_mood_based_movies(
        cache_key, genre_ids, max_runtime, min_year, max_year, keywords, adult
    )


@st.cache_data
def fetch_mood_based_movies(
    _cache_key,
    genre_ids,
    max_runtime=None,
    min_year=None,
    max_year=None,
    keywords=None,
    adult=False,
):
    from .api_calls import TMDB_API_KEY
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    movies_list = []
    base_url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=en-US&sort_by=vote_average.desc&vote_count.gte=100"

    # Construct query parameters
    query_params = []
    if genre_ids:
        query_params.append(f"with_genres={','.join(map(str, genre_ids))}")
    query_params.append(f"include_adult={adult}")

    # Try multiple query variations for diversity
    attempts = [
        # Full query
        query_params
        + (
            ([f"with_runtime.lte={max_runtime}"] if max_runtime else [])
            + ([f"primary_release_date.gte={min_year}-01-01"] if min_year else [])
            + ([f"primary_release_date.lte={max_year}-12-31"] if max_year else [])
            + ([f"with_keywords={keywords}"] if keywords else [])
            + ["page=1"]
        ),
        # Relax runtime and keywords
        query_params
        + (
            ([f"primary_release_date.gte={min_year}-01-01"] if min_year else [])
            + ([f"primary_release_date.lte={max_year}-12-31"] if max_year else [])
            + ["page=1"]
        ),
        # Random page for diversity
        query_params
        + (
            ([f"primary_release_date.gte={min_year}-01-01"] if min_year else [])
            + ([f"primary_release_date.lte={max_year}-12-31"] if max_year else [])
            + [f"page={np.random.randint(1, 5)}"]
        ),
        # Broad query
        query_params + ["page=1"],
    ]

    for params in attempts:
        url = base_url + "&" + "&".join(params)
        try:
            session = requests.Session()
            retries = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[204, 429, 500, 502, 503, 504],
            )
            session.mount("https://", HTTPAdapter(max_retries=retries))
            response = session.get(url, timeout=5)
            if response.status_code != 200:
                continue
            data = response.json()
            if not isinstance(data, dict) or "results" not in data:
                continue
            for movie in data.get("results", [])[:5]:
                movies_list.append(
                    {
                        "id": movie.get("id", 0),
                        "title": movie.get("title", "Unknown"),
                        "rating": movie.get("vote_average", 0.0),
                        "description": movie.get(
                            "overview", "No description available"
                        ),
                        "poster": f"https://image.tmdb.org/t/p/w500/{movie.get('poster_path')}"
                        if movie.get("poster_path")
                        else "https://via.placeholder.com/200x300?text=No+Poster",
                        "runtime": movie.get("runtime", 120),
                        "release_date": movie.get("release_date", "2000-01-01"),
                        "genres": movie.get("genre_ids", []),
                    }
                )
            if movies_list:
                # Shuffle for diversity
                np.random.shuffle(movies_list)
                return movies_list[:5]
        except Exception as e:
            continue

    # Fallback to popular movies with warning
    st.warning(
        "No movies found matching your mood-based criteria. Showing popular movies."
    )
    return fetch_popular_movies()
