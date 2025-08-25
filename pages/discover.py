import streamlit as st
from components.api_calls import (
    fetch_genres,
    fetch_movies_by_genre,
    fetch_trailer,
    fetch_movie_details,
    fetch_poster,
    fetch_popular_movies,
    search_movies,
)
from components.recommendations import (
    recommend_content_based,
    recommend_collaborative,
    recommend_hybrid,
)
from components.file_handling import save_user_activity, save_watchlist_to_csv
from components.ui_components import create_movie_card, show_status_message, create_loading_spinner
import pandas as pd
import os
import csv


def render_discover_page(movies, similarity, svd_model, **kwargs):
    """Renders the discover page for finding and getting recommendations."""
    
    # Page header
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0;">
            <h1>🔍 Discover Movies</h1>
            <p style="font-size: 1.2rem; color: rgba(255,255,255,0.8); margin-bottom: 2rem;">
                Explore, search, and get AI-powered movie recommendations
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Check if movies data is available
    if movies.empty:
        show_status_message(
            "⚠️ No movies loaded. Please ensure the movie database is available.",
            "warning"
        )
        return
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 AI Recommendations", 
        "🔍 Search & Browse", 
        "🎭 Genre Explorer", 
        "📊 Popular Movies"
    ])
    
    with tab1:
        render_ai_recommendations(movies, similarity, svd_model)
    
    with tab2:
        render_search_browse(movies, similarity)
    
    with tab3:
        render_genre_explorer()
    
    with tab4:
        render_popular_movies()


