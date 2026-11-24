from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.entities import CandidateProfile, SearchHistory, User
from app.schemas.schemas import SearchRequest
from app.api.deps import get_optional_user
from app.services.search_service import search_service

router = APIRouter()

@router.post("/")
def perform_search(
    search_req: SearchRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    profile = None
    organization_id = None
    if current_user:
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
        membership = current_user.memberships[0] if current_user.memberships else None
        organization_id = membership.organization_id if membership else None

    filters = {
        "locations": search_req.locations or [],
        "work_modes": search_req.work_modes or [],
        "opportunity_types": search_req.opportunity_types or [],
        "skills": search_req.skills or [],
        "min_salary": search_req.min_salary or 0,
        "max_experience": search_req.max_experience
    }

    results = search_service.hybrid_search(
        db=db,
        query=search_req.query,
        filters=filters,
        candidate_profile=profile,
        enable_reranking=search_req.enable_reranking,
        page=search_req.page,
        page_size=search_req.page_size,
        organization_id=organization_id
    )

    # Record search history if user is authenticated
    if current_user and search_req.query:
        history = SearchHistory(
            user_id=current_user.id,
            query_text=search_req.query,
            filters=filters,
            retrieval_method=results["retrieval_method"],
            result_count=results["total_matches"],
            latency_ms=results["latency_ms"]
        )
        db.add(history)
        db.commit()

    return results
