from database.connection import get_connection, return_connection
import psycopg2


def create_program(org_id, department_id, name, level, duration_years):
    """Create a program. org_id is required for tenant isolation (denormalized)."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO v3.programs (organization_id, department_id, name, level, duration_years)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (department_id, name) DO NOTHING
            RETURNING program_id
        """, (org_id, department_id, name, level, duration_years))

        row = cursor.fetchone()
        if not row:
            raise ValueError("This program already exists")

        program_id = row[0]
        conn.commit()

        return {
            "program_id": program_id,
            "message": "Program created successfully"
        }

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_programs_by_department(department_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT program_id, name, level, duration_years
            FROM v3.programs
            WHERE department_id = %s
            ORDER BY name
        """, (department_id,))

        rows = cursor.fetchall()
        return [
            {
                "program_id": r[0],
                "name": r[1],
                "level": r[2],
                "duration_years": r[3],
            }
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_programs_by_org(org_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.program_id, p.name, p.level, p.duration_years,
                   d.name AS department_name
            FROM v3.programs p
            JOIN v3.departments d ON d.department_id = p.department_id
            WHERE p.organization_id = %s
            ORDER BY d.name, p.name
        """, (org_id,))

        rows = cursor.fetchall()
        return [
            {
                "program_id": r[0],
                "name": r[1],
                "level": r[2],
                "duration_years": r[3],
                "department_name": r[4],
            }
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_program_by_id(program_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.program_id, p.organization_id, p.department_id,
                   p.name, p.level, p.duration_years
            FROM v3.programs p
            WHERE p.program_id = %s
        """, (program_id,))

        row = cursor.fetchone()
        if not row:
            return None

        return {
            "program_id": row[0],
            "organization_id": row[1],
            "department_id": row[2],
            "name": row[3],
            "level": row[4],
            "duration_years": row[5],
        }

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)