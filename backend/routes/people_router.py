from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from Utils.security import require_org_admin, require_org_member, get_current_user
from services.people_service import register_student, register_faculty, list_students, list_faculty, get_my_context

router = APIRouter(tags=["People"])


# ── Request / Response Models ────────────────────────────────────────

class MyContextResponse(BaseModel):
    user_id: int
    role: str
    department_id: Optional[int] = None
    program_id: Optional[int] = None

class StudentRegisterRequest(BaseModel):
    user_id: int
    program_id: int
    roll_no: str
    admission_year: int

class StudentRegisterResponse(BaseModel):
    user_id: int
    message: str

class StudentListItem(BaseModel):
    user_id: int
    roll_no: str
    admission_year: int
    academic_status: str
    email: str
    program_name: str

class FacultyRegisterRequest(BaseModel):
    user_id: int
    employee_code: str
    department_id: int
    designation: Optional[str] = None
    joining_date: Optional[str] = None

class FacultyRegisterResponse(BaseModel):
    user_id: int
    message: str

class FacultyListItem(BaseModel):
    user_id: int
    employee_code: str
    designation: Optional[str] = None
    employment_status: str
    email: str
    department_name: str


# ── Students ─────────────────────────────────────────────────────────

@router.post("/organization/{org_id}/students",
             response_model=StudentRegisterResponse,
             status_code=status.HTTP_201_CREATED)
def create_student(org_id: int, data: StudentRegisterRequest,
                   current_user=Depends(require_org_admin)):
    try:
        return register_student(data.user_id, org_id, data.program_id,
                                data.roll_no, data.admission_year)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/organization/{org_id}/students",
            response_model=List[StudentListItem])
def get_students(org_id: int, current_user=Depends(require_org_member)):
    return list_students(org_id)


# ── Faculty ──────────────────────────────────────────────────────────

@router.post("/organization/{org_id}/faculty",
             response_model=FacultyRegisterResponse,
             status_code=status.HTTP_201_CREATED)
def create_faculty(org_id: int, data: FacultyRegisterRequest,
                   current_user=Depends(require_org_admin)):
    try:
        return register_faculty(data.user_id, org_id, data.employee_code,
                                data.department_id, data.designation, data.joining_date)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/organization/{org_id}/faculty",
            response_model=List[FacultyListItem])
def get_faculty(org_id: int, current_user=Depends(require_org_member)):
    return list_faculty(org_id)


# ── Context ──────────────────────────────────────────────────────────

@router.get("/organization/{org_id}/me/context",
            response_model=MyContextResponse)
def get_user_context(org_id: int, current_user=Depends(get_current_user)):
    try:
        return get_my_context(current_user["user_id"], org_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
