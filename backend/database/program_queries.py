from database.connection import get_connection

def create_program(department_id, name, level, duration_years):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM v2.programs WHERE department_id = %s AND name = %s", (department_id, name))
        result = cursor.fetchone()

        if result:
            raise ValueError("This program already exists")
        
        cursor.execute("INSERT INTO v2.programs (department_id, name, level, duration_years)VALUES (%s, %s, %s, %s) RETURNING program_id", (department_id, name, level, duration_years))

        program_id = cursor.fetchone()[0]

        conn.commit()
        return program_id

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        conn.close()