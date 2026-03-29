from database.user_queries import create_user, get_user_by_email
from database.connection import get_connection
from database.user_queries import get_user_by_email, create_user
from Utils.security import hash_password, verify_password


def signup_user(email, password):
    existing_user = get_user_by_email(email)
    if existing_user:
        raise Exception("User already exists")

    hashed_password = hash_password(password)
    user_id = create_user(email, hashed_password)["user_id"]

    return {
        "message": "User created successfully",
        "user_id": user_id
    }

from fastapi import HTTPException, status

def login_user(email, password):
    existing_user = get_user_by_email(email)

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    hash_stored = existing_user["password_hash"]
    user_id = existing_user["user_id"]

    if not verify_password(password, hash_stored):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    return {
        "message": "Login successful",
        "user_id": user_id
    }