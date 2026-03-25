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