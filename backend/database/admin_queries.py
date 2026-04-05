from database.connection import get_connection, return_connection


def view_perms(org_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, role, status
            FROM v3.organization_memberships
            WHERE organization_id = %s
            ORDER BY
                CASE role
                    WHEN 'ADMIN' THEN 1
                    WHEN 'FACULTY' THEN 2
                    WHEN 'STUDENT' THEN 3
                    WHEN 'PENDING' THEN 4
                    ELSE 5
                END
        """, (org_id,))

        result = cursor.fetchall()
        return [
            {"user_id": row[0], "role": row[1], "status": row[2]}
            for row in result
        ]

    except Exception as e:
        raise RuntimeError("Failed to fetch organization permissions")

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)
