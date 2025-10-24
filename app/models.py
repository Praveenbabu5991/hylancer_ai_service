# app/models.py - Defines Pydantic models for request/response.

from pydantic import BaseModel, Field
from typing import List, Optional

# --- Request Models ---

class RecommendationRequest(BaseModel):
    query: str = Field(..., description="The user's query for recommendation.")
    top_k: int = Field(5, ge=1, description="Number of recommendations to return.")

class ProjectDescriptionRequest(BaseModel):
    project_title: str = Field(..., description="The title of the project.")
    keywords: List[str] = Field(..., description="Keywords related to the project.")
    length: str = Field("medium", description="Desired length of the description (short, medium, long).")

class BioRequest(BaseModel):
    freelancer_skills: List[str] = Field(..., description="List of skills the freelancer possesses.")
    experience_level: str = Field(..., description="Experience level of the freelancer (e.g., Junior, Mid, Senior).")
    tone: str = Field("professional", description="Desired tone of the bio (e.g., professional, friendly, creative).")

# --- Response Models ---

class RecommendationResponse(BaseModel):
    recommendations: List[str] = Field(..., description="List of recommended items.")

class ProjectDescriptionResponse(BaseModel):
    description: str = Field(..., description="The generated project description.")

class BioResponse(BaseModel):
    bio: str = Field(..., description="The generated freelancer bio.")

class HealthCheckResponse(BaseModel):
    status: str = Field("ok", description="Status of the service.")
    version: str = Field(..., description="Version of the service.")
