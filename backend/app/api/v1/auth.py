from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.core.rate_limit import limiter
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, hash_password, create_access_token
from app.models.entities import User, CandidateProfile, Organization, OrganizationMember
from app.schemas.schemas import UserCreate, UserLogin, Token, UserResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/register", response_model=Token)
@limiter.limit("5/minute")
def register(request: Request, user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email.lower().strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    # Create User
    user = User(
        email=user_in.email.lower().strip(),
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name.strip(),
        role=user_in.role or "candidate"
    )
    db.add(user)
    db.flush()

    # Create associated Organization if specified or personal tenant
    org_name = user_in.organization_name or f"{user.full_name}'s Workspace"
    import re
    slug = re.sub(r'[^a-z0-9]+', '-', org_name.lower()).strip('-') + f"-{user.id[:6]}"
    org = Organization(
        name=org_name,
        slug=slug,
        plan="starter"
    )
    db.add(org)
    db.flush()

    org_member = OrganizationMember(
        organization_id=org.id,
        user_id=user.id,
        role="owner"
    )
    db.add(org_member)

    # Initialize CandidateProfile
    profile = CandidateProfile(
        user_id=user.id,
        organization_id=org.id,
        headline="Software Professional",
        bio="",
        experience_years=0.0,
        skills=[],
        preferred_locations=[],
        preferred_work_modes=["remote", "hybrid"],
        preferred_opportunity_types=["full-time"],
        preferred_min_salary=0,
        preferred_currency="USD",
        preferred_roles=[]
    )
    db.add(profile)
    db.commit()

    token = create_access_token(user.id, claims={"role": user.role, "email": user.email, "org_id": org.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "organization_id": org.id
        }
    }

@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, login_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_in.email.lower().strip()).first()
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is currently inactive."
        )

    membership = db.query(OrganizationMember).filter(OrganizationMember.user_id == user.id).first()
    org_id = membership.organization_id if membership else None

    token = create_access_token(user.id, claims={"role": user.role, "email": user.email, "org_id": org_id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "organization_id": org_id
        }
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
