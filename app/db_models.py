# app/db_models.py
import uuid
from sqlalchemy import Column, Float, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class FreelancerEmbedding(Base):
    __tablename__ = 'freelancer_embeddings'

    freelancer_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bio_embedding = Column(Vector(1536))
    past_project_embedding = Column(Vector(1536))
    success_rate = Column(Float)
    client_satisfaction = Column(Float)
    communication_score = Column(Float)
    hourly_rate = Column(Float)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now())
