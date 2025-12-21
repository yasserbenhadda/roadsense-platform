#!/bin/bash
# Script to test the complete Docker setup

set -e

echo "🐳 Test du setup Docker complet"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a service is running
check_service() {
    local service=$1
    local port=$2
    
    if docker ps | grep -q "$service"; then
        echo -e "${GREEN}$service is running${NC}"
        
        # Check if port is accessible
        if command -v nc &> /dev/null; then
            if nc -z localhost $port 2>/dev/null; then
                echo -e "${GREEN}   Port $port is accessible${NC}"
            else
                echo -e "${YELLOW}   Port $port is not accessible${NC}"
            fi
        fi
        return 0
    else
        echo -e "${RED}$service is not running${NC}"
        return 1
    fi
}

# Function to test API endpoint
test_api_endpoint() {
    local endpoint=$1
    local expected_status=$2
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint" || echo "000")
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}$endpoint returned $expected_status${NC}"
        return 0
    else
        echo -e "${RED}$endpoint returned $response (expected $expected_status)${NC}"
        return 1
    fi
}

echo "Building Docker images..."
docker-compose build

echo ""
echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

echo ""
echo "Checking services..."
echo ""

# Check services
all_ok=true

if ! check_service "crack-detection-api" 8000; then
    all_ok=false
fi

if ! check_service "minio" 9000; then
    all_ok=false
fi

if ! check_service "postgres-crack-detection" 5432; then
    all_ok=false
fi

echo ""
echo "🌐 Testing API endpoints..."
echo ""

# Test API endpoints
if test_api_endpoint "http://localhost:8000/health" "200"; then
    echo -e "${GREEN}Health check passed${NC}"
else
    echo -e "${RED}Health check failed${NC}"
    all_ok=false
fi

if test_api_endpoint "http://localhost:8000/" "200"; then
    echo -e "${GREEN}Root endpoint accessible${NC}"
else
    echo -e "${RED}Root endpoint failed${NC}"
    all_ok=false
fi

echo ""
echo "Service logs (last 10 lines):"
echo ""

echo "--- API Logs ---"
docker-compose logs --tail=10 crack-detection-api

echo ""
echo "--- MinIO Logs ---"
docker-compose logs --tail=5 minio

echo ""
echo "--- PostgreSQL Logs ---"
docker-compose logs --tail=5 postgres

echo ""
echo "=================================="
if [ "$all_ok" = true ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    echo ""
    echo "Services available:"
    echo "   - API: http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/docs"
    echo "   - MinIO Console: http://localhost:9001"
    echo "   - PostgreSQL: localhost:5432"
    echo ""
    echo "To stop services: docker-compose down"
    exit 0
else
    echo -e "${RED}Some tests failed${NC}"
    echo ""
    echo "Check logs with: docker-compose logs"
    exit 1
fi

