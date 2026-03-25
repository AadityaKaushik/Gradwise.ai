from database.connection import get_connection

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