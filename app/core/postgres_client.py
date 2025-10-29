# app/core/postgres_client.py
from typing import List, Tuple, Optional, Dict, Any
from uuid import UUID
import uuid
import time
from datetime import datetime
from sqlalchemy import select, func, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.db_models import FreelancerEmbedding, ProjectEmbedding, RecommendationLog
from app.schemas.embeddings import (
    FreelancerEmbeddingCreateRequest,
    ProjectEmbeddingCreateRequest
)
from app.core.config import get_settings

settings = get_settings()


class PostgresClient:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    # ========== Freelancer Embedding Methods ==========

    async def upsert_freelancer_embedding(
        self,
        freelancer_data: FreelancerEmbeddingCreateRequest,
        bio_embedding: List[float],
        past_project_embedding: Optional[List[float]],
        embedding_model: str,
        data_quality_score: float
    ) -> bool:
        """Upsert freelancer embedding with all fields."""
        insert_stmt = insert(FreelancerEmbedding).values(
            freelancer_id=freelancer_data.freelancer_id,
            bio_embedding=bio_embedding,
            past_project_embedding=past_project_embedding,
            skills=freelancer_data.skills,
            success_rate=freelancer_data.success_rate,
            client_satisfaction=freelancer_data.client_satisfaction,
            communication_score=freelancer_data.communication_score,
            hourly_rate=freelancer_data.hourly_rate,
            availability_status=freelancer_data.availability_status,
            location=freelancer_data.location,
            experience_level=freelancer_data.experience_level,
            total_projects=freelancer_data.total_projects,
            embedding_model=embedding_model,
            embedding_version=settings.EMBEDDING_VERSION,
            data_quality_score=data_quality_score,
            meta_info=freelancer_data.metadata.model_dump(),
        )
        do_update_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[FreelancerEmbedding.freelancer_id],
            set_=dict(
                bio_embedding=insert_stmt.excluded.bio_embedding,
                past_project_embedding=insert_stmt.excluded.past_project_embedding,
                skills=insert_stmt.excluded.skills,
                success_rate=insert_stmt.excluded.success_rate,
                client_satisfaction=insert_stmt.excluded.client_satisfaction,
                communication_score=insert_stmt.excluded.communication_score,
                hourly_rate=insert_stmt.excluded.hourly_rate,
                availability_status=insert_stmt.excluded.availability_status,
                location=insert_stmt.excluded.location,
                experience_level=insert_stmt.excluded.experience_level,
                total_projects=insert_stmt.excluded.total_projects,
                embedding_model=insert_stmt.excluded.embedding_model,
                embedding_version=insert_stmt.excluded.embedding_version,
                data_quality_score=insert_stmt.excluded.data_quality_score,
                meta_info=insert_stmt.excluded.meta_info,
                last_updated=func.now()
            )
        )
        await self.db_session.execute(do_update_stmt)
        await self.db_session.commit()
        return True

    async def get_freelancer_embedding(self, freelancer_id: UUID) -> Optional[FreelancerEmbedding]:
        """Get a freelancer embedding by ID."""
        stmt = select(FreelancerEmbedding).where(FreelancerEmbedding.freelancer_id == freelancer_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_freelancer_embedding(self, freelancer_id: UUID) -> bool:
        """Delete a freelancer embedding."""
        stmt = delete(FreelancerEmbedding).where(FreelancerEmbedding.freelancer_id == freelancer_id)
        result = await self.db_session.execute(stmt)
        await self.db_session.commit()
        return result.rowcount > 0

    async def search_freelancer_embeddings(
        self,
        project_embedding: List[float],
        candidate_ids: Optional[List[UUID]] = None,
        top_k: int = 20
    ) -> List[Tuple[FreelancerEmbedding, float, float]]:
        """
        Search for similar freelancers using vector similarity.

        Returns: List of (FreelancerEmbedding, bio_distance, past_project_distance) tuples
        """
        bio_dist_expr = FreelancerEmbedding.bio_embedding.cosine_distance(project_embedding)
        past_dist_expr = FreelancerEmbedding.past_project_embedding.cosine_distance(project_embedding)

        stmt = select(
            FreelancerEmbedding,
            bio_dist_expr.label("bio_distance"),
            past_dist_expr.label("past_project_distance")
        )

        # Apply candidate filter if provided
        if candidate_ids:
            stmt = stmt.filter(FreelancerEmbedding.freelancer_id.in_(candidate_ids))

        stmt = stmt.order_by(bio_dist_expr).limit(top_k)

        result = await self.db_session.execute(stmt)
        return result.all()

    async def get_freelancers_by_ids(self, freelancer_ids: List[UUID]) -> List[FreelancerEmbedding]:
        """Get multiple freelancers by IDs. If empty list, returns all."""
        if not freelancer_ids:
            stmt = select(FreelancerEmbedding)
        else:
            stmt = select(FreelancerEmbedding).filter(FreelancerEmbedding.freelancer_id.in_(freelancer_ids))
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_all_freelancer_embeddings(self) -> List[FreelancerEmbedding]:
        """Get all freelancer embeddings."""
        stmt = select(FreelancerEmbedding)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    # ========== Project Embedding Methods ==========

    async def upsert_project_embedding(
        self,
        project_data: ProjectEmbeddingCreateRequest,
        project_embedding: List[float],
        embedding_model: str,
        data_quality_score: float
    ) -> bool:
        """Upsert project embedding with all fields."""
        insert_stmt = insert(ProjectEmbedding).values(
            project_id=project_data.project_id,
            project_embedding=project_embedding,
            required_skills=project_data.required_skills,
            budget=project_data.budget,
            required_experience_level=project_data.required_experience_level,
            preferred_location=project_data.preferred_location,
            status=project_data.status,
            project_title=project_data.title,
            embedding_model=embedding_model,
            embedding_version=settings.EMBEDDING_VERSION,
            data_quality_score=data_quality_score,
            meta_info=project_data.metadata.model_dump(),
        )
        do_update_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[ProjectEmbedding.project_id],
            set_=dict(
                project_embedding=insert_stmt.excluded.project_embedding,
                required_skills=insert_stmt.excluded.required_skills,
                budget=insert_stmt.excluded.budget,
                required_experience_level=insert_stmt.excluded.required_experience_level,
                preferred_location=insert_stmt.excluded.preferred_location,
                status=insert_stmt.excluded.status,
                project_title=insert_stmt.excluded.project_title,
                embedding_model=insert_stmt.excluded.embedding_model,
                embedding_version=insert_stmt.excluded.embedding_version,
                data_quality_score=insert_stmt.excluded.data_quality_score,
                meta_info=insert_stmt.excluded.meta_info,
                last_updated=func.now()
            )
        )
        await self.db_session.execute(do_update_stmt)
        await self.db_session.commit()
        return True

    async def get_project_embedding(self, project_id: UUID) -> Optional[ProjectEmbedding]:
        """Get a project embedding by ID."""
        stmt = select(ProjectEmbedding).where(ProjectEmbedding.project_id == project_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_project_embedding(self, project_id: UUID) -> bool:
        """Delete a project embedding."""
        stmt = delete(ProjectEmbedding).where(ProjectEmbedding.project_id == project_id)
        result = await self.db_session.execute(stmt)
        await self.db_session.commit()
        return result.rowcount > 0

    async def search_project_embeddings(
        self,
        freelancer_bio_embedding: List[float],
        freelancer_past_embedding: Optional[List[float]],
        project_candidate_ids: Optional[List[UUID]] = None,
        top_k: int = 20
    ) -> List[Tuple[ProjectEmbedding, float]]:
        """
        Search for similar projects using vector similarity.

        Returns: List of (ProjectEmbedding, distance) tuples
        """
        # Use bio embedding as primary, past embedding as secondary if available
        if freelancer_past_embedding is not None:
            # Use weighted average of bio and past project embeddings
            search_embedding = [
                (b * 0.3 + p * 0.7) for b, p in zip(freelancer_bio_embedding, freelancer_past_embedding)
            ]
        else:
            search_embedding = freelancer_bio_embedding

        dist_expr = ProjectEmbedding.project_embedding.cosine_distance(search_embedding)

        stmt = select(
            ProjectEmbedding,
            dist_expr.label("distance")
        ).filter(ProjectEmbedding.status == "open")  # Only open projects

        # Apply candidate filter if provided
        if project_candidate_ids:
            stmt = stmt.filter(ProjectEmbedding.project_id.in_(project_candidate_ids))

        stmt = stmt.order_by(dist_expr).limit(top_k)

        result = await self.db_session.execute(stmt)
        return result.all()

    async def get_projects_by_ids(self, project_ids: List[UUID]) -> List[ProjectEmbedding]:
        """Get multiple projects by IDs. If empty list, returns all open projects."""
        if not project_ids:
            stmt = select(ProjectEmbedding).filter(ProjectEmbedding.status == "open")
        else:
            stmt = select(ProjectEmbedding).filter(ProjectEmbedding.project_id.in_(project_ids))
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_all_project_embeddings(self) -> List[ProjectEmbedding]:
        """Get all project embeddings."""
        stmt = select(ProjectEmbedding)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    # ========== Recommendation Logging Methods ==========

    async def log_recommendation(
        self,
        recommendation_type: str,
        request_id: UUID,
        entity_id: UUID,
        recommended_ids: List[Dict[str, Any]],
        filters_applied: Optional[Dict[str, Any]],
        avg_score: float,
        result_count: int,
        execution_time_ms: int
    ) -> bool:
        """Log a recommendation request for analytics."""
        try:
            log_entry = RecommendationLog(
                log_id=uuid.uuid4(),
                recommendation_type=recommendation_type,
                request_id=request_id,
                entity_id=entity_id,
                recommended_ids=recommended_ids,
                filters_applied=filters_applied,
                avg_score=avg_score,
                result_count=result_count,
                execution_time_ms=execution_time_ms,
            )
            self.db_session.add(log_entry)
            await self.db_session.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to log recommendation: {e}")
            await self.db_session.rollback()
            return False

    # ========== Statistics Methods ==========

    async def get_total_freelancer_embeddings(self) -> int:
        """Get total count of freelancer embeddings."""
        stmt = select(func.count()).select_from(FreelancerEmbedding)
        result = await self.db_session.execute(stmt)
        return result.scalar()

    async def get_total_project_embeddings(self) -> int:
        """Get total count of project embeddings."""
        stmt = select(func.count()).select_from(ProjectEmbedding)
        result = await self.db_session.execute(stmt)
        return result.scalar()

    async def get_recommendations_count_today(self) -> int:
        """Get count of recommendations made today."""
        stmt = select(func.count()).select_from(RecommendationLog).where(
            func.date(RecommendationLog.created_at) == func.current_date()
        )
        result = await self.db_session.execute(stmt)
        return result.scalar()
