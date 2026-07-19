from database.connection import get_connection, return_connection
import psycopg2


def create_course(org_id, course_code, course_name, credits):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO v3.courses (organization_id, course_code, course_name, credits)
            VALUES (%s, %s, %s, %s)
            RETURNING course_id
        """, (org_id, course_code, course_name, credits))

        row = cursor.fetchone()
        if not row:
            raise ValueError("Failed to create course")

        course_id = row[0]
        conn.commit()

        return {
            "course_id": course_id,
            "message": "Course created successfully"
        }

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise ValueError("A course with this code already exists in this organization")

    except psycopg2.errors.CheckViolation:
        conn.rollback()
        raise ValueError("Credits must be between 1 and 20")

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_courses_by_org(org_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT course_id, course_code, course_name, credits
            FROM v3.courses
            WHERE organization_id = %s
            ORDER BY course_code
        """, (org_id,))

        rows = cursor.fetchall()
        return [
            {
                "course_id": r[0],
                "course_code": r[1],
                "course_name": r[2],
                "credits": r[3],
            }
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_course_by_id(course_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT course_id, organization_id, course_code, course_name, credits
            FROM v3.courses
            WHERE course_id = %s
        """, (course_id,))

        row = cursor.fetchone()
        if not row:
            return None

        return {
            "course_id": row[0],
            "organization_id": row[1],
            "course_code": row[2],
            "course_name": row[3],
            "credits": row[4],
        }

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)
