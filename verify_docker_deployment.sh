#!/bin/bash
# verify_docker_deployment.sh - Comprehensive verification script for Hylancer AI Service Docker deployment
# This script verifies that all services are running correctly and producing expected results

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_HOST="${API_HOST:-localhost}"
API_PORT="${API_PORT:-8000}"
BASE_URL="http://${API_HOST}:${API_PORT}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Hylancer AI Service - Verification Script${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Function to print success message
print_success() {
    echo -e "${GREEN} $1${NC}"
}

# Function to print error message
print_error() {
    echo -e "${RED} $1${NC}"
}

# Function to print info message
print_info() {
    echo -e "${YELLOW}’ $1${NC}"
}

# Test counter
total_tests=0
passed_tests=0

# Function to run test
run_test() {
    local test_name=$1
    local test_command=$2

    total_tests=$((total_tests + 1))
    print_info "Test $total_tests: $test_name"

    if eval "$test_command"; then
        print_success "PASSED: $test_name"
        passed_tests=$((passed_tests + 1))
        return 0
    else
        print_error "FAILED: $test_name"
        return 1
    fi
}

echo -e "\n${BLUE}[1] Checking Docker Services Status${NC}"
echo "========================================\n"

# Check if Docker is running
run_test "Docker daemon is running" "docker info >/dev/null 2>&1"

# Check if docker-compose is available
run_test "Docker Compose is available" "docker compose version >/dev/null 2>&1"

# Check if containers are running
run_test "PostgreSQL container is running" "docker compose ps postgres | grep -q 'Up'"
run_test "AI Service container is running" "docker compose ps ai_service | grep -q 'Up'"

echo -e "\n${BLUE}[2] Checking Container Health${NC}"
echo "========================================\n"

# Check PostgreSQL health
run_test "PostgreSQL is healthy" "docker compose ps postgres | grep -q 'healthy'"

# Wait for AI service to be healthy (with timeout)
print_info "Waiting for AI service to be healthy (up to 60s)..."
timeout=60
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker compose ps ai_service | grep -q "healthy"; then
        break
    fi
    sleep 2
    elapsed=$((elapsed + 2))
done
run_test "AI Service is healthy" "docker compose ps ai_service | grep -q 'healthy'"

echo -e "\n${BLUE}[3] Checking Database Connection${NC}"
echo "========================================\n"

# Check PostgreSQL is accessible
run_test "PostgreSQL is accessible" "docker compose exec -T postgres pg_isready -U user -d hylancer_ai >/dev/null 2>&1"

# Check pgvector extension
run_test "pgvector extension is installed" "docker compose exec -T postgres psql -U user -d hylancer_ai -c 'SELECT * FROM pg_extension WHERE extname = \\\'vector\\\';' | grep -q vector"

echo -e "\n${BLUE}[4] Checking API Endpoints${NC}"
echo "========================================\n"

# Health check
run_test "Health endpoint is accessible" "curl -sf ${BASE_URL}/health >/dev/null"

# Get health response
health_response=$(curl -s ${BASE_URL}/health)
print_info "Health Response: $health_response"

# Metrics endpoint
run_test "Metrics endpoint is accessible" "curl -sf ${BASE_URL}/api/v1/metrics >/dev/null"

# Get metrics
metrics=$(curl -s ${BASE_URL}/api/v1/metrics | python3 -m json.tool 2>/dev/null || echo "{}")
echo -e "\n${YELLOW}Current Metrics:${NC}"
echo "$metrics" | head -20

echo -e "\n${BLUE}[5] Testing Core Recommendation APIs${NC}"
echo "========================================\n"

# Test hylancer recommendation endpoint
print_info "Testing /api/v1/recommend_hylancer endpoint..."
recommend_response=$(curl -s -X POST "${BASE_URL}/api/v1/recommend_hylancer" \
    -H "Content-Type: application/json" \
    -d '{"project_id": "11111111-2222-3333-4444-555555555501", "top_k": 3}' 2>/dev/null || echo '{"detail":"error"}')

if echo "$recommend_response" | grep -q "hylancer_id"; then
    print_success "Hylancer recommendation endpoint working"
    passed_tests=$((passed_tests + 1))
    total_tests=$((total_tests + 1))

    # Extract and display results count
    results_count=$(echo "$recommend_response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('total_results', 0))" 2>/dev/null || echo "0")
    print_info "Returned $results_count recommendations"
