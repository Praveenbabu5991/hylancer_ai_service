# Hylancer AI Service

This is an AI microservice built with FastAPI and LangChain, designed to provide intelligent recommendations and content generation for the Hylancer platform.

## Features

- **Freelancer Recommendation:** Recommends freelancers based on project requirements.
- **Project Recommendation:** Recommends projects to freelancers based on their skills.
- **Freelancer and Project Embedding Management:** CRUD operations for freelancer and project embeddings, including listing all embeddings.
- **Project Description Generation:** Creates compelling project descriptions.
- **Freelancer Bio Generation:** Crafts professional bios for freelancers.
- **LLM Flexibility:** Supports Gemini, AWS Bedrock, and a mock LLM for development.
- **Local Vector Database:** Uses ChromaDB for local vector storage and retrieval.
- **Internal Service Integration:** Provides a robust client for communicating with other internal microservices.
- **Containerized:** Docker and Docker Compose for easy deployment.

## Technologies Used

- **Framework:** FastAPI
- **AI Framework:** LangChain
- **LLM Providers:** Google Gemini, AWS Bedrock (optional), MockLLM
- **Vector Database:** PostgreSQL with pgvector
- **ORM:** SQLAlchemy
- **Database Migrations:** Alembic
- **HTTP Client:** httpx (for internal service communication)
- **Containerization:** Docker, Docker Compose
- **Language:** Python 3.11
- **Configuration:** `python-dotenv`
- **Logging:** `loguru`
- **Testing:** `pytest`, `FastAPI TestClient`

## Setup and Installation

For detailed setup and installation instructions, please refer to the [Quick Start Guide](quick_start_guide.md).

## Usage

For details on how to use the API and its endpoints, please refer to the [Quick Start Guide](quick_start_guide.md).

## Development

To run the application locally without Docker (e.g., for faster development iterations):

1.  **Create and activate a virtual environment:**
    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the FastAPI application:**
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The `--reload` flag enables hot-reloading during development.

## Testing

To run the tests:

1.  Ensure dependencies are installed (see Development section).
2.  Run pytest:
    ```bash
    pytest
    ```

## Project Structure

```
hylancer-ai-service/
├── .env.example
├── .gitignore
├── alembic.ini
├── alembic/
├── Dockerfile
├── init-db.sql
├── ingest_sample_data.py
├── quick_start_guide.md
├── README.md
├── app/
│   ├── __init__.py
│   ├── agents/
│   │   ├── generation_agent.py
│   │   └── recommendation_agent.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── endpoints/
│   │       │   ├── embeddings.py
│   │       │   ├── generate.py
│   │       │   ├── generation.py
│   │       │   ├── health.py
│   │       │   ├── recommend.py
│   │       │   └── __pycache__/
│   │       └── router.py
│   ├── config.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── llm_client.py
│   │   ├── llm.py
│   │   ├── postgres_client.py
│   │   ├── vector_client.py
│   │   ├── vector_store.py
│   │   └── __pycache__/
│   ├── db_models.py
│   ├── dependencies.py
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── base_client.py
│   │   ├── billing_management.py
│   │   ├── chat_management.py
│   │   ├── payment_management.py
│   │   ├── project_management.py
│   │   └── user_management.py
│   ├── main.py
│   ├── models.py
│   ├── __pycache__/
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── embeddings.py
│   │   ├── generate.py
│   │   ├── generation.py
│   │   ├── recommend.py
│   │   └── __pycache__/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── embedding_service.py
│   │   ├── generation_service.py
│   │   ├── recommendation_service.py
│   │   └── __pycache__/
│   └── utils/
│       ├── parser.py
│       ├── prompts.py
│       ├── scoring.py
│       └── __pycache__/
├── data/
│   └── .gitkeep
├── docker-compose.yml
├── notebooks/
│   └── .gitkeep
├── requirements.txt
├── scripts/
│   └── .gitkeep
├── terraform/
│   └── .gitkeep
└── tests/
    ├── __init__.py
    ├── test_generate.py
    ├── test_recommend.py
    └── test_smoke.py
```