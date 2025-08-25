import streamlit as st
from components.api_calls import fetch_poster, fetch_trailer, fetch_movie_details
from components.file_handling import save_user_activity
import pandas as pd
import os
import csv


def render_watchlist_page(movies, **kwargs):
    """Renders the user's watchlist page."""
    st.markdown("<h2>Watchlist</h2>", unsafe_allow_html=True)
    if st.session_state.current_user:
        try:
            reviews_df = pd.read_csv("user_reviews.csv", header=0)
            user_reviews = reviews_df[
                reviews_df["user"] == st.session_state.current_user
            ]
            top_rated_ids = (
                user_reviews.sort_values("rating", ascending=False)
                .head(5)["movie_id"]
                .tolist()
            )
            favorite_genres = set()
            for mid in top_rated_ids:
                details = fetch_movie_details(mid)
                genre = details.get("genre")
                if genre:
                    favorite_genres.add(genre)
            notified_file = f"notified_{st.session_state.current_user}.txt"
            notified_ids = set()
            if os.path.exists(notified_file):
                with open(notified_file) as f:
                    notified_ids = set(f.read().splitlines())
            new_movies = movies[
                movies["genre"].isin(favorite_genres)
                & ~movies["id"].astype(str).isin(notified_ids)
            ]
            if not new_movies.empty:
                st.info(
                    f"New movies added in your favorite genres: {', '.join(new_movies['title'].head(3))}"
                )
                with open(notified_file, "a") as f:
                    for mid in new_movies["id"].astype(str).head(3):
                        f.write(mid + "\n")
        except Exception:
            pass
        if st.session_state.watchlist:
            st.markdown("<div class='watchlist-container'>", unsafe_allow_html=True)
            watchlist_titles = [item["title"] for item in st.session_state.watchlist]
            share_text = "My Watchlist: " + ", ".join(watchlist_titles)
            st.text_area("Share your watchlist:", value=share_text, height=50)
            st.button(
                "Copy to Clipboard", on_click=lambda: st.session_state.update({"copied": True})
            )
            if st.session_state.get("copied"):
                st.success("Watchlist copied! You can share it with friends.")
            cols = st.columns(3)
            for idx, item in enumerate(st.session_state.watchlist):
                with cols[idx % 3]:
                    movie = item["title"]
                    movie_id = item["movie_id"]
                    poster = (
                        fetch_poster(movie_id)
                        if movie_id
                        else "https://via.placeholder.com/200x300?text=No+Poster"
                    )
                    trailer_url = fetch_trailer(movie_id) if movie_id else None
                    rating = (
                        movies[movies["id"] == movie_id]["vote_average"].iloc[0]
                        if not movies.empty
                        and movie_id in movies["id"].values
                        and "vote_average" in movies
                        and pd.notna(
                            movies[movies["id"] == movie_id]["vote_average"].iloc[0]
                        )
                        else fetch_movie_details(movie_id)["rating"]
                    )
                    description = (
                        movies[movies["id"] == movie_id]["overview"].iloc[0]
                        if not movies.empty
                        and movie_id in movies["id"].values
                        and "overview" in movies
                        and pd.notna(
                            movies[movies["id"] == movie_id]["overview"].iloc[0]
                        )
                        else fetch_movie_details(movie_id)["description"]
                    )
                    if st.button(
                        f"Details: {movie}", key=f"details_wl_{movie_id}_{idx}"
                    ):
                        st.session_state.selected_movie_details = movie_id
                    st.markdown(
                        f"""
                        <div class="movie-card">
                            <img src="{poster}" style="width: 100%; border-radius: 10px;">
                            <h3>{movie}</h3>
                            <p>⭐ {rating:.1f}</p>
                            <p>{description[:100]}...</p>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("Watch Now", key=f"watch_wl_{movie_id}_{idx}"):
                            if st.session_state.current_user:
                                save_user_activity(
                                    st.session_state.current_user,
                                    "watched",
                                    movie,
                                    movie_id,
                                )
                                st.session_state[f"rating_movie_{movie_id}"] = movie
                                st.session_state[f"show_rating_{movie_id}"] = True
                                st.session_state[f"rating_movie_id_{movie_id}"] = (
                                    movie_id
                                )
                            else:
                                st.warning("Please sign in to watch movies.")
                    with col2:
                        if st.button("Remove", key=f"remove_wl_{movie_id}_{idx}"):
                            st.session_state.watchlist = [
                                item
                                for item in st.session_state.watchlist
                                if item["movie_id"] != movie_id
                            ]
                            filename = f"watchlist_{st.session_state.current_user}.csv"
                            if st.session_state.watchlist:
                                pd.DataFrame(st.session_state.watchlist).to_csv(
                                    filename, index=False, quoting=csv.QUOTE_NONNUMERIC
                                )
                            else:
                                if os.path.exists(filename):
                                    os.remove(filename)
                            st.success(f"Removed {movie} from watchlist!")
                    with col3:
                        if trailer_url:
                            if st.button("Trailer", key=f"trailer_wl_{movie_id}_{idx}"):
                                st.markdown(
                                    f'<a href="{trailer_url}" target="_blank">Watch Trailer</a>',
                                    unsafe_allow_html=True,
                                )
                    if st.session_state.get(f"show_rating_{movie_id}", False):
                        rating = st.slider(
                            f"Rate {movie} (1-5)",
                            1,
                            5,
                            key=f"rating_wl_{movie_id}_{idx}",
                        )
                        review = st.text_area(
                            f"Write a review for {movie}",
                            key=f"review_wl_{movie_id}_{idx}",
                        )
                        if st.button(
                            "Submit Rating & Review",
                            key=f"submit_rating_wl_{movie_id}_{idx}",
                        ):
                            save_user_activity(
                                st.session_state.current_user,
                                "rated",
                                movie,
                                movie_id,
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
                                        movie_id,
                                        movie,
                                        rating,
                                        review,
                                    ]
                                )
                            st.success(
                                f"Rated {movie} with {rating} stars and review submitted!"
                            )
                            st.session_state[f"show_rating_{movie_id}"] = False
            st.markdown("</div>", unsafe_allow_html=True)
            if st.session_state.get("selected_movie_details"):
                movie_id = st.session_state.selected_movie_details
                details = fetch_movie_details(movie_id)
                st.markdown(f"## Movie Details")
                st.image(fetch_poster(movie_id), width=200)
                st.markdown(f"**Title:** {details.get('title', '')}")
                st.markdown(f"**Release Date:** {details.get('release_date', 'N/A')}")
                st.markdown(f"**Director:** {details.get('director', 'N/A')}")
                st.markdown(f"**Cast:** {details.get('cast', 'N/A')}")
                st.markdown(f"**Description:** {details.get('description', '')}")
                st.markdown(f"**Rating:** {details.get('rating', 'N/A')}")
                trailer_url = fetch_trailer(movie_id)
                if trailer_url:
                    st.markdown(
                        f'<a href="{trailer_url}" target="_blank">Watch Trailer</a>',
                        unsafe_allow_html=True,
                    )
                try:
                    reviews_df = pd.read_csv("user_reviews.csv", header=0)
                    movie_reviews = reviews_df[reviews_df["movie_id"] == movie_id]
                    if not movie_reviews.empty:
                        avg_rating = movie_reviews["rating"].astype(float).mean()
                        st.markdown(f"**Average Rating:** {avg_rating:.1f} ⭐")
                        st.markdown("**Recent Reviews:**")
                        for _, row in movie_reviews.tail(5).iterrows():
                            st.markdown(
                                f"- *{row['user']}*: {row['review']} ({row['rating']}⭐)"
                            )
                except Exception:
                    pass
                if st.button("Back to Watchlist", key="back_to_watchlist"):
                    st.session_state.selected_movie_details = None
        else:
            st.info("Your watchlist is empty.")
    else:
        st.warning("Please sign in to view your watchlist.")
