from database.connection import get_connection, return_connection
import psycopg2


def publish_result(enrollment_id, final_grade, grade_points):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO v3.final_results (enrollment_id, final_grade, grade_points, published_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (enrollment_id)
                DO UPDATE SET final_grade = EXCLUDED.final_grade,
                              grade_points = EXCLUDED.grade_points,
                              published_at = NOW()
            RETURNING enrollment_id
        """, (enrollment_id, final_grade, grade_points))

        row = cursor.fetchone()
        conn.commit()

        return {
            "enrollment_id": row[0],
            "message": "Result published successfully"
        }

    except psycopg2.errors.CheckViolation:
        conn.rollback()
        raise ValueError("Grade points must be between 0 and 10")

    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        raise ValueError("Invalid enrollment reference")

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_result_by_enrollment(enrollment_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT fr.enrollment_id, fr.final_grade, fr.grade_points, fr.published_at
            FROM v3.final_results fr
            WHERE fr.enrollment_id = %s
        """, (enrollment_id,))

        row = cursor.fetchone()
        if not row:
            return None

        return {
            "enrollment_id": row[0],
            "final_grade": row[1],
            "grade_points": float(row[2]),
            "published_at": str(row[3]) if row[3] else None,
        }

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_results_by_offering(offering_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT fr.enrollment_id, fr.final_grade, fr.grade_points, fr.published_at,
                   s.roll_no, u.email, s.user_id AS student_user_id
            FROM v3.final_results fr
            JOIN v3.enrollments e ON e.enrollment_id = fr.enrollment_id
            JOIN v3.students s ON s.user_id = e.student_user_id
            JOIN v3.users u ON u.user_id = s.user_id
            WHERE e.offering_id = %s
            ORDER BY s.roll_no
        """, (offering_id,))

        rows = cursor.fetchall()
        return [
            {
                "enrollment_id": r[0],
                "final_grade": r[1],
                "grade_points": float(r[2]),
                "published_at": str(r[3]) if r[3] else None,
                "roll_no": r[4],
                "email": r[5],
                "student_user_id": r[6],
            }
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_results_by_student(student_user_id):
    """Full transcript: all final results for a student across all enrollments."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT fr.enrollment_id, fr.final_grade, fr.grade_points, fr.published_at,
                   c.course_code, c.course_name, c.credits,
                   ap.label AS period_label, co.section
            FROM v3.final_results fr
            JOIN v3.enrollments e ON e.enrollment_id = fr.enrollment_id
            JOIN v3.course_offerings co ON co.offering_id = e.offering_id
            JOIN v3.courses c ON c.course_id = co.course_id
            JOIN v3.academic_periods ap ON ap.period_id = co.period_id
            WHERE e.student_user_id = %s
            ORDER BY ap.start_date DESC, c.course_code
        """, (student_user_id,))

        rows = cursor.fetchall()
        return [
            {
                "enrollment_id": r[0],
                "final_grade": r[1],
                "grade_points": float(r[2]),
                "published_at": str(r[3]) if r[3] else None,
                "course_code": r[4],
                "course_name": r[5],
                "credits": r[6],
                "period_label": r[7],
                "section": r[8],
            }
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)
