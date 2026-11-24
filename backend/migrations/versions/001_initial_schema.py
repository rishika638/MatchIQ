"""initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-23 16:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from app.core.database import VectorType

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 0. Enable pgvector extension if postgres
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, default=False),
        sa.Column('role', sa.String(length=50), nullable=False, default='candidate'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. organizations
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('plan', sa.String(length=50), nullable=False, default='starter'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_slug'), 'organizations', ['slug'], unique=True)

    # 3. organization_members
    op.create_table(
        'organization_members',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, default='member'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'user_id', name='uq_org_member')
    )
    op.create_index(op.f('ix_organization_members_org_id'), 'organization_members', ['organization_id'], unique=False)
    op.create_index(op.f('ix_organization_members_user_id'), 'organization_members', ['user_id'], unique=False)

    # 4. candidate_profiles
    op.create_table(
        'candidate_profiles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=True),
        sa.Column('headline', sa.String(length=255), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('experience_years', sa.Float(), nullable=False, default=0.0),
        sa.Column('preferred_locations', sa.JSON(), nullable=False),
        sa.Column('preferred_work_modes', sa.JSON(), nullable=False),
        sa.Column('preferred_opportunity_types', sa.JSON(), nullable=False),
        sa.Column('preferred_min_salary', sa.Integer(), nullable=False, default=0),
        sa.Column('preferred_currency', sa.String(length=10), nullable=False, default='USD'),
        sa.Column('skills', sa.JSON(), nullable=False),
        sa.Column('education', sa.JSON(), nullable=False),
        sa.Column('experience_records', sa.JSON(), nullable=False),
        sa.Column('projects', sa.JSON(), nullable=False),
        sa.Column('preferred_roles', sa.JSON(), nullable=False),
        sa.Column('resume_filename', sa.String(length=255), nullable=True),
        sa.Column('resume_raw_text', sa.Text(), nullable=True),
        sa.Column('extracted_data', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # 5. skills
    op.create_table(
        'skills',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('normalized_name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False, default='general'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_skills_name'), 'skills', ['name'], unique=True)
    op.create_index(op.f('ix_skills_normalized_name'), 'skills', ['normalized_name'], unique=True)

    # 6. opportunities
    op.create_table(
        'opportunities',
        sa.Column('id', sa.String(length=100), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('company', sa.String(length=255), nullable=False),
        sa.Column('department', sa.String(length=255), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.Column('work_mode', sa.String(length=50), nullable=False, default='hybrid'),
        sa.Column('opportunity_type', sa.String(length=50), nullable=False, default='full-time'),
        sa.Column('experience_level', sa.String(length=50), nullable=False, default='mid'),
        sa.Column('min_years_experience', sa.Integer(), nullable=False, default=0),
        sa.Column('max_years_experience', sa.Integer(), nullable=False, default=15),
        sa.Column('min_salary', sa.Integer(), nullable=False, default=0),
        sa.Column('max_salary', sa.Integer(), nullable=False, default=0),
        sa.Column('currency', sa.String(length=10), nullable=False, default='USD'),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('responsibilities', sa.JSON(), nullable=False),
        sa.Column('benefits', sa.JSON(), nullable=False),
        sa.Column('required_skills', sa.JSON(), nullable=False),
        sa.Column('nice_to_have_skills', sa.JSON(), nullable=False),
        sa.Column('is_synthetic', sa.Boolean(), nullable=False, default=True),
        sa.Column('source', sa.String(length=100), nullable=False, default='manual'),
        sa.Column('application_url', sa.String(length=500), nullable=True),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_opportunities_title'), 'opportunities', ['title'], unique=False)
    op.create_index(op.f('ix_opportunities_company'), 'opportunities', ['company'], unique=False)
    op.create_index(op.f('ix_opportunities_location'), 'opportunities', ['location'], unique=False)
    op.create_index(op.f('ix_opportunities_work_mode'), 'opportunities', ['work_mode'], unique=False)
    op.create_index(op.f('ix_opportunities_type'), 'opportunities', ['opportunity_type'], unique=False)
    op.create_index(op.f('ix_opportunities_status'), 'opportunities', ['status'], unique=False)

    # Full text search index on postgres
    if bind.dialect.name == "postgresql":
        op.execute("""
            CREATE INDEX ix_opportunities_fts ON opportunities 
            USING gin(to_tsvector('english', title || ' ' || company || ' ' || description));
        """)

    # 7. opportunity_skills
    op.create_table(
        'opportunity_skills',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('opportunity_id', sa.String(length=100), nullable=False),
        sa.Column('skill_name', sa.String(length=100), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=False, default=True),
        sa.Column('importance_weight', sa.Float(), nullable=False, default=1.0),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_opportunity_skills_opp_id'), 'opportunity_skills', ['opportunity_id'], unique=False)
    op.create_index(op.f('ix_opportunity_skills_skill_name'), 'opportunity_skills', ['skill_name'], unique=False)

    # 8. embeddings
    op.create_table(
        'embeddings',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.String(length=100), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('embedding_dimension', sa.Integer(), nullable=False, default=384),
        sa.Column('vector', VectorType(dim=384), nullable=False),
        sa.Column('text_hash', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_embeddings_entity'), 'embeddings', ['entity_type', 'entity_id'], unique=False)
    op.create_index(op.f('ix_embeddings_hash'), 'embeddings', ['text_hash'], unique=False)

    # 9. saved_opportunities
    op.create_table(
        'saved_opportunities',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=True),
        sa.Column('opportunity_id', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, default='saved'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'opportunity_id', name='uq_user_saved_opp')
    )

    # 10. search_history
    op.create_table(
        'search_history',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=True),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('filters', sa.JSON(), nullable=False),
        sa.Column('retrieval_method', sa.String(length=50), nullable=False, default='hybrid_rrf'),
        sa.Column('result_count', sa.Integer(), nullable=False, default=0),
        sa.Column('latency_ms', sa.Float(), nullable=False, default=0.0),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 11. conversations
    op.create_table(
        'conversations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False, default='Career Strategy Chat'),
        sa.Column('context_summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 12. messages
    op.create_table(
        'messages',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('conversation_id', sa.String(length=36), nullable=False),
        sa.Column('sender', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', sa.JSON(), nullable=True),
        sa.Column('tool_results', sa.JSON(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 13. user_preferences
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=True),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'key', name='uq_user_preference_key')
    )

    # 14. agent_actions
    op.create_table(
        'agent_actions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('conversation_id', sa.String(length=36), nullable=True),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=True),
        sa.Column('tool_name', sa.String(length=100), nullable=False),
        sa.Column('arguments', sa.JSON(), nullable=False),
        sa.Column('result', sa.JSON(), nullable=True),
        sa.Column('execution_status', sa.String(length=50), nullable=False, default='executed'),
        sa.Column('requires_confirmation', sa.Boolean(), nullable=False, default=False),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 15. recommendation_feedbacks
    op.create_table(
        'recommendation_feedbacks',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=True),
        sa.Column('opportunity_id', sa.String(length=100), nullable=False),
        sa.Column('feedback_type', sa.String(length=50), nullable=False),
        sa.Column('query_or_context', sa.Text(), nullable=True),
        sa.Column('score_snapshot', sa.JSON(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 16. ingestion_jobs
    op.create_table(
        'ingestion_jobs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=True),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('total_records', sa.Integer(), nullable=False, default=0),
        sa.Column('processed_records', sa.Integer(), nullable=False, default=0),
        sa.Column('successful_records', sa.Integer(), nullable=False, default=0),
        sa.Column('failed_records', sa.Integer(), nullable=False, default=0),
        sa.Column('status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('errors_log', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # 17. evaluation_queries
    op.create_table(
        'evaluation_queries',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('candidate_profile_json', sa.JSON(), nullable=False),
        sa.Column('intent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 18. relevance_judgments
    op.create_table(
        'relevance_judgments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('query_id', sa.String(length=50), nullable=False),
        sa.Column('opportunity_id', sa.String(length=100), nullable=False),
        sa.Column('grade', sa.Integer(), nullable=False, default=0),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['query_id'], ['evaluation_queries.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 19. evaluation_runs
    op.create_table(
        'evaluation_runs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=True),
        sa.Column('dataset_version', sa.String(length=50), nullable=False, default='v1.0'),
        sa.Column('retrieval_method', sa.String(length=50), nullable=False),
        sa.Column('embedding_model', sa.String(length=100), nullable=False),
        sa.Column('reranker_model', sa.String(length=100), nullable=True),
        sa.Column('precision_at_k', sa.JSON(), nullable=False),
        sa.Column('recall_at_k', sa.JSON(), nullable=False),
        sa.Column('mrr', sa.Float(), nullable=False, default=0.0),
        sa.Column('ndcg_at_k', sa.JSON(), nullable=False),
        sa.Column('average_latency_ms', sa.Float(), nullable=False, default=0.0),
        sa.Column('detailed_metrics', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('evaluation_runs')
    op.drop_table('relevance_judgments')
    op.drop_table('evaluation_queries')
    op.drop_table('ingestion_jobs')
    op.drop_table('recommendation_feedbacks')
    op.drop_table('agent_actions')
    op.drop_table('user_preferences')
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('search_history')
    op.drop_table('saved_opportunities')
    op.drop_table('embeddings')
    op.drop_table('opportunity_skills')
    op.drop_table('opportunities')
    op.drop_table('skills')
    op.drop_table('candidate_profiles')
    op.drop_table('organization_members')
    op.drop_table('organizations')
    op.drop_table('users')
