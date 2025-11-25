# app/db_models.py
import uuid
from sqlalchemy import Column, Float, DateTime, func, String, Integer, DECIMAL, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class FreelancerEmbedding(Base):
    __tablename__ = 'freelancer_embeddings'

    freelancer_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bio_embedding = Column(Vector(1536))  # OpenAI: 1536, Gemini: 768 (update via migration)
    past_project_embedding = Column(Vector(1536), nullable=True)
    skills = Column(JSONB, nullable=False)  # Array of skills ["React", "Node.js", ...]
    success_rate = Column(Float, nullable=True)
    client_satisfaction = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    hourly_rate = Column(DECIMAL(10, 2), nullable=True)
    availability_status = Column(String(20), nullable=True, default='available')  # 'available', 'busy', 'unavailable'
    location = Column(String(255), nullable=True)
    experience_level = Column(Integer, nullable=True)  # 1-5 scale
    total_projects = Column(Integer, nullable=True, default=0)
    embedding_model = Column(String(50), nullable=False)  # 'openai-text-embedding-3-large', 'gemini-embedding-001'
    embedding_version = Column(String(20), nullable=False)
    data_quality_score = Column(Float, nullable=False)  # Profile completeness (0.0-1.0)
    meta_info = Column(JSONB, nullable=True)  # {is_new_freelancer, has_past_projects, feedback_count}
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now(), nullable=False)


class ProjectEmbedding(Base):
    __tablename__ = 'project_embeddings'

    project_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_embedding = Column(Vector(1536), nullable=False)  # OpenAI: 1536, Gemini: 768
    required_skills = Column(JSONB, nullable=False)  # Array of required skills ["Python", "Django", ...]
    budget = Column(DECIMAL(14, 2), nullable=False)
    required_experience_level = Column(Integer, nullable=False)  # Minimum freelancer level (1-5)
    preferred_location = Column(String(255), nullable=True)  # NULL = remote
    status = Column(String(20), nullable=False, default='open')  # 'open', 'in_progress', 'completed', etc.
    project_title = Column(String(255), nullable=False)  # Stored for quick reference
    embedding_model = Column(String(50), nullable=False)
    embedding_version = Column(String(20), nullable=False)
    data_quality_score = Column(Float, nullable=False)  # Project description quality (0.0-1.0)
    meta_info = Column(JSONB, nullable=False)  # {is_generic_description, skill_count}
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now(), nullable=False)


class RecommendationLog(Base):
    __tablename__ = 'recommendation_logs'

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_type = Column(String(20), nullable=False)  # 'freelancer' or 'project'
    request_id = Column(UUID(as_uuid=True), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)  # freelancer_id or project_id requesting recommendations
    recommended_ids = Column(JSONB, nullable=False)  # Array of recommended IDs with scores
    filters_applied = Column(JSONB, nullable=True)  # Hard filters used in query
    avg_score = Column(Float, nullable=True)  # Average score of top 10 results
    result_count = Column(Integer, nullable=False)
    execution_time_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
