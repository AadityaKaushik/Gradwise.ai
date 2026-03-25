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
        SELECT user_id FROM v2.users
        WHERE email = %s
        """
        cursor.execute(query, (email,))
        result = user_id = cursor.fetchone()[0]
        cursor.close()
        if result is None:
            return None
        return result[0]
    finally:
        conn.close()