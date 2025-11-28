# app/services/embedding_service.py
from typing import Optional
from uuid import UUID
from loguru import logger

from app.core.llm_client import get_embedding
from app.core.postgres_client import PostgresClient
from app.core.config import get_settings
from app.schemas.embeddings import (
    HylancerEmbeddingCreateRequest,
    HylancerEmbeddingUpdateRequest,
    HylancerEmbeddingResponse,
    HylancerEmbeddingStatusResponse,
    HylancerMetadata,
    ProjectEmbeddingCreateRequest,
    ProjectEmbeddingUpdateRequest,
    ProjectEmbeddingResponse,
    ProjectEmbeddingStatusResponse,
    ProjectMetadata,
)
from app.utils.scoring import (
    calculate_data_quality_score,
    calculate_project_data_quality_score,
    is_generic_project_description
)

settings = get_settings()


class HylancerEmbeddingService:
    """Service for managing hylancer embeddings."""

    def __init__(self, postgres_client: PostgresClient):
        self.postgres_client = postgres_client

    async def create_or_update_embedding(
        self,
        hylancer_data: HylancerEmbeddingCreateRequest
    ) -> HylancerEmbeddingResponse:
        """Create or update hylancer embedding."""
        logger.info(f"Generating embeddings for hylancer_id: {hylancer_data.hylancer_id}")

        # Generate bio embedding
        logger.debug("Generating bio embedding...")
        bio_embedding = await get_embedding(hylancer_data.bio)

        # Generate past project embedding if available
        past_project_embedding = None
        if hylancer_data.past_projects and len(hylancer_data.past_projects) > 50:
            logger.debug("Generating past project embedding...")
            past_project_embedding = await get_embedding(hylancer_data.past_projects)

        # Ensure metadata is present
        if hylancer_data.metadata is None:
            hylancer_data.metadata = HylancerMetadata(
                is_new_hylancer=True,
                has_past_projects=False,
                feedback_count=0
            )

        # Calculate data quality score
        data_quality_score = calculate_data_quality_score(
            bio_length=len(hylancer_data.bio),
            skills_count=len(hylancer_data.skills),
            has_past_projects=hylancer_data.metadata.has_past_projects,
            total_projects=hylancer_data.total_projects,
            feedback_count=hylancer_data.metadata.feedback_count
        )

        logger.debug(f"Data quality score: {data_quality_score}")

        # Upsert to database
        existed = await self.postgres_client.upsert_freelancer_embedding(
            freelancer_data=hylancer_data,
            bio_embedding=bio_embedding,
            past_project_embedding=past_project_embedding,
            embedding_model=settings.EMBEDDING_MODEL,
            data_quality_score=data_quality_score
        )

        logger.info(f"Successfully upserted embedding for hylancer_id: {hylancer_data.hylancer_id}")

        return HylancerEmbeddingResponse(
            hylancer_id=hylancer_data.hylancer_id,
            created=existed,
            embedding_model=settings.EMBEDDING_MODEL,
            data_quality_score=data_quality_score
        )

    async def update_embedding(
        self,
        hylancer_id: UUID,
        update_data: HylancerEmbeddingUpdateRequest
    ) -> HylancerEmbeddingResponse:
        """Update hylancer embedding."""
        logger.info(f"Updating embedding for hylancer_id: {hylancer_id}")

        # Fetch existing
        existing = await self.postgres_client.get_freelancer_embedding(hylancer_id)
        if not existing:
             raise ValueError(f"Hylancer not found: {hylancer_id}")

        update_dict = {}

        # Handle Bio
        if update_data.bio is not None:
            logger.debug("Generating bio embedding...")
            bio_embedding = await get_embedding(update_data.bio)
            update_dict["bio_embedding"] = bio_embedding
        
        # Handle Past Projects
        if update_data.past_projects is not None:
             if len(update_data.past_projects) > 50:
                logger.debug("Generating past project embedding...")
                past_project_embedding = await get_embedding(update_data.past_projects)
                update_dict["past_project_embedding"] = past_project_embedding
             else:
                update_dict["past_project_embedding"] = None

        # Handle other fields
        if update_data.skills is not None:
            update_dict["skills"] = update_data.skills
        if update_data.success_rate is not None:
            update_dict["success_rate"] = update_data.success_rate
        if update_data.client_satisfaction is not None:
            update_dict["client_satisfaction"] = update_data.client_satisfaction
        if update_data.communication_score is not None:
            update_dict["communication_score"] = update_data.communication_score
        if update_data.hourly_rate is not None:
            update_dict["hourly_rate"] = update_data.hourly_rate
        if update_data.availability_status is not None:
            update_dict["availability_status"] = update_data.availability_status
        if update_data.location is not None:
            update_dict["location"] = update_data.location
        if update_data.experience_level is not None:
            update_dict["experience_level"] = update_data.experience_level
        if update_data.total_projects is not None:
            update_dict["total_projects"] = update_data.total_projects
        if update_data.metadata is not None:
            update_dict["meta_info"] = update_data.metadata.model_dump()

        # Recalculate score only if bio is updated (since we need bio length)
        if update_data.bio is not None:
             skills_count = len(update_data.skills) if update_data.skills is not None else len(existing.skills)
             
             meta_info = update_data.metadata.model_dump() if update_data.metadata else existing.meta_info
             has_past_projects = meta_info.get("has_past_projects", False)
             feedback_count = meta_info.get("feedback_count", 0)
             
             total_projects = update_data.total_projects if update_data.total_projects is not None else existing.total_projects

             data_quality_score = calculate_data_quality_score(
                bio_length=len(update_data.bio),
                skills_count=skills_count,
                has_past_projects=has_past_projects,
                total_projects=total_projects,
                feedback_count=feedback_count
             )
             update_dict["data_quality_score"] = data_quality_score
        
        await self.postgres_client.update_freelancer_embedding_partial(hylancer_id, update_dict)
        
        dq_score = update_dict.get("data_quality_score", existing.data_quality_score)
        
        return HylancerEmbeddingResponse(
            hylancer_id=hylancer_id,
            created=False,
            embedding_model=settings.EMBEDDING_MODEL,
            data_quality_score=dq_score
        )

    async def get_embedding_status(self, hylancer_id: UUID) -> Optional[HylancerEmbeddingStatusResponse]:
        """Get status of hylancer embedding."""
        embedding = await self.postgres_client.get_freelancer_embedding(hylancer_id)

        if not embedding:
            return HylancerEmbeddingStatusResponse(
                hylancer_id=hylancer_id,
                exists=False
            )

        return HylancerEmbeddingStatusResponse(
            hylancer_id=hylancer_id,
            exists=True,
            last_updated=embedding.last_updated,
            embedding_model=embedding.embedding_model,
            data_quality_score=embedding.data_quality_score
        )

    async def delete_embedding(self, hylancer_id: UUID) -> bool:
        """Delete hylancer embedding."""
        logger.info(f"Deleting embedding for hylancer_id: {hylancer_id}")
        return await self.postgres_client.delete_freelancer_embedding(hylancer_id)

    async def get_all_hylancer_embeddings(self):
        """Get all hylancer embeddings."""
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

        # Handle nullable required_experience_level
        if project_data.required_experience_level is None:
            logger.warning("required_experience_level is None, defaulting to 1.")
            project_data.required_experience_level = 1

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

    async def update_embedding(
        self,
        project_id: UUID,
        update_data: ProjectEmbeddingUpdateRequest
    ) -> ProjectEmbeddingResponse:
        """Update project embedding."""
        logger.info(f"Updating embedding for project_id: {project_id}")

        # Fetch existing project
        existing = await self.postgres_client.get_project_embedding(project_id)
        if not existing:
            raise ValueError(f"Project not found: {project_id}")

        update_dict = {}

        # Handle title and description - regenerate embedding if either changes
        if update_data.title is not None or update_data.description is not None:
            # Use updated values or fallback to existing
            title = update_data.title if update_data.title is not None else existing.project_title
            description = update_data.description if update_data.description is not None else ""

            # Get existing description from meta_info if not provided
            if update_data.description is None:
                # We need to store description in meta_info or fetch from another source
                # For now, we'll only regenerate if description is provided
                pass

            if update_data.title is not None or update_data.description is not None:
                project_text = f"{title}. {description}"
                logger.debug("Generating project embedding...")
                project_embedding = await get_embedding(project_text)
                update_dict["project_embedding"] = project_embedding

                if update_data.title is not None:
                    update_dict["project_title"] = update_data.title

        # Handle other fields
        if update_data.required_skills is not None:
            update_dict["required_skills"] = update_data.required_skills
        if update_data.budget is not None:
            update_dict["budget"] = update_data.budget
        if update_data.required_experience_level is not None:
            update_dict["required_experience_level"] = update_data.required_experience_level
        if update_data.preferred_location is not None:
            update_dict["preferred_location"] = update_data.preferred_location
        if update_data.status is not None:
            update_dict["status"] = update_data.status
        if update_data.metadata is not None:
            update_dict["meta_info"] = update_data.metadata.model_dump()

        # Recalculate data quality score if relevant fields changed
        if update_data.title is not None or update_data.description is not None or update_data.required_skills is not None:
            title_length = len(update_data.title) if update_data.title is not None else len(existing.project_title)
            description_length = len(update_data.description) if update_data.description is not None else 0
            skills_count = len(update_data.required_skills) if update_data.required_skills is not None else len(existing.required_skills)

            data_quality_score = calculate_project_data_quality_score(
                title_length=title_length,
                description_length=description_length,
                skills_count=skills_count
            )
            update_dict["data_quality_score"] = data_quality_score

        await self.postgres_client.update_project_embedding_partial(project_id, update_dict)

        dq_score = update_dict.get("data_quality_score", existing.data_quality_score)

        return ProjectEmbeddingResponse(
            project_id=project_id,
            created=False,
            embedding_model=settings.EMBEDDING_MODEL,
            data_quality_score=dq_score
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
