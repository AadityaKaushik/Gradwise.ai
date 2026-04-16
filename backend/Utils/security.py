import bcrypt
import secrets
import string

# PASSWORDS AND CRYPTO WORK
def generate_org_key(length=50):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_password(raw_password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(raw_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(to_check, stored):
    return bcrypt.checkpw(to_check.encode(), stored.encode())


# JWT AUTHENTICATION WORK
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY environment variable is not set")
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=100)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return payload
    except JWTError:
        return None

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


from fastapi import Request, HTTPException, Header

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):

    token = credentials.credentials  # this extracts the token after "Bearer"

    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(401, "Invalid token")

    return payload


def require_org_admin(org_id: int, current_user: dict = Depends(get_current_user)):
    from database.membership_queries import get_user_role_in_org

    user_id = current_user["user_id"]
    role = get_user_role_in_org(user_id, org_id)

    if role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not an admin of this organization"
        )

    return current_user