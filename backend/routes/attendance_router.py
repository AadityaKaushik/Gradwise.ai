from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from Utils.security import get_current_user
from services.attendance_service import (
    create_attendance_session, list_sessions,
    mark_attendance, bulk_mark_attendance,
    get_session_attendance, get_attendance_report
)

router = APIRouter(tags=["Attendance"])


# ── Request / Response Models ────────────────────────────────────────

class SessionRequest(BaseModel):
    session_date: str
    topic: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: int
    message: str

class SessionListItem(BaseModel):
    session_id: int
    session_date: str
    topic: Optional[str] = None

class AttendanceRecord(BaseModel):
    student_user_id: int
    status: str

class SingleAttendanceRequest(BaseModel):
    student_user_id: int
    status: str

class BulkAttendanceRequest(BaseModel):
    records: List[AttendanceRecord]

class AttendanceResponse(BaseModel):
    record_id: Optional[int] = None
    count: Optional[int] = None
    message: str

class AttendanceListItem(BaseModel):
    record_id: int
    student_user_id: int
    status: str
    roll_no: str
    email: str

class AttendanceSummary(BaseModel):
    student_user_id: int
    offering_id: int
    total_sessions: int
    present: int
    late: int
    absent: int
    excused: int
    attendance_percentage: float


# ── Sessions ─────────────────────────────────────────────────────────

@router.post("/offerings/{offering_id}/sessions",
             response_model=SessionResponse,
             status_code=status.HTTP_201_CREATED)
def create_session(offering_id: int, data: SessionRequest,
                   current_user=Depends(get_current_user)):
    try:
        return create_attendance_session(offering_id, data.session_date, data.topic)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/offerings/{offering_id}/sessions",
            response_model=List[SessionListItem])
def get_sessions(offering_id: int,
                 current_user=Depends(get_current_user)):
    return list_sessions(offering_id)


# ── Attendance ───────────────────────────────────────────────────────

@router.post("/sessions/{session_id}/attendance",
             response_model=AttendanceResponse,
             status_code=status.HTTP_201_CREATED)
def record_attendance(session_id: int, data: SingleAttendanceRequest,
                      current_user=Depends(get_current_user)):
    try:
        return mark_attendance(session_id, data.student_user_id, data.status.upper())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/sessions/{session_id}/attendance/bulk",
             response_model=AttendanceResponse,
             status_code=status.HTTP_201_CREATED)
def record_bulk_attendance(session_id: int, data: BulkAttendanceRequest,
                           current_user=Depends(get_current_user)):
    try:
        records = [{"student_user_id": r.student_user_id, "status": r.status.upper()}
                   for r in data.records]
        return bulk_mark_attendance(session_id, records)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/sessions/{session_id}/attendance",
            response_model=List[AttendanceListItem])
def get_attendance(session_id: int,
                   current_user=Depends(get_current_user)):
    return get_session_attendance(session_id)


@router.get("/students/{user_id}/attendance/{offering_id}",
            response_model=AttendanceSummary)
def get_student_attendance(user_id: int, offering_id: int,
                           current_user=Depends(get_current_user)):
    return get_attendance_report(user_id, offering_id)
