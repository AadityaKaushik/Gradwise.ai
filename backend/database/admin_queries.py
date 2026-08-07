from database.connection import get_connection, return_connection


def view_perms(org_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT om.user_id, u.email, om.role, om.status
            FROM v3.organization_memberships om
            JOIN v3.users u ON u.user_id = om.user_id
            WHERE om.organization_id = %s
            ORDER BY
                CASE om.role
                    WHEN 'ADMIN' THEN 1
                    WHEN 'FACULTY' THEN 2
                    WHEN 'STUDENT' THEN 3
                    WHEN 'PENDING' THEN 4
                    ELSE 5
                END
        """, (org_id,))

        result = cursor.fetchall()
        return [
            {"user_id": row[0], "email": row[1], "role": row[2], "status": row[3]}
            for row in result
        ]

    except Exception as e:
        raise RuntimeError("Failed to fetch organization permissions")

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