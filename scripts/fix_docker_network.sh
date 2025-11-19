#!/bin/bash
# fix_docker_network.sh - Add Docker network 172.19.0.0/16 to PostgreSQL

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Adding Docker network 172.19.0.0/16 to PostgreSQL access...${NC}"

PG_VERSION=16
PG_HBA="/etc/postgresql/${PG_VERSION}/main/pg_hba.conf"

# Check if rule already exists
if sudo grep -q "172.19.0.0/16" ${PG_HBA}; then
    echo -e "${GREEN}✓ Network 172.19.0.0/16 already allowed${NC}"
else
    # Add the new network
    echo "host    all             all             172.19.0.0/16           md5" | sudo tee -a ${PG_HBA} > /dev/null
    echo -e "${GREEN}✓ Added network 172.19.0.0/16${NC}"

    # Restart PostgreSQL
    echo -e "${YELLOW}Restarting PostgreSQL...${NC}"
    sudo systemctl restart postgresql
    sleep 2
    echo -e "${GREEN}✓ PostgreSQL restarted${NC}"
fi

echo ""
echo "Current pg_hba.conf Docker rules:"
sudo grep "172." ${PG_HBA} | grep -v "^#"
