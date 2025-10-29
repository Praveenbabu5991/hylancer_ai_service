# app/schemas/generation.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class GenerateProjectDescriptionRequest(BaseModel):
    """
    Request to generate project description using AI.

    Example:
    {
        "category": "AI",
        "sub_category": "NLP",
        "required_skills": ["ML", "Python", "TensorFlow"],
        "budget_type": "Fixed-Price",
        "budget": 10000,
        "deadline": "2025-12-15"
    }
    """
    category: str = Field(..., min_length=2, description="Project category")
    sub_category: str = Field(..., min_length=2, description="Project subcategory")
    required_skills: List[str] = Field(..., min_items=1, description="Required skills")
    budget_type: str = Field(..., pattern="^(Fixed-Price|Hourly)$", description="Budget type")
    budget: float = Field(..., gt=0, description="Budget amount")
    deadline: Optional[str] = Field(None, description="Project deadline (YYYY-MM-DD)")

class GenerateProjectDescriptionResponse(BaseModel):
    """Response with generated project description."""
    title: str
    description: str
    suggested_skills: List[str]
    estimated_duration: str
    complexity_level: str  # "beginner", "intermediate", "expert"

class GenerateBioDescriptionRequest(BaseModel):
    """
    Request to generate bio description for a hylancer.

    Example:
    {
        "name": "Alice Johnson",
        "title": "Senior Data Scientist",
        "skills": ["Python", "TensorFlow", "Scikit-learn", "SQL", "BigQuery"],
        "years_of_experience": 8,
        "top_achievements": [
            "Developed a predictive model that increased sales by 15%.",
            "Led a team to build a real-time analytics dashboard."
        ],
        "personality_traits": ["analytical", "team-player", "proactive"]
    }
    """
    name: str = Field(..., min_length=2, description="Hylancer name")
    title: str = Field(..., min_length=5, description="Professional title")
    skills: List[str] = Field(..., min_items=3, description="Technical skills")
    years_of_experience: int = Field(..., ge=0, le=50, description="Years of experience")
    top_achievements: List[str] = Field(default=[], description="Key achievements")
    personality_traits: Optional[List[str]] = Field(default=[], description="Personality traits")

class GenerateBioDescriptionResponse(BaseModel):
    """Response with generated bio description."""
    bio: str
    headline: str
    suggested_hourly_rate: float
    experience_level: int  # 1-5
