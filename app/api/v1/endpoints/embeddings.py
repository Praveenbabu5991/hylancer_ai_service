# app/api/v1/endpoints/embeddings.py
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from loguru import logger

from app.core.db import get_db
from app.core.postgres_client import PostgresClient
from app.services.embedding_service import FreelancerEmbeddingService, ProjectEmbeddingService
from app.schemas.embeddings import (
    FreelancerEmbeddingCreateRequest,
    FreelancerEmbeddingResponse,
    FreelancerEmbeddingStatusResponse,
    FreelancerEmbeddingDeleteResponse,
    FreelancerListResponse,
    FreelancerSchema,
    ProjectEmbeddingCreateRequest,
    ProjectEmbeddingResponse,
    ProjectEmbeddingStatusResponse,
    ProjectEmbeddingDeleteResponse,
    ProjectListResponse,
    ProjectSchema,
)

router = APIRouter()


# ========== Dependency Injectors ==========

async def get_freelancer_embedding_service(db: AsyncSession = Depends(get_db)) -> FreelancerEmbeddingService:
    postgres_client = PostgresClient(db)
    return FreelancerEmbeddingService(postgres_client)


async def get_project_embedding_service(db: AsyncSession = Depends(get_db)) -> ProjectEmbeddingService:
    postgres_client = PostgresClient(db)
    return ProjectEmbeddingService(postgres_client)


# ========== Freelancer Embedding Endpoints ==========

async def create_freelancer_embedding(
    request: FreelancerEmbeddingCreateRequest = Body(
        ...,
        example={
            "freelancer_id": "7c573112-87c5-4b08-b393-91a6b25ad7e4",
            "bio": "Experienced software engineer with a passion for building scalable web applications. Proficient in Python, JavaScript, and various frameworks. Proven track record of delivering high-quality code and leading successful projects.",
            "past_projects": "Developed a full-stack e-commerce platform using React and Node.js. Implemented a real-time chat application with WebSockets. Contributed to an open-source data visualization library.",
            "skills": ["Python", "JavaScript", "React", "Node.js", "PostgreSQL", "Docker"],
            "success_rate": 0.95,
            "client_satisfaction": 0.92,
            "communication_score": 0.98,
            "hourly_rate": 75.0,
            "availability_status": "available",
            "location": "Remote",
            "experience_level": 4,
            "total_projects": 15,
            "metadata": {
                "is_new_freelancer": False,
                "has_past_projects": True,
                "feedback_count": 25
            }
        }
    ),
    service: FreelancerEmbeddingService = Depends(get_freelancer_embedding_service)
):
    """Create or update freelancer embedding with bio and past projects."""
    try:
        logger.info(f"Received request to create embedding for freelancer_id: {request.freelancer_id}")
        response = await service.create_or_update_embedding(request)
        return response
    except Exception as e:
        logger.exception(f"Error creating freelancer embedding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create embedding: {str(e)}"
        )


@router.put(
    "/embeddings/{freelancer_id}",
    response_model=FreelancerEmbeddingResponse,
    summary="Update Freelancer Embedding",
    description="Update existing freelancer embedding"
)
async def update_freelancer_embedding(
    freelancer_id: UUID,
    request: FreelancerEmbeddingCreateRequest = Body(
        ...,
        example={
            "freelancer_id": "7c573112-87c5-4b08-b393-91a6b25ad7e4",
            "bio": "Experienced software engineer with a passion for building scalable web applications. Proficient in Python, JavaScript, and various frameworks. Proven track record of delivering high-quality code and leading successful projects.",
            "past_projects": "Developed a full-stack e-commerce platform using React and Node.js. Implemented a real-time chat application with WebSockets. Contributed to an open-source data visualization library.",
            "skills": ["Python", "JavaScript", "React", "Node.js", "PostgreSQL", "Docker"],
            "success_rate": 0.95,
            "client_satisfaction": 0.92,
            "communication_score": 0.98,
            "hourly_rate": 75.0,
            "availability_status": "available",
            "location": "Remote",
            "experience_level": 4,
            "total_projects": 15,
            "metadata": {
                "is_new_freelancer": False,
                "has_past_projects": True,
                "feedback_count": 25
            }
        }
    ),
    service: FreelancerEmbeddingService = Depends(get_freelancer_embedding_service)
):
    """Update freelancer embedding."""
    if freelancer_id != request.freelancer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Freelancer ID in path and body do not match"
        )

    try:
        logger.info(f"Received request to update embedding for freelancer_id: {freelancer_id}")
        response = await service.create_or_update_embedding(request)
        return response
    except Exception as e:
        logger.exception(f"Error updating freelancer embedding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update embedding: {str(e)}"
        )


@router.get(
    "/embeddings/{freelancer_id}",
    response_model=FreelancerEmbeddingStatusResponse,
    summary="Get Freelancer Embedding Status",
    description="Get the status and metadata of a freelancer embedding"
)
async def get_freelancer_embedding_status(
    freelancer_id: UUID,
    service: FreelancerEmbeddingService = Depends(get_freelancer_embedding_service)
):
    """Get freelancer embedding status."""
    try:
        response = await service.get_embedding_status(freelancer_id)
        if not response or not response.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Freelancer embedding not found for ID: {freelancer_id}"
            )
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting freelancer embedding status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get embedding status: {str(e)}"
        )


@router.delete(
    "/embeddings/{freelancer_id}",
    response_model=FreelancerEmbeddingDeleteResponse,
    summary="Delete Freelancer Embedding",
    description="Delete a freelancer embedding"
)
async def delete_freelancer_embedding(
    freelancer_id: UUID,
    service: FreelancerEmbeddingService = Depends(get_freelancer_embedding_service)
):
    """Delete freelancer embedding."""
    try:
        logger.info(f"Received request to delete embedding for freelancer_id: {freelancer_id}")
        deleted = await service.delete_embedding(freelancer_id)
        return FreelancerEmbeddingDeleteResponse(
            freelancer_id=freelancer_id,
            deleted=deleted
        )
    except Exception as e:
        logger.exception(f"Error deleting freelancer embedding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete embedding: {str(e)}"
        )

