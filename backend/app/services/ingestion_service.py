import csv
import io
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.entities import Opportunity, OpportunitySkill, Embedding, IngestionJob, Skill
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)

class IngestionService:
    @classmethod
    def validate_record(cls, record: Dict[str, Any], row_num: int) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Validates individual opportunity record. Returns (is_valid, error_msg, cleaned_record).
        """
        title = str(record.get("title", "")).strip()
        company = str(record.get("company", "")).strip()
        description = str(record.get("description", "")).strip()

        if not title:
            return False, f"Row {row_num}: Missing required field 'title'.", {}
        if not company:
            return False, f"Row {row_num}: Missing required field 'company'.", {}
        if not description or len(description) < 20:
            return False, f"Row {row_num}: 'description' is too short or missing (min 20 characters).", {}

        # Parse skills
        def parse_list(val):
            if isinstance(val, list):
                return [str(v).strip() for v in val if str(v).strip()]
            if isinstance(val, str):
                if ";" in val:
                    return [s.strip() for s in val.split(";") if s.strip()]
                return [s.strip() for s in val.split(",") if s.strip()]
            return []

        required_skills = parse_list(record.get("required_skills", []))
        nice_to_have_skills = parse_list(record.get("nice_to_have_skills", []))
        responsibilities = parse_list(record.get("responsibilities", []))
        benefits = parse_list(record.get("benefits", []))

        # Safe int conversion
        def safe_int(val, default):
            try:
                return int(float(val))
            except Exception:
                return default

        min_exp = safe_int(record.get("min_years_experience"), 0)
        max_exp = safe_int(record.get("max_years_experience"), max(min_exp + 3, 10))
        min_salary = safe_int(record.get("min_salary"), 0)
        max_salary = safe_int(record.get("max_salary"), 0)

        cleaned = {
            "id": str(record.get("id") or f"opp-ingest-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{row_num}"),
            "title": title,
            "company": company,
            "department": str(record.get("department", "Engineering")).strip(),
            "location": str(record.get("location", "Remote")).strip(),
            "work_mode": str(record.get("work_mode", "hybrid")).lower().strip(),
            "opportunity_type": str(record.get("opportunity_type", "full-time")).lower().strip(),
            "experience_level": str(record.get("experience_level", "mid")).lower().strip(),
            "min_years_experience": min_exp,
            "max_years_experience": max_exp,
            "min_salary": min_salary,
            "max_salary": max_salary,
            "currency": str(record.get("currency", "USD")).upper().strip(),
            "description": description,
            "responsibilities": responsibilities,
            "benefits": benefits,
            "required_skills": required_skills,
            "nice_to_have_skills": nice_to_have_skills,
            "is_synthetic": bool(record.get("is_synthetic", True)),
            "source": str(record.get("source", "ingestion_upload")).strip(),
            "application_url": str(record.get("application_url", "")).strip(),
            "contact_email": str(record.get("contact_email", "")).strip(),
            "status": "active"
        }
        return True, None, cleaned

    @classmethod
    def index_opportunity_embedding(cls, db: Session, opp: Opportunity) -> Embedding:
        """
        Creates or updates dense 384-d semantic embedding for an opportunity.
        """
        text_content = (
            f"Title: {opp.title}. Company: {opp.company}. Location: {opp.location} ({opp.work_mode}). "
            f"Type: {opp.opportunity_type}. Description: {opp.description}. "
            f"Required Skills: {', '.join(opp.required_skills or [])}. Nice to have: {', '.join(opp.nice_to_have_skills or [])}"
        )
        text_hash = embedding_service.get_text_hash(text_content)
        
        # Check existing embedding
        existing_emb = db.query(Embedding).filter(
            Embedding.entity_type == "opportunity",
            Embedding.entity_id == opp.id
        ).first()

        if existing_emb and existing_emb.text_hash == text_hash:
            return existing_emb

        vector = embedding_service.embed_text(text_content)
        if existing_emb:
            existing_emb.vector = vector
            existing_emb.text_hash = text_hash
            existing_emb.model_name = embedding_service._model.__class__.__name__ if embedding_service._model else "DeterministicFeatureProjector-384"
            return existing_emb

        new_emb = Embedding(
            entity_type="opportunity",
            entity_id=opp.id,
            model_name=embedding_service._model.__class__.__name__ if embedding_service._model else "DeterministicFeatureProjector-384",
            embedding_dimension=384,
            vector=vector,
            text_hash=text_hash
        )
        db.add(new_emb)
        return new_emb

    @classmethod
    def ingest_records(
        cls,
        db: Session,
        raw_records: List[Dict[str, Any]],
        file_name: str,
        file_type: str,
        organization_id: Optional[str] = None
    ) -> IngestionJob:
        """
        Processes batch of opportunity records with validation, duplicate checking,
        database insertion, embedding generation, and job tracking.
        """
        job = IngestionJob(
            organization_id=organization_id,
            file_name=file_name,
            file_type=file_type,
            total_records=len(raw_records),
            processed_records=0,
            successful_records=0,
            failed_records=0,
            status="processing",
            errors_log=[]
        )
        db.add(job)
        db.commit()

        successful = 0
        failed = 0
        errors = []

        for idx, raw_record in enumerate(raw_records, start=1):
            is_valid, err_msg, cleaned = cls.validate_record(raw_record, idx)
            if not is_valid:
                failed += 1
                errors.append({"row": idx, "error": err_msg})
                continue

            try:
                # Match existing opportunities only by their stable ID
                existing = db.query(Opportunity).filter(
                    Opportunity.id == cleaned["id"]
                ).first()

                if existing:
                    # Update existing record
                    for k, v in cleaned.items():
                        if k == "id":
                            continue
                        setattr(existing, k, v)
                    if organization_id:
                        existing.organization_id = organization_id
                    opp = existing
                else:
                    opp = Opportunity(
                        organization_id=organization_id,
                        **cleaned
                    )
                    db.add(opp)
                    db.flush()

                # Sync opportunity skills
                db.query(OpportunitySkill).filter(OpportunitySkill.opportunity_id == opp.id).delete()
                for req_s in (opp.required_skills or []):
                    db.add(OpportunitySkill(
                        opportunity_id=opp.id,
                        skill_name=req_s,
                        is_required=True,
                        importance_weight=1.0
                    ))
                for nice_s in (opp.nice_to_have_skills or []):
                    db.add(OpportunitySkill(
                        opportunity_id=opp.id,
                        skill_name=nice_s,
                        is_required=False,
                        importance_weight=0.5
                    ))

                # Generate & store embedding
                cls.index_opportunity_embedding(db, opp)
                db.commit()
                successful += 1

            except Exception as e:
                db.rollback()
                failed += 1
                errors.append({"row": idx, "error": f"Database error for record '{cleaned.get('title')}': {str(e)}"})
                logger.error(f"Error ingesting row {idx}: {e}")

            # Commit in batches of 25
            if idx % 25 == 0:
                try:
                    db.commit()
                except Exception as commit_err:
                    db.rollback()
                    logger.error(f"Batch commit error: {commit_err}")

        # Final commit & job wrap up
        try:
            db.commit()
        except Exception as e:
            db.rollback()

        job.processed_records = len(raw_records)
        job.successful_records = successful
        job.failed_records = failed
        job.status = "completed" if failed == 0 else ("completed" if successful > 0 else "failed")
        job.errors_log = errors[:100]  # Store top 100 errors
        job.completed_at = datetime.now(timezone.utc)
        db.commit()

        return job

    @classmethod
    def reindex_all_embeddings(cls, db: Session, organization_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Re-indexes all active opportunities when model or embedding parameters change.
        """
        opp_query = db.query(Opportunity).filter(Opportunity.status == "active")
        if organization_id:
            opp_query = opp_query.filter(
                or_(Opportunity.organization_id == organization_id, Opportunity.organization_id.is_(None))
            )
        opps = opp_query.all()
        reindexed_count = 0
        for opp in opps:
            cls.index_opportunity_embedding(db, opp)
            reindexed_count += 1
        db.commit()
        return {"total_opportunities": len(opps), "reindexed": reindexed_count}

ingestion_service = IngestionService()





