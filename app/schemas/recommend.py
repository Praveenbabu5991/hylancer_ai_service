# app/schemas/recommend.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID

# Hylancer Recommendation (for Clients)

class HylancerRecommendRequest(BaseModel):
    """
    Request to recommend hylancers for a project.

    Example:
    {
        "project_id": "11111111-2222-3333-4444-555555555501",
        "top_k": 20
    }
    """
    project_id: UUID = Field(..., description="ID of the project")
    top_k: int = Field(default=20, ge=1, le=100, description="Number of top recommendations to return")

class HylancerScoreComponents(BaseModel):
    bio_similarity: float
    past_project_similarity: float
    skill_overlap: float
    success_rate: float
    client_satisfaction: float
    communication_score: float

class HylancerRecommendationMetadata(BaseModel):
    is_new_hylancer: bool
    matched_skills: List[str]
    confidence: str  # "high", "medium", "low"

class HylancerRecommendationResult(BaseModel):
    hylancer_id: UUID
    score: float
    components: HylancerScoreComponents
    reason: str
    metadata: HylancerRecommendationMetadata

class HylancerRecommendResponse(BaseModel):
    project_id: UUID
    total_results: int
    results: List[HylancerRecommendationResult]

# Project Recommendation (for Hylancers)

class ProjectRecommendRequest(BaseModel):
    """
    Request to recommend projects for a hylancer.

    Note: hylancer_id is extracted from JWT token, not from request body.

    Example:
    {
        "top_k": 20
    }
    """
    top_k: int = Field(default=20, ge=1, le=100, description="Number of top recommendations to return")

class ProjectScoreComponents(BaseModel):
    project_similarity: float  # past_project_embedding vs project_embedding
    skill_overlap: float
    bio_similarity: float  # bio_embedding vs project_embedding

class ProjectRecommendationMetadata(BaseModel):
    matched_skills: List[str]
    confidence: str  # "high", "medium", "low"

class ProjectRecommendationResult(BaseModel):
    project_id: UUID
    score: float
    components: ProjectScoreComponents
    reason: str
    metadata: ProjectRecommendationMetadata

class ProjectRecommendResponse(BaseModel):
    hylancer_id: UUID
    total_results: int
    results: List[ProjectRecommendationResult]
