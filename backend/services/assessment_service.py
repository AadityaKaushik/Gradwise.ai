from database.assessment_queries import (
    create_assessment, get_assessments_by_offering,
    record_score, get_scores_by_assessment, get_scores_by_student
)
from database.offering_queries import get_offering_by_id
from database.enrollment_queries import get_enrollments_by_offering


def create_new_assessment(offering_id, assessment_type, title, max_marks, weightage, assessment_date=None):
    """Create an assessment with weightage validation."""
    # Validate the offering exists
    offering = get_offering_by_id(offering_id)
    if not offering:
        raise ValueError("Course offering not found")

    # Check total weightage doesn't exceed 100%
    existing = get_assessments_by_offering(offering_id)
    total_weightage = sum(a["weightage"] for a in existing)
    if total_weightage + weightage > 100:
        raise ValueError(
            f"Total weightage would be {total_weightage + weightage}%. "
            f"Available: {100 - total_weightage}%"
        )

    valid_types = {"QUIZ", "MIDTERM", "FINAL", "ASSIGNMENT", "PROJECT", "LAB", "PRESENTATION", "OTHER"}
    if assessment_type not in valid_types:
        raise ValueError(f"Invalid assessment type. Must be one of: {', '.join(valid_types)}")

    return create_assessment(offering_id, assessment_type, title, max_marks, weightage, assessment_date)


def list_assessments(offering_id):
    return get_assessments_by_offering(offering_id)


def record_student_score(assessment_id, student_user_id, marks):
    """Record a score with marks validation."""
    from database.assessment_queries import get_assessments_by_offering
    from database.connection import get_connection, return_connection

    # Get the assessment to check max_marks
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT max_marks, offering_id FROM v3.assessments WHERE assessment_id = %s
        """, (assessment_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("Assessment not found")

        max_marks, offering_id = row

        if marks > max_marks:
            raise ValueError(f"Marks ({marks}) cannot exceed max marks ({max_marks})")

        # Verify student is enrolled in this offering
        cursor.execute("""
            SELECT enrollment_id FROM v3.enrollments
            WHERE student_user_id = %s AND offering_id = %s AND status = 'ENROLLED'
        """, (student_user_id, offering_id))
        if not cursor.fetchone():
            raise ValueError("Student is not actively enrolled in this offering")

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)

    return record_score(assessment_id, student_user_id, marks)


def list_scores_for_assessment(assessment_id):
    return get_scores_by_assessment(assessment_id)


def get_student_performance(student_user_id, offering_id):
    """Get all scores for a student in an offering, with weighted percentages."""
    scores = get_scores_by_student(student_user_id, offering_id)

    total_weighted = 0
    total_weightage = 0

    for s in scores:
        if s["marks"] is not None:
            percentage = (s["marks"] / s["max_marks"]) * 100
            s["percentage"] = round(percentage, 2)
            s["weighted_score"] = round(percentage * s["weightage"] / 100, 2)
            total_weighted += s["weighted_score"]
            total_weightage += s["weightage"]
        else:
            s["percentage"] = None
            s["weighted_score"] = None

    return {
        "scores": scores,
        "total_weighted_score": round(total_weighted, 2),
        "weightage_covered": total_weightage,
    }
