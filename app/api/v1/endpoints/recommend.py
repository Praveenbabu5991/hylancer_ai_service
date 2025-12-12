# app/api/v1/endpoints/recommend.py
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.db import get_db
from app.core.postgres_client import PostgresClient
from app.services.recommendation_service import RecommendationService
from app.schemas.recommend import (
    HylancerRecommendRequest,
    HylancerRecommendResponse,
    ProjectRecommendRequest,
    ProjectRecommendResponse,
)
from app.security.dependencies import require_authenticated_user
from app.security.models import UserDetails

router = APIRouter()


# ========== Dependency Injector ==========

async def get_recommendation_service(db: AsyncSession = Depends(get_db)) -> RecommendationService:
    postgres_client = PostgresClient(db)
    return RecommendationService(postgres_client)


# ========== Recommendation Endpoints ==========

@router.post(
    "/recommend_hylancer",
    response_model=HylancerRecommendResponse,
    summary="Recommend Hylancers for a Project",
    description="Get AI-powered hylancer recommendations based on project requirements"
)
async def recommend_hylancers(
    request: HylancerRecommendRequest = Body(
        ...,
        example={
            "project_id": "b582a86f-4e21-4c18-943a-b6ab1ec6f907",
            "top_k": 5
        }
    ),
    service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Recommend hylancers for a project using:
    - Vector similarity (bio + past projects)
    - Skill overlap (Jaccard similarity)
    - Business metrics (success rate, client satisfaction, communication)
    - Dynamic weight adjustment
    - Cold-start boost for new hylancers
    """
    try:
        logger.info(f"Received request to recommend hylancers for project_id: {request.project_id}")
        response = await service.recommend_hylancers(request)
        return response
    except Exception as e:
        logger.exception(f"Error recommending freelancers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.post(
    "/recommend_projects",
    response_model=ProjectRecommendResponse,
    summary="Recommend Projects for a Freelancer",
    description="Get AI-powered project recommendations based on freelancer experience and skills. Requires authentication."
)
async def recommend_projects(
    request: ProjectRecommendRequest = Body(
        ...,
        example={
            "top_k": 5
        }
    ),
    current_user: UserDetails = Depends(require_authenticated_user),
    service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Recommend projects for a freelancer using:
    - 50% project similarity (past work vs project description)
    - 25% skill overlap
    - 25% bio similarity

    Authentication required: hylancer_id is extracted from JWT token.
    """
    try:
        hylancer_id = current_user.user_id
        logger.info(f"Received request to recommend projects for hylancer_id: {hylancer_id} (from JWT)")
        response = await service.recommend_projects(request, hylancer_id)
        return response
    except Exception as e:
        logger.exception(f"Error recommending projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )
