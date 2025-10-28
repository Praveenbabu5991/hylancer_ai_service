# app/api/v1/endpoints/recommend.py - API endpoint for freelancer recommendation.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.postgres_client import PostgresClient
from app.services.recommendation_service import RecommendationService
from app.schemas.recommend import RecommendRequest, RecommendResponse

router = APIRouter()

async def get_recommendation_service(db: AsyncSession = Depends(get_db)) -> RecommendationService:
    postgres_client = PostgresClient(db)
    return RecommendationService(postgres_client)

@router.post("/recommend", response_model=RecommendResponse)
async def recommend_freelancers(
    request: RecommendRequest,
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """Recommends freelancers based on project criteria."""
    try:
        response = await recommendation_service.recommend_freelancers(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
