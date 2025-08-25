import streamlit as st
from components.api_calls import fetch_popular_movies
from components.ui_components import create_movie_card, create_rating_section, show_status_message, create_loading_spinner


def render_home_page(**kwargs):
    """Renders the modern home page with popular movies and recommendations."""
    
    # Header section
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0;">
            <h1>🎬 MovieMind</h1>
            <p style="font-size: 1.2rem; color: rgba(255,255,255,0.8); margin-bottom: 2rem;">
                Discover your next favorite movie with AI-powered recommendations
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Welcome message for signed-in users
    if st.session_state.current_user:
        st.markdown(
            f"""
            <div style="background: rgba(78, 205, 196, 0.1); border: 1px solid rgba(78, 205, 196, 0.3); 
                        border-radius: 10px; padding: 1rem; margin: 1rem 0;">
                <h3 style="color: #4ecdc4; margin: 0;">Welcome back, {st.session_state.current_username}! 👋</h3>
                <p style="margin: 0.5rem 0 0 0; color: rgba(255,255,255,0.8);">
                    Ready to discover your next favorite movie?
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style="background: rgba(255, 152, 0, 0.1); border: 1px solid rgba(255, 152, 0, 0.3); 
                        border-radius: 10px; padding: 1rem; margin: 1rem 0;">
                <h3 style="color: #ff9800; margin: 0;">🔐 Sign in to unlock full features!</h3>
                <p style="margin: 0.5rem 0 0 0; color: rgba(255,255,255,0.8);">
                    Get personalized recommendations, track your watchlist, and save your movie history.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Popular Movies Section
    st.markdown("---")
    st.markdown(
        """
        <h2 style="text-align: center; margin: 2rem 0;">🔥 Popular Movies</h2>
        """,
        unsafe_allow_html=True
    )
    
    # Show loading spinner while fetching movies
    with st.spinner("🎬 Loading popular movies..."):
        popular_movies = fetch_popular_movies(limit=6)
    
    if popular_movies:
        # Display popular movies in responsive grid
        st.markdown('<div class="movie-grid">', unsafe_allow_html=True)
        
        for idx, movie in enumerate(popular_movies):
            with st.container():
                create_movie_card(movie, show_actions=True, card_type=f"home_popular_{idx}")
                st.markdown("---")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show more movies button
        if st.button("🎬 Load More Movies", help="Load additional popular movies"):
            st.session_state.show_more_movies = True
            st.rerun()
        
        # Load more movies if requested
        if st.session_state.get("show_more_movies", False):
            with st.spinner("🎬 Loading more movies..."):
                more_movies = fetch_popular_movies(limit=12)
            
            if more_movies:
                st.markdown(
                    """
                    <h3 style="text-align: center; margin: 2rem 0;">📺 More Popular Movies</h3>
                    """,
                    unsafe_allow_html=True
                )
                
                st.markdown('<div class="movie-grid">', unsafe_allow_html=True)
                
                for movie in more_movies[6:]:
                    with st.container():
                        create_movie_card(movie, show_actions=True)
                        if st.session_state.current_user:
                            create_rating_section(movie)
                        st.markdown("---")
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        show_status_message(
            "❌ Unable to load popular movies. Please check your internet connection or try again later.",
            "error"
        )
    
    # Quick Actions Section
    st.markdown("---")
    st.markdown(
        """
        <h2 style="text-align: center; margin: 2rem 0;">⚡ Quick Actions</h2>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Discover Movies", help="Browse movies by genre and get recommendations"):
            st.session_state.page = "discover"
            st.rerun()
    
    with col2:
        if st.button("😊 Mood-Based Recs", help="Get movie recommendations based on your mood"):
            st.session_state.page = "mood"
            st.rerun()
    
    with col3:
        if st.button("📋 My Watchlist", help="View and manage your watchlist"):
            st.session_state.page = "watchlist"
            st.rerun()
    
    # Features Section
    st.markdown("---")
    st.markdown(
        """
        <h2 style="text-align: center; margin: 2rem 0;">✨ Features</h2>
        """,
        unsafe_allow_html=True
    )
    
    features_col1, features_col2 = st.columns(2)
    
    with features_col1:
        st.markdown(
            """
            <div style="background: rgba(255,255,255,0.05); border-radius: 15px; padding: 1.5rem; margin: 1rem 0;">
                <h4 style="color: #4ecdc4; margin-bottom: 1rem;">🤖 AI Recommendations</h4>
                <ul style="color: rgba(255,255,255,0.8); margin: 0; padding-left: 1.5rem;">
                    <li>Content-based filtering</li>
                    <li>Collaborative filtering</li>
                    <li>Hybrid recommendations</li>
                    <li>Mood-based suggestions</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown(
            """
            <div style="background: rgba(255,255,255,0.05); border-radius: 15px; padding: 1.5rem; margin: 1rem 0;">
                <h4 style="color: #ff6b6b; margin-bottom: 1rem;">📊 Personalization</h4>
                <ul style="color: rgba(255,255,255,0.8); margin: 0; padding-left: 1.5rem;">
                    <li>Track your watchlist</li>
                    <li>Rate and review movies</li>
                    <li>View your history</li>
                    <li>Personalized suggestions</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with features_col2:
        st.markdown(
            """
            <div style="background: rgba(255,255,255,0.05); border-radius: 15px; padding: 1.5rem; margin: 1rem 0;">
                <h4 style="color: #4ecdc4; margin-bottom: 1rem;">🎬 Movie Information</h4>
                <ul style="color: rgba(255,255,255,0.8); margin: 0; padding-left: 1.5rem;">
                    <li>Detailed movie info</li>
                    <li>Trailer links</li>
                    <li>Genre filtering</li>
                    <li>Rating and reviews</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown(
            """
            <div style="background: rgba(255,255,255,0.05); border-radius: 15px; padding: 1.5rem; margin: 1rem 0;">
                <h4 style="color: #ff6b6b; margin-bottom: 1rem;">📱 Responsive Design</h4>
                <ul style="color: rgba(255,255,255,0.8); margin: 0; padding-left: 1.5rem;">
                    <li>Mobile-friendly interface</li>
                    <li>Modern UI design</li>
                    <li>Fast loading times</li>
                    <li>Easy navigation</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0; color: rgba(255,255,255,0.6);">
            <p>🎬 MovieMind - Your AI-powered movie companion</p>
            <p style="font-size: 0.9rem;">Powered by TMDB API and machine learning</p>
        </div>
        """,
        unsafe_allow_html=True
    )
