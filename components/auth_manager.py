import json
import os
from components.user_management import get_user_by_username


def save_auth_state(username, user_id):
    """Save authentication state to a temporary file."""
    auth_data = {
        "username": username,
        "user_id": user_id,
        "authenticated": True
    }
    try:
        with open(".auth_state.json", "w") as f:
            json.dump(auth_data, f)
    except Exception:
        pass


def load_auth_state():
    """Load authentication state from file."""
    try:
        if os.path.exists(".auth_state.json"):
            with open(".auth_state.json", "r") as f:
                return json.load(f)
    except Exception:
        pass
    return None


def clear_auth_state():
    """Clear authentication state file."""
    try:
        if os.path.exists(".auth_state.json"):
            os.remove(".auth_state.json")
    except Exception:
        pass


def restore_auth_session():
    """Restore authentication session from file."""
    auth_state = load_auth_state()
    if auth_state and auth_state.get("authenticated"):
        user = get_user_by_username(auth_state.get("username"))
        if user:
            return {
                "user_id": user.get("id"),
                "username": auth_state.get("username"),
                "authenticated": True
            }
    return None
