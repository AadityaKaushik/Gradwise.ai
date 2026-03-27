from database.connection import get_connection


# def create_membership(user_id, org_id, role):
#     conn = get_connection()
#     try:
#         cursor = conn.cursor()
#         query = """
#             INSERT INTO v2.organization_memberships(user_id, organization_id, role)
#             VALUES (%s, %s, %s)
#             returning membership_id
#         """
#         cursor.execute(query, (user_id, org_id, role))
#         membership_id = cursor.fetchone()[0]
#         conn.commit()
#         cursor.close()
#         return membership_id
#     finally:
#         conn.close()

def create_membership(user_id, org_id, role):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT membership_id
            FROM v2.organization_memberships
            WHERE user_id = %s AND organization_id = %s
        """, (user_id, org_id))

        if cursor.fetchone():
            raise ValueError("User already in this organization")

        cursor.execute("""
            INSERT INTO v2.organization_memberships (user_id, organization_id, role)
            VALUES (%s, %s, %s)
            RETURNING membership_id
        """, (user_id, org_id, role))

        membership_id = cursor.fetchone()[0]
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
        conn.close()