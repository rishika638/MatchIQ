import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey,
    Index, JSON, Enum, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.core.database import Base, VectorType

def generate_uuid():
    return str(uuid.uuid4())

def get_utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    role = Column(String(50), default="candidate", nullable=False)  # candidate, recruiter, admin
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    # Relationships
    memberships = relationship("OrganizationMember", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("CandidateProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    saved_opportunities = relationship("SavedOpportunity", back_populates="user", cascade="all, delete-orphan")
    search_history = relationship("SearchHistory", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("RecommendationFeedback", back_populates="user", cascade="all, delete-orphan")


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    plan = Column(String(50), default="starter", nullable=False)  # starter, pro, enterprise
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    # Relationships
    members = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    opportunities = relationship("Opportunity", back_populates="organization", cascade="all, delete-orphan")
    ingestion_jobs = relationship("IngestionJob", back_populates="organization", cascade="all, delete-orphan")


class OrganizationMember(Base):
    __tablename__ = "organization_members"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), default="member", nullable=False)  # owner, admin, member, viewer
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="memberships")

    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_org_member"),
    )


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    
    headline = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    experience_years = Column(Float, default=0.0, nullable=False)
    
    # Preferred constraints
    preferred_locations = Column(JSON, default=list, nullable=False)  # list of strings
    preferred_work_modes = Column(JSON, default=list, nullable=False)  # ["remote", "hybrid", "onsite"]
    preferred_opportunity_types = Column(JSON, default=list, nullable=False)  # ["full-time", "contract", "internship"]
    preferred_min_salary = Column(Integer, default=0, nullable=False)
    preferred_currency = Column(String(10), default="USD", nullable=False)
    
    # Skills and extraction
    skills = Column(JSON, default=list, nullable=False)  # list of skill strings
    education = Column(JSON, default=list, nullable=False)  # list of edu objects
    experience_records = Column(JSON, default=list, nullable=False)  # list of job history objects
    projects = Column(JSON, default=list, nullable=False)  # list of project objects
    preferred_roles = Column(JSON, default=list, nullable=False)
    
    resume_filename = Column(String(255), nullable=True)
    resume_raw_text = Column(Text, nullable=True)
    extracted_data = Column(JSON, default=dict, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    user = relationship("User", back_populates="profile")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False, index=True)
    normalized_name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), default="general", nullable=False)  # language, framework, database, cloud, etc.
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(String(100), primary_key=True, default=generate_uuid)  # Support string IDs like opp-seed-001 or UUIDs
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    department = Column(String(255), nullable=True)
    location = Column(String(255), nullable=False, index=True)
    work_mode = Column(String(50), default="hybrid", nullable=False, index=True)  # remote, hybrid, onsite
    opportunity_type = Column(String(50), default="full-time", nullable=False, index=True)  # full-time, contract, internship
    experience_level = Column(String(50), default="mid", nullable=False, index=True)  # entry, mid, senior, lead, staff
    
    min_years_experience = Column(Integer, default=0, nullable=False)
    max_years_experience = Column(Integer, default=15, nullable=False)
    min_salary = Column(Integer, default=0, nullable=False)
    max_salary = Column(Integer, default=0, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    
    description = Column(Text, nullable=False)
    responsibilities = Column(JSON, default=list, nullable=False)
    benefits = Column(JSON, default=list, nullable=False)
    
    required_skills = Column(JSON, default=list, nullable=False)
    nice_to_have_skills = Column(JSON, default=list, nullable=False)
    
    is_synthetic = Column(Boolean, default=True, nullable=False)
    source = Column(String(100), default="manual", nullable=False)
    application_url = Column(String(500), nullable=True)
    contact_email = Column(String(255), nullable=True)
    status = Column(String(50), default="active", nullable=False, index=True)  # active, closed, draft
    
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="opportunities")
    opportunity_skills = relationship("OpportunitySkill", back_populates="opportunity", cascade="all, delete-orphan")
    saved_by = relationship("SavedOpportunity", back_populates="opportunity", cascade="all, delete-orphan")
    feedbacks = relationship("RecommendationFeedback", back_populates="opportunity", cascade="all, delete-orphan")


class OpportunitySkill(Base):
    __tablename__ = "opportunity_skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    opportunity_id = Column(String(100), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False, index=True)
    is_required = Column(Boolean, default=True, nullable=False)
    importance_weight = Column(Float, default=1.0, nullable=False)

    opportunity = relationship("Opportunity", back_populates="opportunity_skills")


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    entity_type = Column(String(50), nullable=False, index=True)  # opportunity, candidate_profile, search_query
    entity_id = Column(String(100), nullable=False, index=True)
    model_name = Column(String(100), nullable=False)
    embedding_dimension = Column(Integer, default=384, nullable=False)
    
    # Hybrid vector: Vector(384) on PostgreSQL, JSON on SQLite
    vector = Column(VectorType(dim=384), nullable=False)
    text_hash = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    __table_args__ = (
        Index("idx_embedding_entity", "entity_type", "entity_id"),
    )


