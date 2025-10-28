# app/core/postgres_client.py
from typing import List, Tuple
from uuid import UUID
import numpy as np
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from pgvector.sqlalchemy import Vector
from app.db_models import FreelancerEmbedding
from app.schemas.embeddings import EmbeddingCreateRequest

class PostgresClient:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def upsert_freelancer_embedding(
        self,
        freelancer_data: EmbeddingCreateRequest,
        bio_embedding: List[float],
        past_project_embedding: List[float]
    ) -> bool:
        insert_stmt = insert(FreelancerEmbedding).values(
            freelancer_id=freelancer_data.freelancer_id,
            bio_embedding=bio_embedding,
            past_project_embedding=past_project_embedding,
            success_rate=freelancer_data.success_rate,
            client_satisfaction=freelancer_data.client_satisfaction,
            communication_score=freelancer_data.communication_score,
            hourly_rate=freelancer_data.hourly_rate,
        )
        do_update_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[FreelancerEmbedding.freelancer_id],
            set_=dict(
                bio_embedding=insert_stmt.excluded.bio_embedding,
                past_project_embedding=insert_stmt.excluded.past_project_embedding,
                success_rate=insert_stmt.excluded.success_rate,
                client_satisfaction=insert_stmt.excluded.client_satisfaction,
                communication_score=insert_stmt.excluded.communication_score,
                hourly_rate=insert_stmt.excluded.hourly_rate,
                last_updated=func.now()
            )
        )
        await self.db_session.execute(do_update_stmt)
        await self.db_session.commit()
        return True

    async def search_freelancer_embeddings(
        self,
        project_embedding: List[float],
        candidate_ids: List[UUID],
        top_k: int
    ) -> List[Tuple[FreelancerEmbedding, float, float]]: # Return (freelancer, bio_dist, past_dist)
        bio_dist_expr = FreelancerEmbedding.bio_embedding.cosine_distance(project_embedding)
        past_dist_expr = FreelancerEmbedding.past_project_embedding.cosine_distance(project_embedding)

        stmt = (
            select(
                FreelancerEmbedding,
                bio_dist_expr.label("bio_distance"),
                past_dist_expr.label("past_project_distance")
            )
            .filter(FreelancerEmbedding.freelancer_id.in_(candidate_ids))
            .order_by(bio_dist_expr + past_dist_expr) # Order by combined distance
            .limit(top_k)
        )
        result = await self.db_session.execute(stmt)
        return result.all() # Returns list of (FreelancerEmbedding, bio_distance, past_project_distance) tuples

    async def get_freelancers_by_ids(self, freelancer_ids: List[UUID]) -> List[FreelancerEmbedding]:
        # If candidate_ids is empty, fetch all freelancers
        if not freelancer_ids:
            stmt = select(FreelancerEmbedding)
        else:
            stmt = select(FreelancerEmbedding).filter(FreelancerEmbedding.freelancer_id.in_(freelancer_ids))
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_all_freelancer_rates(self) -> List[float]:
        stmt = select(FreelancerEmbedding.hourly_rate)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()
