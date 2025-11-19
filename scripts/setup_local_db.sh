#!/bin/bash
# setup_local_db.sh - Automated setup script for local PostgreSQL database
# This script sets up the Hylancer AI database on your local PostgreSQL server

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables from .env file
if [ -f .env ]; then
    echo -e "${GREEN}Loading environment variables from .env...${NC}"
    export $(grep -v '^#' .env | xargs)
else
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please create a .env file with your database credentials."
    exit 1
fi

# Set default values if not provided
POSTGRES_USER=${POSTGRES_USER:-user}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-password}
POSTGRES_DB=${POSTGRES_DB:-hylancer_ai}
POSTGRES_HOST=${POSTGRES_HOST:-localhost}
POSTGRES_PORT=${POSTGRES_PORT:-5432}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Hylancer AI Local Database Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Database Configuration:"
echo "  Host: $POSTGRES_HOST"
echo "  Port: $POSTGRES_PORT"
echo "  Database: $POSTGRES_DB"
echo "  User: $POSTGRES_USER"
echo ""

# Check if PostgreSQL is installed
echo -e "${YELLOW}[1/6] Checking PostgreSQL installation...${NC}"
if ! command -v psql &> /dev/null; then
    echo -e "${RED}Error: PostgreSQL is not installed!${NC}"
    echo "Please install PostgreSQL first:"
    echo "  Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
    echo "  macOS: brew install postgresql"
    exit 1
fi
echo -e "${GREEN}✓ PostgreSQL is installed${NC}"

# Check if PostgreSQL service is running
echo -e "${YELLOW}[2/6] Checking PostgreSQL service status...${NC}"
if ! sudo systemctl is-active --quiet postgresql 2>/dev/null && ! pgrep -x postgres > /dev/null; then
    echo -e "${RED}Error: PostgreSQL service is not running!${NC}"
    echo "Start PostgreSQL with: sudo systemctl start postgresql"
    exit 1
fi
echo -e "${GREEN}✓ PostgreSQL service is running${NC}"

# Check if pgvector extension is available
echo -e "${YELLOW}[3/6] Checking pgvector extension availability...${NC}"
PGVECTOR_CHECK=$(sudo -u postgres psql -tAc "SELECT COUNT(*) FROM pg_available_extensions WHERE name='vector';")
if [ "$PGVECTOR_CHECK" -eq "0" ]; then
    echo -e "${RED}Error: pgvector extension is not installed!${NC}"
    echo "Please install pgvector:"
    echo "  Ubuntu/Debian: sudo apt-get install postgresql-17-pgvector"
    echo "  macOS: brew install pgvector"
    echo ""
    echo "Or build from source: https://github.com/pgvector/pgvector"
    exit 1
fi
echo -e "${GREEN}✓ pgvector extension is available${NC}"

# Create database user if it doesn't exist
echo -e "${YELLOW}[4/6] Creating database user...${NC}"
USER_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$POSTGRES_USER';")
if [ -z "$USER_EXISTS" ]; then
    echo "Creating user: $POSTGRES_USER"
    sudo -u postgres psql -c "CREATE USER \"$POSTGRES_USER\" WITH PASSWORD '$POSTGRES_PASSWORD' CREATEDB;"
    echo -e "${GREEN}✓ User '$POSTGRES_USER' created with CREATEDB permission${NC}"
else
    echo -e "${GREEN}✓ User '$POSTGRES_USER' already exists${NC}"
    # Update password and grant CREATEDB permission
    sudo -u postgres psql -c "ALTER USER \"$POSTGRES_USER\" WITH PASSWORD '$POSTGRES_PASSWORD' CREATEDB;"
    echo -e "${GREEN}✓ CREATEDB permission granted${NC}"
fi

# Create database
echo -e "${YELLOW}[5/6] Creating database...${NC}"
DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$POSTGRES_DB';")
if [ -z "$DB_EXISTS" ]; then
    echo "Creating database: $POSTGRES_DB"
    sudo -u postgres psql -c "CREATE DATABASE \"$POSTGRES_DB\" OWNER \"$POSTGRES_USER\";"
    echo -e "${GREEN}✓ Database '$POSTGRES_DB' created${NC}"
else
    echo -e "${GREEN}✓ Database '$POSTGRES_DB' already exists${NC}"
fi

# Enable pgvector extension
echo -e "${YELLOW}[6/6] Enabling pgvector extension...${NC}"
sudo -u postgres psql -d "$POSTGRES_DB" -c "CREATE EXTENSION IF NOT EXISTS vector;"
echo -e "${GREEN}✓ pgvector extension enabled${NC}"

# Grant privileges
echo -e "${YELLOW}Granting privileges to user...${NC}"
sudo -u postgres psql -d "$POSTGRES_DB" -c "GRANT ALL PRIVILEGES ON DATABASE \"$POSTGRES_DB\" TO \"$POSTGRES_USER\";"
sudo -u postgres psql -d "$POSTGRES_DB" -c "GRANT ALL PRIVILEGES ON SCHEMA public TO \"$POSTGRES_USER\";"
sudo -u postgres psql -d "$POSTGRES_DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO \"$POSTGRES_USER\";"
sudo -u postgres psql -d "$POSTGRES_DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO \"$POSTGRES_USER\";"
echo -e "${GREEN}✓ Privileges granted${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Database Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Update your .env file to use LOCAL PostgreSQL:"
echo "     DATABASE_URL=postgresql+asyncpg://$POSTGRES_USER:$POSTGRES_PASSWORD@host.docker.internal:$POSTGRES_PORT/$POSTGRES_DB"
echo ""
echo "  2. Run Alembic migrations to create tables:"
echo "     docker-compose run --rm ai_service alembic upgrade head"
echo ""
echo "  3. Start your application with Docker Compose:"
echo "     docker-compose up"
echo ""
echo -e "${YELLOW}Note: The service will connect to your LOCAL PostgreSQL from inside the Docker container.${NC}"
echo -e "${YELLOW}To switch back to container PostgreSQL, update DATABASE_URL in .env to use 'postgres' as host.${NC}"
