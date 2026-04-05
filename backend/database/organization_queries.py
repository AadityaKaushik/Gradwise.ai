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
            INSERT INTO v3.organizations (name, invite_key)
            VALUES (%s, %s)
            RETURNING organization_id, invite_key
        """, (name, org_key))

        row = cursor.fetchone()
        org_id, invite_key = row

        cursor.execute("""
            INSERT INTO v3.organization_memberships (user_id, organization_id, role)
            VALUES (%s, %s, 'ADMIN')
        """, (user_id, org_id))

        conn.commit()

        return {
            "organization_id": org_id,
            "invite_key": invite_key
        }

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise ValueError("Organization with this name already exists")

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

        cursor.execute("""
            SELECT organization_id, invite_expires_at
            FROM v3.organizations
            WHERE invite_key = %s
        """, (invite_key,))

        result = cursor.fetchone()

        if not result:
            raise ValueError("Invalid invite key")

        org_id, key_expiry = result

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
