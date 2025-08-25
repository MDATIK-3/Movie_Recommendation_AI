import streamlit as st
from components.api_calls import fetch_genres, fetch_trailer
from components.recommendations import recommend_mood_based
from components.file_handling import save_user_activity, save_watchlist_to_csv
import os
import csv


def render_mood_page(**kwargs):
    """Renders the mood-based recommendation page."""
    st.markdown("<h2>Mood-Based Recommendations</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p>Answer a few questions to get movie recommendations tailored to your mood and preferences. All fields are optional.</p>",
        unsafe_allow_html=True,
    )

    with st.form("mood_form"):
        mood = st.selectbox(
            "What’s your current mood?",
            ["", "Happy", "Sad", "Stressed", "Excited", "Relaxed", "Bored", "Angry"],
            index=0,
        )
        motivation = st.selectbox(
            "Are you looking for something motivational or uplifting?",
            ["", "Yes", "No", "Neutral"],
            index=0,
        )
        watching_with = st.selectbox(
            "Who are you watching with?",
            ["", "Alone", "Friends", "Family", "Partner", "Kids"],
            index=0,
        )
        occasion = st.selectbox(
            "Is this for a special occasion?",
            ["", "Date Night", "Casual", "Party", "Family Night", "None"],
            index=0,
        )
        time = st.selectbox(
            "How much time do you have?",
            ["", "Less than 1 hour", "1-2 hours", "2+ hours"],
            index=0,
        )
        genre = st.selectbox(
            "What genre are you in the mood for?",
            [""] + list(fetch_genres().values()),
            index=0,
        )
        tone = st.selectbox(
            "What kind of tone do you prefer?",
            [
                "",
                "Light-hearted",
                "Serious",
                "Emotional",
                "Fun",
                "Epic",
                "Thought-provoking",
            ],
            index=0,
        )
        romantic = st.selectbox(
            "Are you looking for something romantic?", ["", "Yes", "No", "Maybe"], index=0
        )
        pace = st.selectbox(
            "Do you want something fast-paced or slow-paced?",
            ["", "Fast-paced", "Slow-paced", "Balanced"],
            index=0,
        )
        release = st.selectbox(
            "Do you prefer newer releases or classics?",
            ["", "New (post-2010)", "Classics (pre-2010)", "No preference"],
            index=0,
        )
        mature = st.selectbox(
            "Are you okay with intense or mature themes?",
            ["", "Yes", "No", "Neutral"],
            index=0,
        )

        submit_button = st.form_submit_button("Get Recommendations")

        if submit_button:
            answers = {
                "mood": mood if mood else None,
                "motivation": motivation if motivation else None,
                "watching_with": watching_with if watching_with else None,
                "occasion": occasion if occasion else None,
                "time": time if time else None,
                "genre": genre if genre else None,
                "tone": tone if tone else None,
                "romantic": romantic if romantic else None,
                "pace": pace if pace else None,
                "release": release if release else None,
                "mature": mature if mature else None,
            }
            st.session_state.mood_answers = answers
            st.session_state.mood_recommendations = recommend_mood_based(
                answers, fetch_genres()
            )
            if st.session_state.mood_recommendations:
                st.success("Recommendations generated based on your mood!")
            else:
                st.warning(
                    "No movies found for your preferences. Showing popular movies instead."
                )

    if st.session_state.mood_recommendations:
        st.subheader("Movies for Your Mood")
        cols = st.columns(3)
        for idx, movie in enumerate(st.session_state.mood_recommendations):
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
                    if st.button("Watch Now", key=f"watch_mood_{movie['id']}"):
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
                        "Add to Watchlist", key=f"watchlist_mood_{movie['id']}"
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
                        if st.button("Watch Trailer", key=f"trailer_mood_{movie['id']}"):
                            st.markdown(
                                f'<a href="{trailer_url}" target="_blank">Watch Trailer</a>',
                                unsafe_allow_html=True,
                            )
                if st.session_state.get(f"show_rating_{movie['id']}", False):
                    rating = st.slider(
                        f"Rate {movie['title']} (1-5)",
                        1,
                        5,
                        key=f"rating_mood_{movie['id']}",
                    )
                    review = st.text_area(
                        f"Write a review for {movie['title']}",
                        key=f"review_mood_{movie['id']}",
                    )
                    if st.button(
                        "Submit Rating & Review",
                        key=f"submit_rating_mood_{movie['id']}",
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
            "No mood-based recommendations available. Please submit your preferences or adjust filters."
        )
