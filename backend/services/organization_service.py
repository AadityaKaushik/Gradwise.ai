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
            FROM v3.organizations
            WHERE invite_key = %s
        """, (invite_key,))

        row = cursor.fetchone()

        if not row:
            raise ValueError("Invalid invite key")

        org_id, expiry_time = row

        # Use timezone-aware comparison (TIMESTAMPTZ)
        if expiry_time and expiry_time < datetime.now(timezone.utc):
            raise ValueError("Invite key expired")

        # New joiners get PENDING role — admin assigns actual role later
        return create_membership(user_id, org_id, role="PENDING")

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
            SELECT om.organization_id, om.role, om.status, o.name, o.invite_key
            FROM v3.organization_memberships om
            JOIN v3.organizations o ON o.organization_id = om.organization_id
            WHERE om.user_id = %s
            ORDER BY o.name
        """, (user_id,))

        rows = cursor.fetchall()

        return [
            {
                "organization_id": r[0],
                "role": r[1],
                "status": r[2],
                "name": r[3],
                "invite_key": r[4]
            }
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)