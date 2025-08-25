import streamlit as st
from components.api_calls import fetch_poster, fetch_trailer, fetch_movie_details
from components.file_handling import save_user_activity, remove_from_watchlist
from components.ui_components import create_movie_card, show_status_message
import pandas as pd
import os
import csv


def render_watchlist_page(movies, **kwargs):
    """Renders the user's watchlist page."""
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0;">
            <h1>📋 My Watchlist</h1>
            <p style="font-size: 1.2rem; color: rgba(255,255,255,0.8); margin-bottom: 2rem;">
                Movies you want to watch later
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Check if user is signed in
    if not st.session_state.current_user:
        show_status_message(
            "⚠️ Please sign in to view your watchlist.",
            "warning"
        )
        return
    
    # Load watchlist from file
    from components.file_handling import load_watchlist_from_csv
    watchlist = load_watchlist_from_csv(st.session_state.current_user)
    
    if not watchlist:
        st.markdown(
            """
            <div style="text-align: center; padding: 3rem 0;">
                <h3 style="color: #4ecdc4;">Your watchlist is empty</h3>
                <p style="color: rgba(255,255,255,0.8); margin: 1rem 0;">
                    Start adding movies to your watchlist from the Home or Discover pages!
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
    
    # Display watchlist stats
    st.markdown(
        f"""
        <div style="background: rgba(78, 205, 196, 0.1); border: 1px solid rgba(78, 205, 196, 0.3); 
                    border-radius: 15px; padding: 1.5rem; margin: 1rem 0;">
            <h3 style="color: #4ecdc4; margin: 0;">📊 Watchlist Stats</h3>
            <p style="margin: 0.5rem 0 0 0; color: rgba(255,255,255,0.8);">
                You have <strong>{len(watchlist)}</strong> movies in your watchlist
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Share watchlist feature
    with st.expander("📤 Share Your Watchlist", expanded=False):
        watchlist_titles = [item["title"] for item in watchlist]
        share_text = "My MovieMind Watchlist: " + ", ".join(watchlist_titles)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text_area(
                "Share text:",
                value=share_text,
                height=100,
                help="Copy this text to share your watchlist with friends"
            )
        with col2:
            if st.button("📋 Copy", help="Copy to clipboard"):
                st.session_state.copied = True
                st.success("✅ Copied to clipboard!")
    
    # Display movies in grid
    st.markdown("---")
    st.markdown(
        """
        <h2 style="text-align: center; margin: 2rem 0;">🎬 Your Watchlist</h2>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown('<div class="movie-grid">', unsafe_allow_html=True)
    
    for idx, item in enumerate(watchlist):
        with st.container():
            # Get movie details
            movie_title = item["title"]
            movie_id = item["movie_id"]
            
            # Create movie object for the card component
            movie = {
                "id": movie_id,
                "title": movie_title,
                "poster": fetch_poster(movie_id),
                "rating": 0.0,  # Will be fetched by the card component
                "description": "Loading..."  # Will be fetched by the card component
            }
            
            # Create the movie card
            create_movie_card(movie, show_actions=True, card_type=f"watchlist_{idx}")
            
            # Add remove from watchlist button
            col1, col2, col3 = st.columns(3)
            with col2:
                if st.button(
                    "🗑️ Remove from Watchlist",
                    key=f"remove_watchlist_{movie_id}_{idx}",
                    help=f"Remove '{movie_title}' from your watchlist"
                ):
                    if remove_from_watchlist(st.session_state.current_user, movie_id):
                        show_status_message(f"✅ Removed '{movie_title}' from watchlist", "success")
                        st.rerun()
                    else:
                        show_status_message(f"❌ Error removing '{movie_title}' from watchlist", "error")
            
            st.markdown("---")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Watchlist management options
    st.markdown("---")
    st.markdown(
        """
        <h3 style="text-align: center; margin: 2rem 0;">⚙️ Watchlist Management</h3>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Watchlist", help="Reload your watchlist from the server"):
            st.rerun()
    
    with col2:
        if st.button("📊 Export Watchlist", help="Download your watchlist as a CSV file"):
            # Create CSV data
            csv_data = pd.DataFrame(watchlist)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data.to_csv(index=False),
                file_name=f"watchlist_{st.session_state.current_user}.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("🗑️ Clear All", help="Remove all movies from your watchlist"):
            if st.button("⚠️ Confirm Clear All", key="confirm_clear"):
                # Clear watchlist file
                filename = f"watchlist_{st.session_state.current_user}.csv"
                if os.path.exists(filename):
                    os.remove(filename)
                show_status_message("✅ Watchlist cleared successfully", "success")
                st.rerun()
    
    # Recommendations based on watchlist
    if len(watchlist) > 0:
        st.markdown("---")
        st.markdown(
            """
            <h3 style="text-align: center; margin: 2rem 0;">💡 Recommendations</h3>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown(
            """
            <div style="background: rgba(255,255,255,0.05); border-radius: 15px; padding: 1.5rem; margin: 1rem 0;">
                <h4 style="color: #4ecdc4; margin-bottom: 1rem;">🎯 Based on your watchlist, you might also like:</h4>
                <ul style="color: rgba(255,255,255,0.8); margin: 0; padding-left: 1.5rem;">
                    <li>Try the <strong>Discover</strong> page for AI-powered recommendations</li>
                    <li>Use <strong>Mood-Based</strong> recommendations for personalized suggestions</li>
                    <li>Check out <strong>Popular Movies</strong> for trending content</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