class SavedOpportunity(Base):
    __tablename__ = "saved_opportunities"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    opportunity_id = Column(String(100), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    status = Column(String(50), default="saved", nullable=False, index=True)  # saved, applied, interviewing, offered, archived
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    user = relationship("User", back_populates="saved_opportunities")
    opportunity = relationship("Opportunity", back_populates="saved_by")

    __table_args__ = (
        UniqueConstraint("user_id", "opportunity_id", name="uq_user_saved_opp"),
    )


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    
    query_text = Column(Text, nullable=False)
    filters = Column(JSON, default=dict, nullable=False)
    retrieval_method = Column(String(50), default="hybrid_rrf", nullable=False)
    result_count = Column(Integer, default=0, nullable=False)
    latency_ms = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    user = relationship("User", back_populates="search_history")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    
    title = Column(String(255), default="Career Strategy Chat", nullable=False)
    context_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
    agent_actions = relationship("AgentAction", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender = Column(String(20), nullable=False)  # user, assistant, system, tool
    content = Column(Text, nullable=False)
    tool_calls = Column(JSON, default=list, nullable=True)
    tool_results = Column(JSON, default=list, nullable=True)
    metadata_json = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    
    key = Column(String(100), nullable=False, index=True)
    value = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    user = relationship("User", back_populates="preferences")

    __table_args__ = (
        UniqueConstraint("user_id", "key", name="uq_user_preference_key"),
    )


class AgentAction(Base):
    __tablename__ = "agent_actions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    
    tool_name = Column(String(100), nullable=False, index=True)
    arguments = Column(JSON, default=dict, nullable=False)
    result = Column(JSON, default=dict, nullable=True)
    execution_status = Column(String(50), default="executed", nullable=False)  # pending, executed, failed, rejected
    requires_confirmation = Column(Boolean, default=False, nullable=False)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    conversation = relationship("Conversation", back_populates="agent_actions")


class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedbacks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    opportunity_id = Column(String(100), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    feedback_type = Column(String(50), nullable=False, index=True)  # relevant, not_relevant, applied, not_interested
    query_or_context = Column(Text, nullable=True)
    score_snapshot = Column(JSON, default=dict, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    user = relationship("User", back_populates="feedbacks")
    opportunity = relationship("Opportunity", back_populates="feedbacks")


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # json, csv
    total_records = Column(Integer, default=0, nullable=False)
    processed_records = Column(Integer, default=0, nullable=False)
    successful_records = Column(Integer, default=0, nullable=False)
    failed_records = Column(Integer, default=0, nullable=False)
    status = Column(String(50), default="pending", nullable=False, index=True)  # pending, processing, completed, failed
    errors_log = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    organization = relationship("Organization", back_populates="ingestion_jobs")


class EvaluationQuery(Base):
    __tablename__ = "evaluation_queries"

    id = Column(String(50), primary_key=True)  # eval-q01, etc.
    query_text = Column(Text, nullable=False)
    candidate_profile_json = Column(JSON, default=dict, nullable=False)
    intent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    judgments = relationship("RelevanceJudgment", back_populates="query", cascade="all, delete-orphan")


class RelevanceJudgment(Base):
    __tablename__ = "relevance_judgments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    query_id = Column(String(50), ForeignKey("evaluation_queries.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id = Column(String(100), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    grade = Column(Integer, default=0, nullable=False)  # 0 to 3
    rationale = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    query = relationship("EvaluationQuery", back_populates="judgments")


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    
    dataset_version = Column(String(50), default="v1.0", nullable=False)
    retrieval_method = Column(String(50), nullable=False, index=True)  # keyword, semantic, hybrid, hybrid_reranked
    embedding_model = Column(String(100), nullable=False)
    reranker_model = Column(String(100), nullable=True)
    
    precision_at_k = Column(JSON, default=dict, nullable=False)  # {"k=1": 1.0, "k=3": 0.88, "k=5": 0.76}
    recall_at_k = Column(JSON, default=dict, nullable=False)     # {"k=5": 0.82, "k=10": 0.95}
    mrr = Column(Float, default=0.0, nullable=False)
    ndcg_at_k = Column(JSON, default=dict, nullable=False)       # {"k=3": 0.91, "k=5": 0.88, "k=10": 0.85}
    average_latency_ms = Column(Float, default=0.0, nullable=False)
    detailed_metrics = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
