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