from database.connection import get_connection


def create_membership(user_id, org_id, role):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO v2.organization_memberships(user_id, organization_id, role)
            VALUES (%s, %s, %s)
            returning membership_id
        """
        cursor.execute(query, (user_id, org_id, role))
        membership_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        return membership_id
    finally:
        conn.close()