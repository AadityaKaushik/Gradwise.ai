from database.department_queries import create_department, get_departments_by_org, get_department_by_id
from database.program_queries import create_program, get_programs_by_org, get_programs_by_department
from database.course_queries import create_course, get_courses_by_org
from database.program_course_queries import map_course_to_program, get_courses_for_program, remove_course_from_program
from database.academic_period_queries import create_period, get_periods_by_org, set_current_period, get_current_period


def setup_department(org_id, name, code):
    return create_department(org_id, name, code)


def setup_program(org_id, department_id, name, level, duration_years):
    # Validate that the department belongs to this organization
    dept = get_department_by_id(department_id)
    if not dept:
        raise ValueError("Department not found")
    if dept["organization_id"] != org_id:
        raise ValueError("Department does not belong to this organization")

    return create_program(org_id, department_id, name, level, duration_years)


def setup_course(org_id, course_code, course_name, credits):
    return create_course(org_id, course_code, course_name, credits)


def map_course(org_id, program_id, course_id, semester, is_core=True):
    # Validate that the program belongs to this organization
    from database.program_queries import get_program_by_id
    from database.course_queries import get_course_by_id

    program = get_program_by_id(program_id)
    if not program:
        raise ValueError("Program not found")
    if program["organization_id"] != org_id:
        raise ValueError("Program does not belong to this organization")

    course = get_course_by_id(course_id)
    if not course:
        raise ValueError("Course not found")
    if course["organization_id"] != org_id:
        raise ValueError("Course does not belong to this organization")

    return map_course_to_program(program_id, course_id, semester, is_core)


def unmap_course(program_id, course_id):
    return remove_course_from_program(program_id, course_id)


def setup_period(org_id, label, semester_number, academic_year, start_date, end_date):
    return create_period(org_id, label, semester_number, academic_year, start_date, end_date)


def activate_period(org_id, period_id):
    return set_current_period(org_id, period_id)


def list_departments(org_id):
    return get_departments_by_org(org_id)


def list_programs(org_id):
    return get_programs_by_org(org_id)


def list_courses(org_id):
    return get_courses_by_org(org_id)


def list_program_courses(program_id):
    return get_courses_for_program(program_id)


def list_periods(org_id):
    return get_periods_by_org(org_id)
