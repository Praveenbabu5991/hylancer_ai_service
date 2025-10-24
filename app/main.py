# app/main.py - Main FastAPI application entry point.

import sys
import pysqlite3
sys.modules["sqlite3"] = sys.modules["pysqlite3"] = pysqlite3

from fastapi import FastAPI
from app.core.config import get_settings
from app.api.v1.router import api_router
from app.models import HealthCheckResponse
from loguru import logger

settings = get_settings()

# Configure logging
logger.add(
    "logs/file_{time}.log",
    rotation="500 MB",
    retention="10 days",
    level="DEBUG" if settings.ENV == "dev" else "INFO",
    enqueue=True
)

app = FastAPI(
    title="Hylancer AI Service",
    version="1.0.0",
    description="AI-powered microservice for Hylancer platform, offering freelancer/project recommendations and content generation.",
    debug=settings.ENV == "dev"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Hylancer AI Service starting up...")
    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
    logger.info(f"ChromaDB Path: {settings.CHROMA_DB_PATH}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Hylancer AI Service shutting down...")

app.include_router(api_router, prefix="/api/v1")

@app.get("/health", response_model=HealthCheckResponse, tags=["monitoring"])
async def health_check():
    """Checks the health of the service."""
    logger.debug("Health check endpoint called.")
    return HealthCheckResponse(status="ok", version=app.version)
