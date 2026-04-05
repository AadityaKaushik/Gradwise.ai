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


def update_membership_role(org_id, target_user_id, new_role):
    """Admin action: assign a role to a PENDING member."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE v3.organization_memberships
            SET role = %s
            WHERE organization_id = %s AND user_id = %s
            RETURNING membership_id, role
        """, (new_role, org_id, target_user_id))

        row = cursor.fetchone()
        if not row:
            raise ValueError("Membership not found")

        conn.commit()

        return {
            "membership_id": row[0],
            "role": row[1],
            "message": "Role updated successfully"
        }

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)