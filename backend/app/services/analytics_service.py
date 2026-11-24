from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from collections import Counter

from app.models.entities import (
    Opportunity, SavedOpportunity, CandidateProfile, SearchHistory,
    RecommendationFeedback, IngestionJob, EvaluationRun
)
from app.services.matching_service import matching_engine

class AnalyticsService:
    @classmethod
    def get_dashboard_metrics(cls, db: Session, user_id: str) -> Dict[str, Any]:
        """
        Calculates live database-driven intelligence dashboard metrics.
        No fabricated values.
        """
        total_opportunities = db.query(func.count(Opportunity.id)).filter(Opportunity.status == "active").scalar() or 0
        saved_count = db.query(func.count(SavedOpportunity.id)).filter(
            SavedOpportunity.user_id == user_id,
            SavedOpportunity.status == "saved"
        ).scalar() or 0
        applied_count = db.query(func.count(SavedOpportunity.id)).filter(
            SavedOpportunity.user_id == user_id,
            SavedOpportunity.status == "applied"
        ).scalar() or 0

        # Candidate profile
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()

        # Compute average compatibility across saved opportunities or top active roles
        avg_compatibility = 0.0
        missing_skills_counter = Counter()
        matching_skills_counter = Counter()
        
        saved_records = db.query(SavedOpportunity).filter(SavedOpportunity.user_id == user_id).all()
        sample_opps = [s.opportunity for s in saved_records if s.opportunity]
        if not sample_opps:
            sample_opps = db.query(Opportunity).filter(Opportunity.status == "active").limit(10).all()

        if profile and sample_opps:
            scores = []
            for opp in sample_opps:
                analysis = matching_engine.calculate_compatibility(opp, profile)
                scores.append(analysis["overall_compatibility"])
                for s in analysis.get("missing_skills", []):
                    missing_skills_counter[s] += 1
                for s in analysis.get("matching_skills", []):
                    matching_skills_counter[s] += 1
            if scores:
                avg_compatibility = round(sum(scores) / len(scores), 1)

        # Recent searches
        recent_searches = db.query(SearchHistory).filter(
            SearchHistory.user_id == user_id
        ).order_by(desc(SearchHistory.created_at)).limit(5).all()

        # Feedback distribution
        feedbacks = db.query(
            RecommendationFeedback.feedback_type,
            func.count(RecommendationFeedback.id)
        ).filter(
            RecommendationFeedback.user_id == user_id
        ).group_by(RecommendationFeedback.feedback_type).all()
        feedback_breakdown = {fb[0]: fb[1] for fb in feedbacks}

        # Opportunity breakdown by work mode
        mode_counts = db.query(
            Opportunity.work_mode,
            func.count(Opportunity.id)
        ).filter(Opportunity.status == "active").group_by(Opportunity.work_mode).all()
        work_mode_distribution = {m[0]: m[1] for m in mode_counts}

        return {
            "total_active_opportunities": total_opportunities,
            "saved_opportunities": saved_count,
            "applied_opportunities": applied_count,
            "average_compatibility": avg_compatibility,
            "top_missing_skills": [{"skill": k, "demand_count": v} for k, v in missing_skills_counter.most_common(6)],
            "top_matching_skills": [{"skill": k, "frequency": v} for k, v in matching_skills_counter.most_common(6)],
            "work_mode_distribution": work_mode_distribution,
            "feedback_summary": feedback_breakdown,
            "recent_searches": [
                {
                    "query": s.query_text,
                    "retrieval_method": s.retrieval_method,
                    "result_count": s.result_count,
                    "latency_ms": s.latency_ms,
                    "created_at": s.created_at.isoformat() if s.created_at else None
                } for s in recent_searches
            ]
        }

    @classmethod
    def get_feedback_analytics(cls, db: Session, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Feedback loop metrics: relevant, not_relevant, applied, not_interested.
        Calculates recommendation relevance ratio and user engagement.
        """
        query = db.query(RecommendationFeedback)
        if user_id:
            query = query.filter(RecommendationFeedback.user_id == user_id)
        
        all_fb = query.all()
        total = len(all_fb)
        counts = Counter([fb.feedback_type for fb in all_fb])

        # Positive relevance ratio: (relevant + applied) / total
        positive = counts.get("relevant", 0) + counts.get("applied", 0)
        relevance_ratio = round((positive / float(total)) * 100, 1) if total > 0 else 0.0

        return {
            "total_feedback_events": total,
            "breakdown": {
                "relevant": counts.get("relevant", 0),
                "not_relevant": counts.get("not_relevant", 0),
                "applied": counts.get("applied", 0),
                "not_interested": counts.get("not_interested", 0)
            },
            "positive_relevance_rate": relevance_ratio,
            "notice": "Real-time user feedback tracking; used to evaluate candidate preference alignment."
        }

analytics_service = AnalyticsService()
