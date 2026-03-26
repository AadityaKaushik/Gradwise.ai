from database.user_queries import create_user, get_user_by_email
from database.connection import get_connection
from Utils.security import hash_password

def user_signup(email, password):
    create_user(email, hash_password(password))