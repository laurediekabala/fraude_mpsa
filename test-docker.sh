#!/bin/bash
# Docker Deployment Test Script
# Teste que tous les services sont opérationnels

set -e

# Couleurs
BLUE='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Docker Deployment Test Suite${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════
# Test 1: Docker Installation
# ═══════════════════════════════════════════════════════════════

echo -e "${YELLOW}[1/7]${NC} Checking Docker installation..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✅${NC} Docker installed: $DOCKER_VERSION"
else
    echo -e "${RED}❌${NC} Docker not installed!"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════
# Test 2: Docker Compose Installation
# ═══════════════════════════════════════════════════════════════

echo -e "${YELLOW}[2/7]${NC} Checking Docker Compose installation..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo -e "${GREEN}✅${NC} Docker Compose installed: $COMPOSE_VERSION"
else
    echo -e "${RED}❌${NC} Docker Compose not installed!"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════
# Test 3: Docker Daemon Running
# ═══════════════════════════════════════════════════════════════

echo -e "${YELLOW}[3/7]${NC} Checking Docker daemon..."
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} Docker daemon is running"
else
    echo -e "${RED}❌${NC} Docker daemon is not running!"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════
# Test 4: Build Images
# ═══════════════════════════════════════════════════════════════

echo -e "${YELLOW}[4/7]${NC} Building Docker images..."
if docker-compose build --quiet > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} Images built successfully"
else
    echo -e "${RED}❌${NC} Failed to build images!"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════
# Test 5: Start Services
# ═══════════════════════════════════════════════════════════════

echo -e "${YELLOW}[5/7]${NC} Starting services..."
docker-compose up -d > /dev/null 2>&1
echo -e "${GREEN}✅${NC} Services started"

# Wait for services to be ready
echo "Waiting for services to be healthy (30 seconds)..."
sleep 30

# ═══════════════════════════════════════════════════════════════
# Test 6: Health Checks
# ═══════════════════════════════════════════════════════════════

echo -e "${YELLOW}[6/7]${NC} Checking service health..."

# Check API
API_HEALTH=$(curl -s -w "%{http_code}" http://localhost:5000/health)
if [ "$API_HEALTH" = "200" ]; then
    echo -e "${GREEN}✅${NC} API health check passed"
else
    echo -e "${RED}❌${NC} API health check failed (status: $API_HEALTH)"
    echo "API Logs:"
    docker-compose logs api | tail -20
fi

# Check Streamlit
STREAMLIT_HEALTH=$(curl -s -w "%{http_code}" http://localhost:8501/_stcore/health)
if [ "$STREAMLIT_HEALTH" = "200" ]; then
    echo -e "${GREEN}✅${NC} Streamlit health check passed"
else
    echo -e "${RED}❌${NC} Streamlit health check failed (status: $STREAMLIT_HEALTH)"
    echo "Streamlit Logs:"
    docker-compose logs streamlit | tail -20
fi

# ═══════════════════════════════════════════════════════════════
# Test 7: API Endpoints
# ═══════════════════════════════════════════════════════════════

echo -e "${YELLOW}[7/7]${NC} Testing API endpoints..."

# Test predict endpoint
PREDICT_RESPONSE=$(curl -s -X POST http://localhost:5000/predict \
    -H "Content-Type: application/json" \
    -d '{
        "step": 100,
        "type": "TRANSFER",
        "amount": 5000,
        "oldbalanceOrg": 50000,
        "newbalanceOrig": 45000,
        "oldbalanceDest": 10000,
        "newbalanceDest": 15000,
        "hour": 10,
        "erreur_orig": 0.0,
        "erreur_dst": 0.0,
        "videur_orig": 0,
        "videur_dest": 0
    }')

if echo "$PREDICT_RESPONSE" | grep -q "probability"; then
    echo -e "${GREEN}✅${NC} Predict endpoint works"
else
    echo -e "${RED}❌${NC} Predict endpoint failed"
    echo "Response: $PREDICT_RESPONSE"
fi

# ═══════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ All tests completed!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

echo ""
echo "Services are running at:"
echo -e "  ${BLUE}API:        http://localhost:5000${NC}"
echo -e "  ${BLUE}Streamlit:  http://localhost:8501${NC}"
echo ""
echo "To stop services, run:"
echo "  docker-compose down"
echo ""
echo "To view logs, run:"
echo "  docker-compose logs -f"
echo ""
