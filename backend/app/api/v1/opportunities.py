from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.core.database import get_db
from app.models.entities import Opportunity, CandidateProfile, SavedOpportunity, User
from app.api.deps import get_optional_user, get_current_user
from app.services.matching_service import matching_engine

router = APIRouter()

@router.get("/")
def list_opportunities(
    work_mode: Optional[str] = None,
    opportunity_type: Optional[str] = None,
    experience_level: Optional[str] = None,
    location: Optional[str] = None,
    skip: int = 0,
    limit: int = 25,
    db: Session = Depends(get_db)
):
    query = db.query(Opportunity).filter(Opportunity.status == "active")
    if work_mode:
        query = query.filter(Opportunity.work_mode == work_mode)
    if opportunity_type:
        query = query.filter(Opportunity.opportunity_type == opportunity_type)
    if experience_level:
        query = query.filter(Opportunity.experience_level == experience_level)
    if location:
        query = query.filter(Opportunity.location.ilike(f"%{location}%"))

    total = query.count()
    items = query.order_by(Opportunity.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items
    }

@router.get("/{opportunity_id}")
def get_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    compatibility = None
    saved_status = None
    if current_user:
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
        if profile:
            compatibility = matching_engine.calculate_compatibility(opp, profile)
        saved = db.query(SavedOpportunity).filter(
            SavedOpportunity.user_id == current_user.id,
            SavedOpportunity.opportunity_id == opp.id
        ).first()
        if saved:
            saved_status = saved.status

    return {
        "opportunity": opp,
        "compatibility": compatibility,
        "user_saved_status": saved_status
    }

@router.post("/compare")
def compare_opportunities(
    payload: Dict[str, List[str]],
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    opp_ids = payload.get("opportunity_ids", [])
    if not opp_ids or len(opp_ids) < 2 or len(opp_ids) > 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide between 2 and 4 opportunity IDs to compare."
        )

    opps = db.query(Opportunity).filter(Opportunity.id.in_(opp_ids)).all()
    if not opps:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specified opportunities not found")

    profile = None
    if current_user:
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()

    comparisons = []
    for opp in opps:
        compat = matching_engine.calculate_compatibility(opp, profile) if profile else None
        comparisons.append({
            "opportunity": opp,
            "compatibility": compat
        })

    return {
        "compared_count": len(comparisons),
        "results": comparisons
    }
