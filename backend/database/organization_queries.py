from database.connection import get_connection, return_connection
from Utils.security import generate_org_key
import psycopg2

def create_org(name, user_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        org_key = generate_org_key()

        cursor.execute("""
            INSERT INTO v2.organizations (name, invite_key)
            VALUES (%s, %s)
            ON CONFLICT (name) DO NOTHING
            RETURNING organization_id
        """, (name, org_key))

        row = cursor.fetchone()
        if not row:
            raise ValueError("Organization with this name already exists")

        org_id = row[0]

        cursor.execute("""
            INSERT INTO v2.organization_memberships (user_id, organization_id, role)
            VALUES (%s, %s, %s)
        """, (user_id, org_id, "Admin"))

        conn.commit()

        return {
            "organization_id": org_id,
            "invite_key": org_key
        }

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_org_by_invite_key(invite_key):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        query = """
            SELECT organization_id, invite_expires_at
            FROM v2.organizations
            WHERE invite_key = %s
        """

        cursor.execute(query, (invite_key,))

        result = cursor.fetchone()

        if not result:
            raise ValueError("Invalid invite key")

        org_id = result[0]
        key_expiry = result[1]

    
        return {
            "org_id": org_id,
            "key_expiry": key_expiry
        }
    
    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)
