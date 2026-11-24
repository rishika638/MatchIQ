from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.entities import RecommendationFeedback, Opportunity, User
from app.schemas.schemas import FeedbackCreate
from app.api.deps import get_current_user
from app.services.analytics_service import analytics_service

router = APIRouter()

@router.post("/")
def submit_feedback(
    payload: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if payload.feedback_type not in ["relevant", "not_relevant", "applied", "not_interested"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid feedback_type. Allowed: relevant, not_relevant, applied, not_interested"
        )

    opp = db.query(Opportunity).filter(Opportunity.id == payload.opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    fb = RecommendationFeedback(
        user_id=current_user.id,
        opportunity_id=payload.opportunity_id,
        feedback_type=payload.feedback_type,
        query_or_context=payload.query_or_context,
        notes=payload.notes,
        score_snapshot={"source": opp.source, "work_mode": opp.work_mode, "experience_level": opp.experience_level}
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)

    return {"status": "success", "message": "Feedback recorded successfully", "feedback_id": fb.id}

@router.get("/analytics")
def get_feedback_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return analytics_service.get_feedback_analytics(db, user_id=current_user.id)
