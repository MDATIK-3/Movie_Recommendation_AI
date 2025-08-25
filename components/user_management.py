import pandas as pd
import os
import csv
from datetime import datetime


def load_users():
    """Load users from CSV file with improved error handling."""
    if os.path.exists("users.csv"):
        try:
            df = pd.read_csv("users.csv")
            # Convert to list of dictionaries for easier handling
            return df.to_dict('records')
        except Exception as e:
            print(f"Error loading users: {e}")
            return []
    else:
        # Create default users file if it doesn't exist
        create_default_users()
        return []


def create_default_users():
    """Create a default users CSV file with sample data."""
    default_users = [
        {"id": 1, "username": "demo", "password": "demo123", "email": "demo@example.com", "created_at": "2024-01-01"},
        {"id": 2, "username": "admin", "password": "admin123", "email": "admin@example.com", "created_at": "2024-01-01"}
    ]
    
    try:
        with open("users.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "username", "password", "email", "created_at"])
            writer.writeheader()
            writer.writerows(default_users)
    except Exception as e:
        print(f"Error creating default users: {e}")


def save_user(user_data):
    """Save a new user to the CSV file."""
    try:
        # Load existing users
        users = load_users()
        
        # Check if username already exists
        if any(user.get("username") == user_data.get("username") for user in users):
            return False
        
        # Add new user
        users.append(user_data)
        
        # Save back to CSV
        with open("users.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "username", "password", "email", "created_at"])
            writer.writeheader()
            writer.writerows(users)
        
        return True
    except Exception as e:
        print(f"Error saving user: {e}")
        return False


def get_user_by_username(username):
    """Get user data by username."""
    users = load_users()
    for user in users:
        if user.get("username") == username:
            return user
    return None


def update_user_profile(user_id, profile_data):
    """Update user profile information."""
    try:
        users = load_users()
        
        # Find and update user
        for user in users:
            if user.get("id") == user_id:
                user.update(profile_data)
                break
        
        # Save back to CSV
        with open("users.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "username", "password", "email", "created_at"])
            writer.writeheader()
            writer.writerows(users)
        
        return True
    except Exception as e:
        print(f"Error updating user profile: {e}")
        return False


def delete_user(user_id):
    """Delete a user from the system."""
    try:
        users = load_users()
        
        # Remove user
        users = [user for user in users if user.get("id") != user_id]
        
        # Save back to CSV
        with open("users.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "username", "password", "email", "created_at"])
            writer.writeheader()
            writer.writerows(users)
        
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False


def get_user_statistics(user_id):
    """Get user statistics from activity data."""
    try:
        if not os.path.exists("user_activity.csv"):
            return {"movies_watched": 0, "movies_rated": 0, "watchlist_count": 0}
        
        df = pd.read_csv("user_activity.csv")
        user_activities = df[df["user_id"] == str(user_id)]
        
        stats = {
            "movies_watched": len(user_activities[user_activities["action"] == "watched"]),
            "movies_rated": len(user_activities[user_activities["action"] == "rated"]),
            "watchlist_count": len(user_activities[user_activities["action"] == "added_to_watchlist"])
        }
        
        return stats
    except Exception as e:
        print(f"Error getting user statistics: {e}")
        return {"movies_watched": 0, "movies_rated": 0, "watchlist_count": 0}
