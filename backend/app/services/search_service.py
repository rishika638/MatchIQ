import time
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, text
from app.models.entities import Opportunity, Embedding, CandidateProfile
from app.services.embedding_service import embedding_service
from app.services.reranker_service import reranker_service
from app.services.matching_service import matching_engine
from app.core.config import settings

logger = logging.getLogger(__name__)

class SearchService:
    @staticmethod
    def preprocess_query(query: str) -> str:
        if not query:
            return ""
        # Clean query, strip excess whitespace and special noise
        clean = " ".join(query.strip().split())
        return clean

    @classmethod
    def keyword_search(
        cls,
        db: Session,
        query: str,
        limit: int = 50,
        organization_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves opportunities matching keywords using PostgreSQL Full-Text Search
        or LIKE / ilike clauses across title, company, description, and required_skills.
        """
        clean_q = cls.preprocess_query(query)
        if not clean_q:
            return []

        # Tokenize query for multi-term keyword search
        terms = [t for t in clean_q.split() if len(t) > 2]
        if not terms:
            terms = [clean_q]

        query_filters = [Opportunity.status == "active"]
        if organization_id:
            query_filters.append(
                or_(Opportunity.organization_id == organization_id, Opportunity.organization_id == None)
            )

        # Build term filters
        keyword_clauses = []
        for term in terms:
            term_wildcard = f"%{term}%"
            keyword_clauses.append(
                or_(
                    Opportunity.title.ilike(term_wildcard),
                    Opportunity.company.ilike(term_wildcard),
                    Opportunity.description.ilike(term_wildcard),
                    Opportunity.location.ilike(term_wildcard),
                    # Convert JSON skills to text search
                    Opportunity.required_skills.astext.ilike(term_wildcard) if hasattr(Opportunity.required_skills, "astext") else Opportunity.title.ilike(term_wildcard)
                )
            )

        stmt = db.query(Opportunity).filter(
            and_(*query_filters),
            or_(*keyword_clauses)
        ).limit(limit)

        results = stmt.all()
        scored = []
        clean_q_lower = clean_q.lower()
        for rank, opp in enumerate(results):
            # Keyword relevance heuristic based on occurrences
            title_lower = opp.title.lower()
            desc_lower = opp.description.lower()
            matches = sum(1 for t in terms if t.lower() in title_lower) * 3 + sum(1 for t in terms if t.lower() in desc_lower)
            scored.append({
                "opportunity": opp,
                "opportunity_id": opp.id,
                "keyword_score": float(matches),
                "keyword_rank": rank + 1
            })

        # Sort by keyword matches descending
        scored.sort(key=lambda x: x["keyword_score"], reverse=True)
        for i, item in enumerate(scored):
            item["keyword_rank"] = i + 1
        return scored

    @classmethod
    def semantic_search(
        cls,
        db: Session,
        query: str,
        limit: int = 50,
        organization_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves opportunities by vector cosine similarity.
        Works via pgvector if PostgreSQL extension is active,
        or via in-memory cached cosine comparison for resilient operation.
        """
        clean_q = cls.preprocess_query(query)
        if not clean_q:
            return []

        query_emb = embedding_service.embed_text(clean_q)

        # Retrieve stored opportunity embeddings
        embeddings = db.query(Embedding).filter(
            Embedding.entity_type == "opportunity"
        ).all()

        scored = []
        # Preload active opportunities
        opp_query = db.query(Opportunity).filter(Opportunity.status == "active")
        if organization_id:
            opp_query = opp_query.filter(
                or_(Opportunity.organization_id == organization_id, Opportunity.organization_id == None)
            )
        opp_map = {opp.id: opp for opp in opp_query.all()}

        for emb_record in embeddings:
            opp_id = emb_record.entity_id
            if opp_id not in opp_map:
                continue

            vector_data = emb_record.vector
            if isinstance(vector_data, str):
                import json
                try:
                    vector_data = json.loads(vector_data)
                except Exception:
                    continue

            sim = embedding_service.cosine_similarity(query_emb, vector_data)
            scored.append({
                "opportunity": opp_map[opp_id],
                "opportunity_id": opp_id,
                "semantic_score": float(sim)
            })

        scored.sort(key=lambda x: x["semantic_score"], reverse=True)
        scored = scored[:limit]
        for i, item in enumerate(scored):
            item["semantic_rank"] = i + 1
        return scored

    @classmethod
    def hybrid_search(
        cls,
        db: Session,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        candidate_profile: Optional[CandidateProfile] = None,
        enable_reranking: bool = False,
        page: int = 1,
        page_size: int = 20,
        organization_id: Optional[str] = None,
        rrf_k: int = 60
    ) -> Dict[str, Any]:
        """
        Complete 8-stage hybrid retrieval & ranking pipeline:
        1. Preprocess query
        2. Generate query embedding
        3. Semantic retrieval
        4. Keyword retrieval
        5. Reciprocal Rank Fusion (RRF)
        6. Hard eligibility filtering
        7. Optional Cross-Encoder reranking
        8. Explainable matching breakdown and pagination
        """
        start_time = time.time()
        clean_q = cls.preprocess_query(query)

        # If query is blank and candidate profile exists, construct query from candidate background
        if not clean_q and candidate_profile:
            clean_q = f"{candidate_profile.headline or ''} {' '.join(candidate_profile.skills or [])}"

        # 1 & 2 & 3. Keyword and Semantic Retrieval
        keyword_results = cls.keyword_search(db, clean_q, limit=100, organization_id=organization_id)
        semantic_results = cls.semantic_search(db, clean_q, limit=100, organization_id=organization_id)

        # 4. Reciprocal Rank Fusion (RRF)
        rrf_scores: Dict[str, float] = {}
        items_map: Dict[str, Any] = {}
        sem_score_map: Dict[str, float] = {}
        kw_score_map: Dict[str, float] = {}

        for item in semantic_results:
            opp_id = item["opportunity_id"]
            items_map[opp_id] = item["opportunity"]
            sem_score_map[opp_id] = item["semantic_score"]
            rank = item["semantic_rank"]
            rrf_scores[opp_id] = rrf_scores.get(opp_id, 0.0) + (1.0 / (rrf_k + rank))

        for item in keyword_results:
            opp_id = item["opportunity_id"]
            items_map[opp_id] = item["opportunity"]
            kw_score_map[opp_id] = item["keyword_score"]
            rank = item["keyword_rank"]
            rrf_scores[opp_id] = rrf_scores.get(opp_id, 0.0) + (1.0 / (rrf_k + rank))

        # If neither yielded results, load active opportunities directly
        if not rrf_scores:
            base_opps = db.query(Opportunity).filter(Opportunity.status == "active").limit(100).all()
            for rank, opp in enumerate(base_opps):
                items_map[opp.id] = opp
                rrf_scores[opp.id] = 1.0 / (rrf_k + rank + 1)
                sem_score_map[opp.id] = 0.5
                kw_score_map[opp.id] = 0.0

        # 5. Hard Eligibility and User Filters
        filtered_items = []
        flt = filters or {}
        
        target_locations = [l.lower() for l in flt.get("locations", []) if l]
        target_work_modes = [m.lower() for m in flt.get("work_modes", []) if m]
        target_types = [t.lower() for t in flt.get("opportunity_types", []) if t]
        target_skills = [s.lower() for s in flt.get("skills", []) if s]
        min_salary_req = flt.get("min_salary", 0) or 0
        max_exp_filter = flt.get("max_experience", None)

        for opp_id, rrf_score in rrf_scores.items():
            opp = items_map[opp_id]
            
            # Location filter
            if target_locations:
                loc_lower = opp.location.lower()
                if not any(tl in loc_lower for tl in target_locations) and opp.work_mode != "remote":
                    continue

            # Work mode filter
            if target_work_modes and opp.work_mode.lower() not in target_work_modes:
                continue

            # Opportunity type filter
            if target_types and opp.opportunity_type.lower() not in target_types:
                continue

            # Salary filter
            if min_salary_req > 0 and opp.max_salary > 0 and opp.max_salary < min_salary_req:
                continue

            # Experience filter
            if max_exp_filter is not None and opp.min_years_experience > max_exp_filter:
                continue

            # Skills filter
            if target_skills:
                opp_skills = [s.lower() for s in (opp.required_skills or []) + (opp.nice_to_have_skills or [])]
                if not any(ts in opp_skills for ts in target_skills):
                    continue

            filtered_items.append({
                "opportunity": opp,
                "opportunity_id": opp_id,
                "rrf_score": rrf_score,
                "semantic_score": sem_score_map.get(opp_id, 0.0),
                "keyword_score": kw_score_map.get(opp_id, 0.0)
            })

        # 6. Optional Cross-Encoder Reranking
        if enable_reranking and filtered_items:
            candidate_texts = [
                f"{item['opportunity'].title} at {item['opportunity'].company}. {item['opportunity'].description} Skills: {', '.join(item['opportunity'].required_skills or [])}"
                for item in filtered_items
            ]
            reranker_scores = reranker_service.rerank(clean_q, candidate_texts)
            for idx, item in enumerate(filtered_items):
                item["reranker_score"] = reranker_scores[idx] if idx < len(reranker_scores) else 0.5
                # Combined reranked score = 0.5 * normalized_rrf + 0.5 * reranker
                item["final_score"] = 0.4 * (item["rrf_score"] * 100) + 0.6 * item["reranker_score"]
        else:
            for item in filtered_items:
                item["reranker_score"] = None
                item["final_score"] = item["rrf_score"]

        # Sort by final score descending
        filtered_items.sort(key=lambda x: x["final_score"], reverse=True)

        # 7. Compute Explainable Match Analysis if candidate profile provided
        total_count = len(filtered_items)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_items = filtered_items[start_idx:end_idx]

        results = []
        for item in paginated_items:
            opp = item["opportunity"]
            match_analysis = None
            if candidate_profile:
                match_analysis = matching_engine.calculate_compatibility(
                    opportunity=opp,
                    profile=candidate_profile,
                    semantic_sim=item["semantic_score"]
                )

            results.append({
                "opportunity": {
                    "id": opp.id,
                    "title": opp.title,
                    "company": opp.company,
                    "department": opp.department,
                    "location": opp.location,
                    "work_mode": opp.work_mode,
                    "opportunity_type": opp.opportunity_type,
                    "experience_level": opp.experience_level,
                    "min_years_experience": opp.min_years_experience,
                    "max_years_experience": opp.max_years_experience,
                    "min_salary": opp.min_salary,
                    "max_salary": opp.max_salary,
                    "currency": opp.currency,
                    "description": opp.description,
                    "responsibilities": opp.responsibilities,
                    "benefits": opp.benefits,
                    "required_skills": opp.required_skills,
                    "nice_to_have_skills": opp.nice_to_have_skills,
                    "is_synthetic": opp.is_synthetic,
                    "source": opp.source,
                    "application_url": opp.application_url,
                    "contact_email": opp.contact_email,
                    "created_at": opp.created_at.isoformat() if opp.created_at else None
                },
                "retrieval_meta": {
                    "rrf_score": round(item["rrf_score"], 5),
                    "semantic_score": round(item["semantic_score"], 4),
                    "keyword_score": round(item["keyword_score"], 2),
                    "reranker_score": round(item["reranker_score"], 4) if item["reranker_score"] is not None else None,
                    "final_score": round(item["final_score"], 4),
                    "cross_encoder_applied": enable_reranking
                },
                "compatibility": match_analysis
            })

        latency = (time.time() - start_time) * 1000.0

        return {
            "query": clean_q,
            "retrieval_method": "hybrid_reranked" if enable_reranking else "hybrid_rrf",
            "total_matches": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size if page_size > 0 else 1,
            "latency_ms": round(latency, 2),
            "results": results
        }

search_service = SearchService()
