# Quick Start Guide: Hylancer AI Service

This guide will walk you through setting up and running the Hylancer AI Service locally using Docker Compose. It covers prerequisites, environment setup, database initialization, sample data ingestion, and API access.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

-   **Git**: For cloning the repository.
-   **Docker & Docker Compose**: For containerizing the application and its services.
    -   [Install Docker Engine](https://docs.docker.com/engine/install/)
    -   [Install Docker Compose](https://docs.docker.com/compose/install/)
-   **Python 3.9+**: While the application runs in Docker, you'll need Python locally to run the database migration and sample data ingestion scripts.
    -   [Install Python](https://www.python.org/downloads/)
-   **Poetry (Optional but Recommended)**: For managing Python dependencies locally.
    -   [Install Poetry](https://python-poetry.org/docs/#installation)

## 1. Clone the Repository

First, clone the Hylancer AI Service repository to your local machine:

```bash
git clone https://github.com/your-username/hylancer_ai_service.git
cd hylancer_ai_service
```

## 2. Environment Setup

Create a `.env` file by copying the provided example. This file will store your environment variables, including database credentials and API keys.

```bash
cp .env.example .env
```

Open the newly created `.env` file and fill in the necessary values. At a minimum, you should configure the `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, and `OPENAI_API_KEY` (or equivalent for your chosen LLM provider).

```ini
# .env

# Database Configuration
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=hylancer_ai
POSTGRES_PORT=5433

# Application Configuration
APP_PORT=8000
ENV=development

# LLM Configuration (Example for OpenAI)
LLM_PROVIDER=openai
OPENAI_API_KEY="your_openai_api_key_here"
# GEMINI_API_KEY="your_gemini_api_key_here"
# EMBEDDING_MODEL=text-embedding-ada-002 # or text-embedding-3-small, text-embedding-3-large
EMBEDDING_MODEL=text-embedding-3-large
```

## 3. Run Docker Compose

Start the PostgreSQL database and the Hylancer AI Service application using Docker Compose. The `--build` flag ensures that the Docker images are built from scratch, and `--force-recreate` ensures that containers are recreated even if their configuration hasn't changed.

```bash
docker compose up --build --force-recreate -d
```

This command will:
-   Build the `hylancer-ai-service` Docker image.
-   Start the `hylancer-postgres` container (PostgreSQL with `pgvector`).
-   Start the `hylancer-ai-service` application container.

Verify that both containers are running:

```bash
docker ps
```

You should see `hylancer-postgres` and `hylancer-ai-service` listed as `Up`.

## 4. Initialize Database Schema (Run Migrations)

The database tables need to be created using Alembic migrations. Ensure your local Python environment has the project dependencies installed (preferably in a virtual environment).

If you are using Poetry:

```bash
poetry install
poetry shell
```

Otherwise, create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Once your environment is set up, run the Alembic migrations:

```bash
./venv/bin/alembic upgrade head
```

This will create all necessary tables, including `freelancer_embeddings` and `project_embeddings`.

## 5. Ingest Sample Data

To demonstrate the API functionality, ingest some sample data into the database. This script uses the API endpoints to create sample freelancer and project embeddings.

```bash
./venv/bin/python ingest_sample_data.py
```

## 6. Access the API Documentation (Swagger UI)

Once the service is running, you can access the interactive API documentation (Swagger UI) in your web browser:

[http://localhost:8000/docs](http://localhost:8000/docs)

Here you can explore all available endpoints, their request/response schemas, and try them out directly.

## 7. Test Endpoints

You can test the endpoints using `curl` or directly from the Swagger UI.

### Health Check

```bash
curl http://localhost:8000/health
# Expected Output: {"status":"ok","version":"1.0.0"}
```

### Get All Freelancer Embeddings

```bash
curl http://localhost:8000/api/v1/embeddings
# Expected Output: JSON array of freelancer data
```

### Get All Project Embeddings

```bash
curl http://localhost:8000/api/v1/project_embeddings
# Expected Output: JSON array of project data
```

### Recommend Hylancers for a Project

Use a `project_id` from the output of `GET /api/v1/project_embeddings`.

```bash
curl -X POST "http://localhost:8000/api/v1/recommend_hylancer" \
  -H "Content-Type: application/json" \
  -d '{ "project_id": "<YOUR_PROJECT_ID_HERE>", "top_k": 5 }'
```

### Recommend Projects for a Freelancer

Use a `freelancer_id` from the output of `GET /api/v1/embeddings`.

```bash
curl -X POST "http://localhost:8000/api/v1/recommend_projects" \
  -H "Content-Type: application/json" \
  -d '{ "hylancer_id": "<YOUR_FREELANCER_ID_HERE>", "top_k": 5 }'
```

This completes the quick start guide. You now have a fully functional Hylancer AI Service running locally with sample data!
