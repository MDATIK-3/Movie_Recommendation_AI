import streamlit as st


def custom_css():
    st.markdown(
        """
    <style>
    body {
        background-color: #121212;
        color: white;
        margin: 0;
        padding: 0;
    }
    .stApp {
        background-color: #121212;
        color: white;
    }
    h1, h2, h3 {
        color: white;
    }
    .stButton>button {
        background-color: #4a4a4a;
        color: white;
        border-radius: 5px;
        width: 100%;
        min-width: 80px;
        font-size: 1em;
    }
    .stTextInput>div>input, .stSelectbox>div>select {
        background-color: #2a2a2a;
        color: white;
        border-radius: 5px;
        width: 100%;
        font-size: 1em;
    }
    .genre-button {
        background-color: #2a2a2a;
        color: white;
        border-radius: 15px;
        padding: 5px 15px;
        margin: 5px;
        display: inline-block;
        font-size: 1em;
    }
    .movie-card {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 10px;
        margin: 10px auto;
        width: 100%;
        max-width: 320px;
        display: block;
        vertical-align: top;
        box-sizing: border-box;
    }
    .movie-card img {
        width: 100%;
        height: auto;
        border-radius: 10px;
    }
    .watchlist-container, .history-container {
        display: flex;
        flex-wrap: wrap;
        overflow-x: auto;
        white-space: normal;
        padding: 10px 0;
    }
    .nav-bar {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
        background-color: #1a1a1a;
    }
    .nav-links button {
        background: none;
        border: none;
        color: white;
        margin: 0 15px;
        text-decoration: none;
        cursor: pointer;
        font-size: 1em;
    }
    .sign-in-btn {
        background-color: #333;
        color: white;
        padding: 5px 15px;
        border-radius: 5px;
        text-decoration: none;
        border: none;
        cursor: pointer;
        font-size: 1em;
    }
    @media (max-width: 900px) {
        .movie-card {
            max-width: 90vw;
            margin: 10px auto;
        }
        .nav-bar {
            flex-direction: column;
            align-items: flex-start;
        }
        .nav-links button {
            margin: 5px 0;
        }
    }
    @media (max-width: 600px) {
        .movie-card {
            max-width: 98vw;
            margin: 10px auto;
            font-size: 0.95em;
        }
        h1, h2, h3 {
            font-size: 1.2em;
        }
        .nav-bar {
            padding: 5px;
        }
        .stButton>button, .sign-in-btn {
            font-size: 0.95em;
            padding: 8px 10px;
        }
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def navigation_bar():
    st.markdown("<div class='nav-bar'>", unsafe_allow_html=True)
    col_logo, col_links, col_signin = st.columns([1, 4, 1])
    # No branding/logo
    with col_links:
        col_home, col_discover, col_mood, col_watchlist, col_history = st.columns(5)
        with col_home:
            if st.button("Home", key="nav_home"):
                st.session_state.page = "home"
                st.session_state.show_recommendations = False
                st.session_state.selected_genre = None
        with col_discover:
            if st.button("Discover", key="nav_discover"):
                st.session_state.page = "discover"
        with col_mood:
            if st.button("Mood-Based", key="nav_mood"):
                st.session_state.page = "mood"
        with col_watchlist:
            if st.button("Watchlist", key="nav_watchlist"):
                st.session_state.page = "watchlist"
        with col_history:
            if st.button("History", key="nav_history"):
                st.session_state.page = "history"
    with col_signin:
        if st.session_state.current_user:
            if st.button(
                f"Sign Out ({st.session_state.current_username})", key="nav_signout"
            ):
                st.session_state.current_user = None
                st.session_state.current_username = None
                st.session_state.watchlist = []
                st.session_state.mood_answers = {}
                st.session_state.mood_recommendations = []
                st.session_state.page = "home"
                st.success("Signed out successfully!")
        else:
            if st.button("Sign In", key="nav_signin"):
                st.session_state.page = "signin"
    st.markdown("</div>", unsafe_allow_html=True)
