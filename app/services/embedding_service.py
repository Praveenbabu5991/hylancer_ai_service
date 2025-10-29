# app/services/embedding_service.py
from typing import Optional
from uuid import UUID
from loguru import logger

from app.core.llm_client import get_embedding
from app.core.postgres_client import PostgresClient
from app.core.config import get_settings
from app.schemas.embeddings import (
    FreelancerEmbeddingCreateRequest,
    FreelancerEmbeddingResponse,
    FreelancerEmbeddingStatusResponse,
    ProjectEmbeddingCreateRequest,
    ProjectEmbeddingResponse,
    ProjectEmbeddingStatusResponse,
)
from app.utils.scoring import (
    calculate_data_quality_score,
    calculate_project_data_quality_score,
    is_generic_project_description
)

settings = get_settings()


class FreelancerEmbeddingService:
    """Service for managing freelancer embeddings."""

    def __init__(self, postgres_client: PostgresClient):
        self.postgres_client = postgres_client

    async def create_or_update_embedding(
        self,
        freelancer_data: FreelancerEmbeddingCreateRequest
    ) -> FreelancerEmbeddingResponse:
        """Create or update freelancer embedding."""
        logger.info(f"Generating embeddings for freelancer_id: {freelancer_data.freelancer_id}")

        # Generate bio embedding
        logger.debug("Generating bio embedding...")
        bio_embedding = await get_embedding(freelancer_data.bio)

        # Generate past project embedding if available
        past_project_embedding = None
        if freelancer_data.past_projects and len(freelancer_data.past_projects) > 50:
            logger.debug("Generating past project embedding...")
            past_project_embedding = await get_embedding(freelancer_data.past_projects)

        # Calculate data quality score
        data_quality_score = calculate_data_quality_score(
            bio_length=len(freelancer_data.bio),
            skills_count=len(freelancer_data.skills),
            has_past_projects=freelancer_data.metadata.has_past_projects,
            total_projects=freelancer_data.total_projects,
            feedback_count=freelancer_data.metadata.feedback_count
        )

        logger.debug(f"Data quality score: {data_quality_score}")

        # Upsert to database
        existed = await self.postgres_client.upsert_freelancer_embedding(
            freelancer_data=freelancer_data,
            bio_embedding=bio_embedding,
            past_project_embedding=past_project_embedding,
            embedding_model=settings.EMBEDDING_MODEL,
            data_quality_score=data_quality_score
        )

        logger.info(f"Successfully upserted embedding for freelancer_id: {freelancer_data.freelancer_id}")

        return FreelancerEmbeddingResponse(
            freelancer_id=freelancer_data.freelancer_id,
            created=existed,
            embedding_model=settings.EMBEDDING_MODEL,
            data_quality_score=data_quality_score
        )

    async def get_embedding_status(self, freelancer_id: UUID) -> Optional[FreelancerEmbeddingStatusResponse]:
        """Get status of freelancer embedding."""
        embedding = await self.postgres_client.get_freelancer_embedding(freelancer_id)

        if not embedding:
            return FreelancerEmbeddingStatusResponse(
                freelancer_id=freelancer_id,
                exists=False
            )

        return FreelancerEmbeddingStatusResponse(
            freelancer_id=freelancer_id,
            exists=True,
            last_updated=embedding.last_updated,
            embedding_model=embedding.embedding_model,
            data_quality_score=embedding.data_quality_score
        )

    async def delete_embedding(self, freelancer_id: UUID) -> bool:
        """Delete freelancer embedding."""
        logger.info(f"Deleting embedding for freelancer_id: {freelancer_id}")
        return await self.postgres_client.delete_freelancer_embedding(freelancer_id)

    async def get_all_freelancer_embeddings(self):
        """Get all freelancer embeddings."""
        return await self.postgres_client.get_all_freelancer_embeddings()


class ProjectEmbeddingService:
    """Service for managing project embeddings."""

    def __init__(self, postgres_client: PostgresClient):
        self.postgres_client = postgres_client

    async def create_or_update_embedding(
        self,
        project_data: ProjectEmbeddingCreateRequest
    ) -> ProjectEmbeddingResponse:
        """Create or update project embedding."""
        logger.info(f"Generating embedding for project_id: {project_data.project_id}")

        # Combine title and description for embedding
        project_text = f"{project_data.title}. {project_data.description}"

        # Generate project embedding
        logger.debug("Generating project embedding...")
        project_embedding = await get_embedding(project_text)

        # Calculate data quality score
        data_quality_score = calculate_project_data_quality_score(
            title_length=len(project_data.title),
            description_length=len(project_data.description),
            skills_count=len(project_data.required_skills)
        )

        logger.debug(f"Data quality score: {data_quality_score}")

        # Upsert to database
        existed = await self.postgres_client.upsert_project_embedding(
            project_data=project_data,
            project_embedding=project_embedding,
            embedding_model=settings.EMBEDDING_MODEL,
            data_quality_score=data_quality_score
        )

        logger.info(f"Successfully upserted embedding for project_id: {project_data.project_id}")

        return ProjectEmbeddingResponse(
            project_id=project_data.project_id,
            created=existed,
            embedding_model=settings.EMBEDDING_MODEL,
            data_quality_score=data_quality_score
        )

    async def get_embedding_status(self, project_id: UUID) -> Optional[ProjectEmbeddingStatusResponse]:
        """Get status of project embedding."""
        embedding = await self.postgres_client.get_project_embedding(project_id)

        if not embedding:
            return ProjectEmbeddingStatusResponse(
                project_id=project_id,
                exists=False
            )

        return ProjectEmbeddingStatusResponse(
            project_id=project_id,
            exists=True,
            last_updated=embedding.last_updated,
            embedding_model=embedding.embedding_model,
            data_quality_score=embedding.data_quality_score
        )

    async def delete_embedding(self, project_id: UUID) -> bool:
        """Delete project embedding."""
        logger.info(f"Deleting embedding for project_id: {project_id}")
        return await self.postgres_client.delete_project_embedding(project_id)

    async def get_all_project_embeddings(self):
        """Get all project embeddings."""
        return await self.postgres_client.get_all_project_embeddings()
