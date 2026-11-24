from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.entities import SavedOpportunity, Opportunity, User, CandidateProfile
from app.schemas.schemas import SavedOpportunityCreate, SavedOpportunityUpdate
from app.api.deps import get_current_user
from app.services.matching_service import matching_engine

router = APIRouter()

@router.get("/")
def get_saved_opportunities(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(SavedOpportunity).filter(SavedOpportunity.user_id == current_user.id)
    if status_filter:
        query = query.filter(SavedOpportunity.status == status_filter)

    saved_items = query.order_by(SavedOpportunity.updated_at.desc()).all()
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()

    results = []
    for item in saved_items:
        opp = item.opportunity
        compat = matching_engine.calculate_compatibility(opp, profile) if (opp and profile) else None
        results.append({
            "id": item.id,
            "opportunity_id": item.opportunity_id,
            "status": item.status,
            "notes": item.notes,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
            "opportunity": opp,
            "compatibility": compat
        })

    return results

@router.post("/")
def save_opportunity(
    payload: SavedOpportunityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    opp = db.query(Opportunity).filter(Opportunity.id == payload.opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity does not exist")

    existing = db.query(SavedOpportunity).filter(
        SavedOpportunity.user_id == current_user.id,
        SavedOpportunity.opportunity_id == payload.opportunity_id
    ).first()

    if existing:
        if payload.status:
            existing.status = payload.status
        if payload.notes:
            existing.notes = payload.notes
        db.commit()
        db.refresh(existing)
        return {"status": "updated", "saved_opportunity": existing}

    saved = SavedOpportunity(
        user_id=current_user.id,
        opportunity_id=payload.opportunity_id,
        status=payload.status or "saved",
        notes=payload.notes
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return {"status": "created", "saved_opportunity": saved}

@router.patch("/{opportunity_id}")
def update_saved_status(
    opportunity_id: str,
    payload: SavedOpportunityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    saved = db.query(SavedOpportunity).filter(
        SavedOpportunity.user_id == current_user.id,
        SavedOpportunity.opportunity_id == opportunity_id
    ).first()

    if not saved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved opportunity record not found")

    if payload.status:
        saved.status = payload.status
    if payload.notes is not None:
        saved.notes = payload.notes

    db.commit()
    db.refresh(saved)
    return saved

@router.delete("/{opportunity_id}")
def remove_saved_opportunity(
    opportunity_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    saved = db.query(SavedOpportunity).filter(
        SavedOpportunity.user_id == current_user.id,
        SavedOpportunity.opportunity_id == opportunity_id
    ).first()

    if not saved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    db.delete(saved)
    db.commit()
    return {"status": "success", "message": "Removed from saved opportunities"}
