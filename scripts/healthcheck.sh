#!/bin/bash
# Simple health check script for monitoring

URL="${1:-http://localhost:5000/health}"
TIMEOUT="${2:-5}"

response=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$URL")

if [ "$response" = "200" ]; then
    echo "✅ Healthy"
    exit 0
else
    echo "❌ Unhealthy (HTTP $response)"
    exit 1
fi
