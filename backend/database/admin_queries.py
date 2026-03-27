from database.connection import get_connection

def view_perms(org_id):
        conn = get_connection()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, role 
                FROM v2.organization_memberships 
                WHERE organization_id = %s
                ORDER BY 
                    CASE role
                        WHEN 'Admin' THEN 1
                        WHEN 'Faculty' THEN 2
                        WHEN 'Student' THEN 3
                        ELSE 4
                    END
            """, (org_id,))
            result = cursor.fetchall()

