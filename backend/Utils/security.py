import bcrypt
import secrets
import string

# PASSWORDS AND CRYPTO WORK
def generate_org_key(length=50):
    alphabet=string.ascii_letters+string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_password(raw_password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(raw_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(to_check, stored):
    return bcrypt.checkpw(to_check.encode(), stored.encode())


# JWT AUTHENTICATION WORK
from jose import jwt, JWTError
from datetime import datetime, timedelta

SECRET_KEY = "AADITYAKAUSHIK1234"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=100)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=[ALGORITHM])
    return encoded_jwt

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None