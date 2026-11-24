from typing import Dict, Any, List, Optional
from app.models.entities import Opportunity, CandidateProfile
from app.services.embedding_service import embedding_service

class MatchingEngine:
    # Default component weights (sum = 1.0)
    DEFAULT_WEIGHTS = {
        "semantic_similarity": 0.30,
        "skills_overlap": 0.30,
        "experience_compatibility": 0.15,
        "role_relevance": 0.15,
        "preference_compatibility": 0.10
    }

    @classmethod
    def evaluate_eligibility(cls, opportunity: Opportunity, profile: CandidateProfile) -> Dict[str, Any]:
        """
        Hard constraint verification separate from continuous relevance ranking.
        """
        violations = []
        
        # 1. Experience ceiling / floor
        exp_years = profile.experience_years or 0.0
        min_exp = opportunity.min_years_experience or 0
        if exp_years < min_exp:
            gap = min_exp - exp_years
            violations.append(f"Requires minimum {min_exp} years experience (candidate has {exp_years:.1f} years, gap: {gap:.1f} yrs)")

        # 2. Opportunity type (e.g. if candidate strictly requires internship or full-time)
        if profile.preferred_opportunity_types and len(profile.preferred_opportunity_types) > 0:
            if opportunity.opportunity_type not in profile.preferred_opportunity_types:
                violations.append(f"Opportunity type '{opportunity.opportunity_type}' not in candidate preferences: {profile.preferred_opportunity_types}")

        # 3. Work mode constraint
        if profile.preferred_work_modes and len(profile.preferred_work_modes) > 0:
            if opportunity.work_mode not in profile.preferred_work_modes:
                violations.append(f"Work mode '{opportunity.work_mode}' not in candidate preferences: {profile.preferred_work_modes}")

        is_eligible = len(violations) == 0
        return {
            "is_eligible": is_eligible,
            "violations": violations,
            "status": "Eligible" if is_eligible else "Constraint Gap"
        }

    @classmethod
    def calculate_compatibility(
        cls,
        opportunity: Opportunity,
        profile: CandidateProfile,
        semantic_sim: Optional[float] = None,
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Computes transparent, explainable compatibility breakdown.
        """
        w = weights or cls.DEFAULT_WEIGHTS

        # 1. Semantic Similarity
        if semantic_sim is None:
            candidate_text = f"{profile.headline or ''} {profile.bio or ''} {' '.join(profile.skills or [])}"
            opp_text = f"{opportunity.title} {opportunity.description} {' '.join(opportunity.required_skills or [])}"
            emb_c = embedding_service.embed_text(candidate_text)
            emb_o = embedding_service.embed_text(opp_text)
            semantic_score = max(0.0, min(1.0, embedding_service.cosine_similarity(emb_c, emb_o)))
        else:
            semantic_score = max(0.0, min(1.0, semantic_sim))

        # 2. Skills Overlap
        candidate_skills = {s.lower().strip() for s in (profile.skills or [])}
        req_skills = [s.strip() for s in (opportunity.required_skills or [])]
        nice_skills = [s.strip() for s in (opportunity.nice_to_have_skills or [])]

        matched_req = [s for s in req_skills if s.lower() in candidate_skills]
        missing_req = [s for s in req_skills if s.lower() not in candidate_skills]
        matched_nice = [s for s in nice_skills if s.lower() in candidate_skills]
        missing_nice = [s for s in nice_skills if s.lower() not in candidate_skills]

        req_weight = 0.75
        nice_weight = 0.25

        req_ratio = len(matched_req) / max(len(req_skills), 1)
        nice_ratio = len(matched_nice) / max(len(nice_skills), 1) if nice_skills else 1.0

        skills_score = req_ratio * req_weight + nice_ratio * nice_weight

        # 3. Experience Compatibility
        cand_exp = profile.experience_years
        min_exp = opportunity.min_years_experience
        max_exp = opportunity.max_years_experience

        if cand_exp >= min_exp and cand_exp <= max_exp + 2:
            exp_score = 1.0
        elif cand_exp < min_exp:
            deficit = min_exp - cand_exp
            exp_score = max(0.0, 1.0 - (deficit * 0.25))
        else:
            surplus = cand_exp - (max_exp + 2)
            exp_score = max(0.6, 1.0 - (surplus * 0.1))

        # 4. Role Relevance
        title_lower = opportunity.title.lower()
        cand_title = (profile.headline or "").lower()
        pref_roles = [r.lower() for r in (profile.preferred_roles or [])]

        role_match = 0.5  # baseline
        if any(r in title_lower for r in pref_roles):
            role_match = 1.0
        elif cand_title and any(token in title_lower for token in cand_title.split() if len(token) > 3):
            role_match = 0.85
        elif any(token in title_lower for s in (profile.skills or []) for token in s.lower().split() if len(token) > 3):
            role_match = 0.70

        # 5. Preference Compatibility
        pref_score = 1.0
        pref_penalties = 0.0

        if profile.preferred_locations and opportunity.location not in profile.preferred_locations:
            if opportunity.work_mode != "remote":
                pref_penalties += 0.4
        if profile.preferred_work_modes and opportunity.work_mode not in profile.preferred_work_modes:
            pref_penalties += 0.3
        cand_min_sal = profile.preferred_min_salary or 0
        opp_max_sal = opportunity.max_salary or 0
        if cand_min_sal > 0 and opp_max_sal > 0:
            if opp_max_sal < cand_min_sal:
                pref_penalties += 0.3

        pref_score = max(0.0, 1.0 - pref_penalties)

        # Weighted aggregate
        overall_score = (
            semantic_score * w.get("semantic_similarity", 0.3) +
            skills_score * w.get("skills_overlap", 0.3) +
            exp_score * w.get("experience_compatibility", 0.15) +
            role_match * w.get("role_relevance", 0.15) +
            pref_score * w.get("preference_compatibility", 0.10)
        )
        overall_score = round(overall_score * 100.0, 1)

        # Eligibility check
        eligibility = cls.evaluate_eligibility(opportunity, profile)

        # Generate transparent explanation
        explanations = []
        if req_ratio >= 0.8:
            explanations.append(f"Strong required skill alignment ({len(matched_req)}/{len(req_skills)} matched: {', '.join(matched_req[:3])}).")
        elif req_ratio >= 0.5:
            explanations.append(f"Moderate core skill overlap ({len(matched_req)}/{len(req_skills)} matched).")
        else:
            explanations.append(f"Notable skill gap in required competencies (Missing: {', '.join(missing_req[:3])}).")

        if exp_score >= 0.9:
            explanations.append(f"Candidate experience ({cand_exp:.1f} yrs) fits expected tenure ({min_exp}-{max_exp} yrs).")
        else:
            explanations.append(f"Experience gap: role expects {min_exp}+ yrs while profile has {cand_exp:.1f} yrs.")

        if opportunity.work_mode in (profile.preferred_work_modes or []):
            explanations.append(f"Work mode '{opportunity.work_mode}' aligns with preferences.")

        return {
            "overall_compatibility": overall_score,
            "components": {
                "semantic_similarity": round(semantic_score * 100, 1),
                "skills_overlap": round(skills_score * 100, 1),
                "experience_compatibility": round(exp_score * 100, 1),
                "role_relevance": round(role_match * 100, 1),
                "preference_compatibility": round(pref_score * 100, 1)
            },
            "weights_used": w,
            "matching_skills": matched_req + matched_nice,
            "missing_skills": missing_req,
            "nice_to_have_missing": missing_nice,
            "eligibility": eligibility,
            "explanation": " ".join(explanations),
            "methodology_notice": "Explainable heuristic weighted matching engine; scores reflect transparent feature overlap."
        }

matching_engine = MatchingEngine()
