from database.connection import get_connection, return_connection
import psycopg2

def create_user(email, password_hash):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO v2.users (email, password_hash)
            VALUES (%s, %s)
            RETURNING user_id
        """, (email, password_hash))

        user_id = cursor.fetchone()[0]
        conn.commit()

        return {"user_id": user_id}

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise ValueError("User already exists")

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)

def get_user_by_email(email):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user_id, email, password_hash
            FROM v2.users
            WHERE email = %s
        """, (email,))

        result = cursor.fetchone()

        if not result:
            return None

        user_id, email, password_hash = result

        return {
            "user_id": user_id,
            "email": email,
            "password_hash": password_hash
        }

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)