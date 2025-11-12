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

class GenerateBioFromResumeRequest(BaseModel):
    """
    Request to generate bio description from a resume.

    Example:
    {
        "resume_text": "John Doe\\nSenior Software Engineer\\n\\nExperience:\\n- 5 years at Google..."
    }
    """
    resume_text: str = Field(..., min_length=50, description="Resume text content (minimum 50 characters)")

class ParsedResumeData(BaseModel):
    """Structured data parsed from a resume."""
    name: str
    title: str
    skills: List[str]
    years_of_experience: int
    top_achievements: List[str]
    personality_traits: Optional[List[str]] = []

class GenerateBioFromResumeResponse(BaseModel):
    """Response with generated bio from resume."""
    bio: str
    headline: str
    suggested_hourly_rate: float
    experience_level: int  # 1-5
    parsed_data: ParsedResumeData  # Include parsed resume data for transparency

class KnowYourWorthRequest(BaseModel):
    """
    Request to calculate freelancer worth in Indian context.

    Example:
    {
        "name": "Rahul Sharma",
        "skills": ["Python", "Django", "React", "AWS"],
        "years_of_experience": 5,
        "specialization": "Full-Stack Development",
        "city": "Bangalore",
        "education_level": "Bachelor's",
        "english_proficiency": "Fluent",
        "certifications": ["AWS Certified", "Google Cloud Professional"],
        "portfolio_projects": 12,
        "client_reviews_average": 4.8
    }
    """
    name: str = Field(..., min_length=2, description="Freelancer name")
    skills: List[str] = Field(..., min_items=1, max_items=20, description="Technical skills")
    years_of_experience: int = Field(..., ge=0, le=50, description="Years of professional experience")
    specialization: str = Field(..., min_length=3, description="Primary specialization/domain")
    city: str = Field(..., min_length=2, description="City in India")
    education_level: str = Field(..., description="Education level: High School, Bachelor's, Master's, PhD")
    english_proficiency: str = Field(..., description="English proficiency: Basic, Intermediate, Fluent, Native")
    certifications: Optional[List[str]] = Field(default=[], description="Professional certifications")
    portfolio_projects: Optional[int] = Field(default=0, ge=0, description="Number of portfolio projects")
    client_reviews_average: Optional[float] = Field(default=0.0, ge=0.0, le=5.0, description="Average client rating (0-5)")

class WorthBreakdown(BaseModel):
    """Breakdown of worth calculation factors."""
    base_rate: float
    experience_multiplier: float
    skill_premium: float
    location_adjustment: float
    education_bonus: float
    certification_bonus: float
    portfolio_bonus: float
    reputation_bonus: float

class MarketInsights(BaseModel):
    """Market insights for the freelancer."""
    tier: str  # "Entry-Level", "Mid-Level", "Senior", "Expert"
    market_position: str  # Percentile position
    demand_level: str  # "Low", "Medium", "High", "Very High"
    competitive_advantage: List[str]
    improvement_suggestions: List[str]

class KnowYourWorthResponse(BaseModel):
    """Response with freelancer worth calculation."""
    estimated_hourly_rate_inr: float
    estimated_hourly_rate_usd: float
    monthly_earning_potential_inr: float  # Based on 160 hours/month
    annual_earning_potential_inr: float
    worth_breakdown: WorthBreakdown
    market_insights: MarketInsights
    comparison_message: str
    recommendations: List[str]