@router.get(
    "/embeddings",
    response_model=FreelancerListResponse,
    summary="Get All Freelancer Embeddings",
    description="Retrieve a list of all stored freelancer embeddings"
)
async def get_all_freelancers(
    service: FreelancerEmbeddingService = Depends(get_freelancer_embedding_service)
):
    """Retrieve all freelancer embeddings."""
    try:
        freelancers = await service.get_all_freelancer_embeddings()
        return FreelancerListResponse(
            total_freelancers=len(freelancers),
            freelancers=[FreelancerSchema.model_validate(f) for f in freelancers]
        )
    except Exception as e:
        logger.exception(f"Error retrieving all freelancer embeddings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve freelancer embeddings: {str(e)}"
        )

# ========== Project Embedding Endpoints ==========

@router.post(
    "/project_embeddings",
    response_model=ProjectEmbeddingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Project Embedding",
    description="Generate and store embedding for a project"
)
async def create_project_embedding(
    request: ProjectEmbeddingCreateRequest = Body(
        ...,
        example={
            "project_id": "b582a86f-4e21-4c18-943a-b6ab1ec6f907",
            "title": "Develop a new e-commerce platform",
            "description": "We are looking for a skilled full-stack developer to build a new e-commerce platform from scratch. The platform should include user authentication, product listings, shopping cart functionality, and payment integration. Experience with modern web technologies is essential.",
            "required_skills": ["React", "Node.js", "PostgreSQL", "AWS"],
            "budget": 15000.0,
            "required_experience_level": 4,
            "preferred_location": "Remote",
            "status": "open",
            "metadata": {
                "is_generic_description": False,
                "skill_count": 4
            }
        }
    ),
    service: ProjectEmbeddingService = Depends(get_project_embedding_service)
):
    """Create or update project embedding."""
    try:
        logger.info(f"Received request to create embedding for project_id: {request.project_id}")
        response = await service.create_or_update_embedding(request)
        return response
    except Exception as e:
        logger.exception(f"Error creating project embedding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create embedding: {str(e)}"
        )


@router.put(
    "/project_embeddings/{project_id}",
    response_model=ProjectEmbeddingResponse,
    summary="Update Project Embedding",
    description="Update existing project embedding"
)
async def update_project_embedding(
    project_id: UUID,
    request: ProjectEmbeddingCreateRequest = Body(
        ...,
        example={
            "project_id": "b582a86f-4e21-4c18-943a-b6ab1ec6f907",
            "title": "Develop a new e-commerce platform",
            "description": "We are looking for a skilled full-stack developer to build a new e-commerce platform from scratch. The platform should include user authentication, product listings, shopping cart functionality, and payment integration. Experience with modern web technologies is essential.",
            "required_skills": ["React", "Node.js", "PostgreSQL", "AWS"],
            "budget": 15000.0,
            "required_experience_level": 4,
            "preferred_location": "Remote",
            "status": "open",
            "metadata": {
                "is_generic_description": False,
                "skill_count": 4
            }
        }
    ),
    service: ProjectEmbeddingService = Depends(get_project_embedding_service)
):
    """Update project embedding."""
    if project_id != request.project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project ID in path and body do not match"
        )

    try:
        logger.info(f"Received request to update embedding for project_id: {project_id}")
        response = await service.create_or_update_embedding(request)
        return response
    except Exception as e:
        logger.exception(f"Error updating project embedding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update embedding: {str(e)}"
        )


@router.get(
    "/project_embeddings/{project_id}",
    response_model=ProjectEmbeddingStatusResponse,
    summary="Get Project Embedding Status",
    description="Get the status and metadata of a project embedding"
)
async def get_project_embedding_status(
    project_id: UUID,
    service: ProjectEmbeddingService = Depends(get_project_embedding_service)
):
    """Get project embedding status."""
    try:
        response = await service.get_embedding_status(project_id)
        if not response or not response.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project embedding not found for ID: {project_id}"
            )
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting project embedding status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get embedding status: {str(e)}"
        )


@router.delete(
    "/project_embeddings/{project_id}",
    response_model=ProjectEmbeddingDeleteResponse,
    summary="Delete Project Embedding",
    description="Delete a project embedding"
)
async def delete_project_embedding(
    project_id: UUID,
    service: ProjectEmbeddingService = Depends(get_project_embedding_service)
):
    """Delete project embedding."""
    try:
        logger.info(f"Received request to delete embedding for project_id: {project_id}")
        deleted = await service.delete_embedding(project_id)
        return ProjectEmbeddingDeleteResponse(
            project_id=project_id,
            deleted=deleted
        )
    except Exception as e:
        logger.exception(f"Error deleting project embedding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete embedding: {str(e)}"
        )

@router.get(
    "/project_embeddings",
    response_model=ProjectListResponse,
    summary="Get All Project Embeddings",
    description="Retrieve a list of all stored project embeddings"
)
async def get_all_projects(
    service: ProjectEmbeddingService = Depends(get_project_embedding_service)
):
    """Retrieve all project embeddings."""
    try:
        projects = await service.get_all_project_embeddings()
        return ProjectListResponse(
            total_projects=len(projects),
            projects=[ProjectSchema.model_validate(p) for p in projects]
        )
    except Exception as e:
        logger.exception(f"Error retrieving all project embeddings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve project embeddings: {str(e)}"
        )
