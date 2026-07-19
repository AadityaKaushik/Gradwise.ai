from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from Utils.security import require_org_admin, require_org_member, get_current_user
from services.teaching_service import (
    create_course_offering, list_offerings,
    enroll_student_in_offering, list_enrollments_for_offering,
    list_enrollments_for_student, change_enrollment_status
)

router = APIRouter(tags=["Teaching"])


# ── Request / Response Models ────────────────────────────────────────

class OfferingRequest(BaseModel):
    course_id: int
    faculty_user_id: int
    period_id: int
    section: str = "A"

class OfferingResponse(BaseModel):
    offering_id: int
    message: str

class OfferingListItem(BaseModel):
    offering_id: int
    section: str
    course_id: int
    course_code: str
    course_name: str
    credits: int
    faculty_user_id: int
    faculty_email: str
    employee_code: str

class EnrollRequest(BaseModel):
    student_user_id: int

class EnrollResponse(BaseModel):
    enrollment_id: int
    message: str

class EnrollmentListItem(BaseModel):
    enrollment_id: int
    student_user_id: int
    status: str
    roll_no: str
    email: str

class StudentEnrollmentItem(BaseModel):
    enrollment_id: int
    offering_id: int
    status: str
    course_code: str
    course_name: str
    credits: int
    period_label: str
    section: str
    faculty_user_id: int
    faculty_email: str

class EnrollmentStatusRequest(BaseModel):
    status: str

class EnrollmentStatusResponse(BaseModel):
    enrollment_id: int
    status: str
    message: str


# ── Course Offerings ─────────────────────────────────────────────────

@router.post("/organization/{org_id}/offerings",
             response_model=OfferingResponse,
             status_code=status.HTTP_201_CREATED)
def create_offering(org_id: int, data: OfferingRequest,
                    current_user=Depends(require_org_admin)):
    try:
        return create_course_offering(org_id, data.course_id, data.faculty_user_id,
                                      data.period_id, data.section)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/organization/{org_id}/offerings",
            response_model=List[OfferingListItem])
def get_offerings(org_id: int, period_id: int,
                  current_user=Depends(require_org_member)):
    return list_offerings(org_id, period_id)


# ── Enrollments ──────────────────────────────────────────────────────

@router.post("/offerings/{offering_id}/enrollments",
             response_model=EnrollResponse,
             status_code=status.HTTP_201_CREATED)
def enroll_student(offering_id: int, data: EnrollRequest,
                   current_user=Depends(get_current_user)):
    try:
        return enroll_student_in_offering(data.student_user_id, offering_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/offerings/{offering_id}/enrollments",
            response_model=List[EnrollmentListItem])
def get_enrollments(offering_id: int,
                    current_user=Depends(get_current_user)):
    return list_enrollments_for_offering(offering_id)


@router.get("/students/{user_id}/enrollments",
            response_model=List[StudentEnrollmentItem])
def get_student_enrollments(user_id: int,
                            current_user=Depends(get_current_user)):
    return list_enrollments_for_student(user_id)


@router.patch("/enrollments/{enrollment_id}/status",
              response_model=EnrollmentStatusResponse)
def update_enrollment(enrollment_id: int, data: EnrollmentStatusRequest,
                      current_user=Depends(get_current_user)):
    try:
        return change_enrollment_status(enrollment_id, data.status.upper())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
