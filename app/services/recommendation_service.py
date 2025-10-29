# app/services/recommendation_service.py
from typing import List, Optional
from uuid import UUID
import uuid
import time
from loguru import logger

from app.core.postgres_client import PostgresClient
from app.core.config import get_settings
from app.schemas.recommend import (
    HylancerRecommendRequest,
    HylancerRecommendResponse,
    HylancerRecommendationResult,
    HylancerScoreComponents,
    HylancerRecommendationMetadata,
    ProjectRecommendRequest,
    ProjectRecommendResponse,
    ProjectRecommendationResult,
    ProjectScoreComponents,
    ProjectRecommendationMetadata,
)
from app.utils.scoring import (
    calculate_jaccard_similarity,
    get_matched_skills,
    calculate_confidence_level,
    adjust_freelancer_weights,
    calculate_budget_fit,
    generate_freelancer_recommendation_reason,
    generate_project_recommendation_reason,
)

settings = get_settings()


class RecommendationService:
    """Service for handling recommendation logic."""

    def __init__(self, postgres_client: PostgresClient):
        self.postgres_client = postgres_client

    async def recommend_hylancers(
        self,
        request: HylancerRecommendRequest
    ) -> HylancerRecommendResponse:
        """
        Recommend freelancers for a project based on semantic similarity and metrics.

        According to PRD:
        - Vector similarity search (bio + past projects)
        - Skill overlap (Jaccard similarity)
        - Business metrics (success rate, client satisfaction, communication)
        - Dynamic weight adjustment for new freelancers/low feedback
        - Cold-start boost
        """
        start_time = time.time()
        request_id = uuid.uuid4()

        logger.info(f"Recommending freelancers for project_id: {request.project_id}")

        # Get project embedding
        project_embedding_obj = await self.postgres_client.get_project_embedding(request.project_id)
        if not project_embedding_obj:
            logger.warning(f"Project embedding not found for project_id: {request.project_id}")
            return HylancerRecommendResponse(
                project_id=request.project_id,
                total_results=0,
                results=[]
            )

        project_embedding = project_embedding_obj.project_embedding
        project_skills = project_embedding_obj.required_skills

        # Search for similar freelancers
        # Fetch more candidates than needed for filtering
        search_results = await self.postgres_client.search_freelancer_embeddings(
            project_embedding=project_embedding,
            candidate_ids=None,  # No filtering - get all available freelancers
            top_k=request.top_k * 3
        )

        logger.debug(f"Found {len(search_results)} candidate freelancers")

        results: List[HylancerRecommendationResult] = []

        for freelancer_obj, bio_distance, past_project_distance in search_results:
            # Convert distance to similarity (1 - distance)
            bio_similarity = max(0.0, 1.0 - bio_distance) if bio_distance is not None else 0.0

            # Handle None for past_project_distance (e.g., new freelancers)
            if past_project_distance is not None:
                past_project_similarity = max(0.0, 1.0 - past_project_distance)
            else:
                past_project_similarity = 0.0

            # Calculate skill overlap using Jaccard similarity
            skill_overlap = calculate_jaccard_similarity(freelancer_obj.skills, project_skills)
            matched_skills = get_matched_skills(freelancer_obj.skills, project_skills)

            # Get metadata
            meta_info = freelancer_obj.meta_info if freelancer_obj.meta_info else {}
            has_past_projects = meta_info.get("has_past_projects", False)
            feedback_count = meta_info.get("feedback_count", 0)
            is_new_freelancer = meta_info.get("is_new_freelancer", False)

            # Dynamically adjust weights based on freelancer data availability
            weights = adjust_freelancer_weights(
                has_past_projects=has_past_projects,
                feedback_count=feedback_count
            )

            # Calculate weighted score
            final_score = (
                weights["bio_similarity"] * bio_similarity +
                weights["past_project_similarity"] * past_project_similarity +
                weights["skill_overlap"] * skill_overlap +
                weights["success_rate"] * freelancer_obj.success_rate +
                weights["client_satisfaction"] * freelancer_obj.client_satisfaction +
                weights["communication_score"] * freelancer_obj.communication_score
            )

            # Apply cold-start boost if enabled
            if settings.COLD_START_BOOST_ENABLED and is_new_freelancer:
                if freelancer_obj.total_projects < settings.NEW_FREELANCER_PROJECT_THRESHOLD:
                    final_score += settings.COLD_START_BOOST_AMOUNT
                    logger.debug(f"Applied cold-start boost to freelancer {freelancer_obj.freelancer_id}")

            # Clamp score between 0 and 1
            final_score = max(0.0, min(1.0, final_score))

            # Skip if below minimum score threshold
            if final_score < settings.MINIMUM_SCORE:
                continue

            # Determine confidence level
            confidence = calculate_confidence_level(final_score)

            # Generate human-readable reason
            reason = generate_freelancer_recommendation_reason(
                bio_similarity=bio_similarity,
                past_project_similarity=past_project_similarity,
                skill_overlap=skill_overlap,
                matched_skills=matched_skills,
                total_projects=freelancer_obj.total_projects,
                client_satisfaction=freelancer_obj.client_satisfaction,
                communication_score=freelancer_obj.communication_score,
                is_new_freelancer=is_new_freelancer
            )

            # Create result
            result = HylancerRecommendationResult(
                hylancer_id=freelancer_obj.freelancer_id,
                score=final_score,
                components=HylancerScoreComponents(
                    bio_similarity=bio_similarity,
                    past_project_similarity=past_project_similarity,
                    skill_overlap=skill_overlap,
                    success_rate=freelancer_obj.success_rate,
                    client_satisfaction=freelancer_obj.client_satisfaction,
                    communication_score=freelancer_obj.communication_score
                ),
                reason=reason,
                metadata=HylancerRecommendationMetadata(
                    is_new_hylancer=is_new_freelancer,
                    matched_skills=matched_skills,
                    confidence=confidence
                )
            )

            results.append(result)

        # Sort by score descending
        results.sort(key=lambda x: x.score, reverse=True)

        # Limit to top_k
        results = results[:request.top_k]

        # Calculate execution time
        execution_time_ms = int((time.time() - start_time) * 1000)

        # Log recommendation for analytics
        if results:
            avg_score = sum(r.score for r in results) / len(results)
            recommended_ids = [
                {"hylancer_id": str(r.hylancer_id), "score": r.score}
                for r in results
            ]
        else:
            avg_score = 0.0
            recommended_ids = []

        await self.postgres_client.log_recommendation(
            recommendation_type="freelancer",
            request_id=request_id,
            entity_id=request.project_id,
            recommended_ids=recommended_ids,
            filters_applied={"min_score": settings.MINIMUM_SCORE, "top_k": request.top_k},
            avg_score=avg_score,
            result_count=len(results),
            execution_time_ms=execution_time_ms
        )

        logger.info(f"Recommended {len(results)} freelancers in {execution_time_ms}ms")

        return HylancerRecommendResponse(
            project_id=request.project_id,
            total_results=len(results),
            results=results
        )

    async def recommend_projects(
        self,
        request: ProjectRecommendRequest
    ) -> ProjectRecommendResponse:
        """
        Recommend projects for a freelancer based on their experience and skills.

        According to PRD:
        - 50% project similarity (past projects vs project description)
        - 25% skill overlap
        - 25% bio similarity
        """
        start_time = time.time()
        request_id = uuid.uuid4()

        logger.info(f"Recommending projects for hylancer_id: {request.hylancer_id}")

        # Get freelancer embedding
        freelancer_obj = await self.postgres_client.get_freelancer_embedding(request.hylancer_id)
        if not freelancer_obj:
            logger.warning(f"Freelancer embedding not found for hylancer_id: {request.hylancer_id}")
            return ProjectRecommendResponse(
                hylancer_id=request.hylancer_id,
                total_results=0,
                results=[]
            )

        # Search for similar projects
        search_results = await self.postgres_client.search_project_embeddings(
            freelancer_bio_embedding=freelancer_obj.bio_embedding,
            freelancer_past_embedding=freelancer_obj.past_project_embedding,
            project_candidate_ids=None,  # No filtering - get all open projects
            top_k=request.top_k * 2
        )

        logger.debug(f"Found {len(search_results)} candidate projects")

        results: List[ProjectRecommendationResult] = []

        for project_obj, distance in search_results:
            # Convert distance to similarity
            # The distance returned is based on weighted combination in PostgresClient
            # We'll use it as the primary project_similarity score
            project_similarity = max(0.0, 1.0 - distance)

            # Calculate skill overlap
            skill_overlap = calculate_jaccard_similarity(freelancer_obj.skills, project_obj.required_skills)
            matched_skills = get_matched_skills(freelancer_obj.skills, project_obj.required_skills)

            # Calculate bio similarity separately for component breakdown
            # (for display purposes, actual search used combined embedding)
            bio_similarity = project_similarity * 0.5  # Approximation

            # Calculate final score according to PRD weights
            final_score = (
                settings.PROJECT_SIMILARITY_WEIGHT * project_similarity +
                settings.PROJECT_SKILL_OVERLAP_WEIGHT * skill_overlap +
                settings.PROJECT_BIO_SIMILARITY_WEIGHT * bio_similarity
            )

            # Clamp score
            final_score = max(0.0, min(1.0, final_score))

            # Skip if below minimum score threshold
            if final_score < settings.MINIMUM_SCORE:
                continue

            # Calculate budget fit
            budget_fit = calculate_budget_fit(
                freelancer_hourly_rate=float(freelancer_obj.hourly_rate),
                project_budget=float(project_obj.budget)
            )

            # Determine confidence level
            confidence = calculate_confidence_level(final_score)

            # Generate human-readable reason
            reason = generate_project_recommendation_reason(
                project_similarity=project_similarity,
                skill_overlap=skill_overlap,
                matched_skills=matched_skills,
                budget_fit=budget_fit
            )

            # Create result
            result = ProjectRecommendationResult(
                project_id=project_obj.project_id,
                score=final_score,
                components=ProjectScoreComponents(
                    project_similarity=project_similarity,
                    skill_overlap=skill_overlap,
                    bio_similarity=bio_similarity
                ),
                reason=reason,
                metadata=ProjectRecommendationMetadata(
                    matched_skills=matched_skills,
                    budget_fit=budget_fit,
                    confidence=confidence
                )
            )

            results.append(result)

        # Sort by score descending
        results.sort(key=lambda x: x.score, reverse=True)

        # Limit to top_k
        results = results[:request.top_k]

        # Calculate execution time
        execution_time_ms = int((time.time() - start_time) * 1000)

        # Log recommendation for analytics
        if results:
            avg_score = sum(r.score for r in results) / len(results)
            recommended_ids = [
                {"project_id": str(r.project_id), "score": r.score}
                for r in results
            ]
        else:
            avg_score = 0.0
            recommended_ids = []

        await self.postgres_client.log_recommendation(
            recommendation_type="project",
            request_id=request_id,
            entity_id=request.hylancer_id,
            recommended_ids=recommended_ids,
            filters_applied={"min_score": settings.MINIMUM_SCORE, "top_k": request.top_k},
            avg_score=avg_score,
            result_count=len(results),
            execution_time_ms=execution_time_ms
        )

        logger.info(f"Recommended {len(results)} projects in {execution_time_ms}ms")

        return ProjectRecommendResponse(
            hylancer_id=request.hylancer_id,
            total_results=len(results),
            results=results
        )
