# app/api/v1/endpoints/recommend.py - API endpoints for freelancer and project recommendations.

from fastapi import APIRouter, Depends, HTTPException
from app.models import RecommendationRequest, RecommendationResponse
from app.agents.recommendation_agent import recommend_hylancer_agent, recommend_project_agent

router = APIRouter()

@router.post("/recommend-hylancer", response_model=RecommendationResponse)
async def recommend_hylancer(request: RecommendationRequest):
    """Recommends freelancers based on a query."""
    try:
        result = await recommend_hylancer_agent(request.query, request.top_k)
        return RecommendationResponse(recommendations=result.get("recommendations", []))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommend-project", response_model=RecommendationResponse)
async def recommend_project(request: RecommendationRequest):
    """Recommends projects based on a query."""
    try:
        result = await recommend_project_agent(request.query, request.top_k)
        return RecommendationResponse(recommendations=result.get("recommendations", []))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
