# app/api/v1/endpoints/embeddings.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from loguru import logger # Import logger

from app.core.db import get_db
from app.core.postgres_client import PostgresClient
from app.services.embedding_service import EmbeddingService
from app.schemas.embeddings import EmbeddingCreateRequest, EmbeddingCreateResponse

router = APIRouter()

async def get_embedding_service(db: AsyncSession = Depends(get_db)) -> EmbeddingService:
    postgres_client = PostgresClient(db)
    # LLMClient is now implicitly used by get_embedding in EmbeddingService
    return EmbeddingService(postgres_client)

@router.post("/embeddings", response_model=EmbeddingCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_embedding(
    request: EmbeddingCreateRequest,
    embedding_service: EmbeddingService = Depends(get_embedding_service)
):
    try:
        logger.debug(f"Attempting to create embedding for freelancer_id: {request.freelancer_id}")
        created = await embedding_service.create_or_update_embedding(request)
        logger.debug(f"Embedding creation successful for freelancer_id: {request.freelancer_id}")
        return EmbeddingCreateResponse(freelancer_id=request.freelancer_id, created=created)
    except Exception as e:
        logger.exception(f"Error creating embedding for freelancer_id: {request.freelancer_id}") # Log exception
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/embeddings/{freelancer_id}", response_model=EmbeddingCreateResponse)
async def update_embedding(
    freelancer_id: UUID,
    request: EmbeddingCreateRequest,
    embedding_service: EmbeddingService = Depends(get_embedding_service)
):
    if freelancer_id != request.freelancer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Freelancer ID in path and body do not match."
        )
    try:
        logger.debug(f"Attempting to update embedding for freelancer_id: {freelancer_id}")
        updated = await embedding_service.create_or_update_embedding(request)
        logger.debug(f"Embedding update successful for freelancer_id: {freelancer_id}")
        return EmbeddingCreateResponse(freelancer_id=freelancer_id, created=updated)
    except Exception as e:
        logger.exception(f"Error updating embedding for freelancer_id: {freelancer_id}") # Log exception
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
