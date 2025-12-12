# app/security/models.py
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID


class UserDetails(BaseModel):
    """
    User details extracted from JWT token.
    Mirrors the UserDetails from Project Management Service.
    """
    user_id: UUID
    email: str
    name: str
    roles: List[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "name": "John Doe",
                "roles": ["Hylancer", "Client"]
            }
        }
