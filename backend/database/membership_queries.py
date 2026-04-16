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


def get_user_role_in_org(user_id, org_id):
    """Returns the user's role in the given org, or None if not a member."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT role
            FROM v3.organization_memberships
            WHERE user_id = %s AND organization_id = %s
        """, (user_id, org_id))

        row = cursor.fetchone()
        return row[0] if row else None

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)
