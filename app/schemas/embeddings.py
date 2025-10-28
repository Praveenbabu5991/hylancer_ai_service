# app/schemas/embeddings.py
from pydantic import BaseModel
from uuid import UUID

class EmbeddingCreateRequest(BaseModel):
    freelancer_id: UUID
    bio: str
    past_projects: str
    success_rate: float
    client_satisfaction: float
    communication_score: float
    hourly_rate: float

class EmbeddingCreateResponse(BaseModel):
    status: str = "ok"
    freelancer_id: UUID
    created: bool
