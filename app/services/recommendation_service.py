# app/services/recommendation_service.py
from typing import List, Optional
from uuid import UUID
import numpy as np

from app.core.llm_client import get_embedding
from app.core.postgres_client import PostgresClient
from app.schemas.recommend import RecommendRequest, RecommendResponse, Result, ScoreComponents
from app.db_models import FreelancerEmbedding

class RecommendationService:
    def __init__(
        self,
        postgres_client: PostgresClient,
    ):
        self.postgres_client = postgres_client

    async def recommend_freelancers(self, request: RecommendRequest) -> RecommendResponse:
        # 1. Get candidate freelancer IDs (mocked for now, assuming interservice call)
        # In a real scenario, this would involve calling User/Project service
        # to filter freelancers by skills, budget, region, and active status.
        # For now, we'll fetch all freelancer IDs from our embeddings table.
        all_freelancer_rates = await self.postgres_client.get_all_freelancer_rates()
        if not all_freelancer_rates:
            return RecommendResponse(results=[])

        min_hourly_rate = min(all_freelancer_rates)
        max_hourly_rate = max(all_freelancer_rates)

        # Fetch all freelancer IDs from the embeddings table for now
        # In a real scenario, this would be filtered by skills, budget, region
        # from other services or directly from a more comprehensive freelancer table.
        all_freelancers = await self.postgres_client.get_freelancers_by_ids([]) # Empty list to get all

        candidate_ids = [f.freelancer_id for f in all_freelancers]
        if not candidate_ids:
            return RecommendResponse(results=[])

        # 2. Compute project embedding
        project_embedding = await get_embedding(request.project_description)

        # 3. Perform vector similarity search
        # This returns (FreelancerEmbedding, bio_distance, past_project_distance) tuples
        top_freelancer_data = await self.postgres_client.search_freelancer_embeddings(
            project_embedding=project_embedding,
            candidate_ids=candidate_ids,
            top_k=request.top_k * 2 # Fetch more to allow for filtering/scoring
        )

        results: List[Result] = []
        for fe_obj, bio_distance, past_project_distance in top_freelancer_data:
            # Convert distance to similarity (1 - distance)
            bio_similarity = 1 - bio_distance
            past_similarity = 1 - past_project_distance

            # Normalize hourly rate: lower rate = higher score
            # Ensure no division by zero if min_hourly_rate == max_hourly_rate
            if max_hourly_rate == min_hourly_rate:
                hourly_score = 1.0
            else:
                hourly_score = 1 - ((fe_obj.hourly_rate - min_hourly_rate) / (max_hourly_rate - min_hourly_rate))
            hourly_score = max(0.0, min(1.0, hourly_score)) # Clamp between 0 and 1

            # Apply budget filter
            if not (request.budget_min <= fe_obj.hourly_rate <= request.budget_max):
                continue # Skip if outside budget

            # Weighted final score (as per user's formula)
            final_score = (
                0.30 * bio_similarity + 
                0.20 * past_similarity + 
                0.15 * fe_obj.success_rate + 
                0.15 * fe_obj.client_satisfaction + 
                0.10 * fe_obj.communication_score + 
                0.10 * hourly_score
            )

            # Clamp final score between 0 and 1
            final_score = max(0.0, min(1.0, final_score))

            components = ScoreComponents(
                bio_score=bio_similarity,
                past_score=past_similarity,
                success_rate=fe_obj.success_rate,
                client_satisfaction=fe_obj.client_satisfaction,
                communication_score=fe_obj.communication_score,
                hourly_score=hourly_score
            )

            # Generate reason (simple for now)
            reason = f"Strong match in {'bio' if bio_similarity > past_similarity else 'past projects'} " \
                     f"({final_score:.2f} score). High success rate ({fe_obj.success_rate:.2f})."

            results.append(Result(
                freelancer_id=fe_obj.freelancer_id,
                score=final_score,
                components=components,
                reason=reason
            ))

        # Sort results by score in descending order
        results.sort(key=lambda x: x.score, reverse=True)

        return RecommendResponse(results=results[:request.top_k])