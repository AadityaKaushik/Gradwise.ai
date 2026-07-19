from database.connection import get_connection, return_connection
import psycopg2


def create_assessment(offering_id, assessment_type, title, max_marks, weightage, assessment_date=None):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO v3.assessments
                (offering_id, type, title, max_marks, weightage, assessment_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING assessment_id
        """, (offering_id, assessment_type, title, max_marks, weightage, assessment_date))

        row = cursor.fetchone()
        if not row:
            raise ValueError("Failed to create assessment")

        assessment_id = row[0]
        conn.commit()

        return {
            "assessment_id": assessment_id,
            "message": "Assessment created successfully"
        }

    except psycopg2.errors.CheckViolation:
        conn.rollback()
        raise ValueError("Invalid marks or weightage (marks > 0, weightage between 0 and 100)")

    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        raise ValueError("Invalid course offering reference")

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_assessments_by_offering(offering_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT assessment_id, type, title, max_marks, weightage, assessment_date
            FROM v3.assessments
            WHERE offering_id = %s
            ORDER BY assessment_date NULLS LAST, title
        """, (offering_id,))

        rows = cursor.fetchall()
        return [
            {
                "assessment_id": r[0],
                "type": r[1],
                "title": r[2],
                "max_marks": r[3],
                "weightage": float(r[4]),
                "assessment_date": str(r[5]) if r[5] else None,
            }
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def record_score(assessment_id, student_user_id, marks):
    """Insert or update a student's score for an assessment."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO v3.assessment_scores (assessment_id, student_user_id, marks)
            VALUES (%s, %s, %s)
            ON CONFLICT (assessment_id, student_user_id)
                DO UPDATE SET marks = EXCLUDED.marks
            RETURNING score_id
        """, (assessment_id, student_user_id, marks))

        row = cursor.fetchone()
        score_id = row[0]
        conn.commit()

        return {
            "score_id": score_id,
            "message": "Score recorded successfully"
        }

    except psycopg2.errors.CheckViolation:
        conn.rollback()
        raise ValueError("Marks must be >= 0")

    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        raise ValueError("Invalid assessment or student reference")

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_scores_by_assessment(assessment_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT sc.score_id, sc.student_user_id, sc.marks,
                   s.roll_no, u.email
            FROM v3.assessment_scores sc
            JOIN v3.students s ON s.user_id = sc.student_user_id
            JOIN v3.users u ON u.user_id = s.user_id
            WHERE sc.assessment_id = %s
            ORDER BY s.roll_no
        """, (assessment_id,))

        rows = cursor.fetchall()
        return [
            {
                "score_id": r[0],
                "student_user_id": r[1],
                "marks": float(r[2]),
                "roll_no": r[3],
                "email": r[4],
            }
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_scores_by_student(student_user_id, offering_id):
    """Get all of a student's scores for assessments in a specific offering."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.assessment_id, a.type, a.title, a.max_marks, a.weightage,
                   sc.marks, sc.score_id
            FROM v3.assessments a
            LEFT JOIN v3.assessment_scores sc
                ON sc.assessment_id = a.assessment_id
                AND sc.student_user_id = %s
            WHERE a.offering_id = %s
            ORDER BY a.assessment_date NULLS LAST, a.title
        """, (student_user_id, offering_id))

        rows = cursor.fetchall()
        return [
            {
                "assessment_id": r[0],
                "type": r[1],
                "title": r[2],
                "max_marks": r[3],
                "weightage": float(r[4]),
                "marks": float(r[5]) if r[5] is not None else None,
                "score_id": r[6],
            }
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)
