from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.entities import User
from app.api.deps import get_current_user
from app.services.analytics_service import analytics_service

router = APIRouter()

@router.get("/dashboard")
def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return analytics_service.get_dashboard_metrics(db, user_id=current_user.id)
