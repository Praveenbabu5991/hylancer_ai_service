# app/api/v1/endpoints/embeddings.py
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from loguru import logger

from app.core.db import get_db
from app.core.postgres_client import PostgresClient
from app.services.embedding_service import HylancerEmbeddingService, ProjectEmbeddingService
from app.schemas.embeddings import (
    HylancerEmbeddingCreateRequest,
    HylancerEmbeddingUpdateRequest,
    HylancerEmbeddingResponse,
    HylancerEmbeddingStatusResponse,
    HylancerEmbeddingDeleteResponse,
    HylancerListResponse,
    HylancerSchema,
    ProjectEmbeddingCreateRequest,
    ProjectEmbeddingResponse,
    ProjectEmbeddingStatusResponse,
    ProjectEmbeddingDeleteResponse,
    ProjectListResponse,
    ProjectSchema,
)

router = APIRouter()


# ========== Dependency Injectors ==========

async def get_hylancer_embedding_service(db: AsyncSession = Depends(get_db)) -> HylancerEmbeddingService:
    postgres_client = PostgresClient(db)
    return HylancerEmbeddingService(postgres_client)


async def get_project_embedding_service(db: AsyncSession = Depends(get_db)) -> ProjectEmbeddingService:
    postgres_client = PostgresClient(db)
    return ProjectEmbeddingService(postgres_client)


# ========== Hylancer Embedding Endpoints ==========

@router.post(
    "/hylancer_embeddings",
    response_model=HylancerEmbeddingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Hylancer Embedding",
    description="Generate and store embedding for a hylancer"
)
async def create_hylancer_embedding(
    request: HylancerEmbeddingCreateRequest = Body(
        ...,
        example={
            "hylancer_id": "7c573112-87c5-4b08-b393-91a6b25ad7e4",
            "bio": "Experienced software engineer.",
            "skills": ["Python"],
        }
    ),
    service: HylancerEmbeddingService = Depends(get_hylancer_embedding_service)
):
    """Create or update hylancer embedding with bio and past projects."""
    try:
        logger.info(f"Received request to create embedding for hylancer_id: {request.hylancer_id}")
        response = await service.create_or_update_embedding(request)
        return response
    except Exception as e:
        logger.exception(f"Error creating hylancer embedding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create embedding: {str(e)}"
        )


@router.put(
    "/hylancer_embeddings/{hylancer_id}",
    response_model=HylancerEmbeddingResponse,
    summary="Update Hylancer Embedding",
    description="""Update existing hylancer embedding with partial data.

    Common usage patterns:
    - Call 1: Update bio and skills
    - Call 2: Update past_projects (last 25 merged), total_projects (count), and client_satisfaction (rating)

    All fields are optional - send only what needs to be updated."""
)
async def update_hylancer_embedding(
    hylancer_id: UUID,
    request: HylancerEmbeddingUpdateRequest = Body(
        ...,
        examples={
            "basic_profile": {
                "summary": "Update bio and skills",
                "description": "Common Call 1: Update basic profile information",
                "value": {
                    "bio": "Updated bio text",
                    "skills": ["Python", "Django", "FastAPI"]
                }
            },
            "past_projects_metrics": {
                "summary": "Update past projects and metrics",
                "description": "Common Call 2: Update past projects (last 25 merged), total count, and ratings",
                "value": {
                    "past_projects": "Project 1 description... Project 2 description... Project 25 description",
                    "total_projects": 150,
                    "client_satisfaction": 0.96
                }
            },
            "partial_update": {
                "summary": "Update any single field",
                "description": "You can update any combination of fields",
                "value": {
                    "hourly_rate": 100.0
                }
            }
        }
    ),
    service: HylancerEmbeddingService = Depends(get_hylancer_embedding_service)
):
    """Update hylancer embedding with partial data.

    All fields are optional. Common usage:
    - Call 1: Update bio and skills
    - Call 2: Update past_projects, total_projects, and client_satisfaction
    """
    try:
        logger.info(f"Received request to update embedding for hylancer_id: {hylancer_id}")
        response = await service.update_embedding(hylancer_id, request)
        return response
    except Exception as e:
        logger.exception(f"Error updating hylancer embedding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update embedding: {str(e)}"
        )


@router.get(
    "/hylancer_embeddings/{hylancer_id}",
    response_model=HylancerEmbeddingStatusResponse,
    summary="Get Hylancer Embedding Status",
    description="Get the status and metadata of a hylancer embedding"
)
async def get_hylancer_embedding_status(
    hylancer_id: UUID,
    service: HylancerEmbeddingService = Depends(get_hylancer_embedding_service)
):
    """Get hylancer embedding status."""
    try:
        response = await service.get_embedding_status(hylancer_id)
        if not response or not response.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hylancer embedding not found for ID: {hylancer_id}"
            )
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting hylancer embedding status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get embedding status: {str(e)}"
        )


@router.delete(
    "/hylancer_embeddings/{hylancer_id}",
    response_model=HylancerEmbeddingDeleteResponse,
    summary="Delete Hylancer Embedding",
    description="Delete a hylancer embedding"
)
async def delete_hylancer_embedding(
    hylancer_id: UUID,
    service: HylancerEmbeddingService = Depends(get_hylancer_embedding_service)
):
    """Delete hylancer embedding."""
    try:
        logger.info(f"Received request to delete embedding for hylancer_id: {hylancer_id}")
        deleted = await service.delete_embedding(hylancer_id)
        return HylancerEmbeddingDeleteResponse(
            hylancer_id=hylancer_id,
            deleted=deleted
        )
    except Exception as e:
        logger.exception(f"Error deleting hylancer embedding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete embedding: {str(e)}"
        )

@router.get(
    "/hylancer_embeddings",
    response_model=HylancerListResponse,
    summary="Get All Hylancer Embeddings",
    description="Retrieve a list of all stored hylancer embeddings"
)
async def get_all_hylancers(
    service: HylancerEmbeddingService = Depends(get_hylancer_embedding_service)
):
    """Retrieve all hylancer embeddings."""
    try:
        hylancers = await service.get_all_hylancer_embeddings()
        return HylancerListResponse(
            total_hylancers=len(hylancers),
            hylancers=[HylancerSchema.model_validate(h) for h in hylancers]
        )
    except Exception as e:
        logger.exception(f"Error retrieving all hylancer embeddings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve hylancer embeddings: {str(e)}"
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
