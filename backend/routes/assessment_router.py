from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from Utils.security import get_current_user
from services.assessment_service import (
    create_new_assessment, list_assessments,
    record_student_score, list_scores_for_assessment,
    get_student_performance
)

router = APIRouter(tags=["Assessments"])


# ── Request / Response Models ────────────────────────────────────────

class AssessmentRequest(BaseModel):
    type: str
    title: Optional[str] = None
    max_marks: int
    weightage: float
    assessment_date: Optional[str] = None

class AssessmentResponse(BaseModel):
    assessment_id: int
    message: str

class AssessmentListItem(BaseModel):
    assessment_id: int
    type: str
    title: Optional[str] = None
    max_marks: int
    weightage: float
    assessment_date: Optional[str] = None

class ScoreRequest(BaseModel):
    student_user_id: int
    marks: float

class ScoreResponse(BaseModel):
    score_id: int
    message: str

class ScoreListItem(BaseModel):
    score_id: int
    student_user_id: int
    marks: float
    roll_no: str
    email: str

class PerformanceScoreItem(BaseModel):
    assessment_id: int
    type: str
    title: Optional[str] = None
    max_marks: int
    weightage: float
    marks: Optional[float] = None
    percentage: Optional[float] = None
    weighted_score: Optional[float] = None

class PerformanceResponse(BaseModel):
    scores: List[PerformanceScoreItem]
    total_weighted_score: float
    weightage_covered: float


# ── Assessments ──────────────────────────────────────────────────────

@router.post("/offerings/{offering_id}/assessments",
             response_model=AssessmentResponse,
             status_code=status.HTTP_201_CREATED)
def create_assessment(offering_id: int, data: AssessmentRequest,
                      current_user=Depends(get_current_user)):
    try:
        return create_new_assessment(offering_id, data.type.upper(), data.title,
                                     data.max_marks, data.weightage, data.assessment_date)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/offerings/{offering_id}/assessments",
            response_model=List[AssessmentListItem])
def get_assessments(offering_id: int,
                    current_user=Depends(get_current_user)):
    return list_assessments(offering_id)


# ── Scores ───────────────────────────────────────────────────────────

@router.post("/assessments/{assessment_id}/scores",
             response_model=ScoreResponse,
             status_code=status.HTTP_201_CREATED)
def record_score(assessment_id: int, data: ScoreRequest,
                 current_user=Depends(get_current_user)):
    try:
        return record_student_score(assessment_id, data.student_user_id, data.marks)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/assessments/{assessment_id}/scores",
            response_model=List[ScoreListItem])
def get_scores(assessment_id: int,
               current_user=Depends(get_current_user)):
    return list_scores_for_assessment(assessment_id)


@router.get("/students/{user_id}/performance/{offering_id}",
            response_model=PerformanceResponse)
def get_performance(user_id: int, offering_id: int,
                    current_user=Depends(get_current_user)):
    return get_student_performance(user_id, offering_id)
