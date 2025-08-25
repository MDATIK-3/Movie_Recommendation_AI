import streamlit as st
from components.api_calls import fetch_popular_movies, fetch_trailer
from components.file_handling import save_user_activity, save_watchlist_to_csv
import os
import csv


def render_home_page(**kwargs):
    """Renders the home page of the application."""
    st.markdown(
        "<h1 style='text-align: center;'>Discover Movies You'll Love</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; color: #b0b0b0;'>Let our AI find your perfect next watch based on your unique taste</p>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<h2 style='text-align: center;'>Popular Movies</h2>", unsafe_allow_html=True
    )
    popular_movies = fetch_popular_movies()
    if popular_movies:
        cols = st.columns(3)
        for idx, movie in enumerate(popular_movies[:3]):
            with cols[idx % 3]:
                trailer_url = fetch_trailer(movie["id"])
                st.markdown(
                    f"""
                    <div class="movie-card">
                        <img src="{movie['poster']}" style="width: 100%; border-radius: 10px;">
                        <h3>{movie['title']}</h3>
                        <p>⭐ {movie['rating']:.1f}</p>
                        <p>{movie['description'][:100]}...</p>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Watch Now", key=f"watch_pop_{movie['id']}"):
                        if st.session_state.current_user:
                            save_user_activity(
                                st.session_state.current_user,
                                "watched",
                                movie["title"],
                                movie["id"],
                            )
                            st.session_state[f"rating_movie_{movie['id']}"] = movie[
                                "title"
                            ]
                            st.session_state[f"show_rating_{movie['id']}"] = True
                            st.session_state[f"rating_movie_id_{movie['id']}"] = movie[
                                "id"
                            ]
                        else:
                            st.warning("Please sign in to watch movies.")
                with col2:
                    if st.button(
                        "Add to Watchlist", key=f"watchlist_pop_{movie['id']}"
                    ):
                        if st.session_state.current_user:
                            if not any(
                                item["title"] == movie["title"]
                                for item in st.session_state.watchlist
                            ):
                                st.session_state.watchlist.append(
                                    {"title": movie["title"], "movie_id": movie["id"]}
                                )
                                save_watchlist_to_csv(
                                    st.session_state.current_user,
                                    movie["title"],
                                    movie["id"],
                                )
                                save_user_activity(
                                    st.session_state.current_user,
                                    "added_to_watchlist",
                                    movie["title"],
                                    movie["id"],
                                )
                                st.success(f"Added {movie['title']} to watchlist!")
                        else:
                            st.warning(
                                "Please sign in to add movies to your watchlist."
                            )
                with col3:
                    if trailer_url:
                        if st.button("Watch Trailer", key=f"trailer_pop_{movie['id']}"):
                            st.markdown(
                                f'<a href="{trailer_url}" target="_blank">Watch Trailer</a>',
                                unsafe_allow_html=True,
                            )
                if st.session_state.get(f"show_rating_{movie['id']}", False):
                    rating = st.slider(
                        f"Rate {movie['title']} (1-5)",
                        1,
                        5,
                        key=f"rating_pop_{movie['id']}",
                    )
                    review = st.text_area(
                        f"Write a review for {movie['title']}",
                        key=f"review_pop_{movie['id']}",
                    )
                    if st.button(
                        "Submit Rating & Review", key=f"submit_rating_pop_{movie['id']}"
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
    else:
        st.info(
            "Could not fetch popular movies. Please check your API key or internet connection."
        )
