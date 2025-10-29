# app/api/v1/endpoints/health.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime
from loguru import logger

from app.core.db import get_db
from app.core.postgres_client import PostgresClient
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


# ========== Response Models ==========

class HealthResponse(BaseModel):
    status: str
    database: str
    embedding_api: str
    timestamp: datetime


class MetricsResponse(BaseModel):
    total_freelancer_embeddings: int
    total_project_embeddings: int
    recommendations_today: int
    service_status: str


# ========== Endpoints ==========

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health status of the AI Recommendation Service"
)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Perform a health check on the service and its dependencies.

    Returns:
    - Service status
    - Database connectivity
    - Embedding API availability
    - Current timestamp
    """
    try:
        # Check database connection
        postgres_client = PostgresClient(db)
        await postgres_client.get_total_freelancer_embeddings()
        database_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        database_status = "disconnected"

    # Check embedding API (for now, just check if provider is configured)
    if settings.LLM_PROVIDER in ["openai", "gemini", "mock"]:
        embedding_api_status = "available"
    else:
        embedding_api_status = "unavailable"

    # Overall status
    if database_status == "connected" and embedding_api_status == "available":
        overall_status = "healthy"
    else:
        overall_status = "unhealthy"

    return HealthResponse(
        status=overall_status,
        database=database_status,
        embedding_api=embedding_api_status,
        timestamp=datetime.utcnow()
    )


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Service Metrics",
    description="Get operational metrics for the AI Recommendation Service"
)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    """
    Get service metrics including:
    - Total freelancer embeddings
    - Total project embeddings
    - Recommendations made today
    - Overall service status
    """
    try:
        postgres_client = PostgresClient(db)

        # Fetch metrics
        total_freelancer_embeddings = await postgres_client.get_total_freelancer_embeddings()
        total_project_embeddings = await postgres_client.get_total_project_embeddings()
        recommendations_today = await postgres_client.get_recommendations_count_today()

        return MetricsResponse(
            total_freelancer_embeddings=total_freelancer_embeddings,
            total_project_embeddings=total_project_embeddings,
            recommendations_today=recommendations_today,
            service_status="operational"
        )
    except Exception as e:
        logger.exception(f"Error fetching metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch metrics: {str(e)}"
        )
