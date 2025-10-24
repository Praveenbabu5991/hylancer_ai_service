# tests/test_smoke.py - Uses FastAPI TestClient to test /health and /generate-bio.

from fastapi.testclient import TestClient
from app.main import app
from app.models import HealthCheckResponse, BioRequest, BioResponse

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

def test_recommend_hylancer_mock_mode():
    request_payload = {
        "query": "Looking for a Python developer",
        "top_k": 2
    }
    response = client.post("/api/v1/recommend-hylancer", json=request_payload)
    assert response.status_code == 200
    recommendations = response.json()["recommendations"]
    assert len(recommendations) == 2
    assert "Mock Hylancer 1" in recommendations[0]

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