else
    print_error "Hylancer recommendation endpoint failed"
    total_tests=$((total_tests + 1))
    echo "Response: $recommend_response"
fi

# Test project recommendation endpoint
print_info "Testing /api/v1/recommend_projects endpoint..."
project_response=$(curl -s -X POST "${BASE_URL}/api/v1/recommend_projects" \
    -H "Content-Type: application/json" \
    -d '{"hylancer_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890", "top_k": 3}' 2>/dev/null || echo '{"detail":"error"}')

if echo "$project_response" | grep -q "project_id"; then
    print_success "Project recommendation endpoint working"
    passed_tests=$((passed_tests + 1))
    total_tests=$((total_tests + 1))

    results_count=$(echo "$project_response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('total_results', 0))" 2>/dev/null || echo "0")
    print_info "Returned $results_count project recommendations"
else
    print_error "Project recommendation endpoint failed"
    total_tests=$((total_tests + 1))
    echo "Response: $project_response"
fi

echo -e "\n${BLUE}[6] Testing Generation APIs${NC}"
echo "========================================\n"

# Test project description generation
print_info "Testing /api/v1/generate_project_description endpoint..."
gen_project_response=$(curl -s -X POST "${BASE_URL}/api/v1/generate_project_description" \
    -H "Content-Type: application/json" \
    -d '{"category":"Web Development","sub_category":"E-commerce","required_skills":["React","Node.js"],"budget_type":"Fixed-Price","budget":5000}' 2>/dev/null || echo '{"detail":"error"}')

if echo "$gen_project_response" | grep -q "title"; then
    print_success "Project description generation endpoint working"
    passed_tests=$((passed_tests + 1))
    total_tests=$((total_tests + 1))
else
    print_error "Project description generation endpoint failed"
    total_tests=$((total_tests + 1))
    echo "Response: $gen_project_response"
fi

# Test bio description generation
print_info "Testing /api/v1/generate_bio_description endpoint..."
gen_bio_response=$(curl -s -X POST "${BASE_URL}/api/v1/generate_bio_description" \
    -H "Content-Type: application/json" \
    -d '{"name":"John Doe","title":"Senior Developer","skills":["Python","React"],"years_of_experience":5}' 2>/dev/null || echo '{"detail":"error"}')

if echo "$gen_bio_response" | grep -q "bio"; then
    print_success "Bio description generation endpoint working"
    passed_tests=$((passed_tests + 1))
    total_tests=$((total_tests + 1))
else
    print_error "Bio description generation endpoint failed"
    total_tests=$((total_tests + 1))
    echo "Response: $gen_bio_response"
fi

echo -e "\n${BLUE}[7] Checking Logs${NC}"
echo "========================================\n"

# Check recent logs from AI service
print_info "Recent AI Service logs (last 10 lines):"
docker compose logs --tail=10 ai_service 2>/dev/null | tail -10

# Check for errors in logs
error_count=$(docker compose logs ai_service 2>/dev/null | grep -i error | wc -l)
if [ "$error_count" -eq 0 ]; then
    print_success "No errors found in AI service logs"
    passed_tests=$((passed_tests + 1))
    total_tests=$((total_tests + 1))
else
    print_error "Found $error_count errors in AI service logs"
    total_tests=$((total_tests + 1))
fi

echo -e "\n${BLUE}[8] Resource Usage${NC}"
echo "========================================\n"

# Container stats
print_info "Container resource usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" hylancer-ai-service hylancer-postgres 2>/dev/null || print_error "Could not fetch container stats"

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}Verification Summary${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "Total Tests: ${total_tests}"
echo -e "Passed: ${GREEN}${passed_tests}${NC}"
echo -e "Failed: ${RED}$((total_tests - passed_tests))${NC}"
echo -e "Success Rate: $(awk "BEGIN {printf \"%.1f\", (${passed_tests}/${total_tests})*100}")%\n"

if [ $passed_tests -eq $total_tests ]; then
    echo -e "${GREEN} All verifications passed! Deployment is healthy.${NC}\n"
    exit 0
else
    echo -e "${YELLOW}  Some verifications failed. Check the output above for details.${NC}\n"
    echo -e "${YELLOW}Troubleshooting tips:${NC}"
    echo -e "  1. Check logs: docker compose logs -f"
    echo -e "  2. Restart services: docker compose restart"
    echo -e "  3. Check .env file configuration"
    echo -e "  4. Verify database migrations: docker compose exec ai_service alembic current\n"
    exit 1
fi
