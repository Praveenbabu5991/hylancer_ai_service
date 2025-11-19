#!/bin/bash
# entrypoint.sh - Docker entrypoint script for AI service
# Initializes database and runs migrations before starting the application

set -e

echo "========================================="
echo "Hylancer AI Service - Starting"
echo "========================================="

# Step 1: Initialize database (create DB and enable pgvector)
/app/scripts/init_database.sh

# Step 2: Run database migrations
echo "[Migrations] Running Alembic migrations..."
alembic upgrade head
echo "[Migrations] Complete!"
echo ""

# Step 3: Start the application
echo "[Application] Starting FastAPI server..."
exec "$@"
