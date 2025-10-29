# app/schemas/embeddings.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

# Freelancer Embeddings

class FreelancerMetadata(BaseModel):
    is_new_freelancer: bool
    has_past_projects: bool
    feedback_count: int

class FreelancerEmbeddingCreateRequest(BaseModel):
    freelancer_id: UUID
    bio: str = Field(..., min_length=100, description="Freelancer bio (minimum 100 characters)")
    past_projects: str = Field(default="", description="Concatenated past project descriptions")
    skills: List[str] = Field(..., min_length=3, description="Array of skills (minimum 3)")
    success_rate: float = Field(..., ge=0.0, le=1.0)
    client_satisfaction: float = Field(..., ge=0.0, le=1.0)
    communication_score: float = Field(..., ge=0.0, le=1.0)
    hourly_rate: float = Field(..., gt=0)
    availability_status: str = Field(default="available", pattern="^(available|busy|unavailable)$")
    location: Optional[str] = None
    experience_level: int = Field(..., ge=1, le=5, description="Experience level 1-5")
    total_projects: int = Field(default=0, ge=0)
    metadata: FreelancerMetadata

class FreelancerEmbeddingResponse(BaseModel):
    status: str = "ok"
    freelancer_id: UUID
    created: bool
    embedding_model: str
    data_quality_score: float

class FreelancerEmbeddingStatusResponse(BaseModel):
    freelancer_id: UUID
    exists: bool
    last_updated: Optional[datetime] = None
    embedding_model: Optional[str] = None
    data_quality_score: Optional[float] = None

class FreelancerEmbeddingDeleteResponse(BaseModel):
    status: str = "ok"
    freelancer_id: UUID
    deleted: bool

class FreelancerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    freelancer_id: UUID
    skills: List[str]
    success_rate: float
    client_satisfaction: float
    communication_score: float
    hourly_rate: float
    availability_status: str
    location: Optional[str]
    experience_level: int
    total_projects: int
    embedding_model: str
    embedding_version: str
    data_quality_score: float
    meta_info: Dict[str, Any]
    created_at: datetime
    last_updated: datetime

class FreelancerListResponse(BaseModel):
    total_freelancers: int
    freelancers: List[FreelancerSchema]

# Project Embeddings

class ProjectMetadata(BaseModel):
    is_generic_description: bool
    skill_count: int

class ProjectEmbeddingCreateRequest(BaseModel):
    project_id: UUID
    title: str = Field(..., min_length=10, description="Project title (minimum 10 characters)")
    description: str = Field(..., min_length=150, description="Project description (minimum 150 characters)")
    required_skills: List[str] = Field(..., min_length=2, description="Required skills (minimum 2)")
    budget: float = Field(..., gt=0)
    required_experience_level: int = Field(..., ge=1, le=5)
    preferred_location: Optional[str] = None
    status: str = Field(default="open", pattern="^(open|in_progress|completed|cancelled|on_hold)$")
    metadata: ProjectMetadata

class ProjectEmbeddingResponse(BaseModel):
    status: str = "ok"
    project_id: UUID
    created: bool
    embedding_model: str
    data_quality_score: float

class ProjectEmbeddingStatusResponse(BaseModel):
    project_id: UUID
    exists: bool
    last_updated: Optional[datetime] = None
    embedding_model: Optional[str] = None
    data_quality_score: Optional[float] = None

class ProjectEmbeddingDeleteResponse(BaseModel):
    status: str = "ok"
    project_id: UUID
    deleted: bool

class ProjectSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: UUID
    project_title: str
    required_skills: List[str]
    budget: float
    required_experience_level: int
    preferred_location: Optional[str]
    status: str
    embedding_model: str
    embedding_version: str
    data_quality_score: float
    meta_info: Dict[str, Any]
    created_at: datetime
    last_updated: datetime

class ProjectListResponse(BaseModel):
    total_projects: int
    projects: List[ProjectSchema]
