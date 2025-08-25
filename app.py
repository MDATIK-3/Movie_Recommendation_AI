import streamlit as st
from components.ui_components import custom_css, navigation_bar
from components.file_handling import load_pickles, load_watchlist_from_csv
from components.user_management import load_users
from pages import home, discover, mood, watchlist, history, signin

movies, similarity, svd_model = load_pickles()
custom_css()

if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_genre" not in st.session_state:
    st.session_state.selected_genre = None
if "show_recommendations" not in st.session_state:
    st.session_state.show_recommendations = False
if "recommendation_type" not in st.session_state:
    st.session_state.recommendation_type = None
if "genre_movies" not in st.session_state:
    st.session_state.genre_movies = []
if "users" not in st.session_state:
    st.session_state.users = load_users()
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "current_username" not in st.session_state:
    st.session_state.current_username = None
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []
if "mood_answers" not in st.session_state:
    st.session_state.mood_answers = {}
if "mood_recommendations" not in st.session_state:
    st.session_state.mood_recommendations = []

if st.session_state.current_user and not st.session_state.watchlist:
    st.session_state.watchlist = load_watchlist_from_csv(st.session_state.current_user)

navigation_bar()

PAGES = {
    "home": home.render_home_page,
    "discover": discover.render_discover_page,
    "mood": mood.render_mood_page,
    "watchlist": watchlist.render_watchlist_page,
    "history": history.render_history_page,
    "signin": signin.render_signin_page,
}

page_function = PAGES.get(st.session_state.page)

if page_function:
    page_function(movies=movies, similarity=similarity, svd_model=svd_model)
else:
    home.render_home_page(movies=movies, similarity=similarity, svd_model=svd_model)
