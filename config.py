"""
Configuration file for MovieMind application.
Centralizes all app settings and constants.
"""

import os
from typing import Dict, Any

# App Configuration
APP_NAME = "MovieMind"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "AI-Powered Movie Recommendation System"

# API Configuration
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "9ef5ae6fc8b8f484e9295dc97d8d32ea")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Cache Configuration
CACHE_TTL = {
    "popular_movies": 3600,  # 1 hour
    "genres": 3600,          # 1 hour
    "movie_details": 1800,   # 30 minutes
    "posters": 3600,         # 1 hour
    "trailers": 1800,        # 30 minutes
}

# UI Configuration
UI_CONFIG = {
    "theme": {
        "primary_color": "#4ecdc4",
        "secondary_color": "#ff6b6b",
        "background_gradient": "linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)",
        "card_background": "rgba(255, 255, 255, 0.05)",
        "text_color": "#ffffff",
        "text_secondary": "rgba(255, 255, 255, 0.8)"
    },
    "responsive_breakpoints": {
        "mobile": 480,
        "tablet": 768,
        "desktop": 1024
    },
    "movie_grid": {
        "desktop": 3,
        "tablet": 2,
        "mobile": 1
    }
}

# Recommendation Configuration
RECOMMENDATION_CONFIG = {
    "default_limit": 5,
    "max_limit": 20,
    "content_weight": 0.6,
    "collaborative_weight": 0.4,
    "similarity_threshold": 0.1
}

# Mood-Genre Mappings
MOOD_GENRE_MAPPINGS = {
    "happy": [35, 10751, 16],      # Comedy, Family, Animation
    "sad": [18, 10749, 10402],     # Drama, Romance, Music
    "excited": [28, 12, 878],      # Action, Adventure, Sci-Fi
    "relaxed": [99, 36, 14],       # Documentary, History, Fantasy
    "scared": [27, 53, 9648],      # Horror, Thriller, Mystery
    "romantic": [10749, 18, 35],   # Romance, Drama, Comedy
    "adventurous": [12, 28, 14],   # Adventure, Action, Fantasy
    "thoughtful": [18, 99, 36]     # Drama, Documentary, History
}

# File Paths
DATA_FILES = {
    "movies": "movies.csv",
    "users": "users.csv",
    "user_activity": "user_activity.csv",
    "user_reviews": "user_reviews.csv",
    "watchlist_prefix": "watchlist_"
}

# Default User Credentials
DEFAULT_USERS = [
    {
        "id": 1,
        "username": "demo",
        "password": "demo123",
        "email": "demo@example.com",
        "created_at": "2024-01-01"
    },
    {
        "id": 2,
        "username": "admin",
        "password": "admin123",
        "email": "admin@example.com",
        "created_at": "2024-01-01"
    }
]

# Demo Movies (fallback when API is unavailable)
DEMO_MOVIES = [
    {
        "id": 1,
        "title": "The Shawshank Redemption",
        "rating": 9.3,
        "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        "poster": "https://via.placeholder.com/300x450?text=Shawshank+Redemption",
        "runtime": 142,
        "release_date": "1994-09-22",
        "genres": [18, 80]
    },
    {
        "id": 2,
        "title": "The Godfather",
        "rating": 9.2,
        "description": "The aging patriarch of an organized crime dynasty transfers control to his reluctant son.",
        "poster": "https://via.placeholder.com/300x450?text=The+Godfather",
        "runtime": 175,
        "release_date": "1972-03-14",
        "genres": [18, 80]
    },
    {
        "id": 3,
        "title": "Pulp Fiction",
        "rating": 8.9,
        "description": "The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.",
        "poster": "https://via.placeholder.com/300x450?text=Pulp+Fiction",
        "runtime": 154,
        "release_date": "1994-10-14",
        "genres": [18, 80]
    }
]

# Error Messages
ERROR_MESSAGES = {
    "api_key_missing": "❌ TMDB_API_KEY environment variable not set. Please set it to use movie features.",
    "api_key_invalid": "❌ Invalid API key. Please check your TMDB_API_KEY.",
    "network_error": "⚠️ Network connection error. Using demo data.",
    "timeout_error": "⚠️ Request timed out. Using demo data.",
    "file_not_found": "❌ Required data file not found.",
    "data_loading_error": "❌ Error loading data.",
    "recommendation_error": "❌ Error generating recommendations.",
    "user_not_found": "❌ User not found.",
    "invalid_credentials": "❌ Invalid username or password.",
    "username_exists": "❌ Username already exists. Please choose a different one.",
    "password_mismatch": "❌ Passwords do not match. Please try again.",
    "password_too_short": "⚠️ Password must be at least 4 characters long."
}

# Success Messages
SUCCESS_MESSAGES = {
    "welcome_back": "✅ Welcome back, {}!",
    "account_created": "✅ Account created successfully! Welcome, {}!",
    "signed_out": "✅ Signed out successfully!",
    "movie_added_watchlist": "✅ Added '{}' to watchlist!",
    "movie_removed_watchlist": "✅ Removed '{}' from watchlist!",
    "movie_watched": "✅ Added '{}' to your history!",
    "rating_submitted": "✅ Rated '{}' with {} stars!",
    "data_loaded": "✅ Loaded movie database successfully",
    "similarity_loaded": "✅ Loaded similarity matrix",
    "model_loaded": "✅ Loaded SVD model"
}

# Warning Messages
WARNING_MESSAGES = {
    "demo_mode": "ℹ️ Running in demo mode. Set TMDB_API_KEY for full functionality.",
    "no_similarity": "ℹ️ No similarity.pkl found. Creating basic similarity matrix...",
    "no_model": "ℹ️ No svd_model.pkl found. Using fallback predictor...",
    "no_ratings": "⚠️ No ratings found for your account. Please rate some movies first.",
    "sign_in_required": "⚠️ Please sign in to access this feature.",
    "api_unavailable": "⚠️ API temporarily unavailable. Using demo data."
}

def get_config() -> Dict[str, Any]:
    """Get complete configuration dictionary."""
    return {
        "app": {
            "name": APP_NAME,
            "version": APP_VERSION,
            "description": APP_DESCRIPTION
        },
        "api": {
            "tmdb_key": TMDB_API_KEY,
            "tmdb_base_url": TMDB_BASE_URL,
            "tmdb_image_base_url": TMDB_IMAGE_BASE_URL
        },
        "cache": CACHE_TTL,
        "ui": UI_CONFIG,
        "recommendations": RECOMMENDATION_CONFIG,
        "mood_genres": MOOD_GENRE_MAPPINGS,
        "files": DATA_FILES,
        "default_users": DEFAULT_USERS,
        "demo_movies": DEMO_MOVIES,
        "messages": {
            "errors": ERROR_MESSAGES,
            "success": SUCCESS_MESSAGES,
            "warnings": WARNING_MESSAGES
        }
    }
