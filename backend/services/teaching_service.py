from database.offering_queries import create_offering, get_offerings_by_period, get_offering_by_id
from database.enrollment_queries import (
    enroll_student, get_enrollments_by_offering, get_enrollments_by_student,
    update_enrollment_status
)
from database.faculty_queries import get_faculty_by_user_id
from database.student_queries import get_student_by_user_id
from database.course_queries import get_course_by_id


def create_course_offering(org_id, course_id, faculty_user_id, period_id, section="A"):
    """Create a course offering with validation."""
    # Validate faculty exists and belongs to org
    faculty = get_faculty_by_user_id(faculty_user_id)
    if not faculty:
        raise ValueError("Faculty profile not found")
    if faculty["organization_id"] != org_id:
        raise ValueError("Faculty does not belong to this organization")

    # Validate course belongs to org
    course = get_course_by_id(course_id)
    if not course:
        raise ValueError("Course not found")
    if course["organization_id"] != org_id:
        raise ValueError("Course does not belong to this organization")

    return create_offering(org_id, course_id, faculty_user_id, period_id, section)


def list_offerings(org_id, period_id):
    return get_offerings_by_period(org_id, period_id)


def enroll_student_in_offering(student_user_id, offering_id):
    """Enroll a student with validation."""
    student = get_student_by_user_id(student_user_id)
    if not student:
        raise ValueError("Student profile not found")

    offering = get_offering_by_id(offering_id)
    if not offering:
        raise ValueError("Course offering not found")

    # Verify student and offering belong to same org
    if student["organization_id"] != offering["organization_id"]:
        raise ValueError("Student and offering belong to different organizations")

    return enroll_student(student_user_id, offering_id)


def list_enrollments_for_offering(offering_id):
    return get_enrollments_by_offering(offering_id)


def list_enrollments_for_student(student_user_id):
    return get_enrollments_by_student(student_user_id)


def change_enrollment_status(enrollment_id, new_status):
    valid_statuses = {"ENROLLED", "DROPPED", "COMPLETED", "WITHDRAWN"}
    if new_status not in valid_statuses:
        raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    return update_enrollment_status(enrollment_id, new_status)
