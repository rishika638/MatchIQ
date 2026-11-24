from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.entities import Opportunity, CandidateProfile, SavedOpportunity, UserPreference, AgentAction
from app.services.search_service import search_service
from app.services.matching_service import matching_engine

# --- Pydantic Argument Schemas for Strict Tool Validation ---

class SearchOpportunitiesArgs(BaseModel):
    query: str = Field(..., description="Natural language search query e.g. 'Senior Python distributed systems' or 'Frontend intern'")
    locations: Optional[List[str]] = Field(default=None, description="Optional list of locations")
    work_modes: Optional[List[str]] = Field(default=None, description="Optional work modes: remote, hybrid, onsite")
    opportunity_types: Optional[List[str]] = Field(default=None, description="Optional types: full-time, contract, internship")
    min_salary: Optional[int] = Field(default=None, description="Optional minimum annual compensation")

class GetOpportunityDetailsArgs(BaseModel):
    opportunity_id: str = Field(..., description="The unique ID of the opportunity, e.g. 'opp-seed-001'")

class SaveOpportunityArgs(BaseModel):
    opportunity_id: str = Field(..., description="The unique ID of the opportunity to save")
    notes: Optional[str] = Field(default=None, description="Optional user notes")

class CompareOpportunitiesArgs(BaseModel):
    opportunity_ids: List[str] = Field(..., description="List of 2 to 4 opportunity IDs to compare side by side", min_length=2, max_length=4)

class UpdateCandidatePreferencesArgs(BaseModel):
    preferred_locations: Optional[List[str]] = Field(default=None, description="Preferred locations list")
    preferred_work_modes: Optional[List[str]] = Field(default=None, description="Preferred work modes e.g. ['remote']")
    preferred_opportunity_types: Optional[List[str]] = Field(default=None, description="e.g. ['full-time', 'internship']")
    preferred_min_salary: Optional[int] = Field(default=None, description="Minimum salary threshold")

class AnalyzeSkillGapsArgs(BaseModel):
    opportunity_id: str = Field(..., description="The unique ID of the opportunity to analyze against candidate profile")

# --- Tool Execution Registry ---