def render_ai_recommendations(movies, similarity, svd_model):
    """Render AI-powered recommendation section."""
    
    st.markdown(
        """
        <div style="background: rgba(78, 205, 196, 0.1); border: 1px solid rgba(78, 205, 196, 0.3); 
                    border-radius: 15px; padding: 2rem; margin: 1rem 0;">
            <h3 style="color: #4ecdc4; text-align: center; margin-bottom: 1rem;">🤖 AI-Powered Recommendations</h3>
            <p style="color: rgba(255,255,255,0.8); text-align: center; margin: 0;">
                Choose a movie and get personalized recommendations using different AI algorithms
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Movie selection
    movie_list = movies["title"].dropna().unique()
    selected_movie = st.selectbox(
        "🎥 Select a movie for recommendations:",
        movie_list,
        help="Choose a movie you like to get similar recommendations"
    )
    
    # Recommendation buttons
    st.markdown("### 🚀 Get Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(
            "🎬 Content-Based", 
            help="Find movies similar in content (genres, themes, etc.)",
            use_container_width=True
        ):
            if selected_movie in movie_list:
                with st.spinner("🎬 Finding content-based recommendations..."):
                    recommended_names, recommended_posters = recommend_content_based(
                        selected_movie, movies, similarity
                    )
                    if recommended_names:
                        display_recommendations(recommended_names, recommended_posters, "Content-Based")
                    else:
                        show_status_message("❌ Could not generate content-based recommendations.", "error")
            else:
                show_status_message(f"❌ Movie '{selected_movie}' not found in database.", "error")
        
        if st.button(
            "👥 Collaborative", 
            help="Find movies based on what similar users liked",
            use_container_width=True
        ):
            user_id = st.session_state.current_user if st.session_state.current_user else 1
            with st.spinner("👥 Finding collaborative recommendations..."):
                recommended_names, recommended_posters = recommend_collaborative(
                    user_id, movies, svd_model
                )
                if recommended_names:
                    display_recommendations(recommended_names, recommended_posters, "Collaborative")
                else:
                    show_status_message("❌ Could not generate collaborative recommendations.", "error")
    
    with col2:
        if st.button(
            "🔄 Hybrid", 
            help="Combine content-based and collaborative filtering",
            use_container_width=True
        ):
            user_id = st.session_state.current_user if st.session_state.current_user else 1
            with st.spinner("🔄 Finding hybrid recommendations..."):
                recommended_names, recommended_posters = recommend_hybrid(
                    selected_movie, user_id, movies, similarity, svd_model
                )
                if recommended_names:
                    display_recommendations(recommended_names, recommended_posters, "Hybrid")
                else:
                    show_status_message("❌ Could not generate hybrid recommendations.", "error")
        
        if st.button(
            "⭐ Personalized", 
            help="Get recommendations based on your ratings",
            use_container_width=True
        ):
            if not st.session_state.current_user:
                show_status_message("⚠️ Please sign in to get personalized recommendations.", "warning")
            else:
                with st.spinner("⭐ Finding personalized recommendations..."):
                    get_personalized_recommendations(movies, similarity)


def render_search_browse(movies, similarity):
    """Render search and browse section."""
    
    st.markdown(
        """
        <div style="background: rgba(255, 107, 107, 0.1); border: 1px solid rgba(255, 107, 107, 0.3); 
                    border-radius: 15px; padding: 2rem; margin: 1rem 0;">
            <h3 style="color: #ff6b6b; text-align: center; margin-bottom: 1rem;">🔍 Search & Browse</h3>
            <p style="color: rgba(255,255,255,0.8); text-align: center; margin: 0;">
                Search for specific movies or browse through the database
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Search functionality
    search_query = st.text_input(
        "🔍 Search movies by title:",
        placeholder="Enter movie title...",
        help="Search for movies in our database"
    )
    
    if search_query:
        with st.spinner(f"🔍 Searching for '{search_query}'..."):
            # Search in local database
            filtered_movies = movies[
                movies["title"].str.contains(search_query, case=False, na=False)
            ]
            
            if not filtered_movies.empty:
                st.success(f"✅ Found {len(filtered_movies)} movies matching '{search_query}'")
                
                # Display search results
                st.markdown("### 📋 Search Results")
                display_movie_grid(filtered_movies.head(6), "search")
                
                # Show recommendations based on first result
                if len(filtered_movies) > 0:
                    first_title = filtered_movies.head(1)["title"].iloc[0]
                    st.markdown("### 🎯 Similar Movies")
                    with st.spinner("Finding similar movies..."):
                        names, posters = recommend_content_based(first_title, movies, similarity)
                        if names:
                            display_recommendations(names, posters, "Similar to your search")
            else:
                st.warning(f"⚠️ No movies found matching '{search_query}'")
                
                # Try API search as fallback
                st.markdown("### 🌐 Searching online...")
                with st.spinner("Searching online databases..."):
                    try:
                        api_results = search_movies(search_query, 6)
                        if api_results:
                            st.success(f"✅ Found {len(api_results)} movies online")
                            display_api_movies(api_results, "online_search")
                        else:
                            st.info("ℹ️ No movies found online either. Try a different search term.")
                    except Exception as e:
                        st.error(f"❌ Error searching online: {e}")


def render_genre_explorer():
    """Render genre exploration section."""
    
    st.markdown(
        """
        <div style="background: rgba(255, 193, 7, 0.1); border: 1px solid rgba(255, 193, 7, 0.3); 
                    border-radius: 15px; padding: 2rem; margin: 1rem 0;">
            <h3 style="color: #ffc107; text-align: center; margin-bottom: 1rem;">🎭 Genre Explorer</h3>
            <p style="color: rgba(255,255,255,0.8); text-align: center; margin: 0;">
                Explore movies by genre and discover new favorites
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Get genres
    try:
        genre_map = fetch_genres()
        if not genre_map:
            show_status_message("⚠️ Could not load genres. Using default genres.", "warning")
            genre_map = {
                28: "Action", 35: "Comedy", 18: "Drama", 878: "Sci-Fi",
                27: "Horror", 10749: "Romance", 53: "Thriller", 12: "Adventure"
            }
    except Exception as e:
        st.error(f"❌ Error loading genres: {e}")
        return
    
    # Popular genres
    popular_genres = ["Action", "Comedy", "Drama", "Sci-Fi", "Horror", "Romance", "Thriller", "Adventure"]
    
    st.markdown("### 🎯 Popular Genres")
    
    # Create responsive genre grid
    cols = st.columns(4)
    for idx, genre in enumerate(popular_genres):
        with cols[idx % 4]:
            if st.button(
                f"🎭 {genre}",
                key=f"genre_{genre}",
                use_container_width=True,
                help=f"Explore {genre} movies"
            ):
                # Find genre ID
                genre_id = None
                for gid, gname in genre_map.items():
                    if gname.lower() == genre.lower():
                        genre_id = gid
                        break
                
                if genre_id:
                    with st.spinner(f"🎭 Loading {genre} movies..."):
                        try:
                            genre_movies = fetch_movies_by_genre(genre_id)
                            if genre_movies:
                                st.session_state.selected_genre = genre
                                st.session_state.genre_movies = genre_movies
                                st.rerun()
                            else:
                                show_status_message(f"⚠️ No {genre} movies found.", "warning")
                        except Exception as e:
                            show_status_message(f"❌ Error loading {genre} movies: {e}", "error")
                else:
                    show_status_message(f"⚠️ Genre '{genre}' not found in database.", "warning")
    
    # Display selected genre movies
    if st.session_state.get("selected_genre") and st.session_state.get("genre_movies"):
        st.markdown("---")
        st.markdown(f"### 🎭 {st.session_state.selected_genre} Movies")
        
        display_api_movies(st.session_state.genre_movies, "genre")
        
        # Clear selection button
        if st.button("🔄 Clear Genre Selection"):
            st.session_state.selected_genre = None
            st.session_state.genre_movies = None
            st.rerun()


def render_popular_movies():
    """Render popular movies section."""
    
    st.markdown(
        """
        <div style="background: rgba(40, 167, 69, 0.1); border: 1px solid rgba(40, 167, 69, 0.3); 
                    border-radius: 15px; padding: 2rem; margin: 1rem 0;">
            <h3 style="color: #28a745; text-align: center; margin-bottom: 1rem;">📊 Popular Movies</h3>
            <p style="color: rgba(255,255,255,0.8); text-align: center; margin: 0;">
                Discover what's trending and popular right now
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Load popular movies
    with st.spinner("📊 Loading popular movies..."):
        try:
            popular_movies = fetch_popular_movies(12)
            if popular_movies:
                st.success(f"✅ Loaded {len(popular_movies)} popular movies")
                display_api_movies(popular_movies, "popular")
            else:
                show_status_message("⚠️ Could not load popular movies.", "warning")
        except Exception as e:
            show_status_message(f"❌ Error loading popular movies: {e}", "error")


def display_recommendations(names, posters, recommendation_type):
    """Display recommendation results."""
    
    st.markdown(f"### 🎯 {recommendation_type} Recommendations")
    
    if not names or not posters:
        show_status_message("⚠️ No recommendations found.", "warning")
        return
    
    # Create movie objects for display
    movies_to_display = []
    for name, poster in zip(names, posters):
        movies_to_display.append({
            "title": name,
            "poster": poster,
            "rating": 0.0,  # Will be fetched by card component
            "description": "Loading..."  # Will be fetched by card component
        })
    
    # Display in responsive grid
    st.markdown('<div class="movie-grid">', unsafe_allow_html=True)
    
    for idx, movie in enumerate(movies_to_display):
        with st.container():
            create_movie_card(movie, show_actions=True, card_type=f"rec_{recommendation_type.lower()}_{idx}")
            st.markdown("---")
    
    st.markdown('</div>', unsafe_allow_html=True)


def display_movie_grid(movies_df, context):
    """Display movies from DataFrame in responsive grid."""
    
    st.markdown('<div class="movie-grid">', unsafe_allow_html=True)
    
    for idx, movie in enumerate(movies_df.itertuples()):
        with st.container():
            # Create movie object
            movie_obj = {
                "id": movie.id,
                "title": movie.title,
                "poster": fetch_poster(movie.id),
                "rating": getattr(movie, 'vote_average', 0.0),
                "description": getattr(movie, 'overview', 'No description available')
            }
            
            create_movie_card(movie_obj, show_actions=True, card_type=f"grid_{context}_{idx}")
            st.markdown("---")
    
    st.markdown('</div>', unsafe_allow_html=True)


def display_api_movies(movies_list, context):
    """Display movies from API results in responsive grid."""
    
    if not movies_list:
        show_status_message("⚠️ No movies to display.", "warning")
        return
    
    st.markdown('<div class="movie-grid">', unsafe_allow_html=True)
    
    for idx, movie in enumerate(movies_list):
        with st.container():
            # Create movie object
            movie_obj = {
                "id": movie.get("id", idx),
                "title": movie.get("title", "Unknown"),
                "poster": movie.get("poster", "https://via.placeholder.com/300x450?text=No+Poster"),
                "rating": movie.get("rating", 0.0),
                "description": movie.get("description", "No description available")
            }
            
            create_movie_card(movie_obj, show_actions=True, card_type=f"api_{context}_{idx}")
            st.markdown("---")
    
    st.markdown('</div>', unsafe_allow_html=True)


def get_personalized_recommendations(movies, similarity):
    """Get personalized recommendations based on user ratings."""
    
    try:
        top_rated = []
        csv_path = "user_reviews.csv"
        
        if os.path.exists(csv_path):
            reviews_df = pd.read_csv(csv_path, header=0)
            reviews_df["user"] = reviews_df["user"].astype(str)
            uid = str(st.session_state.current_user)
            
            user_reviews = reviews_df[reviews_df["user"] == uid]
            if not user_reviews.empty:
                top_rated = (
                    user_reviews.sort_values("rating", ascending=False)
                    .head(5)["title"]
                    .tolist()
                )
        
        if not top_rated:
            show_status_message(
                "⚠️ No ratings found. Showing popular movies instead.",
                "warning"
            )
            popular = fetch_popular_movies(5)
            if popular:
                names = [m["title"] for m in popular]
                posters = [m["poster"] for m in popular]
                display_recommendations(names, posters, "Popular Movies")
            return
        
        # Get recommendations based on top rated movies
        personalized_names = []
        personalized_posters = []
        
        for title in top_rated:
            names, posters = recommend_content_based(title, movies, similarity)
            for n, p in zip(names, posters):
                if n not in personalized_names:
                    personalized_names.append(n)
                    personalized_posters.append(p)
        
        if personalized_names:
            display_recommendations(personalized_names, personalized_posters, "Personalized")
        else:
            show_status_message(
                "⚠️ No personalized recommendations found. Showing popular movies instead.",
                "warning"
            )
            popular = fetch_popular_movies(5)
            if popular:
                names = [m["title"] for m in popular]
                posters = [m["poster"] for m in popular]
                display_recommendations(names, posters, "Popular Movies")
                
    except Exception as e:
        show_status_message(f"❌ Error getting personalized recommendations: {e}", "error")
