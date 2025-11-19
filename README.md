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

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key (or Gemini/Bedrock credentials)

### Option 1: Container Mode (Recommended for Quick Start)

1. **Clone and configure**:
   ```bash
   git clone <repository-url>
   cd hylancer-ai-service
   cp .env.example .env
   ```

2. **Add your API keys** to `.env`:
   ```env
   OPENAI_API_KEY=your_key_here
   # Or use Gemini:
   # LLM_PROVIDER=gemini
   # GOOGLE_API_KEY=your_key_here
   ```

3. **Start the service**:
   ```bash
   docker-compose up
   ```

4. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

**That's it!** Database and tables are created automatically.

### Option 2: Local PostgreSQL Mode

If you want to use your local PostgreSQL instead of the container:

1. **Install pgvector** (one-time):
   ```bash
   ./scripts/install_pgvector.sh
   ```

2. **Configure PostgreSQL** for Docker (one-time):
   ```bash
   ./scripts/configure_postgres_docker.sh
   ./scripts/fix_docker_network.sh
   ```

3. **Update `.env`** to use local PostgreSQL:
   ```env
   # Use your postgres superuser credentials
   DATABASE_URL=postgresql+asyncpg://postgres:your_password@host.docker.internal:5432/hylancer_ai
   ```

4. **Start the service**:
   ```bash
   docker-compose up
   ```

**Database auto-created!** No manual setup needed.

For detailed setup instructions and troubleshooting, see [DATABASE_SETUP.md](DATABASE_SETUP.md).

## Deployment

### AWS ECR Deployment

1. **Build the image**:
   ```bash
   docker build -t hylancer-ai-service .
   ```

2. **Tag and push to ECR**:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   docker tag hylancer-ai-service:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/hylancer-ai-service:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/hylancer-ai-service:latest
   ```

3. **Configure environment**:
   - Set `DATABASE_URL` to AWS RDS PostgreSQL endpoint
   - Ensure RDS has pgvector extension installed
   - Set API keys via AWS Secrets Manager or environment variables

4. **Deploy** via ECS, EKS, or EC2

### Environment Variables

Required in `.env` or production environment:

```env
# LLM Provider
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key

# Database (auto-created on startup)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database

# Optional: Internal microservices
USER_SERVICE_URL=http://user-management:8085
PROJECT_SERVICE_URL=http://project-management:8084
```

## API Usage

### Interactive Documentation
Visit http://localhost:8000/docs for interactive API documentation.

### Example: Generate Freelancer Bio
```bash
curl -X POST "http://localhost:8000/api/v1/generation/generate-bio" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123",
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "experience_years": 5
  }'
```

### Example: Get Freelancer Recommendations
```bash
curl -X POST "http://localhost:8000/api/v1/recommendations/freelancers" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "456",
    "project_description": "Need Python developer for API development",
    "required_skills": ["Python", "FastAPI"]
  }'
```

For more examples, see [Quick Start Guide](quick_start_guide.md).

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