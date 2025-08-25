import streamlit as st
from components.api_calls import fetch_poster, fetch_movie_details
import pandas as pd
import os


def render_history_page(**kwargs):
    """Renders the user's activity history page."""
    st.markdown("<h2>Your Activity History</h2>", unsafe_allow_html=True)
    if st.session_state.current_user:
        if os.path.exists("user_activity.csv"):
            try:
                activity_df = pd.read_csv("user_activity.csv")
                user_activity = activity_df[
                    activity_df["user_id"] == st.session_state.current_user
                ]
                user_activity = user_activity.sort_values(
                    by="timestamp", ascending=False
                )
                if user_activity.empty:
                    st.info("No activity history found.")
                else:
                    st.markdown("<div class='history-container'>", unsafe_allow_html=True)
                    cols = st.columns(3)
                    for idx, row in user_activity.iterrows():
                        with cols[idx % 3]:
                            action = row["action"]
                            title = row["title"]
                            movie_id = row["movie_id"]
                            rating = row["rating"] if pd.notna(row["rating"]) else None
                            timestamp = row["timestamp"]
                            poster = (
                                fetch_poster(movie_id)
                                if movie_id
                                else "https://via.placeholder.com/200x300?text=No+Poster"
                            )
                            description = fetch_movie_details(movie_id)["description"]
                            if action == "watched":
                                action_text = f"Watched on {timestamp}"
                            elif action == "rated":
                                action_text = f"Rated {rating}/5 on {timestamp}"
                            elif action == "added_to_watchlist":
                                action_text = f"Added to watchlist on {timestamp}"
                            else:
                                action_text = f"Unknown action on {timestamp}"
                            st.markdown(
                                f"""
                                <div class="movie-card">
                                    <img src="{poster}" style="width: 100%; border-radius: 10px;">
                                    <h3>{title}</h3>
                                    <p>{action_text}</p>
                                    <p>{description[:100]}...</p>
                                </div>
                            """,
                                unsafe_allow_html=True,
                            )
                    st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"Error reading activity history: {e}")
        else:
            st.info("No activity history yet.")
    else:
        st.warning("Please sign in to view your activity history.")
