import streamlit as st
from components.api_calls import (
    fetch_genres,
    fetch_movies_by_genre,
    fetch_trailer,
    fetch_movie_details,
    fetch_poster,
    fetch_popular_movies,
)
from components.recommendations import (
    recommend_content_based,
    recommend_collaborative,
    recommend_hybrid,
)
from components.file_handling import save_user_activity, save_watchlist_to_csv
import pandas as pd
import os
import csv


def render_discover_page(movies, similarity, svd_model, **kwargs):
    """Renders the discover page for finding and getting recommendations."""
    if not movies.empty:
        user_id = st.session_state.current_user if st.session_state.current_user else 1
        movie_list = movies["title"].dropna().unique()
        selected_movie = st.selectbox("🎥 Pick a movie for recommendations", movie_list)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Get Content-Based Recommendations", key="content_based"):
                if selected_movie in movie_list:
                    recommended_names, recommended_posters = recommend_content_based(
                        selected_movie, movies, similarity
                    )
                    if recommended_names:
                        st.session_state.show_recommendations = True
                        st.session_state.recommended_names = recommended_names
                        st.session_state.recommended_posters = recommended_posters
                        st.session_state.recommendation_type = "content"
                    else:
                        st.error("Could not generate content-based recommendations.")
                else:
                    st.error(f"Movie '{selected_movie}' not found in the database.")
        with col2:
            if st.button("Get Collaborative Recommendations", key="collaborative"):
                recommended_names, recommended_posters = recommend_collaborative(
                    user_id, movies, svd_model
                )
                if recommended_names:
                    st.session_state.show_recommendations = True
                    st.session_state.recommended_names = recommended_names
                    st.session_state.recommended_posters = recommended_posters
                    st.session_state.recommendation_type = "collaborative"
                else:
                    st.error("Could not generate collaborative recommendations.")
        with col3:
            if st.button("Get Hybrid Recommendations", key="hybrid"):
                recommended_names, recommended_posters = recommend_hybrid(
                    selected_movie, user_id, movies, similarity, svd_model
                )
                if recommended_names:
                    st.session_state.show_recommendations = True
                    st.session_state.recommended_names = recommended_names
                    st.session_state.recommended_posters = recommended_posters
                    st.session_state.recommendation_type = "hybrid"
                else:
                    st.error("Could not generate hybrid recommendations.")
        with col4:
            if st.button("Get Personalized Recommendations", key="personalized"):
                try:
                    top_rated = []
                    csv_path = "user_reviews.csv"
                    if os.path.exists(csv_path):
                        reviews_df = pd.read_csv(csv_path, header=0)
                        reviews_df["user"] = reviews_df["user"].astype(str)
                        uid = (
                            str(st.session_state.current_user)
                            if st.session_state.get("current_user") is not None
                            else None
                        )
                        if uid:
                            user_reviews = reviews_df[reviews_df["user"] == uid]
                            if not user_reviews.empty:
                                top_rated = (
                                    user_reviews.sort_values(
                                        "rating", ascending=False
                                    )
                                    .head(5)["title"]
                                    .tolist()
                                )

                    if not top_rated:
                        st.warning(
                            "No ratings found for your account. Please rate some movies first."
                        )
                        st.session_state.show_recommendations = True
                        popular = fetch_popular_movies()[:5]
                        st.session_state.recommended_names = [
                            m["title"] for m in popular
                        ]
                        st.session_state.recommended_posters = [
                            m["poster"] for m in popular
                        ]
                        st.session_state.recommendation_type = "popular"
                    else:
                        personalized_names = []
                        personalized_posters = []
                        for title in top_rated:
                            names, posters = recommend_content_based(
                                title, movies, similarity
                            )
                            for n, p in zip(names, posters):
                                if n not in personalized_names:
                                    personalized_names.append(n)
                                    personalized_posters.append(p)
                        if personalized_names:
                            st.session_state.show_recommendations = True
                            st.session_state.recommended_names = personalized_names
                            st.session_state.recommended_posters = (
                                personalized_posters
                            )
                            st.session_state.recommendation_type = "personalized"
                        else:
                            st.warning(
                                "No personalized recommendations found. Showing popular movies instead."
                            )
                            st.session_state.show_recommendations = True
                            popular = fetch_popular_movies()[:5]
                            st.session_state.recommended_names = [
                                m["title"] for m in popular
                            ]
                            st.session_state.recommended_posters = [
                                m["poster"] for m in popular
                            ]
                            st.session_state.recommendation_type = "popular"
                except Exception as e:
                    st.error(f"Error loading ratings from CSV: {e}")
    else:
        st.warning(
            "No movies loaded from .pkl file. Please ensure the file is correct."
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown(
        "<h2 style='text-align: center;'>Recommended for You</h2>",
        unsafe_allow_html=True,
    )

    search_query = st.text_input("", placeholder="Search movies...")

    genre_map = fetch_genres()
    genre_names = [
        "Action",
        "Comedy",
        "Drama",
        "Sci-Fi",
        "Horror",
        "Romance",
        "Thriller",
        "Adventure",
    ]
    genre_ids = {
        name: gid for gid, name in genre_map.items() if name in genre_names
    }

    cols = st.columns(len(genre_names))
    for idx, genre in enumerate(genre_names):
        with cols[idx]:
            if st.button(genre, key=f"genre_{genre}"):
                genre_id = genre_ids.get(genre)
                if genre_id:
                    st.session_state.selected_genre = genre
                    st.session_state.genre_movies = fetch_movies_by_genre(genre_id)
                    st.session_state.show_recommendations = False

    if st.session_state.selected_genre and st.session_state.genre_movies:
        st.subheader(f"{st.session_state.selected_genre} Movies")
        cols = st.columns(3)
        for idx, movie in enumerate(st.session_state.genre_movies[:3]):
            with cols[idx % 3]:
                trailer_url = fetch_trailer(movie["id"])
                st.markdown(
                    f"""
                    <div class='movie-card' style='padding-bottom: 0;'>
                        <img src='{movie['poster']}' style='width: 100%; border-radius: 10px;'>
                        <h3>{movie['title']}</h3>
                        <p>⭐ {movie['rating']:.1f}</p>
                        <p>{movie['description'][:100]}...</p>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.button("Watch Now", key=f'watch_genre_{movie["id"]}')
                with col2:
                    st.button(
                        "Add to Watchlist", key=f'watchlist_genre_{movie["id"]}'
                    )
                with col3:
                    if trailer_url:
                        st.markdown(
                            f'<a href="{trailer_url}" target="_blank">Watch Trailer</a>',
                            unsafe_allow_html=True,
                        )
                if st.session_state.get(f"show_rating_{movie['id']}", False):
                    rating = st.slider(
                        f"Rate {movie['title']} (1-5)",
                        1,
                        5,
                        key=f"rating_genre_{movie['id']}",
                    )
                    review = st.text_area(
                        f"Write a review for {movie['title']}",
                        key=f"review_genre_{movie['id']}",
                    )
                    if st.button(
                        "Submit Rating & Review",
                        key=f"submit_rating_genre_{movie['id']}",
                    ):
                        if st.session_state.current_user:
                            save_user_activity(
                                st.session_state.current_user,
                                "rated",
                                movie["title"],
                                movie["id"],
                                rating,
                            )
                            file_exists = os.path.exists("user_reviews.csv")
                            with open(
                                "user_reviews.csv", "a", newline="", encoding="utf-8"
                            ) as f:
                                writer = csv.writer(f)
                                if not file_exists:
                                    writer.writerow(
                                        ["user", "movie_id", "title", "rating", "review"]
                                    )
                                writer.writerow(
                                    [
                                        st.session_state.current_user,
                                        movie["id"],
                                        movie["title"],
                                        rating,
                                        review,
                                    ]
                                )
                            st.success(
                                f"Rated {movie['title']} with {rating} stars and review submitted!"
                            )
                            st.session_state[f"show_rating_{movie['id']}"] = False
                        else:
                            st.warning("Please sign in to rate movies.")
                try:
                    reviews_df = pd.read_csv("user_reviews.csv", header=0)
                    movie_reviews = reviews_df[reviews_df["movie_id"] == movie["id"]]
                    if not movie_reviews.empty:
                        avg_rating = movie_reviews["rating"].astype(float).mean()
                        st.markdown(f"**Average Rating:** {avg_rating:.1f} ⭐")
                        st.markdown("**Recent Reviews:**")
                        for _, row in movie_reviews.tail(3).iterrows():
                            st.markdown(
                                f"- *{row['user']}*: {row['review']} ({row['rating']}⭐)"
                            )
                except Exception:
                    pass

    if search_query and not movies.empty:
        st.session_state.show_recommendations = False
        st.session_state.selected_genre = None
        st.session_state.last_search = search_query
        filtered_movies = movies[
            movies["title"].str.contains(search_query, case=False, na=False)
        ]
        if not filtered_movies.empty:
            cols = st.columns(3)
            for idx, movie in enumerate(filtered_movies.head(3).itertuples()):
                with cols[idx % 3]:
                    trailer_url = fetch_trailer(movie.id)
                    poster = fetch_poster(movie.id)
                    rating = (
                        movie.vote_average
                        if hasattr(movie, "vote_average")
                        and pd.notna(movie.vote_average)
                        else fetch_movie_details(movie.id)["rating"]
                    )
                    description = (
                        movie.overview
                        if hasattr(movie, "overview") and pd.notna(movie.overview)
                        else fetch_movie_details(movie.id)["description"]
                    )
                    st.markdown(
                        f"""
                        <div class='movie-card' style='padding-bottom: 0;'>
                            <img src='{poster}' style='width: 100%; border-radius: 10px;'>
                            <h3>{movie.title}</h3>
                            <p>⭐ {rating:.1f}</p>
                            <p>{description[:100]}...</p>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("Watch Now", key=f"watch_search_{movie.id}"):
                            if st.session_state.current_user:
                                save_user_activity(
                                    st.session_state.current_user,
                                    "watched",
                                    movie.title,
                                    movie.id,
                                )
                                st.session_state[f"rating_movie_{movie.id}"] = (
                                    movie.title
                                )
                                st.session_state[f"show_rating_{movie.id}"] = True
                                st.session_state[f"rating_movie_id_{movie.id}"] = (
                                    movie.id
                                )
                            else:
                                st.warning("Please sign in to watch movies.")
                    with col2:
                        st.button(
                            "Add to Watchlist", key=f"watchlist_search_{movie.id}"
                        )
                    with col3:
                        if trailer_url:
                            st.markdown(
                                f'<a href="{trailer_url}" target="_blank">Watch Trailer</a>',
                                unsafe_allow_html=True,
                            )
                    if st.session_state.get(f"show_rating_{movie.id}", False):
                        rating = st.slider(
                            f"Rate {movie.title} (1-5)",
                            1,
                            5,
                            key=f"rating_search_{movie.id}",
                        )
                        review = st.text_area(
                            f"Write a review for {movie.title}",
                            key=f"review_search_{movie.id}",
                        )
                        if st.button(
                            "Submit Rating & Review",
                            key=f"submit_rating_search_{movie.id}",
                        ):
                            if st.session_state.current_user:
                                save_user_activity(
                                    st.session_state.current_user,
                                    "rated",
                                    movie.title,
                                    movie.id,
                                    rating,
                                )
                                file_exists = os.path.exists("user_reviews.csv")
                                with open(
                                    "user_reviews.csv",
                                    "a",
                                    newline="",
                                    encoding="utf-8",
                                ) as f:
                                    writer = csv.writer(f)
                                    if not file_exists:
                                        writer.writerow(
                                            [
                                                "user",
                                                "movie_id",
                                                "title",
                                                "rating",
                                                "review",
                                            ]
                                        )
                                    writer.writerow(
                                        [
                                            st.session_state.current_user,
                                            movie.id,
                                            movie.title,
                                            rating,
                                            review,
                                        ]
                                    )
                                st.success(
                                    f"Rated {movie.title} with {rating} stars and review submitted!"
                                )
                                st.session_state[f"show_rating_{movie.id}"] = False
                            else:
                                st.warning("Please sign in to rate movies.")

            try:
                first_title = filtered_movies.head(1)["title"].iloc[0]
                names, posters = recommend_content_based(
                    first_title, movies, similarity
                )
                if names:
                    st.session_state.show_recommendations = True
                    st.session_state.recommended_names = names
                    st.session_state.recommended_posters = posters
                    st.session_state.recommendation_type = "search"
            except Exception:
                pass
    if st.session_state.show_recommendations:
        recommended_names = st.session_state.recommended_names
        recommended_posters = st.session_state.recommended_posters
        recommendation_type = st.session_state.recommendation_type
        st.subheader(f"{recommendation_type.capitalize()}-Based Recommendations")
        cols = st.columns(3)
        for idx, (name, poster) in enumerate(zip(recommended_names, recommended_posters)):
            with cols[idx % 3]:
                movie_id = (
                    movies[movies["title"] == name]["id"].iloc[0]
                    if not movies.empty and name in movies["title"].values
                    else None
                )
                trailer_url = fetch_trailer(movie_id) if movie_id else None
                rating = (
                    movies[movies["title"] == name]["vote_average"].iloc[0]
                    if not movies.empty
                    and name in movies["title"].values
                    and "vote_average" in movies
                    and pd.notna(movies[movies["title"] == name]["vote_average"].iloc[0])
                    else fetch_movie_details(movie_id)["rating"]
                    if movie_id
                    else 0.0
                )
                description = (
                    movies[movies["title"] == name]["overview"].iloc[0]
                    if not movies.empty
                    and name in movies["title"].values
                    and "overview" in movies
                    and pd.notna(movies[movies["title"] == name]["overview"].iloc[0])
                    else fetch_movie_details(movie_id)["description"]
                    if movie_id
                    else "No description available"
                )
                st.markdown(
                    f"""
                    <div class="movie-card">
                        <img src="{poster}" style="width: 100%; border-radius: 10px;">
                        <h3>{name}</h3>
                        <p>⭐ {rating:.1f}</p>
                        <p>{description[:100]}...</p>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Watch Now", key=f"watch_rec_{idx}_{movie_id}"):
                        if st.session_state.current_user:
                            if movie_id:
                                save_user_activity(
                                    st.session_state.current_user,
                                    "watched",
                                    name,
                                    movie_id,
                                )
                                st.session_state[f"rating_movie_{movie_id}"] = name
                                st.session_state[f"show_rating_{movie_id}"] = True
                                st.session_state[f"rating_movie_id_{movie_id}"] = (
                                    movie_id
                                )
                            else:
                                st.error("Cannot watch this movie: Movie ID not found.")
                        else:
                            st.warning("Please sign in to watch movies.")
                with col2:
                    if st.button(
                        "Add to Watchlist", key=f"watchlist_rec_{idx}_{movie_id}"
                    ):
                        if st.session_state.current_user:
                            if movie_id and not any(
                                item["title"] == name
                                for item in st.session_state.watchlist
                            ):
                                st.session_state.watchlist.append(
                                    {"title": name, "movie_id": movie_id}
                                )
                                save_watchlist_to_csv(
                                    st.session_state.current_user, name, movie_id
                                )
                                save_user_activity(
                                    st.session_state.current_user,
                                    "added_to_watchlist",
                                    name,
                                    movie_id,
                                )
                                st.success(f"Added {name} to watchlist!")
                            elif not movie_id:
                                st.error(
                                    "Cannot add to watchlist: Movie ID not found."
                                )
                        else:
                            st.warning(
                                "Please sign in to add movies to your watchlist."
                            )
                with col3:
                    if trailer_url:
                        if st.button("Watch Trailer", key=f"trailer_rec_{idx}_{movie_id}"):
                            st.markdown(
                                f'<a href="{trailer_url}" target="_blank">Watch Trailer</a>',
                                unsafe_allow_html=True,
                            )
                if st.session_state.get(f"show_rating_{movie_id}", False):
                    rating = st.slider(
                        f"Rate {name} (1-5)", 1, 5, key=f"rating_rec_{movie_id}"
                    )
                    review = st.text_area(
                        f"Write a review for {name}", key=f"review_rec_{movie_id}"
                    )
                    if st.button(
                        "Submit Rating & Review", key=f"submit_rating_rec_{movie_id}"
                    ):
                        if st.session_state.current_user:
                            if movie_id:
                                save_user_activity(
                                    st.session_state.current_user,
                                    "rated",
                                    name,
                                    movie_id,
                                    rating,
                                )
                                file_exists = os.path.exists("user_reviews.csv")
                                with open(
                                    "user_reviews.csv",
                                    "a",
                                    newline="",
                                    encoding="utf-8",
                                ) as f:
                                    writer = csv.writer(f)
                                    if not file_exists:
                                        writer.writerow(
                                            [
                                                "user",
                                                "movie_id",
                                                "title",
                                                "rating",
                                                "review",
                                            ]
                                        )
                                    writer.writerow(
                                        [
                                            st.session_state.current_user,
                                            movie_id,
                                            name,
                                            rating,
                                            review,
                                        ]
                                    )
                                st.success(
                                    f"Rated {name} with {rating} stars and review submitted!"
                                )
                                st.session_state[f"show_rating_{movie_id}"] = False
                            else:
                                st.error(
                                    "Cannot rate this movie: Movie ID not found."
                                )
                        else:
                            st.warning("Please sign in to rate movies.")
    else:
        if (
            not movies.empty
            and not st.session_state.selected_genre
            and not search_query
        ):
            cols = st.columns(3)
            for idx, movie in enumerate(movies.head(3).itertuples()):
                with cols[idx % 3]:
                    trailer_url = fetch_trailer(movie.id)
                    poster = fetch_poster(movie.id)
                    rating = (
                        movie.vote_average
                        if hasattr(movie, "vote_average")
                        and pd.notna(movie.vote_average)
                        else fetch_movie_details(movie.id)["rating"]
                    )
                    description = (
                        movie.overview
                        if hasattr(movie, "overview") and pd.notna(movie.overview)
                        else fetch_movie_details(movie.id)["description"]
                    )
                    st.markdown(
                        f"""
                        <div class="movie-card">
                            <img src="{poster}" style="width: 100%; border-radius: 10px;">
                            <h3>{movie.title}</h3>
                            <p>⭐ {rating:.1f}</p>
                            <p>{description[:100]}...</p>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("Watch Now", key=f"watch_{movie.id}"):
                            if st.session_state.current_user:
                                save_user_activity(
                                    st.session_state.current_user,
                                    "watched",
                                    movie.title,
                                    movie.id,
                                )
                                st.session_state[f"rating_movie_{movie.id}"] = (
                                    movie.title
                                )
                                st.session_state[f"show_rating_{movie.id}"] = True
                                st.session_state[f"rating_movie_id_{movie.id}"] = (
                                    movie.id
                                )
                            else:
                                st.warning("Please sign in to watch movies.")
                    with col2:
                        if st.button("Add to Watchlist", key=f"watchlist_{movie.id}"):
                            if st.session_state.current_user:
                                if not any(
                                    item["title"] == movie.title
                                    for item in st.session_state.watchlist
                                ):
                                    st.session_state.watchlist.append(
                                        {"title": movie.title, "movie_id": movie.id}
                                    )
                                    save_watchlist_to_csv(
                                        st.session_state.current_user,
                                        movie.title,
                                        movie.id,
                                    )
                                    save_user_activity(
                                        st.session_state.current_user,
                                        "added_to_watchlist",
                                        movie.title,
                                        movie.id,
                                    )
                                    st.success(f"Added {movie.title} to watchlist!")
                            else:
                                st.warning(
                                    "Please sign in to add movies to your watchlist."
                                )
                    with col3:
                        if trailer_url:
                            if st.button("Watch Trailer", key=f"trailer_{movie.id}"):
                                st.markdown(
                                    f'<a href="{trailer_url}" target="_blank">Watch Trailer</a>',
                                    unsafe_allow_html=True,
                                )
                    if st.session_state.get(f"show_rating_{movie.id}", False):
                        rating = st.slider(
                            f"Rate {movie.title} (1-5)",
                            1,
                            5,
                            key=f"rating_default_{movie.id}",
                        )
                        review = st.text_area(
                            f"Write a review for {movie.title}",
                            key=f"review_default_{movie.id}",
                        )
                        if st.button(
                            "Submit Rating & Review",
                            key=f"submit_rating_default_{movie.id}",
                        ):
                            if st.session_state.current_user:
                                save_user_activity(
                                    st.session_state.current_user,
                                    "rated",
                                    movie.title,
                                    movie.id,
                                    rating,
                                )
                                file_exists = os.path.exists("user_reviews.csv")
                                with open(
                                    "user_reviews.csv",
                                    "a",
                                    newline="",
                                    encoding="utf-8",
                                ) as f:
                                    writer = csv.writer(f)
                                    if not file_exists:
                                        writer.writerow(
                                            [
                                                "user",
                                                "movie_id",
                                                "title",
                                                "rating",
                                                "review",
                                            ]
                                        )
                                    writer.writerow(
                                        [
                                            st.session_state.current_user,
                                            movie.id,
                                            movie.title,
                                            rating,
                                            review,
                                        ]
                                    )
                                st.success(
                                    f"Rated {movie.title} with {rating} stars and review submitted!"
                                )
                                st.session_state[f"show_rating_{movie.id}"] = False
                            else:
                                st.warning("Please sign in to rate movies.")
