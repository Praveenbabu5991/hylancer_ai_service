# app/services/embedding_service.py
from typing import List
from uuid import UUID
from loguru import logger # Import logger
from app.core.llm_client import get_embedding
from app.core.postgres_client import PostgresClient
from app.schemas.embeddings import EmbeddingCreateRequest

class EmbeddingService:
    def __init__(self, postgres_client: PostgresClient):
        self.postgres_client = postgres_client

    async def create_or_update_embedding(self, freelancer_data: EmbeddingCreateRequest) -> bool:
        logger.debug(f"Generating bio embedding for freelancer_id: {freelancer_data.freelancer_id}")
        bio_embedding = await get_embedding(freelancer_data.bio)
        logger.debug(f"Generating past project embedding for freelancer_id: {freelancer_data.freelancer_id}")
        past_project_embedding = await get_embedding(freelancer_data.past_projects)

        logger.debug(f"Upserting embedding for freelancer_id: {freelancer_data.freelancer_id}")
        return await self.postgres_client.upsert_freelancer_embedding(
            freelancer_data,
            bio_embedding,
            past_project_embedding
        )
