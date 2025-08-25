
import streamlit as st


def custom_css():
    """Apply modern, responsive CSS styling."""
    st.markdown(
        """
    <style>
    /* Global Styles */
    * {
        box-sizing: border-box;
    }
    
    body {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin: 0;
        padding: 0;
        min-height: 100vh;
    }
    
    .stApp {
        background: transparent;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    h1 {
        font-size: 2.5rem;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
    }
    
    h2 {
        font-size: 2rem;
        color: #4ecdc4;
        border-bottom: 2px solid #4ecdc4;
        padding-bottom: 0.5rem;
    }
    
    h3 {
        font-size: 1.5rem;
        color: #ff6b6b;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 24px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        width: 100%;
        min-width: 120px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        background: linear-gradient(45deg, #4ecdc4, #ff6b6b);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Secondary Button Style */
    .secondary-btn {
        background: linear-gradient(45deg, #667eea, #764ba2) !important;
    }
    
    .secondary-btn:hover {
        background: linear-gradient(45deg, #764ba2, #667eea) !important;
    }
    
    /* Form Elements */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 12px 16px;
        font-size: 1rem;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #4ecdc4;
        box-shadow: 0 0 20px rgba(78, 205, 196, 0.3);
        outline: none;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.6);
    }
    
    /* Movie Cards */
    .movie-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 20px;
        margin: 15px 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        border-color: rgba(78, 205, 196, 0.3);
    }
    
    .movie-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
    }
    
    .movie-card img {
        width: 100%;
        height: auto;
        max-height: 400px;
        object-fit: contain;
        border-radius: 15px;
        margin-bottom: 15px;
        transition: transform 0.3s ease;
        background: rgba(0, 0, 0, 0.1);
    }
    
    .movie-card:hover img {
        transform: scale(1.02);
    }
    
    .movie-card h3 {
        color: #ffffff;
        font-size: 1.3rem;
        margin: 10px 0;
        font-weight: 600;
    }
    
    .movie-card p {
        color: rgba(255, 255, 255, 0.8);
        line-height: 1.6;
        margin: 8px 0;
    }
    
    .movie-rating {
        color: #ffd700;
        font-size: 1.1rem;
        font-weight: bold;
    }
    
    /* Navigation Bar */
    .nav-container {
        background: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        position: sticky;
        top: 0;
        z-index: 1000;
        padding: 15px 0;
    }
    
    .nav-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
    }
    
    .nav-brand {
        font-size: 1.8rem;
        font-weight: bold;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .nav-links {
        display: flex;
        gap: 20px;
        align-items: center;
    }
    
    .nav-link {
        background: transparent;
        border: none;
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
        text-decoration: none;
        position: relative;
    }
    
    .nav-link:hover {
        background: rgba(255, 255, 255, 0.1);
        color: #4ecdc4;
    }
    
    .nav-link.active {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        color: white;
    }
    
    .user-section {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .user-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
    }
    
    /* Grid Layouts */
    .movie-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
        padding: 20px 0;
    }
    
    .movie-grid-2 {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 15px;
        padding: 15px 0;
    }
    
    .movie-grid-3 {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 10px;
        padding: 10px 0;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        h1 {
            font-size: 2rem;
        }
        
        h2 {
            font-size: 1.5rem;
        }
        
        .nav-content {
            flex-direction: column;
            gap: 15px;
        }
        
        .nav-links {
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
        }
        
        .nav-link {
            padding: 8px 16px;
            font-size: 0.9rem;
        }
        
        .movie-grid {
            grid-template-columns: 1fr;
            gap: 15px;
        }
        
        .movie-card {
            margin: 10px 0;
            padding: 15px;
        }
        
        .movie-card img {
            height: auto;
            max-height: 300px;
            object-fit: contain;
        }
        
        .stButton > button {
            padding: 10px 20px;
            font-size: 0.9rem;
        }
    }
    
    @media (max-width: 480px) {
        h1 {
            font-size: 1.8rem;
        }
        
        .nav-brand {
            font-size: 1.5rem;
        }
        
        .nav-links {
            flex-direction: column;
            width: 100%;
        }
        
        .nav-link {
            width: 100%;
            text-align: center;
        }
        
        .movie-card img {
            height: auto;
            max-height: 250px;
            object-fit: contain;
        }
        
        .stButton > button {
            padding: 8px 16px;
            font-size: 0.8rem;
        }
    }
    
    /* Loading and Status Messages */
    .status-message {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        font-weight: 500;
    }
    
    .success-message {
        background: rgba(76, 175, 80, 0.2);
        border: 1px solid rgba(76, 175, 80, 0.5);
        color: #4caf50;
    }
    
    .error-message {
        background: rgba(244, 67, 54, 0.2);
        border: 1px solid rgba(244, 67, 54, 0.5);
        color: #f44336;
    }
    
    .warning-message {
        background: rgba(255, 152, 0, 0.2);
        border: 1px solid rgba(255, 152, 0, 0.5);
        color: #ff9800;
    }
    
    .info-message {
        background: rgba(33, 150, 243, 0.2);
        border: 1px solid rgba(33, 150, 243, 0.5);
        color: #2196f3;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(45deg, #4ecdc4, #ff6b6b);
    }
    
    /* Trailer Modal Styles */
    .trailer-modal {
        background: rgba(15, 15, 35, 0.95);
        border: 2px solid rgba(78, 205, 196, 0.3);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        backdrop-filter: blur(20px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
    }
    
    .trailer-container {
        width: 100%;
        max-width: 800px;
        margin: 0 auto;
    }
    
    .trailer-iframe {
        width: 100%;
        height: 450px;
        border: none;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    
    .trailer-title {
        color: #4ecdc4;
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        border-bottom: 1px solid rgba(78, 205, 196, 0.3);
        padding-bottom: 15px;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Hide modal when not active */
    .modal-hidden {
        display: none !important;
    }
    
    /* Rating Stars */
    .rating-stars {
        color: #ffd700;
        font-size: 1.2rem;
    }
    
    /* Genre Tags */
    .genre-tag {
        display: inline-block;
        background: rgba(78, 205, 196, 0.2);
        color: #4ecdc4;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 2px;
        border: 1px solid rgba(78, 205, 196, 0.3);
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def navigation_bar():
    """Create a modern, responsive navigation bar."""
    st.markdown(
        """
        <div class="nav-container">
            <div class="nav-content">
                <div class="nav-brand">🎬 MovieMind</div>
                <div class="nav-links">
        """,
        unsafe_allow_html=True,
    )
    
    # Navigation buttons with unique keys
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        if st.button("Home", key="nav_home_main", help="Go to home page"):
            st.session_state.page = "home"
            st.session_state.show_recommendations = False
            st.session_state.selected_genre = None
            st.rerun()
    
    with col2:
        if st.button("Discover", key="nav_discover_main", help="Discover new movies"):
            st.session_state.page = "discover"
            st.rerun()
    
    with col3:
        if st.button("Mood", key="nav_mood_main", help="Get mood-based recommendations"):
            st.session_state.page = "mood"
            st.rerun()
    
    with col4:
        if st.button("Watchlist", key="nav_watchlist_main", help="View your watchlist"):
            st.session_state.page = "watchlist"
            st.rerun()
    
    with col5:
        if st.button("History", key="nav_history_main", help="View your history"):
            st.session_state.page = "history"
            st.rerun()
    
    with col6:
        if st.session_state.current_user:
            if st.button(f"👤 {st.session_state.current_username}", key="nav_signout_main", help="Sign out"):
                st.session_state.current_user = None
                st.session_state.current_username = None
                st.session_state.authenticated = False
                st.session_state.watchlist = []
                st.session_state.mood_answers = {}
                st.session_state.mood_recommendations = []
                
                # Clear authentication file
                from components.auth_manager import clear_auth_state
                clear_auth_state()
                
                st.session_state.page = "home"
                st.success("✅ Signed out successfully!")
                st.rerun()
        else:
            if st.button("Sign In", key="nav_signin_main", help="Sign in to your account"):
                st.session_state.page = "signin"
                st.rerun()
    
    st.markdown("</div></div></div>", unsafe_allow_html=True)


def create_movie_card(movie, show_actions=True, card_type="default"):
    """Create a responsive movie card with actions."""
    title = movie.get('title', 'Unknown Title')
    poster_url = movie.get('poster', 'https://via.placeholder.com/300x450?text=No+Poster')
    rating = movie.get('rating', 0.0)
    description = movie.get('description', 'No description available')
    movie_id = movie.get('id', 0)
    
    # Generate stable unique key for this card instance
    import hashlib
    key_string = f"{card_type}_{movie_id}_{title}"
    unique_key = hashlib.md5(key_string.encode()).hexdigest()[:8]
    
    # Truncate description for better display
    if len(description) > 150:
        description = description[:150] + "..."
    
    card_html = f"""
    <div class="movie-card fade-in">
        <img src="{poster_url}" alt="{title}" onerror="this.src='https://via.placeholder.com/300x450?text=No+Poster'">
        <h3>{title}</h3>
        <p class="movie-rating">⭐ {rating:.1f}/10</p>
        <p>{description}</p>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    if show_actions:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎬 Watch", key=f"watch_{unique_key}", help="Mark as watched"):
                if st.session_state.current_user:
                    try:
                        from components.file_handling import save_user_activity
                        if save_user_activity(
                            st.session_state.current_user,
                            "watched",
                            title,
                            movie_id,
                        ):
                            st.success(f"✅ Added '{title}' to your history!")
                        else:
                            st.error(f"❌ Error adding '{title}' to history.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please sign in to track your watched movies.")
        
        with col2:
            if st.button("📋 Add", key=f"watchlist_{unique_key}", help="Add to watchlist"):
                if st.session_state.current_user:
                    try:
                        from components.file_handling import save_watchlist_to_csv
                        if save_watchlist_to_csv(st.session_state.current_user, title, movie_id):
                            st.success(f"✅ Added '{title}' to watchlist!")
                        else:
                            st.error(f"❌ Error adding '{title}' to watchlist.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please sign in to add movies to your watchlist.")
        
        with col3:
            try:
                from components.api_calls import fetch_trailer
                trailer_url = fetch_trailer(movie_id)
                if trailer_url:
                    # Create a styled link button that opens in new tab
                    st.markdown(
                        f"""
                        <div style="text-align: center;">
                            <a href="{trailer_url}" target="_blank" rel="noopener noreferrer" style="text-decoration: none;">
                                <button style="background: linear-gradient(45deg, #ff6b6b, #4ecdc4); 
                                               color: white; border: none; border-radius: 25px; 
                                               padding: 12px 24px; font-size: 1rem; font-weight: 600; 
                                               cursor: pointer; transition: all 0.3s ease; 
                                               box-shadow: 0 4px 15px rgba(0,0,0,0.2); width: 100%;">
                                    🎥 Watch Trailer
                                </button>
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.button("🎥 Trailer", key=f"trailer_{unique_key}", help="No trailer available", disabled=True)
            except Exception as e:
                st.button("🎥 Trailer", key=f"trailer_{unique_key}", help="Error loading trailer", disabled=True)


def create_rating_section(movie):
    """Create a rating and review section for a movie."""
    movie_id = movie.get('id', 0)
    title = movie.get('title', 'Unknown Title')
    
    # Generate stable unique key for this rating section
    import hashlib
    key_string = f"rating_{movie_id}_{title}"
    unique_key = hashlib.md5(key_string.encode()).hexdigest()[:8]
    
    if st.session_state.get(f"show_rating_{movie_id}", False):
        st.markdown("---")
        st.subheader(f"Rate '{title}'")
        
        col1, col2 = st.columns(2)
        
        with col1:
            rating = st.slider(
                "Rating (1-5 stars)",
                1, 5, 3,
                key=f"rating_{unique_key}",
                help="Rate this movie from 1 to 5 stars"
            )
        
        with col2:
            st.markdown(f"**Your rating:** {'⭐' * rating}")
        
        review = st.text_area(
            "Write your review (optional)",
            key=f"review_{unique_key}",
            help="Share your thoughts about this movie",
            max_chars=500
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Submit Rating", key=f"submit_rating_{unique_key}"):
                if st.session_state.current_user:
                    from components.file_handling import save_user_activity
                    import os
                    import csv
                    
                    save_user_activity(
                        st.session_state.current_user,
                        "rated",
                        title,
                        movie_id,
                        rating,
                    )
                    
                    # Save review to CSV
                    file_exists = os.path.exists("user_reviews.csv")
                    with open("user_reviews.csv", "a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        if not file_exists:
                            writer.writerow(["user", "movie_id", "title", "rating", "review"])
                        writer.writerow([
                            st.session_state.current_user,
                            movie_id,
                            title,
                            rating,
                            review
                        ])
                    
                    st.success(f"✅ Rated '{title}' with {rating} stars!")
                    st.session_state[f"show_rating_{movie_id}"] = False
                else:
                    st.warning("⚠️ Please sign in to rate movies.")
        
        with col2:
            if st.button("Cancel", key=f"cancel_rating_{unique_key}"):
                st.session_state[f"show_rating_{movie_id}"] = False
                st.rerun()


def show_status_message(message, message_type="info"):
    """Display styled status messages."""
    css_class = {
        "success": "success-message",
        "error": "error-message", 
        "warning": "warning-message",
        "info": "info-message"
    }.get(message_type, "info-message")
    
    st.markdown(
        f'<div class="status-message {css_class}">{message}</div>',
        unsafe_allow_html=True
    )


def create_loading_spinner():
    """Create a custom loading spinner."""
    st.markdown(
        """
        <div style="display: flex; justify-content: center; align-items: center; padding: 20px;">
            <div style="width: 40px; height: 40px; border: 4px solid rgba(255,255,255,0.1); border-top: 4px solid #4ecdc4; border-radius: 50%; animation: spin 1s linear infinite;"></div>
        </div>
        <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>
        """,
        unsafe_allow_html=True
    )
