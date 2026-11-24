from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Request
from app.core.rate_limit import limiter
from sqlalchemy.orm import Session
import json
import csv
import io
from typing import Optional

from app.core.database import get_db
from app.models.entities import IngestionJob, User
from app.api.deps import get_current_user
from app.services.ingestion_service import ingestion_service

router = APIRouter()
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_UPLOAD_RECORDS = 10000

@router.post("/upload")
@limiter.limit("5/minute")
async def upload_dataset(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    filename = file.filename.lower()
    if not (filename.endswith(".json") or filename.endswith(".csv")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JSON and CSV files are supported for opportunity ingestion."
        )

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Upload exceeds the 10 MB size limit."
        )
    records = []

    try:
        if filename.endswith(".json"):
            records = json.loads(content.decode("utf-8-sig"))
            if not isinstance(records, list):
                raise ValueError("JSON must contain an array of opportunity objects.")
        else:
            csv_text = content.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(csv_text))
            records = list(reader)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse upload file: {str(e)}"
        )
    if len(records) > MAX_UPLOAD_RECORDS:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Upload exceeds the {MAX_UPLOAD_RECORDS}-record limit."
        )

    membership = current_user.memberships[0] if current_user.memberships else None
    org_id = membership.organization_id if membership else None

    file_type = "json" if filename.endswith(".json") else "csv"
    job = ingestion_service.ingest_records(
        db=db,
        raw_records=records,
        file_name=file.filename,
        file_type=file_type,
        organization_id=org_id
    )

    return {
        "job_id": job.id,
        "status": job.status,
        "total_records": job.total_records,
        "successful_records": job.successful_records,
        "failed_records": job.failed_records,
        "errors": job.errors_log
    }

@router.get("/jobs")
def list_ingestion_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    membership = current_user.memberships[0] if current_user.memberships else None
    organization_id = membership.organization_id if membership else None
    query = db.query(IngestionJob)
    if organization_id:
        query = query.filter(IngestionJob.organization_id == organization_id)
    else:
        query = query.filter(IngestionJob.organization_id.is_(None))
    jobs = query.order_by(IngestionJob.created_at.desc()).limit(15).all()
    return jobs

@router.post("/reindex")
def trigger_reindexing(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    membership = current_user.memberships[0] if current_user.memberships else None
    organization_id = membership.organization_id if membership else None
    res = ingestion_service.reindex_all_embeddings(db, organization_id=organization_id)
    return {
        "status": "success",
        "message": f"Successfully re-indexed embeddings for {res['reindexed']} opportunities.",
        "details": res
    }
