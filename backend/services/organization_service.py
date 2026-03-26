from database.membership_queries import create_membership
from database.connection import get_connection
from datetime import datetime, timezone

def join_organization(user_id, invite_key, role):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        query = """
            SELECT organization_id, invite_expires_at
            FROM v2.organizations
            WHERE invite_key = %s
        """

        cursor.execute(query, (invite_key,))
        row = cursor.fetchone()

        if row is None:
            return None   

        org_id, expiry_time = row

        now = datetime.utcnow()

        if expiry_time is not None and expiry_time < now:
            return None

        cursor.close()
        return create_membership(user_id, org_id, role)

    finally:
        conn.close()

    
def get_organizations(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = """
            SELECT organization_id, role FROM v2.organization_memberships
            WHERE user_id = %s
        """
        cursor.execute(query, (user_id,))
        orgs = cursor.fetchall()
        cursor.close()
        return orgs
    finally:
        conn.close()