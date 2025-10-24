# Hylancer AI Service

This is an AI microservice built with FastAPI and LangChain, designed to provide intelligent recommendations and content generation for the Hylancer platform.

## Features

- **Freelancer Recommendation:** Recommends freelancers based on project requirements.
- **Project Recommendation:** Recommends projects to freelancers based on their skills.
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
- **Vector Database:** ChromaDB
- **HTTP Client:** httpx (for internal service communication)
- **Containerization:** Docker, Docker Compose
- **Language:** Python 3.11
- **Configuration:** `python-dotenv`
- **Logging:** `loguru`
- **Testing:** `pytest`, `FastAPI TestClient`

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd hylancer-ai-service
    ```

2.  **Create `.env` file:**
    Copy the `.env.example` file to `.env` and configure your environment variables. At a minimum, set `LLM_PROVIDER`.
    ```bash
    cp .env.example .env
    ```
    Edit `.env`:
    ```ini
    # .env
    ENV=dev
    APP_PORT=8000
    LLM_PROVIDER=mock # Change to 'gemini' or 'bedrock' for real LLMs
    # GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
    # AWS_ACCESS_KEY_ID="YOUR_AWS_ACCESS_KEY_ID"
    # AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET_ACCESS_KEY"
    # AWS_REGION="us-east-1"

    # Internal Microservice URLs (example values)
    BILLING_SERVICE_URL=http://billing-management:8081
    CHAT_SERVICE_URL=http://chat-management:8082
    PAYMENT_SERVICE_URL=http://payment-management:8083
    PROJECT_SERVICE_URL=http://project-management:8084
    USER_SERVICE_URL=http://user-management:8085
    ```

3.  **Build and run with Docker Compose:**
    ```bash
    docker compose up --build
    ```
    This will build the Docker image and start the FastAPI service.

## Usage

Once the service is running, you can access the API documentation at:

[http://localhost:8000/docs](http://localhost:8000/docs)

Here you will find all available endpoints and can interact with them directly.

### Endpoints:

-   `POST /api/v1/recommend-hylancer`: Recommends freelancers.
-   `POST /api/v1/recommend-project`: Recommends projects.
-   `POST /api/v1/generate-project-description`: Generates project descriptions.
-   `POST /api/v1/generate-bio`: Generates freelancer bios.
-   `GET /health`: Health check endpoint.

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
├── Dockerfile
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
│   │       │   ├── generate.py
│   │       │   └── recommend.py
│   │       └── router.py
│   ├── core/
│   │   ├── config.py
│   │   ├── llm_client.py
│   │   └── vector_client.py
│   ├── integrations/
│   │   ├── __init__.py # Initializes the integrations package.
│   │   ├── base_client.py # Reusable async API client for internal services.
│   │   ├── billing_management.py # Handles communication with the billing-management service.
│   │   ├── chat_management.py # Handles communication with the chat-management service.
│   │   ├── payment_management.py # Handles communication with the payment-management service.
│   │   ├── project_management.py # Handles communication with the project-management service.
│   │   └── user_management.py # Handles communication with the user-management service.
│   ├── main.py
│   ├── models.py
│   ├── services/
│   │   ├── generation_service.py
│   │   └── recommendation_service.py
│   └── utils/
│       ├── parser.py
│       └── prompts.py
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
    └── test_smoke.py
```