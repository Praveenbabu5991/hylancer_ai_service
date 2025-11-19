#!/bin/bash
# install_pgvector.sh - Install pgvector extension for PostgreSQL

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}pgvector Installation Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check PostgreSQL version
PG_VERSION=$(psql --version | grep -oP '\d+' | head -1)
echo -e "${YELLOW}Detected PostgreSQL version: ${PG_VERSION}${NC}"
echo ""

# Check if build tools are installed
echo -e "${YELLOW}[1/5] Checking build dependencies...${NC}"
if ! command -v git &> /dev/null || ! command -v make &> /dev/null || ! command -v gcc &> /dev/null; then
    echo -e "${YELLOW}Installing build dependencies...${NC}"
    sudo apt-get update
    sudo apt-get install -y build-essential git postgresql-server-dev-${PG_VERSION}
else
    echo -e "${GREEN}✓ Build tools are installed${NC}"
    # Still need postgresql-server-dev
    echo -e "${YELLOW}Installing postgresql-server-dev-${PG_VERSION}...${NC}"
    sudo apt-get update
    sudo apt-get install -y postgresql-server-dev-${PG_VERSION}
fi

# Clone pgvector repository
echo -e "${YELLOW}[2/5] Downloading pgvector source code...${NC}"
cd /tmp
if [ -d "pgvector" ]; then
    echo "Removing old pgvector directory..."
    rm -rf pgvector
fi
git clone --branch v0.7.4 https://github.com/pgvector/pgvector.git
cd pgvector
echo -e "${GREEN}✓ Source code downloaded${NC}"

# Build pgvector
echo -e "${YELLOW}[3/5] Building pgvector...${NC}"
make clean || true
make
echo -e "${GREEN}✓ Build completed${NC}"

# Install pgvector
echo -e "${YELLOW}[4/5] Installing pgvector...${NC}"
sudo make install
echo -e "${GREEN}✓ Installation completed${NC}"

# Verify installation
echo -e "${YELLOW}[5/5] Verifying installation...${NC}"
PGVECTOR_CHECK=$(sudo -u postgres psql -tAc "SELECT COUNT(*) FROM pg_available_extensions WHERE name='vector';" 2>/dev/null || echo "0")
if [ "$PGVECTOR_CHECK" -eq "1" ]; then
    echo -e "${GREEN}✓ pgvector extension is now available!${NC}"
else
    echo -e "${RED}Warning: Verification failed. You may need to restart PostgreSQL.${NC}"
    echo -e "${YELLOW}Run: sudo systemctl restart postgresql${NC}"
fi

# Cleanup
cd /tmp
rm -rf pgvector

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}pgvector Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Restart PostgreSQL (recommended):"
echo "     sudo systemctl restart postgresql"
echo ""
echo "  2. Run the database setup script:"
echo "     ./setup_local_db.sh"
echo ""
