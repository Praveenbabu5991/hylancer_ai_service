# app/api/v1/router.py - Combines all v1 API endpoint routers.

from fastapi import APIRouter
from app.api.v1.endpoints import recommend, generate, embeddings # Import embeddings router

api_router = APIRouter()
api_router.include_router(recommend.router, prefix="", tags=["recommendations"])
api_router.include_router(generate.router, prefix="", tags=["generations"])
api_router.include_router(embeddings.router, prefix="", tags=["embeddings"]) # Include embeddings router
