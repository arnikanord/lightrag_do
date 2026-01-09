#!/bin/bash
# Quick script to check API accessibility

API_IP="162.243.201.21"
API_PORT="8000"
API_URL="http://${API_IP}:${API_PORT}"

echo "=== Checking LightRAG API Accessibility ==="
echo "Server IP: $API_IP"
echo "Port: $API_PORT"
echo ""

# Check if port is open
echo "1. Checking if port $API_PORT is accessible..."
if curl -s --connect-timeout 5 "$API_URL/health" > /dev/null 2>&1; then
    echo "   ✓ Port is accessible"
else
    echo "   ✗ Port is not accessible"
    echo "   Checking local service..."
    if curl -s --connect-timeout 2 "http://localhost:8000/health" > /dev/null 2>&1; then
        echo "   ⚠ Service is running locally but not accessible remotely"
        echo "   Possible issues:"
        echo "   - Firewall blocking port 8000"
        echo "   - Docker port mapping issue"
        echo "   - Service not bound to 0.0.0.0"
    else
        echo "   ⚠ Service is not running"
        echo "   Start with: cd /root/gafta-guardian && docker compose up -d"
    fi
    exit 1
fi

echo ""
echo "2. Testing API health endpoint..."
HEALTH_RESPONSE=$(curl -s "$API_URL/health")
if [ $? -eq 0 ]; then
    echo "   ✓ Health check successful"
    echo "   Response:"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    echo "   ✗ Health check failed"
    exit 1
fi

echo ""
echo "3. Testing root endpoint..."
ROOT_RESPONSE=$(curl -s "$API_URL/")
if [ $? -eq 0 ]; then
    echo "   ✓ Root endpoint accessible"
    echo "   Response:"
    echo "$ROOT_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$ROOT_RESPONSE"
else
    echo "   ✗ Root endpoint failed"
    exit 1
fi

echo ""
echo "=== API Status ==="
echo "✓ API is accessible at: $API_URL"
echo "✓ Web interface: $API_URL"
echo "✓ API docs: $API_URL/docs"
echo ""
