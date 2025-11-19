#!/bin/bash
# init_database.sh - Initialize database (works for both container and local PostgreSQL)
# This script runs before the application starts to ensure database exists

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}[Database Initialization] Starting...${NC}"

# Extract database info from DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}ERROR: DATABASE_URL not set${NC}"
    exit 1
fi

# Parse DATABASE_URL (format: postgresql+asyncpg://user:password@host:port/dbname)
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASSWORD=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')

echo -e "${YELLOW}Database Configuration:${NC}"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  User: $DB_USER"
echo "  Database: $DB_NAME"

# Wait for PostgreSQL to be ready
echo -e "${YELLOW}[1/3] Waiting for PostgreSQL to be ready...${NC}"
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "  Waiting for PostgreSQL... (attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 1
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}✗ PostgreSQL not available after $MAX_RETRIES attempts${NC}"
    exit 1
fi

# Check if database exists
echo -e "${YELLOW}[2/3] Checking if database '$DB_NAME' exists...${NC}"
DB_EXISTS=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';" 2>/dev/null || echo "")

if [ -z "$DB_EXISTS" ]; then
    echo -e "${YELLOW}Creating database '$DB_NAME'...${NC}"
    if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE \"$DB_NAME\" OWNER \"$DB_USER\";" 2>&1; then
        echo -e "${GREEN}✓ Database '$DB_NAME' created${NC}"
    else
        echo -e "${RED}✗ Failed to create database${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Database '$DB_NAME' already exists${NC}"
fi

# Check if pgvector extension exists
echo -e "${YELLOW}[3/3] Checking pgvector extension...${NC}"
VECTOR_EXISTS=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT 1 FROM pg_extension WHERE extname='vector';" 2>/dev/null || echo "")

if [ -z "$VECTOR_EXISTS" ]; then
    echo -e "${YELLOW}Enabling pgvector extension...${NC}"
    if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>&1; then
        echo -e "${GREEN}✓ pgvector extension enabled${NC}"
    else
        echo -e "${RED}✗ Failed to enable pgvector extension${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ pgvector extension already enabled${NC}"
fi

echo -e "${GREEN}[Database Initialization] Complete!${NC}"
echo ""
