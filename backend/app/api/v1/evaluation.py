from fastapi import APIRouter, Depends, HTTPException, Query, Request
from app.core.rate_limit import limiter
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.entities import EvaluationRun, EvaluationQuery, RelevanceJudgment
from app.services.evaluation_service import evaluation_engine

router = APIRouter()

@router.get("/benchmark-queries")
def get_benchmark_queries(db: Session = Depends(get_db)):
    queries = db.query(EvaluationQuery).all()
    if not queries:
        evaluation_engine.load_benchmark_dataset(db)
        queries = db.query(EvaluationQuery).all()

    results = []
    for q in queries:
        judgments = db.query(RelevanceJudgment).filter(RelevanceJudgment.query_id == q.id).all()
        results.append({
            "query_id": q.id,
            "query_text": q.query_text,
            "intent": q.intent,
            "candidate_profile": q.candidate_profile_json,
            "judged_opportunities_count": len(judgments)
        })
    return results

@router.post("/run-suite")
@limiter.limit("3/minute")
def trigger_full_evaluation(request: Request, db: Session = Depends(get_db)):
    """
    Executes reproducible benchmark across:
    1. Keyword
    2. Semantic
    3. Hybrid (RRF)
    4. Hybrid + Cross-Encoder Reranked
    """
    runs = evaluation_engine.run_full_suite(db)
    return {
        "message": "Evaluation suite executed successfully",
        "runs_completed": len(runs),
        "results": runs
    }

@router.post("/run/{method}")
def trigger_single_evaluation(method: str, db: Session = Depends(get_db)):
    if method not in ["keyword", "semantic", "hybrid", "hybrid_reranked"]:
        raise HTTPException(
            status_code=400,
            detail="Method must be one of: keyword, semantic, hybrid, hybrid_reranked"
        )
    run = evaluation_engine.run_benchmark_for_method(db, method=method)
    return run

@router.get("/runs")
def list_evaluation_runs(db: Session = Depends(get_db)):
    runs = db.query(EvaluationRun).order_by(EvaluationRun.created_at.desc()).limit(20).all()
    return runs
