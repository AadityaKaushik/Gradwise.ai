from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from Utils.security import get_current_user
from services.grading_service import (
    publish_final_result, get_offering_results, get_student_transcript
)

router = APIRouter(tags=["Results"])


# ── Request / Response Models ────────────────────────────────────────

class ResultRequest(BaseModel):
    final_grade: str
    grade_points: float

class ResultResponse(BaseModel):
    enrollment_id: int
    message: str

class ResultListItem(BaseModel):
    enrollment_id: int
    final_grade: str
    grade_points: float
    published_at: Optional[str] = None
    roll_no: str
    email: str
    student_user_id: int

class TranscriptItem(BaseModel):
    enrollment_id: int
    final_grade: str
    grade_points: float
    published_at: Optional[str] = None
    course_code: str
    course_name: str
    credits: int
    period_label: str
    section: str

class TranscriptResponse(BaseModel):
    results: List[TranscriptItem]
    total_credits: Optional[int] = None
    cgpa: Optional[float] = None


# ── Results ──────────────────────────────────────────────────────────

@router.post("/enrollments/{enrollment_id}/result",
             response_model=ResultResponse,
             status_code=status.HTTP_201_CREATED)
def publish_result(enrollment_id: int, data: ResultRequest,
                   current_user=Depends(get_current_user)):
    try:
        return publish_final_result(enrollment_id, data.final_grade, data.grade_points)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/offerings/{offering_id}/results",
            response_model=List[ResultListItem])
def get_results(offering_id: int,
                current_user=Depends(get_current_user)):
    return get_offering_results(offering_id)


@router.get("/students/{user_id}/transcript",
            response_model=TranscriptResponse)
def get_transcript(user_id: int,
                   current_user=Depends(get_current_user)):
    return get_student_transcript(user_id)
