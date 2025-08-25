import pandas as pd
import os
import bcrypt

USERS_CSV = "users.csv"


def load_users():
    if os.path.exists(USERS_CSV):
        try:
            df = pd.read_csv(USERS_CSV)
            return df
        except Exception:
            return pd.DataFrame(columns=["email", "password"])
    else:
        return pd.DataFrame(columns=["email", "password"])


def save_user(email, password):
    df = load_users()
    if email in df["email"].values:
        return False  # User already exists
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    new_row = pd.DataFrame([{"email": email, "password": hashed}])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(USERS_CSV, index=False)
    return True


def authenticate_user(email, password):
    df = load_users()
    user = df[df["email"] == email]
    if not user.empty:
        hashed = user.iloc[0]["password"]
        if bcrypt.checkpw(password.encode(), hashed.encode()):
            return True
    return False
