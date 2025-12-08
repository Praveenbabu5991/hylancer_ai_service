# app/main.py - Main FastAPI application entry point.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.v1.router import api_router
from loguru import logger
from pydantic import BaseModel, Field # Import BaseModel and Field for HealthCheckResponse

settings = get_settings()

# Configure logging
logger.add(
    "logs/file_{time}.log",
    rotation="500 MB",
    retention="10 days",
    level="DEBUG" if settings.ENV == "dev" else "INFO",
    enqueue=True
)

class HealthCheckResponse(BaseModel): # Define HealthCheckResponse here
    status: str = Field("ok", description="Status of the service.")
    version: str = Field(..., description="Version of the service.")

app = FastAPI(
    title="Hylancer AI Service",
    version="1.0.0",
    description="AI-powered microservice for Hylancer platform, offering freelancer/project recommendations and content generation.",
    debug=settings.ENV == "dev"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Hylancer AI Service starting up...")
    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
    logger.info(f"Database URL: {settings.DATABASE_URL}") # Log new database URL

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Hylancer AI Service shutting down...")

app.include_router(api_router, prefix="/api/v1")

@app.get("/health", response_model=HealthCheckResponse, tags=["monitoring"])
async def health_check():
    """Checks the health of the service."""
    logger.debug("Health check endpoint called.")
    return HealthCheckResponse(status="ok", version=app.version)
