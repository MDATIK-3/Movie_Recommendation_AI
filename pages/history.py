import streamlit as st
from components.api_calls import fetch_poster, fetch_movie_details
from components.ui_components import create_movie_card, show_status_message
import pandas as pd
import os
from datetime import datetime


def render_history_page(**kwargs):
    """Renders the user's activity history page."""
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0;">
            <h1>📚 Your Movie History</h1>
            <p style="font-size: 1.2rem; color: rgba(255,255,255,0.8); margin-bottom: 2rem;">
                Track your movie watching journey and ratings
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Check if user is signed in
    if not st.session_state.current_user:
        show_status_message(
            "⚠️ Please sign in to view your activity history.",
            "warning"
        )
        return
    
    # Load user activity
    if not os.path.exists("user_activity.csv"):
        st.markdown(
            """
            <div style="text-align: center; padding: 3rem 0;">
                <h3 style="color: #4ecdc4;">No activity history yet</h3>
                <p style="color: rgba(255,255,255,0.8); margin: 1rem 0;">
                    Start watching and rating movies to build your history!
                </p>
                <div style="margin-top: 2rem;">
                    <a href="?page=home" style="text-decoration: none;">
                        <button style="background: linear-gradient(45deg, #ff6b6b, #4ecdc4); color: white; border: none; padding: 12px 24px; border-radius: 25px; cursor: pointer; font-size: 1rem;">
                            🏠 Go to Home
                        </button>
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        return
    
    try:
        activity_df = pd.read_csv("user_activity.csv")
        user_activity = activity_df[
            activity_df["user_id"] == str(st.session_state.current_user)
        ]
        user_activity = user_activity.sort_values(by="timestamp", ascending=False)
        
        if user_activity.empty:
            st.markdown(
                """
                <div style="text-align: center; padding: 3rem 0;">
                    <h3 style="color: #4ecdc4;">No activity history yet</h3>
                    <p style="color: rgba(255,255,255,0.8); margin: 1rem 0;">
                        Start watching and rating movies to build your history!
                    </p>
                    <div style="margin-top: 2rem;">
                        <a href="?page=home" style="text-decoration: none;">
                            <button style="background: linear-gradient(45deg, #ff6b6b, #4ecdc4); color: white; border: none; padding: 12px 24px; border-radius: 25px; cursor: pointer; font-size: 1rem;">
                                🏠 Go to Home
                            </button>
                        </a>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            return
        
        # Display activity stats
        total_activities = len(user_activity)
        watched_count = len(user_activity[user_activity["action"] == "watched"])
        rated_count = len(user_activity[user_activity["action"] == "rated"])
        watchlist_count = len(user_activity[user_activity["action"] == "added_to_watchlist"])
        
        st.markdown(
            f"""
            <div style="background: rgba(78, 205, 196, 0.1); border: 1px solid rgba(78, 205, 196, 0.3); 
                        border-radius: 15px; padding: 1.5rem; margin: 1rem 0;">
                <h3 style="color: #4ecdc4; margin: 0;">📊 Activity Summary</h3>
                <div style="display: flex; justify-content: space-around; margin-top: 1rem;">
                    <div style="text-align: center;">
                        <h4 style="color: #ff6b6b; margin: 0;">{total_activities}</h4>
                        <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">Total Activities</p>
                    </div>
                    <div style="text-align: center;">
                        <h4 style="color: #4ecdc4; margin: 0;">{watched_count}</h4>
                        <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">Movies Watched</p>
                    </div>
                    <div style="text-align: center;">
                        <h4 style="color: #ff6b6b; margin: 0;">{rated_count}</h4>
                        <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">Movies Rated</p>
                    </div>
                    <div style="text-align: center;">
                        <h4 style="color: #4ecdc4; margin: 0;">{watchlist_count}</h4>
                        <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">Watchlist Adds</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Filter options
        st.markdown("---")
        st.markdown(
            """
            <h3 style="text-align: center; margin: 2rem 0;">🔍 Filter Activities</h3>
            """,
            unsafe_allow_html=True
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_action = st.selectbox(
                "Filter by action:",
                ["All", "watched", "rated", "added_to_watchlist"],
                help="Filter activities by type"
            )
        
        with col2:
            sort_by = st.selectbox(
                "Sort by:",
                ["timestamp", "title", "rating"],
                help="Sort activities by different criteria"
            )
        
        with col3:
            sort_order = st.selectbox(
                "Order:",
                ["descending", "ascending"],
                help="Sort order"
            )
        
        # Apply filters
        filtered_activity = user_activity.copy()
        if filter_action != "All":
            filtered_activity = filtered_activity[filtered_activity["action"] == filter_action]
        
        # Apply sorting
        ascending = sort_order == "ascending"
        if sort_by == "rating":
            filtered_activity = filtered_activity.sort_values(by="rating", ascending=ascending, na_position='last')
        elif sort_by == "title":
            filtered_activity = filtered_activity.sort_values(by="title", ascending=ascending)
        else:  # timestamp
            filtered_activity = filtered_activity.sort_values(by="timestamp", ascending=ascending)
        
        # Display activities
        st.markdown("---")
        st.markdown(
            f"""
            <h2 style="text-align: center; margin: 2rem 0;">📝 Recent Activities ({len(filtered_activity)})</h2>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown('<div class="movie-grid">', unsafe_allow_html=True)
        
        for idx, row in filtered_activity.iterrows():
            with st.container():
                action = row["action"]
                title = row["title"]
                movie_id = row["movie_id"]
                rating = row["rating"] if pd.notna(row["rating"]) else None
                timestamp = row["timestamp"]
                
                # Format timestamp
                try:
                    dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    formatted_time = dt.strftime("%b %d, %Y at %I:%M %p")
                except:
                    formatted_time = timestamp
                
                # Create movie object for the card component
                movie = {
                    "id": movie_id,
                    "title": title,
                    "poster": fetch_poster(movie_id),
                    "rating": rating if rating else 0.0,
                    "description": f"Action: {action.title()} • {formatted_time}"
                }
                
                # Create the movie card
                create_movie_card(movie, show_actions=False, card_type=f"history_{idx}")
                
                # Show action details
                if action == "watched":
                    action_icon = "🎬"
                    action_text = f"Watched on {formatted_time}"
                elif action == "rated":
                    action_icon = "⭐"
                    action_text = f"Rated {rating}/5 on {formatted_time}"
                elif action == "added_to_watchlist":
                    action_icon = "📋"
                    action_text = f"Added to watchlist on {formatted_time}"
                else:
                    action_icon = "❓"
                    action_text = f"Unknown action on {formatted_time}"
                
                st.markdown(
                    f"""
                    <div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 1rem; margin: 0.5rem 0;">
                        <p style="color: #4ecdc4; margin: 0; font-weight: bold;">
                            {action_icon} {action_text}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.markdown("---")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Export history
        st.markdown("---")
        st.markdown(
            """
            <h3 style="text-align: center; margin: 2rem 0;">📊 Export Your History</h3>
            """,
            unsafe_allow_html=True
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Download Full History", help="Download your complete activity history as CSV"):
                st.download_button(
                    label="📄 Download CSV",
                    data=user_activity.to_csv(index=False),
                    file_name=f"movie_history_{st.session_state.current_user}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📊 View Statistics", help="View detailed statistics about your movie watching habits"):
                st.markdown("### 📈 Your Movie Statistics")
                
                # Calculate statistics
                avg_rating = user_activity[user_activity["action"] == "rated"]["rating"].mean()
                most_watched_genre = "Action"  # Placeholder
                total_watch_time = watched_count * 120  # Assume 2 hours per movie
                
                st.metric("Average Rating", f"{avg_rating:.1f}/5" if not pd.isna(avg_rating) else "N/A")
                st.metric("Total Watch Time", f"{total_watch_time} minutes")
                st.metric("Most Active Month", "January")  # Placeholder
                
    except Exception as e:
        show_status_message(f"❌ Error reading activity history: {e}", "error")
