from database.membership_queries import create_membership
from database.connection import get_connection, return_connection
from datetime import datetime, timezone

def join_organization(user_id, invite_key):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT organization_id, invite_expires_at
            FROM v2.organizations
            WHERE invite_key = %s
        """, (invite_key,))

        row = cursor.fetchone()

        if not row:
            raise ValueError("Invalid invite key")

        org_id, expiry_time = row

        if expiry_time and expiry_time < datetime.utcnow():
            raise ValueError("Invite key expired")

        role = "student"

        return create_membership(user_id, org_id, role)

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)
    
def get_organizations(user_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT organization_id, role 
            FROM v2.organization_memberships
            WHERE user_id = %s
        """, (user_id,))

        rows = cursor.fetchall()

        return [
            {"organization_id": org_id, "role": role}
            for org_id, role in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)