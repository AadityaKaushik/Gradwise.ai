from database.student_queries import create_student, get_students_by_org, get_student_by_user_id
from database.faculty_queries import create_faculty, get_faculty_by_org, get_faculty_by_user_id
from database.membership_queries import get_user_role_in_org
from database.program_queries import get_program_by_id


def register_student(user_id, org_id, program_id, roll_no, admission_year):
    """Register a student profile. Promotes PENDING users to STUDENT."""
    role = get_user_role_in_org(user_id, org_id)
    if role not in ["STUDENT", "PENDING"]:
        raise ValueError(
            f"User must have STUDENT or PENDING membership role (current role: {role or 'not a member'})"
        )

    # Check if student profile already exists
    existing = get_student_by_user_id(user_id)
    if existing:
        raise ValueError("Student profile already exists for this user")

    if role == "PENDING":
        from database.admin_queries import update_membership_role
        update_membership_role(org_id, user_id, "STUDENT")

    return create_student(user_id, org_id, program_id, roll_no, admission_year)


def register_faculty(user_id, org_id, employee_code, department_id, designation=None, joining_date=None):
    """Register a faculty profile. Promotes PENDING users to FACULTY."""
    role = get_user_role_in_org(user_id, org_id)
    if role not in ["FACULTY", "PENDING"]:
        raise ValueError(
            f"User must have FACULTY or PENDING membership role (current role: {role or 'not a member'})"
        )

    # Check if faculty profile already exists
    existing = get_faculty_by_user_id(user_id)
    if existing:
        raise ValueError("Faculty profile already exists for this user")

    if role == "PENDING":
        from database.admin_queries import update_membership_role
        update_membership_role(org_id, user_id, "FACULTY")

    return create_faculty(user_id, org_id, employee_code, department_id, designation, joining_date)


def list_students(org_id):
    return get_students_by_org(org_id)


def list_faculty(org_id):
    return get_faculty_by_org(org_id)


def get_my_context(user_id, org_id):
    role = get_user_role_in_org(user_id, org_id)
    if not role:
        raise ValueError("User is not a member of this organization")

    context = {
        "user_id": user_id,
        "role": role,
        "department_id": None,
        "program_id": None
    }

    if role == "STUDENT":
        student = get_student_by_user_id(user_id)
        if student and student["organization_id"] == org_id:
            context["program_id"] = student["program_id"]
            # fetch department_id
            prog = get_program_by_id(student["program_id"])
            if prog:
                context["department_id"] = prog["department_id"]

    elif role == "FACULTY":
        faculty = get_faculty_by_user_id(user_id)
        if faculty and faculty["organization_id"] == org_id:
            context["department_id"] = faculty["home_department_id"]

    return context
