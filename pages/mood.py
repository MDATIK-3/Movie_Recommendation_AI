import streamlit as st
from components.api_calls import fetch_genres, fetch_trailer
from components.recommendations import recommend_by_mood
from components.file_handling import save_user_activity, save_watchlist_to_csv
from components.ui_components import create_movie_card, show_status_message
import os
import csv


def render_mood_page(**kwargs):
    """Renders the mood-based recommendation page."""
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0;">
            <h1>😊 Mood-Based Recommendations</h1>
            <p style="font-size: 1.2rem; color: rgba(255,255,255,0.8); margin-bottom: 2rem;">
                Tell us how you're feeling and we'll find the perfect movie for you
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Check if user is signed in
    if not st.session_state.current_user:
        show_status_message(
            "⚠️ Please sign in to get personalized mood-based recommendations.",
            "warning"
        )
        return

    with st.form("mood_form"):
        st.markdown(
            """
            <div style="background: rgba(255,255,255,0.05); border-radius: 15px; padding: 2rem; margin: 1rem 0;">
                <h3 style="color: #4ecdc4; text-align: center; margin-bottom: 2rem;">How are you feeling today?</h3>
            """,
            unsafe_allow_html=True
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            mood = st.selectbox(
                "😊 What's your current mood?",
                ["", "happy", "sad", "excited", "relaxed", "scared", "romantic", "adventurous", "thoughtful"],
                index=0,
                help="Select the mood that best describes how you're feeling"
            )
            
            energy = st.selectbox(
                "⚡ Energy level?",
                ["", "high", "medium", "low"],
                index=0,
                help="How much energy do you have right now?"
            )
            
            watching_with = st.selectbox(
                "👥 Who are you watching with?",
                ["", "alone", "friends", "family", "partner", "kids"],
                index=0,
                help="This helps us suggest appropriate content"
            )
        
        with col2:
            time_available = st.selectbox(
                "⏰ How much time do you have?",
                ["", "short (< 90 min)", "medium (90-120 min)", "long (> 120 min)"],
                index=0,
                help="Movie length preference"
            )
            
            genre_preference = st.selectbox(
                "🎭 Any specific genre?",
                [""] + list(fetch_genres().values()),
                index=0,
                help="Leave empty for mood-based suggestions"
            )
            
            avoid_content = st.multiselect(
                "🚫 Content to avoid?",
                ["violence", "scary", "sad", "romance", "action", "drama"],
                help="Select content types you'd prefer to avoid"
            )

        st.markdown("</div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.form_submit_button(
                "🎬 Get Mood-Based Recommendations",
                use_container_width=True,
                help="Get personalized movie suggestions based on your mood"
            )

        if submit_button:
            # Collect answers
            answers = {
                "mood": mood if mood else "neutral",
                "energy": energy if energy else "medium",
                "watching_with": watching_with if watching_with else "alone",
                "time_available": time_available if time_available else "medium",
                "genre_preference": genre_preference if genre_preference else "",
                "avoid_content": avoid_content
            }
            
            st.session_state.mood_answers = answers
            
            # Get recommendations
            with st.spinner("🎬 Finding the perfect movies for your mood..."):
                recommended_movies, recommended_posters = recommend_by_mood(answers)
            
            if recommended_movies:
                # Store the movie objects directly
                st.session_state.mood_recommendations = recommended_movies
                
            else:
                st.session_state.mood_recommendations = []

    # Display recommendations if available
    if st.session_state.get("mood_recommendations"):
        st.markdown("---")
        st.markdown(
            """
            <h2 style="text-align: center; margin: 2rem 0;">🎬 Perfect Movies for Your Mood</h2>
            """,
            unsafe_allow_html=True
        )
        
        # Display mood summary
        if st.session_state.get("mood_answers"):
            answers = st.session_state.mood_answers
            st.markdown(
                f"""
                <div style="background: rgba(78, 205, 196, 0.1); border: 1px solid rgba(78, 205, 196, 0.3); 
                            border-radius: 10px; padding: 1rem; margin: 1rem 0;">
                    <h4 style="color: #4ecdc4; margin: 0;">Mood Profile:</h4>
                    <p style="margin: 0.5rem 0 0 0; color: rgba(255,255,255,0.8);">
                        Feeling: <strong>{answers.get('mood', 'neutral').title()}</strong> | 
                        Energy: <strong>{answers.get('energy', 'medium').title()}</strong> | 
                        Watching: <strong>{answers.get('watching_with', 'alone').title()}</strong>
                    </p>
                    <p style="margin: 0.5rem 0 0 0; color: rgba(255,255,255,0.8);">
                        Time: <strong>{answers.get('time_available', 'medium').title()}</strong> | 
                        Genre: <strong>{answers.get('genre_preference', 'Any').title()}</strong>
                    </p>
                    <p style="margin: 0.5rem 0 0 0; color: rgba(255,255,255,0.8);">
                        Avoiding: <strong>{', '.join(answers.get('avoid_content', ['None']))}</strong>
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Display movies in grid
        st.markdown('<div class="movie-grid">', unsafe_allow_html=True)
        
        for idx, movie in enumerate(st.session_state.mood_recommendations):
            with st.container():
                create_movie_card(movie, show_actions=True, card_type=f"mood_{idx}")
                st.markdown("---")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Clear recommendations button
        if st.button("🔄 Get New Recommendations", help="Start over with new mood preferences"):
            st.session_state.mood_recommendations = []
            st.session_state.mood_answers = {}
            st.rerun()
    
    # Show tips for better recommendations
    st.markdown("---")
    st.markdown(
        """
        <h3 style="text-align: center; margin: 2rem 0;">💡 Tips for Better Recommendations</h3>
        """,
        unsafe_allow_html=True
    )
    
    tips_col1, tips_col2 = st.columns(2)
    
    with tips_col1:
        st.markdown(
            """
            <div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 1rem; margin: 0.5rem 0;">
                <h4 style="color: #4ecdc4; margin-bottom: 0.5rem;">🎯 Be Specific</h4>
                <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">
                    The more specific you are about your mood and preferences, the better our recommendations will be.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown(
            """
            <div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 1rem; margin: 0.5rem 0;">
                <h4 style="color: #ff6b6b; margin-bottom: 0.5rem;">⏰ Consider Time</h4>
                <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">
                    Let us know how much time you have so we can suggest appropriately sized movies.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with tips_col2:
        st.markdown(
            """
            <div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 1rem; margin: 0.5rem 0;">
                <h4 style="color: #4ecdc4; margin-bottom: 0.5rem;">👥 Audience Matters</h4>
                <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">
                    Tell us who you're watching with for age-appropriate and group-friendly suggestions.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown(
            """
            <div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 1rem; margin: 0.5rem 0;">
                <h4 style="color: #ff6b6b; margin-bottom: 0.5rem;">🔄 Try Again</h4>
                <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">
                    Don't like the suggestions? Try again with different preferences or mood settings.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
