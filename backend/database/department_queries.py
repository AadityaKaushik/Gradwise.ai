from database.connection import get_connection

def create_department(org_id, name, code):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT department_id 
            FROM v2.departments 
            WHERE organization_id = %s 
              AND (name = %s OR code = %s)
        """, (org_id, name, code))

        if cursor.fetchone():
            raise ValueError("Department with same name or code already exists")

        cursor.execute("""
            INSERT INTO v2.departments (organization_id, name, code)
            VALUES (%s, %s, %s)
            RETURNING department_id         
        """, (org_id, name, code))

        department_id = cursor.fetchone()[0]
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
        conn.close()