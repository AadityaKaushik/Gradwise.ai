from database.connection import get_connection


def create_user(email, password_hash):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        query = """
        INSERT INTO v2.users (email, password_hash)
        VALUES (%s, %s)
        RETURNING user_id
        """
        cursor.execute(query, (email, password_hash)) 
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
        SELECT user_id, email, password_hash, role FROM v2.users
        JOIN v2.organization_memberships
        ON v2.organization_memberships.user_id = v2.users.user_id
        WHERE email = %s
        """
        cursor.execute(query, (email,))
        result = cursor.fetchone()

        cursor.close()

        if result is None:
            return None

        return result

    finally:
        conn.close()