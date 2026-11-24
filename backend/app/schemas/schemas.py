from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# --- Auth & User ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    role: Optional[str] = "candidate"
    organization_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

# --- Candidate Profile ---
class CandidateProfileUpdate(BaseModel):
    headline: Optional[str] = None
    bio: Optional[str] = None
    experience_years: Optional[float] = None
    skills: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    preferred_work_modes: Optional[List[str]] = None
    preferred_opportunity_types: Optional[List[str]] = None
    preferred_min_salary: Optional[int] = None
    preferred_currency: Optional[str] = "USD"
    preferred_roles: Optional[List[str]] = None
    education: Optional[List[Dict[str, Any]]] = None
    experience_records: Optional[List[Dict[str, Any]]] = None
    projects: Optional[List[Dict[str, Any]]] = None

class CandidateProfileResponse(BaseModel):
    id: str
    user_id: str
    headline: Optional[str]
    bio: Optional[str]
    experience_years: float
    skills: List[str]
    preferred_locations: List[str]
    preferred_work_modes: List[str]
    preferred_opportunity_types: List[str]
    preferred_min_salary: int
    preferred_currency: str
    preferred_roles: List[str]
    education: List[Dict[str, Any]]
    experience_records: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    resume_filename: Optional[str]
    updated_at: datetime

# --- Opportunities ---
class OpportunitySkillItem(BaseModel):
    skill_name: str
    is_required: bool
    importance_weight: float

class OpportunityItem(BaseModel):
    id: str
    title: str
    company: str
    department: Optional[str]
    location: str
    work_mode: str
    opportunity_type: str
    experience_level: str
    min_years_experience: int
    max_years_experience: int
    min_salary: int
    max_salary: int
    currency: str
    description: str
    responsibilities: List[str]
    benefits: List[str]
    required_skills: List[str]
    nice_to_have_skills: List[str]
    is_synthetic: bool
    source: str
    application_url: Optional[str]
    contact_email: Optional[str]
    created_at: Optional[str]

# --- Search ---
class SearchRequest(BaseModel):
    query: str = Field(default="", description="Natural language search query")
    locations: Optional[List[str]] = None
    work_modes: Optional[List[str]] = None
    opportunity_types: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    min_salary: Optional[int] = None
    max_experience: Optional[int] = None
    enable_reranking: bool = False
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=15, ge=1, le=50)

# --- Agent Chat ---
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    response: str
    tools_executed: List[Dict[str, Any]]
    model_used: str

# --- Feedback ---
class FeedbackCreate(BaseModel):
    opportunity_id: str
    feedback_type: str = Field(..., description="relevant, not_relevant, applied, not_interested")
    query_or_context: Optional[str] = None
    notes: Optional[str] = None

# --- Saved Opportunity ---
class SavedOpportunityCreate(BaseModel):
    opportunity_id: str
    status: Optional[str] = "saved"
    notes: Optional[str] = None

class SavedOpportunityUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
