#!/bin/bash
# configure_postgres_docker.sh - Configure PostgreSQL to accept connections from Docker

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Configure PostgreSQL for Docker Access${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Detect PostgreSQL version
PG_VERSION=$(psql --version | grep -oP '\d+' | head -1)
echo -e "${YELLOW}Detected PostgreSQL version: ${PG_VERSION}${NC}"

# PostgreSQL config paths
PG_CONF="/etc/postgresql/${PG_VERSION}/main/postgresql.conf"
PG_HBA="/etc/postgresql/${PG_VERSION}/main/pg_hba.conf"

echo ""
echo -e "${YELLOW}Step 1: Backup current configuration files${NC}"
sudo cp ${PG_CONF} ${PG_CONF}.backup
sudo cp ${PG_HBA} ${PG_HBA}.backup
echo -e "${GREEN}✓ Backups created:${NC}"
echo "  - ${PG_CONF}.backup"
echo "  - ${PG_HBA}.backup"

echo ""
echo -e "${YELLOW}Step 2: Configure PostgreSQL to listen on all interfaces${NC}"
# Check if listen_addresses is already set
if sudo grep -q "^listen_addresses = '\*'" ${PG_CONF}; then
    echo -e "${GREEN}✓ Already configured to listen on all interfaces${NC}"
else
    # Comment out existing listen_addresses
    sudo sed -i "s/^listen_addresses/#listen_addresses/" ${PG_CONF}
    # Add new listen_addresses at the end of CONNECTIONS section
    sudo sed -i "/^#listen_addresses/a listen_addresses = '*'  # Listen on all interfaces for Docker" ${PG_CONF}
    echo -e "${GREEN}✓ Set listen_addresses = '*'${NC}"
fi

echo ""
echo -e "${YELLOW}Step 3: Allow connections from Docker network${NC}"
# Check if Docker rule already exists
if sudo grep -q "172.17.0.0/16" ${PG_HBA}; then
    echo -e "${GREEN}✓ Docker network rule already exists${NC}"
else
    # Add rule to allow Docker network (172.17.0.0/16)
    echo "" | sudo tee -a ${PG_HBA} > /dev/null
    echo "# Allow connections from Docker containers" | sudo tee -a ${PG_HBA} > /dev/null
    echo "host    all             all             172.17.0.0/16           md5" | sudo tee -a ${PG_HBA} > /dev/null
    echo -e "${GREEN}✓ Added Docker network access rule${NC}"
fi

echo ""
echo -e "${YELLOW}Step 4: Restart PostgreSQL service${NC}"
sudo systemctl restart postgresql
sleep 2

# Verify service is running
if sudo systemctl is-active --quiet postgresql; then
    echo -e "${GREEN}✓ PostgreSQL restarted successfully${NC}"
else
    echo -e "${RED}✗ PostgreSQL failed to restart${NC}"
    echo -e "${YELLOW}Restoring backup configurations...${NC}"
    sudo cp ${PG_CONF}.backup ${PG_CONF}
    sudo cp ${PG_HBA}.backup ${PG_HBA}
    sudo systemctl restart postgresql
    echo -e "${RED}Configuration reverted. Please check PostgreSQL logs.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 5: Verify PostgreSQL is listening on all interfaces${NC}"
LISTEN_CHECK=$(ss -tulpn 2>/dev/null | grep 5432 | grep -c "0.0.0.0:5432" || echo "0")
if [ "$LISTEN_CHECK" -gt "0" ]; then
    echo -e "${GREEN}✓ PostgreSQL is now listening on 0.0.0.0:5432${NC}"
else
    echo -e "${YELLOW}⚠ PostgreSQL may still be on localhost only${NC}"
    echo "Current listening status:"
    ss -tulpn 2>/dev/null | grep 5432 || netstat -tulpn | grep 5432
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Configuration Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Changes made:"
echo "  1. PostgreSQL now listens on all interfaces (0.0.0.0)"
echo "  2. Docker network (172.17.0.0/16) can connect"
echo "  3. Password authentication (md5) required"
echo ""
echo "Next steps:"
echo "  1. Test connection from Docker:"
echo "     docker-compose run --rm ai_service alembic upgrade head"
echo ""
echo "  2. If issues persist, check PostgreSQL logs:"
echo "     sudo tail -f /var/log/postgresql/postgresql-${PG_VERSION}-main.log"
echo ""
echo -e "${YELLOW}Note: To revert changes, restore from backups:${NC}"
echo "  sudo cp ${PG_CONF}.backup ${PG_CONF}"
echo "  sudo cp ${PG_HBA}.backup ${PG_HBA}"
echo "  sudo systemctl restart postgresql"
