from database.connection import get_connection
from Utils.security import generate_org_key

def create_org(name, code, type, created_at):
    org_key = generate_org_key();
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO v1.organization (name, code, type, org_signup_key)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (name, code, type, org_key))
        org_id = cursor.fetchone()[0]
        cursor.commit()
        return org_id
    finally:
        cursor.close()


def create_user(org_id, email, password_hash, role):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        query = """
        INSERT INTO v1.users (organization_id, email, password_hash, role)
        VALUES (%s, %s, %s, %s)
        RETURNING user_id
        """
        cursor.execute(query, (org_id, email, password_hash, role)) 
        user_id = cursor.fetchone()[0]

        conn.commit()
        return user_id

    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = """
        SELECT user_id FROM v1.users
        WHERE email = %s
        """
        cursor.execute(query, (email,))
        user_id = cursor.fetchone()[0]
        return user_id
    finally:
        conn.close()