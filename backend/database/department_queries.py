from database.connection import get_connection, return_connection
import psycopg2

def create_department(org_id, name, code):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO v2.departments (organization_id, name, code)
            VALUES (%s, %s, %s)
            ON CONFLICT (organization_id, name) DO NOTHING
            RETURNING department_id         
        """, (org_id, name, code))

        row = cursor.fetchone()
        if not row:
            raise ValueError("Department with same name or code already exists")

        department_id = row[0]
        conn.commit()

        return {"department_id": department_id,
            "message": "Department created successfully"
        }

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)