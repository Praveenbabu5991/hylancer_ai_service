# app/api/v1/router.py - Combines all v1 API endpoint routers.

from fastapi import APIRouter
from app.api.v1.endpoints import recommend, generate, embeddings, health

api_router = APIRouter()

# Recommendation endpoints
api_router.include_router(recommend.router, prefix="", tags=["recommendations"])

# Generation endpoints (legacy)
api_router.include_router(generate.router, prefix="", tags=["generations"])

# Embedding management endpoints
api_router.include_router(embeddings.router, prefix="", tags=["embeddings"])

# Health and metrics endpoints
api_router.include_router(health.router, prefix="", tags=["health"])
