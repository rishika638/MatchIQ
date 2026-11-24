from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Request
from app.core.rate_limit import limiter
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.models.entities import User, CandidateProfile
from app.schemas.schemas import CandidateProfileUpdate, CandidateProfileResponse
from app.api.deps import get_current_user
from app.services.resume_service import resume_service

router = APIRouter()

@router.get("/profile", response_model=CandidateProfileResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        profile = CandidateProfile(
            user_id=current_user.id,
            headline="Software Engineer",
            bio="",
            experience_years=1.0,
            skills=["Python", "FastAPI", "SQL"],
            preferred_locations=["Remote"],
            preferred_work_modes=["remote", "hybrid"],
            preferred_opportunity_types=["full-time"],
            preferred_min_salary=80000,
            preferred_currency="USD",
            preferred_roles=["Backend Engineer"]
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.put("/profile", response_model=CandidateProfileResponse)
def update_profile(
    profile_in: CandidateProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)

    update_data = profile_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(profile, field, val)

    db.commit()
    db.refresh(profile)
    return profile

@router.post("/resume/upload")
@limiter.limit("10/minute")
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Parses uploaded PDF resume, extracts skills, experience, education,
    and returns structured data so the user can review and edit before saving.
    """
    if not file.filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and TXT resume files are supported."
        )

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum allowed limit of 10MB."
        )

    raw_text = ""
    if file.filename.lower().endswith(".pdf"):
        raw_text = resume_service.extract_text_from_pdf(contents)
    else:
        raw_text = contents.decode("utf-8", errors="ignore")

    parsed = resume_service.parse_resume_text(raw_text)

    # Store raw text and extracted data draft in profile
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if profile:
        profile.resume_filename = file.filename
        profile.resume_raw_text = raw_text[:5000]
        profile.extracted_data = parsed
        db.commit()

    return {
        "filename": file.filename,
        "extracted_preview": parsed,
        "message": "Resume successfully extracted. Review and confirm changes before saving to profile."
    }
