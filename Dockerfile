# Dockerfile - Dockerfile to build the hylancer-ai-service application image

# Use a slim Python base image
FROM python:3.11-slim-bullseye

# Set working directory
WORKDIR /app


# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copy the application code
COPY . .
# Explicitly copy the updated recommendation_service.py to ensure it's not cached
COPY app/services/recommendation_service.py app/services/recommendation_service.py

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application using Uvicorn
# --host 0.0.0.0 makes the server accessible from outside the container
# --port 8000 specifies the port
# --reload is removed for production readiness, as per instructions
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