class CareerAgentTools:
    @staticmethod
    def search_opportunities(db: Session, user_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        validated = SearchOpportunitiesArgs(**args)
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
        
        flt = {}
        if validated.locations:
            flt["locations"] = validated.locations
        if validated.work_modes:
            flt["work_modes"] = validated.work_modes
        if validated.opportunity_types:
            flt["opportunity_types"] = validated.opportunity_types
        if validated.min_salary:
            flt["min_salary"] = validated.min_salary

        search_res = search_service.hybrid_search(
            db=db,
            query=validated.query,
            filters=flt,
            candidate_profile=profile,
            enable_reranking=True,
            page=1,
            page_size=5
        )

        compact_matches = []
        for r in search_res["results"]:
            opp = r["opportunity"]
            compat = r.get("compatibility") or {}
            compact_matches.append({
                "id": opp["id"],
                "title": opp["title"],
                "company": opp["company"],
                "location": opp["location"],
                "work_mode": opp["work_mode"],
                "salary_range": f"${opp['min_salary']:,} - ${opp['max_salary']:,}" if opp['max_salary'] else "Not disclosed",
                "required_skills": opp["required_skills"],
                "compatibility_score": compat.get("overall_compatibility"),
                "explanation": compat.get("explanation")
            })

        return {
            "query": validated.query,
            "total_matches": search_res["total_matches"],
            "top_opportunities": compact_matches
        }

    @staticmethod
    def get_opportunity_details(db: Session, user_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        validated = GetOpportunityDetailsArgs(**args)
        opp = db.query(Opportunity).filter(Opportunity.id == validated.opportunity_id).first()
        if not opp:
            return {"error": f"Opportunity with ID '{validated.opportunity_id}' not found in database."}

        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
        compat = None
        if profile:
            compat = matching_engine.calculate_compatibility(opp, profile)

        return {
            "id": opp.id,
            "title": opp.title,
            "company": opp.company,
            "department": opp.department,
            "location": opp.location,
            "work_mode": opp.work_mode,
            "opportunity_type": opp.opportunity_type,
            "experience_range": f"{opp.min_years_experience} - {opp.max_years_experience} years",
            "compensation": f"${opp.min_salary:,} - ${opp.max_salary:,} {opp.currency}",
            "description": opp.description,
            "responsibilities": opp.responsibilities,
            "required_skills": opp.required_skills,
            "nice_to_have_skills": opp.nice_to_have_skills,
            "benefits": opp.benefits,
            "compatibility": compat
        }

    @staticmethod
    def save_opportunity(db: Session, user_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        validated = SaveOpportunityArgs(**args)
        opp = db.query(Opportunity).filter(Opportunity.id == validated.opportunity_id).first()
        if not opp:
            return {"error": f"Opportunity '{validated.opportunity_id}' does not exist."}

        existing = db.query(SavedOpportunity).filter(
            SavedOpportunity.user_id == user_id,
            SavedOpportunity.opportunity_id == validated.opportunity_id
        ).first()

        if existing:
            if validated.notes:
                existing.notes = validated.notes
                db.commit()
            return {"status": "already_saved", "message": f"Opportunity '{opp.title}' at {opp.company} is already in your saved tracker.", "opportunity_id": opp.id}

        saved_item = SavedOpportunity(
            user_id=user_id,
            opportunity_id=validated.opportunity_id,
            status="saved",
            notes=validated.notes
        )
        db.add(saved_item)
        db.commit()
        return {"status": "success", "message": f"Successfully saved '{opp.title}' at {opp.company} to your opportunity tracker.", "opportunity_id": opp.id}

    @staticmethod
    def compare_opportunities(db: Session, user_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        validated = CompareOpportunitiesArgs(**args)
        opps = db.query(Opportunity).filter(Opportunity.id.in_(validated.opportunity_ids)).all()
        if not opps:
            return {"error": "None of the specified opportunities were found."}

        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
        comparisons = []
        for opp in opps:
            compat = matching_engine.calculate_compatibility(opp, profile) if profile else None
            comparisons.append({
                "id": opp.id,
                "title": opp.title,
                "company": opp.company,
                "location": opp.location,
                "work_mode": opp.work_mode,
                "salary": f"${opp.min_salary:,} - ${opp.max_salary:,}",
                "required_skills": opp.required_skills,
                "compatibility_score": compat.get("overall_compatibility") if compat else None,
                "matching_skills": compat.get("matching_skills") if compat else [],
                "missing_skills": compat.get("missing_skills") if compat else [],
                "eligibility": compat.get("eligibility") if compat else None
            })

        return {"compared_count": len(comparisons), "opportunities": comparisons}

    @staticmethod
    def get_candidate_profile(db: Session, user_id: str, args: Dict[str, Any] = None) -> Dict[str, Any]:
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
        if not profile:
            return {"error": "No candidate profile found. Upload resume or edit profile."}

        return {
            "headline": profile.headline,
            "bio": profile.bio,
            "experience_years": profile.experience_years,
            "skills": profile.skills,
            "education": profile.education,
            "preferred_locations": profile.preferred_locations,
            "preferred_work_modes": profile.preferred_work_modes,
            "preferred_opportunity_types": profile.preferred_opportunity_types,
            "preferred_min_salary": profile.preferred_min_salary,
            "preferred_roles": profile.preferred_roles
        }

    @staticmethod
    def update_candidate_preferences(db: Session, user_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        validated = UpdateCandidatePreferencesArgs(**args)
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
        if not profile:
            return {"error": "Candidate profile must exist before updating preferences."}

        updated_fields = []
        if validated.preferred_locations is not None:
            profile.preferred_locations = validated.preferred_locations
            updated_fields.append("preferred_locations")
        if validated.preferred_work_modes is not None:
            profile.preferred_work_modes = validated.preferred_work_modes
            updated_fields.append("preferred_work_modes")
        if validated.preferred_opportunity_types is not None:
            profile.preferred_opportunity_types = validated.preferred_opportunity_types
            updated_fields.append("preferred_opportunity_types")
        if validated.preferred_min_salary is not None:
            profile.preferred_min_salary = validated.preferred_min_salary
            updated_fields.append("preferred_min_salary")

        db.commit()
        return {
            "status": "success",
            "message": f"Updated candidate preferences: {', '.join(updated_fields)}",
            "updated_fields": updated_fields
        }

    @staticmethod
    def analyze_skill_gaps(db: Session, user_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        validated = AnalyzeSkillGapsArgs(**args)
        opp = db.query(Opportunity).filter(Opportunity.id == validated.opportunity_id).first()
        if not opp:
            return {"error": f"Opportunity '{validated.opportunity_id}' not found."}

        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
        if not profile:
            return {"error": "Candidate profile needed for skill gap analysis."}

        compat = matching_engine.calculate_compatibility(opp, profile)
        
        # Actionable preparation roadmap
        prep_recommendations = []
        for missing in compat.get("missing_skills", []):
            prep_recommendations.append(f"Focus on foundational hands-on projects featuring {missing} to bridge required role qualifications.")

        return {
            "opportunity_id": opp.id,
            "opportunity_title": opp.title,
            "company": opp.company,
            "overall_compatibility": compat["overall_compatibility"],
            "component_scores": compat["components"],
            "matching_skills": compat["matching_skills"],
            "missing_required_skills": compat["missing_skills"],
            "missing_nice_to_have": compat["nice_to_have_missing"],
            "preparation_suggestions": prep_recommendations,
            "eligibility": compat["eligibility"]
        }
