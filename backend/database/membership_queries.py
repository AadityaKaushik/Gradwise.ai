from database.connection import get_connection, return_connection
import psycopg2


def create_membership(user_id, org_id, role="PENDING"):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO v3.organization_memberships (user_id, organization_id, role)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, organization_id) DO NOTHING
            RETURNING membership_id
        """, (user_id, org_id, role))

        row = cursor.fetchone()
        if not row:
            raise ValueError("User already in this organization")

        membership_id = row[0]
        conn.commit()

        return {
            "membership_id": membership_id,
            "message": "Membership created"
        }

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)
