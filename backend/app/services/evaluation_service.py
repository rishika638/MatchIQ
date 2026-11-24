import json
import math
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.entities import EvaluationQuery, RelevanceJudgment, EvaluationRun, Opportunity, CandidateProfile
from app.services.search_service import search_service
from app.core.config import settings

logger = logging.getLogger(__name__)

class EvaluationEngine:
    @staticmethod
    def dcg_at_k(r: List[int], k: int) -> float:
        """Discounted Cumulative Gain at rank K"""
        r = r[:k]
        if not r:
            return 0.0
        dcg = 0.0
        for i, rel in enumerate(r):
            # Formula: (2^rel - 1) / log2(i + 2)
            dcg += (math.pow(2, rel) - 1.0) / math.log2(i + 2)
        return dcg

    @classmethod
    def ndcg_at_k(cls, retrieved_grades: List[int], ideal_grades: List[int], k: int) -> float:
        """Normalized Discounted Cumulative Gain at rank K"""
        actual_dcg = cls.dcg_at_k(retrieved_grades, k)
        ideal_dcg = cls.dcg_at_k(sorted(ideal_grades, reverse=True), k)
        if ideal_dcg == 0.0:
            return 0.0
        return min(1.0, actual_dcg / ideal_dcg)

    @staticmethod
    def precision_at_k(retrieved_grades: List[int], k: int, threshold: int = 1) -> float:
        """Precision at rank K for binary/graded relevance >= threshold"""
        sub = retrieved_grades[:k]
        if not sub:
            return 0.0
        relevant_count = sum(1 for g in sub if g >= threshold)
        return relevant_count / float(k)

    @staticmethod
    def recall_at_k(retrieved_grades: List[int], total_relevant: int, k: int, threshold: int = 1) -> float:
        """Recall at rank K"""
        if total_relevant == 0:
            return 0.0
        sub = retrieved_grades[:k]
        relevant_found = sum(1 for g in sub if g >= threshold)
        return min(1.0, relevant_found / float(total_relevant))

    @staticmethod
    def reciprocal_rank(retrieved_grades: List[int], threshold: int = 2) -> float:
        """Reciprocal rank of first highly-relevant or relevant item"""
        for i, g in enumerate(retrieved_grades):
            if g >= threshold:
                return 1.0 / float(i + 1)
        return 0.0

    @classmethod
    def load_benchmark_dataset(cls, db: Session, benchmark_file: str = "data/evaluation/evaluation_benchmark.json") -> int:
        """
        Loads labelled benchmark dataset into evaluation_queries and relevance_judgments tables.
        """
        try:
            with open(benchmark_file, "r", encoding="utf-8") as f:
                benchmarks = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read benchmark file {benchmark_file}: {e}")
            return 0

        loaded_count = 0
        for item in benchmarks:
            q_id = item["query_id"]
            existing = db.query(EvaluationQuery).filter(EvaluationQuery.id == q_id).first()
            if existing:
                existing.query_text = item["query"]
                existing.candidate_profile_json = item.get("candidate_profile", {})
                existing.intent = item.get("intent", "")
            else:
                eq = EvaluationQuery(
                    id=q_id,
                    query_text=item["query"],
                    candidate_profile_json=item.get("candidate_profile", {}),
                    intent=item.get("intent", "")
                )
                db.add(eq)
                db.flush()

            # Replace judgments
            db.query(RelevanceJudgment).filter(RelevanceJudgment.query_id == q_id).delete()
            for j in item.get("judgments", []):
                if "opportunity_id" in j:
                    db.add(RelevanceJudgment(
                        query_id=q_id,
                        opportunity_id=j["opportunity_id"],
                        grade=j.get("grade", 1),
                        rationale=j.get("rationale", "")
                    ))
            loaded_count += 1

        db.commit()
        return loaded_count

    @classmethod
    def run_benchmark_for_method(
        cls,
        db: Session,
        method: str,  # 'keyword', 'semantic', 'hybrid', 'hybrid_reranked'
        organization_id: Optional[str] = None
    ) -> EvaluationRun:
        """
        Runs full reproducible quantitative evaluation across all labelled queries in the database.
        """
        queries = db.query(EvaluationQuery).all()
        if not queries:
            cls.load_benchmark_dataset(db)
            queries = db.query(EvaluationQuery).all()

        p1_list, p3_list, p5_list = [], [], []
        r3_list, r5_list, r10_list = [], [], []
        mrr_list = []
        ndcg3_list, ndcg5_list, ndcg10_list = [], [], []
        latencies = []
        query_breakdowns = []

        for q in queries:
            # Load ground truth judgments
            judgments = db.query(RelevanceJudgment).filter(RelevanceJudgment.query_id == q.id).all()
            ground_truth_map = {j.opportunity_id: j.grade for j in judgments}
            ideal_grades = list(ground_truth_map.values())
            total_relevant = sum(1 for g in ideal_grades if g >= 1)

            # Build mock candidate profile for matching context
            c_data = q.candidate_profile_json or {}
            profile = CandidateProfile(
                headline=c_data.get("title", ""),
                experience_years=float(c_data.get("years_experience", 2.0)),
                skills=c_data.get("skills", []),
                preferred_opportunity_types=c_data.get("preferred_opportunity_types", []),
                preferred_locations=c_data.get("preferred_locations", []),
                preferred_work_modes=[],
                preferred_min_salary=0,
                preferred_roles=[c_data.get("title", "")]
            )

            start_t = time.time()
            if method == "keyword":
                retrieved = search_service.keyword_search(db, q.query_text, limit=10, organization_id=organization_id)
                retrieved_ids = [item["opportunity_id"] for item in retrieved]
            elif method == "semantic":
                retrieved = search_service.semantic_search(db, q.query_text, limit=10, organization_id=organization_id)
                retrieved_ids = [item["opportunity_id"] for item in retrieved]
            elif method == "hybrid":
                search_res = search_service.hybrid_search(
                    db, q.query_text, candidate_profile=profile, enable_reranking=False, page=1, page_size=10, organization_id=organization_id
                )
                retrieved_ids = [r["opportunity"]["id"] for r in search_res["results"]]
            elif method == "hybrid_reranked":
                search_res = search_service.hybrid_search(
                    db, q.query_text, candidate_profile=profile, enable_reranking=True, page=1, page_size=10, organization_id=organization_id
                )
                retrieved_ids = [r["opportunity"]["id"] for r in search_res["results"]]
            else:
                raise ValueError(f"Unknown retrieval method: {method}")

            latency_ms = (time.time() - start_t) * 1000.0
            latencies.append(latency_ms)

            # Map retrieved items to ground truth grades (0 if not in labelled pool)
            retrieved_grades = [ground_truth_map.get(opp_id, 0) for opp_id in retrieved_ids]
            # Pad to 10 if fewer returned
            while len(retrieved_grades) < 10:
                retrieved_grades.append(0)

            # Compute metric scores
            p1 = cls.precision_at_k(retrieved_grades, 1)
            p3 = cls.precision_at_k(retrieved_grades, 3)
            p5 = cls.precision_at_k(retrieved_grades, 5)

            r3 = cls.recall_at_k(retrieved_grades, total_relevant, 3)
            r5 = cls.recall_at_k(retrieved_grades, total_relevant, 5)
            r10 = cls.recall_at_k(retrieved_grades, total_relevant, 10)

            rr = cls.reciprocal_rank(retrieved_grades, threshold=2)

            ndcg3 = cls.ndcg_at_k(retrieved_grades, ideal_grades, 3)
            ndcg5 = cls.ndcg_at_k(retrieved_grades, ideal_grades, 5)
            ndcg10 = cls.ndcg_at_k(retrieved_grades, ideal_grades, 10)

            p1_list.append(p1)
            p3_list.append(p3)
            p5_list.append(p5)
            r3_list.append(r3)
            r5_list.append(r5)
            r10_list.append(r10)
            mrr_list.append(rr)
            ndcg3_list.append(ndcg3)
            ndcg5_list.append(ndcg5)
            ndcg10_list.append(ndcg10)

            query_breakdowns.append({
                "query_id": q.id,
                "query_text": q.query_text,
                "retrieved_count": len(retrieved_ids),
                "top_retrieved_ids": retrieved_ids[:3],
                "retrieved_grades": retrieved_grades[:5],
                "p_at_3": round(p3, 4),
                "r_at_5": round(r5, 4),
                "ndcg_at_5": round(ndcg5, 4),
                "latency_ms": round(latency_ms, 2)
            })

        avg = lambda lst: sum(lst) / len(lst) if lst else 0.0

        eval_run = EvaluationRun(
            organization_id=organization_id,
            dataset_version="v1.0-synthetic-benchmark",
            retrieval_method=method,
            embedding_model=settings.EMBEDDING_MODEL_NAME,
            reranker_model=settings.RERANKER_MODEL_NAME if "reranked" in method else None,
            precision_at_k={
                "k=1": round(avg(p1_list), 4),
                "k=3": round(avg(p3_list), 4),
                "k=5": round(avg(p5_list), 4)
            },
            recall_at_k={
                "k=3": round(avg(r3_list), 4),
                "k=5": round(avg(r5_list), 4),
                "k=10": round(avg(r10_list), 4)
            },
            mrr=round(avg(mrr_list), 4),
            ndcg_at_k={
                "k=3": round(avg(ndcg3_list), 4),
                "k=5": round(avg(ndcg5_list), 4),
                "k=10": round(avg(ndcg10_list), 4)
            },
            average_latency_ms=round(avg(latencies), 2),
            detailed_metrics={
                "query_count": len(queries),
                "queries_evaluated": query_breakdowns
            }
        )
        db.add(eval_run)
        db.commit()
        db.refresh(eval_run)
        return eval_run

    @classmethod
    def run_full_suite(cls, db: Session, organization_id: Optional[str] = None) -> List[EvaluationRun]:
        """
        Executes and compares all 4 retrieval paradigms:
        1. Keyword
        2. Semantic
        3. Hybrid (RRF)
        4. Hybrid + Cross-Encoder Reranked
        """
        runs = []
        for method in ["keyword", "semantic", "hybrid", "hybrid_reranked"]:
            run = cls.run_benchmark_for_method(db, method=method, organization_id=organization_id)
            runs.append(run)
        return runs

evaluation_engine = EvaluationEngine()
