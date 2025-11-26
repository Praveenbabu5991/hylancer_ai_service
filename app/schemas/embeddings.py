# app/schemas/embeddings.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

# Hylancer Embeddings

class HylancerMetadata(BaseModel):
    is_new_hylancer: bool
    has_past_projects: bool
    feedback_count: int

class HylancerEmbeddingCreateRequest(BaseModel):
    hylancer_id: UUID
    bio: str = Field(..., description="Hylancer bio")
    skills: List[str] = Field(..., min_length=1, description="Array of skills (minimum 1)")
    past_projects: str = Field(default="", description="Concatenated past project descriptions")
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    client_satisfaction: float = Field(default=0.0, ge=0.0, le=1.0)
    communication_score: float = Field(default=0.0, ge=0.0, le=1.0)
    hourly_rate: float = Field(default=0.0, ge=0.0)
    availability_status: str = Field(default="available", pattern="^(available|busy|unavailable)$")
    location: Optional[str] = None
    experience_level: int = Field(default=1, ge=1, le=5, description="Experience level 1-5")
    total_projects: int = Field(default=0, ge=0)
    metadata: HylancerMetadata = Field(
        default_factory=lambda: HylancerMetadata(
            is_new_hylancer=True,
            has_past_projects=False,
            feedback_count=0
        )
    )

class HylancerEmbeddingUpdateRequest(BaseModel):
    bio: Optional[str] = Field(default=None, description="Hylancer bio")
    past_projects: Optional[str] = Field(default=None, description="Concatenated past project descriptions")
    skills: Optional[List[str]] = Field(default=None, min_length=1, description="Array of skills (minimum 1)")
    success_rate: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    client_satisfaction: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    communication_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    hourly_rate: Optional[float] = Field(default=None, gt=0)
    availability_status: Optional[str] = Field(default=None, pattern="^(available|busy|unavailable)$")
    location: Optional[str] = None
    experience_level: Optional[int] = Field(default=None, ge=1, le=5, description="Experience level 1-5")
    total_projects: Optional[int] = Field(default=None, ge=0)
    metadata: Optional[HylancerMetadata] = None

class HylancerEmbeddingResponse(BaseModel):
    status: str = "ok"
    hylancer_id: UUID
    created: bool
    embedding_model: str
    data_quality_score: float

class HylancerEmbeddingStatusResponse(BaseModel):
    hylancer_id: UUID
    exists: bool
    last_updated: Optional[datetime] = None
    embedding_model: Optional[str] = None
    data_quality_score: Optional[float] = None

class HylancerEmbeddingDeleteResponse(BaseModel):
    status: str = "ok"
    hylancer_id: UUID
    deleted: bool

class HylancerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    hylancer_id: UUID = Field(..., validation_alias='freelancer_id', serialization_alias='hylancer_id')
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

class HylancerListResponse(BaseModel):
    total_hylancers: int
    hylancers: List[HylancerSchema]

# Project Embeddings

class ProjectMetadata(BaseModel):
    is_generic_description: bool
    skill_count: int

class ProjectEmbeddingCreateRequest(BaseModel):
    project_id: UUID
    title: str = Field(..., min_length=1, description="Project title")
    description: str = Field(..., description="Project description")
    required_skills: List[str] = Field(..., min_length=1, description="Required skills (minimum 1)")
    budget: float = Field(..., gt=0)
    required_experience_level: int = Field(default=1, ge=1, le=5)
    preferred_location: Optional[str] = None
    status: str = Field(default="open", pattern="^(open|in_progress|completed|cancelled|on_hold)$")
    metadata: ProjectMetadata = Field(
        default_factory=lambda: ProjectMetadata(
            is_generic_description=False,
            skill_count=0
        )
    )

class ProjectEmbeddingUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, description="Project title")
    description: Optional[str] = Field(None, description="Project description")
    required_skills: Optional[List[str]] = Field(None, min_length=1, description="Required skills (minimum 1)")
    budget: Optional[float] = Field(None, gt=0)
    required_experience_level: Optional[int] = Field(None, ge=1, le=5)
    preferred_location: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(open|in_progress|completed|cancelled|on_hold)$")
    metadata: Optional[ProjectMetadata] = None

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
