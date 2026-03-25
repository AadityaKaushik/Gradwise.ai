from database.connection import get_connection
from Utils.security import generate_org_key


def create_org(name):
    conn = get_connection()
    try:
        org_key = generate_org_key()
        cursor = conn.cursor()
        query = """
        INSERT INTO v2.organizations (name, invite_key)
        VALUES (%s, %s)
        RETURNING organization_id
        """
        cursor.execute(query, (name, org_key))
        org_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        return org_id, org_key
    finally:
        conn.close()
