from database.connection import get_connection, return_connection
import psycopg2

def create_program(department_id, name, level, duration_years):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO v2.programs (department_id, name, level, duration_years)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (department_id, name) DO NOTHING
            RETURNING program_id
        """, (department_id, name, level, duration_years))

        row = cursor.fetchone()
        if not row:
            raise ValueError("This program already exists")

        program_id = row[0]
        conn.commit()
        return program_id

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)