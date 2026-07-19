from database.attendance_queries import (
    create_session, get_sessions_by_offering,
    record_attendance, bulk_record_attendance,
    get_attendance_by_session, get_student_attendance_summary
)
from database.offering_queries import get_offering_by_id


def create_attendance_session(offering_id, session_date, topic=None):
    """Create an attendance session with offering validation."""
    offering = get_offering_by_id(offering_id)
    if not offering:
        raise ValueError("Course offering not found")

    return create_session(offering_id, session_date, topic)


def list_sessions(offering_id):
    return get_sessions_by_offering(offering_id)


def mark_attendance(session_id, student_user_id, status):
    """Record single attendance with status validation."""
    valid_statuses = {"PRESENT", "ABSENT", "LATE", "EXCUSED"}
    if status not in valid_statuses:
        raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

    return record_attendance(session_id, student_user_id, status)


def bulk_mark_attendance(session_id, records):
    """
    Record attendance for multiple students.
    records: list of dicts with 'student_user_id' and 'status'.
    """
    valid_statuses = {"PRESENT", "ABSENT", "LATE", "EXCUSED"}
    for r in records:
        if r.get("status") not in valid_statuses:
            raise ValueError(
                f"Invalid status '{r.get('status')}' for student {r.get('student_user_id')}. "
                f"Must be one of: {', '.join(valid_statuses)}"
            )

    return bulk_record_attendance(session_id, records)


def get_session_attendance(session_id):
    return get_attendance_by_session(session_id)


def get_attendance_report(student_user_id, offering_id):
    return get_student_attendance_summary(student_user_id, offering_id)
