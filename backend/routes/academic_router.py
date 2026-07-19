from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from Utils.security import require_org_admin, require_org_member
from services.academic_setup_service import (
    setup_department, setup_program, setup_course,
    map_course, unmap_course, setup_period, activate_period,
    list_departments, list_programs, list_courses, list_program_courses, list_periods
)

router = APIRouter(tags=["Academic Structure"])


# ── Request / Response Models ────────────────────────────────────────

class DepartmentRequest(BaseModel):
    name: str
    code: Optional[str] = None

class DepartmentResponse(BaseModel):
    department_id: int
    message: str

class DepartmentListItem(BaseModel):
    department_id: int
    name: str
    code: Optional[str] = None

class ProgramRequest(BaseModel):
    department_id: int
    name: str
    level: str
    duration_years: int

class ProgramResponse(BaseModel):
    program_id: int
    message: str

class ProgramListItem(BaseModel):
    program_id: int
    name: str
    level: str
    duration_years: int
    department_name: Optional[str] = None

class CourseRequest(BaseModel):
    course_code: str
    course_name: str
    credits: int

class CourseResponse(BaseModel):
    course_id: int
    message: str

class CourseListItem(BaseModel):
    course_id: int
    course_code: str
    course_name: str
    credits: int

class ProgramCourseMapRequest(BaseModel):
    course_id: int
    semester: int
    is_core: bool = True

class ProgramCourseMapResponse(BaseModel):
    program_id: int
    course_id: int
    message: str

class ProgramCourseListItem(BaseModel):
    course_id: int
    course_code: str
    course_name: str
    credits: int
    semester: int
    is_core: bool

class PeriodRequest(BaseModel):
    label: str
    semester_number: int
    academic_year: int
    start_date: str
    end_date: str

class PeriodResponse(BaseModel):
    period_id: int
    message: str

class PeriodListItem(BaseModel):
    period_id: int
    label: str
    semester_number: int
    academic_year: str
    start_date: str
    end_date: str
    is_current: bool


# ── Departments ──────────────────────────────────────────────────────

@router.post("/organization/{org_id}/departments",
             response_model=DepartmentResponse,
             status_code=status.HTTP_201_CREATED)
def create_department(org_id: int, data: DepartmentRequest,
                      current_user=Depends(require_org_admin)):
    try:
        return setup_department(org_id, data.name, data.code)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/organization/{org_id}/departments",
            response_model=List[DepartmentListItem])
def get_departments(org_id: int, current_user=Depends(require_org_member)):
    return list_departments(org_id)


# ── Programs ─────────────────────────────────────────────────────────

@router.post("/organization/{org_id}/programs",
             response_model=ProgramResponse,
             status_code=status.HTTP_201_CREATED)
def create_program(org_id: int, data: ProgramRequest,
                   current_user=Depends(require_org_admin)):
    try:
        return setup_program(org_id, data.department_id, data.name,
                             data.level, data.duration_years)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/organization/{org_id}/programs",
            response_model=List[ProgramListItem])
def get_programs(org_id: int, current_user=Depends(require_org_member)):
    return list_programs(org_id)


# ── Courses ──────────────────────────────────────────────────────────

@router.post("/organization/{org_id}/courses",
             response_model=CourseResponse,
             status_code=status.HTTP_201_CREATED)
def create_course(org_id: int, data: CourseRequest,
                  current_user=Depends(require_org_admin)):
    try:
        return setup_course(org_id, data.course_code, data.course_name, data.credits)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/organization/{org_id}/courses",
            response_model=List[CourseListItem])
def get_courses(org_id: int, current_user=Depends(require_org_member)):
    return list_courses(org_id)


# ── Program ↔ Course Mapping ────────────────────────────────────────

@router.post("/programs/{program_id}/courses",
             response_model=ProgramCourseMapResponse,
             status_code=status.HTTP_201_CREATED)
def map_course_to_program(program_id: int, data: ProgramCourseMapRequest,
                          current_user=Depends(require_org_admin)):
    try:
        # We need the org_id for validation — extract from the program
        from database.program_queries import get_program_by_id
        program = get_program_by_id(program_id)
        if not program:
            raise ValueError("Program not found")
        return map_course(program["organization_id"], program_id,
                          data.course_id, data.semester, data.is_core)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/programs/{program_id}/courses",
            response_model=List[ProgramCourseListItem])
def get_program_courses(program_id: int,
                        current_user=Depends(require_org_member)):
    return list_program_courses(program_id)


@router.delete("/programs/{program_id}/courses/{course_id}",
               status_code=status.HTTP_200_OK)
def remove_program_course(program_id: int, course_id: int,
                          current_user=Depends(require_org_admin)):
    try:
        return unmap_course(program_id, course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ── Academic Periods ─────────────────────────────────────────────────

@router.post("/organization/{org_id}/periods",
             response_model=PeriodResponse,
             status_code=status.HTTP_201_CREATED)
def create_period(org_id: int, data: PeriodRequest,
                  current_user=Depends(require_org_admin)):
    try:
        return setup_period(org_id, data.label, data.semester_number,
                            data.academic_year, data.start_date, data.end_date)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/organization/{org_id}/periods",
            response_model=List[PeriodListItem])
def get_periods(org_id: int, current_user=Depends(require_org_member)):
    return list_periods(org_id)


@router.patch("/organization/{org_id}/periods/{period_id}/activate",
              response_model=PeriodResponse)
def activate_period_route(org_id: int, period_id: int,
                          current_user=Depends(require_org_admin)):
    try:
        return activate_period(org_id, period_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
