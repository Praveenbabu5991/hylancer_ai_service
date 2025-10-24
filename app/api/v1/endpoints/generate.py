# app/api/v1/endpoints/generate.py - API endpoints for project description and bio generation.

from fastapi import APIRouter, Depends, HTTPException
from app.models import ProjectDescriptionRequest, ProjectDescriptionResponse, BioRequest, BioResponse
from app.agents.generation_agent import generate_project_description_agent, generate_bio_agent

router = APIRouter()

@router.post("/generate-project-description", response_model=ProjectDescriptionResponse)
async def generate_project_description(request: ProjectDescriptionRequest):
    """Generates a project description based on title, keywords, and desired length."""
    try:
        result = await generate_project_description_agent(request.project_title, request.keywords, request.length)
        return ProjectDescriptionResponse(description=result.get("description", ""))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-bio", response_model=BioResponse)
async def generate_bio(request: BioRequest):
    """Generates a freelancer bio based on skills, experience level, and tone."""
    try:
        result = await generate_bio_agent(request.freelancer_skills, request.experience_level, request.tone)
        return BioResponse(bio=result.get("bio", ""))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
