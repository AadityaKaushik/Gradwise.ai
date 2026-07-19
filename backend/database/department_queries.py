from database.connection import get_connection, return_connection
import psycopg2


def create_department(org_id, name, code):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO v3.departments (organization_id, name, code)
            VALUES (%s, %s, %s)
            ON CONFLICT (organization_id, name) DO NOTHING
            RETURNING department_id
        """, (org_id, name, code))

        row = cursor.fetchone()
        if not row:
            raise ValueError("Department with same name or code already exists")

        department_id = row[0]
        conn.commit()

        return {
            "department_id": department_id,
            "message": "Department created successfully"
        }

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_departments_by_org(org_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT department_id, name, code
            FROM v3.departments
            WHERE organization_id = %s
            ORDER BY name
        """, (org_id,))

        rows = cursor.fetchall()
        return [
            {"department_id": r[0], "name": r[1], "code": r[2]}
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_department_by_id(department_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT department_id, organization_id, name, code
            FROM v3.departments
            WHERE department_id = %s
        """, (department_id,))

        row = cursor.fetchone()
        if not row:
            return None

        return {
            "department_id": row[0],
            "organization_id": row[1],
            "name": row[2],
            "code": row[3],
        }

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)