# app/schemas/recommend.py
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class RecommendRequest(BaseModel):
    project_description: str
    skills: List[str]
    budget_min: int
    budget_max: int
    region: str
    top_k: int = 20

class ScoreComponents(BaseModel):
    bio_score: float
    past_score: float
    success_rate: float
    client_satisfaction: float
    communication_score: float
    hourly_score: float

class Result(BaseModel):
    freelancer_id: UUID
    score: float
    components: ScoreComponents
    reason: str

class RecommendResponse(BaseModel):
    project_id: Optional[str] = None
    results: List[Result]
