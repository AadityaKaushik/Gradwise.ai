from database.connection import get_connection, return_connection
import psycopg2


def create_offering(org_id, course_id, faculty_user_id, period_id, section="A"):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO v3.course_offerings
                (organization_id, course_id, faculty_user_id, period_id, section)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING offering_id
        """, (org_id, course_id, faculty_user_id, period_id, section))

        row = cursor.fetchone()
        if not row:
            raise ValueError("Failed to create course offering")

        offering_id = row[0]
        conn.commit()

        return {
            "offering_id": offering_id,
            "message": "Course offering created successfully"
        }

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise ValueError("This course is already offered in this period and section")

    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        raise ValueError("Invalid course, faculty, or period reference")

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_offerings_by_period(org_id, period_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT co.offering_id, co.section,
                   c.course_id, c.course_code, c.course_name, c.credits,
                   f.user_id AS faculty_user_id, u.email AS faculty_email,
                   f.employee_code
            FROM v3.course_offerings co
            JOIN v3.courses c ON c.course_id = co.course_id
            JOIN v3.faculty f ON f.user_id = co.faculty_user_id
            JOIN v3.users u ON u.user_id = f.user_id
            WHERE co.organization_id = %s AND co.period_id = %s
            ORDER BY c.course_code, co.section
        """, (org_id, period_id))

        rows = cursor.fetchall()
        return [
            {
                "offering_id": r[0],
                "section": r[1],
                "course_id": r[2],
                "course_code": r[3],
                "course_name": r[4],
                "credits": r[5],
                "faculty_user_id": r[6],
                "faculty_email": r[7],
                "employee_code": r[8],
            }
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_offerings_by_faculty(faculty_user_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT co.offering_id, co.section,
                   c.course_code, c.course_name,
                   ap.label AS period_label
            FROM v3.course_offerings co
            JOIN v3.courses c ON c.course_id = co.course_id
            JOIN v3.academic_periods ap ON ap.period_id = co.period_id
            WHERE co.faculty_user_id = %s
            ORDER BY ap.start_date DESC, c.course_code
        """, (faculty_user_id,))

        rows = cursor.fetchall()
        return [
            {
                "offering_id": r[0],
                "section": r[1],
                "course_code": r[2],
                "course_name": r[3],
                "period_label": r[4],
            }
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_offering_by_id(offering_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT co.offering_id, co.organization_id, co.section,
                   c.course_id, c.course_code, c.course_name, c.credits,
                   f.user_id AS faculty_user_id, u.email AS faculty_email,
                   ap.period_id, ap.label AS period_label
            FROM v3.course_offerings co
            JOIN v3.courses c ON c.course_id = co.course_id
            JOIN v3.faculty f ON f.user_id = co.faculty_user_id
            JOIN v3.users u ON u.user_id = f.user_id
            JOIN v3.academic_periods ap ON ap.period_id = co.period_id
            WHERE co.offering_id = %s
        """, (offering_id,))

        row = cursor.fetchone()
        if not row:
            return None

        return {
            "offering_id": row[0],
            "organization_id": row[1],
            "section": row[2],
            "course_id": row[3],
            "course_code": row[4],
            "course_name": row[5],
            "credits": row[6],
            "faculty_user_id": row[7],
            "faculty_email": row[8],
            "period_id": row[9],
            "period_label": row[10],
        }

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)
