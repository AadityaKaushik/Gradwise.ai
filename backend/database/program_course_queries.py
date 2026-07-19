from database.connection import get_connection, return_connection
import psycopg2


def map_course_to_program(program_id, course_id, semester, is_core=True):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO v3.program_courses (program_id, course_id, semester, is_core)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (program_id, course_id) DO NOTHING
        """, (program_id, course_id, semester, is_core))

        if cursor.rowcount == 0:
            raise ValueError("This course is already mapped to this program")

        conn.commit()

        return {
            "program_id": program_id,
            "course_id": course_id,
            "message": "Course mapped to program successfully"
        }

    except psycopg2.errors.CheckViolation:
        conn.rollback()
        raise ValueError("Semester must be > 0")

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_courses_for_program(program_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.course_id, c.course_code, c.course_name, c.credits,
                   pc.semester, pc.is_core
            FROM v3.program_courses pc
            JOIN v3.courses c ON c.course_id = pc.course_id
            WHERE pc.program_id = %s
            ORDER BY pc.semester, c.course_code
        """, (program_id,))

        rows = cursor.fetchall()
        return [
            {
                "course_id": r[0],
                "course_code": r[1],
                "course_name": r[2],
                "credits": r[3],
                "semester": r[4],
                "is_core": r[5],
            }
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def remove_course_from_program(program_id, course_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM v3.program_courses
            WHERE program_id = %s AND course_id = %s
        """, (program_id, course_id))

        if cursor.rowcount == 0:
            raise ValueError("This course is not mapped to this program")

        conn.commit()

        return {"message": "Course removed from program successfully"}

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)
