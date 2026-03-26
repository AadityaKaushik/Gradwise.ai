import secrets
import string

def generate_org_key(length=50):
    alphabet=string.ascii_letters+string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_password(raw_password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(raw_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(to_check, stored):
    return bcrypt.checkpw(to_check.encode(), stored.encode())