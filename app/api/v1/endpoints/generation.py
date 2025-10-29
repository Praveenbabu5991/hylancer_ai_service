# app/api/v1/endpoints/generation.py
from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.services.generation_service import GenerationService
from app.schemas.generation import (
    GenerateProjectDescriptionRequest,
    GenerateProjectDescriptionResponse,
    GenerateBioDescriptionRequest,
    GenerateBioDescriptionResponse,
)

router = APIRouter()


# ========== Dependency Injector ==========

async def get_generation_service() -> GenerationService:
    return GenerationService()


# ========== Generation Endpoints ==========

@router.post(
    "/generate_project_description",
    response_model=GenerateProjectDescriptionResponse,
    summary="Generate Project Description",
    description="Generate a professional project description using AI based on category, skills, and budget"
)
async def generate_project_description(
    request: GenerateProjectDescriptionRequest,
    service: GenerationService = None
):
    """
    Generate a project description using AI.

    This endpoint creates:
    - A compelling project title
    - Detailed project description
    - Suggested skills list
    - Estimated duration
    - Complexity level

    Example request:
    {
        "category": "Web Development",
        "sub_category": "Full-Stack",
        "required_skills": ["React", "Node.js", "PostgreSQL"],
        "budget_type": "Fixed-Price",
        "budget": 5000,
        "deadline": "2025-12-31"
    }
    """
    try:
        if service is None:
            service = await get_generation_service()

        logger.info(f"Generating project description for category: {request.category}")
        response = await service.generate_project_description(request)
        return response
    except Exception as e:
        logger.exception(f"Error generating project description: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate project description: {str(e)}"
        )


@router.post(
    "/generate_bio_description",
    response_model=GenerateBioDescriptionResponse,
    summary="Generate Hylancer Bio",
    description="Generate a professional bio description for a hylancer using AI"
)
async def generate_bio_description(
    request: GenerateBioDescriptionRequest,
    service: GenerationService = None
):
    """
    Generate a professional bio for a hylancer using AI.

    This endpoint creates:
    - A professional bio (150-250 words)
    - A compelling headline
    - Suggested hourly rate
    - Experience level (1-5)

    Example request:
    {
        "name": "John Smith",
        "title": "Senior Full-Stack Developer",
        "skills": ["Python", "React", "AWS", "Docker", "PostgreSQL"],
        "years_of_experience": 8,
        "top_achievements": [
            "Built a SaaS platform serving 10K users",
            "Led a team of 5 developers"
        ],
        "personality_traits": ["problem-solver", "team-player", "detail-oriented"]
    }
    """
    try:
        if service is None:
            service = await get_generation_service()

        logger.info(f"Generating bio description for: {request.name}")
        response = await service.generate_bio_description(request)
        return response
    except Exception as e:
        logger.exception(f"Error generating bio description: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate bio description: {str(e)}"
        )
