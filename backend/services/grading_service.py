from database.result_queries import (
    publish_result, get_result_by_enrollment,
    get_results_by_offering, get_results_by_student
)
from database.enrollment_queries import get_enrollments_by_student
from database.connection import get_connection, return_connection


def publish_final_result(enrollment_id, final_grade, grade_points):
    """Publish a final result with enrollment validation."""
    # Validate the enrollment exists and is in a valid state
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT status FROM v3.enrollments WHERE enrollment_id = %s
        """, (enrollment_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("Enrollment not found")

        status = row[0]
        if status not in ("ENROLLED", "COMPLETED"):
            raise ValueError(
                f"Cannot publish result for enrollment with status '{status}'. "
                f"Must be ENROLLED or COMPLETED"
            )
    finally:
        if cursor:
            cursor.close()
        return_connection(conn)

    return publish_result(enrollment_id, final_grade, grade_points)


def get_offering_results(offering_id):
    return get_results_by_offering(offering_id)


def get_student_transcript(student_user_id):
    """Returns all final results for a student with course details."""
    results = get_results_by_student(student_user_id)

    if not results:
        return {"results": [], "cgpa": None}

    # Compute CGPA (credit-weighted average of grade points)
    total_credits = 0
    total_weighted = 0
    for r in results:
        total_credits += r["credits"]
        total_weighted += r["grade_points"] * r["credits"]

    cgpa = round(total_weighted / total_credits, 2) if total_credits > 0 else 0

    return {
        "results": results,
        "total_credits": total_credits,
        "cgpa": cgpa,
    }
