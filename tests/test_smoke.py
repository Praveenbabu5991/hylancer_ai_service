# tests/test_smoke.py - Uses FastAPI TestClient to test /health, /generate-bio, and /recommend.

from fastapi.testclient import TestClient
from app.main import app, HealthCheckResponse # Import HealthCheckResponse from app.main
from app.models import BioRequest, BioResponse # Keep other imports from app.models
from app.schemas.recommend import RecommendRequest, RecommendResponse # Import new schemas
from uuid import uuid4

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    health_response = HealthCheckResponse(**response.json())
    assert health_response.status == "ok"
    assert health_response.version == app.version

def test_generate_bio_mock_mode():
    # Assuming LLM_PROVIDER is set to 'mock' in .env for testing
    request_payload = {
        "freelancer_skills": ["Python", "FastAPI", "LangChain"],
        "experience_level": "Senior",
        "tone": "professional"
    }
    response = client.post("/api/v1/generate-bio", json=request_payload)
    assert response.status_code == 200
    bio_response = BioResponse(**response.json())
    assert "Mock professional bio for an Senior freelancer with skills Python, FastAPI, LangChain." in bio_response.bio

def test_recommend_freelancers_mock_mode():
    # First, create a mock embedding for a freelancer
    freelancer_id = uuid4()
    embedding_payload = {
        "freelancer_id": str(freelancer_id),
        "bio": "Experienced Python developer with expertise in web scraping and data analysis.",
        "past_projects": "Developed a web scraping tool for e-commerce, analyzed large datasets for a fintech company.",
        "success_rate": 0.95,
        "client_satisfaction": 0.90,
        "communication_score": 0.88,
        "hourly_rate": 50.0
    }
    response = client.post("/api/v1/embeddings", json=embedding_payload)
    assert response.status_code == 201

    # Now, test the recommendation endpoint
    request_payload = {
        "project_description": "Build a data analysis dashboard using Python.",
        "skills": ["Python", "Data Analysis", "Dashboards"],
        "budget_min": 40,
        "budget_max": 60,
        "region": "Any",
        "top_k": 1
    }
    response = client.post("/api/v1/recommend", json=request_payload)
    assert response.status_code == 200
    recommendation_response = RecommendResponse(**response.json())
    assert len(recommendation_response.results) > 0
    assert recommendation_response.results[0].freelancer_id == freelancer_id
    assert recommendation_response.results[0].score > 0

def test_generate_project_description_mock_mode():
    request_payload = {
        "project_title": "AI Chatbot",
        "keywords": ["NLP", "customer service"],
        "length": "short"
    }
    response = client.post("/api/v1/generate-project-description", json=request_payload)
    assert response.status_code == 200
    description = response.json()["description"]
    assert "Mock short description for project 'AI Chatbot'" in description
