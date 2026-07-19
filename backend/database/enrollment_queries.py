from database.connection import get_connection, return_connection
import psycopg2


def enroll_student(student_user_id, offering_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO v3.enrollments (student_user_id, offering_id)
            VALUES (%s, %s)
            ON CONFLICT (student_user_id, offering_id) DO NOTHING
            RETURNING enrollment_id
        """, (student_user_id, offering_id))

        row = cursor.fetchone()
        if not row:
            raise ValueError("Student is already enrolled in this offering")

        enrollment_id = row[0]
        conn.commit()

        return {
            "enrollment_id": enrollment_id,
            "message": "Student enrolled successfully"
        }

    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        raise ValueError("Invalid student or course offering reference")

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_enrollments_by_offering(offering_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT e.enrollment_id, e.student_user_id, e.status,
                   s.roll_no, u.email
            FROM v3.enrollments e
            JOIN v3.students s ON s.user_id = e.student_user_id
            JOIN v3.users u ON u.user_id = s.user_id
            WHERE e.offering_id = %s
            ORDER BY s.roll_no
        """, (offering_id,))

        rows = cursor.fetchall()
        return [
            {
                "enrollment_id": r[0],
                "student_user_id": r[1],
                "status": r[2],
                "roll_no": r[3],
                "email": r[4],
            }
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_enrollments_by_student(student_user_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT e.enrollment_id, e.offering_id, e.status,
                   c.course_code, c.course_name, c.credits,
                   ap.label AS period_label, co.section,
                   f.user_id AS faculty_user_id, u.email AS faculty_email
            FROM v3.enrollments e
            JOIN v3.course_offerings co ON co.offering_id = e.offering_id
            JOIN v3.courses c ON c.course_id = co.course_id
            JOIN v3.academic_periods ap ON ap.period_id = co.period_id
            JOIN v3.faculty f ON f.user_id = co.faculty_user_id
            JOIN v3.users u ON u.user_id = f.user_id
            WHERE e.student_user_id = %s
            ORDER BY ap.start_date DESC, c.course_code
        """, (student_user_id,))

        rows = cursor.fetchall()
        return [
            {
                "enrollment_id": r[0],
                "offering_id": r[1],
                "status": r[2],
                "course_code": r[3],
                "course_name": r[4],
                "credits": r[5],
                "period_label": r[6],
                "section": r[7],
                "faculty_user_id": r[8],
                "faculty_email": r[9],
            }
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def update_enrollment_status(enrollment_id, new_status):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE v3.enrollments
            SET status = %s
            WHERE enrollment_id = %s
            RETURNING enrollment_id, status
        """, (new_status, enrollment_id))

        row = cursor.fetchone()
        if not row:
            raise ValueError("Enrollment not found")

        conn.commit()

        return {
            "enrollment_id": row[0],
            "status": row[1],
            "message": "Enrollment status updated successfully"
        }

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)
