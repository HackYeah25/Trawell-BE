#!/bin/bash

# Health Check Script - Verifies both services are running

echo "🏥 TraWell Health Check"
echo "======================="

# Check Backend
echo -n "Backend (port 8000): "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ RUNNING"
else
    echo "❌ DOWN"
fi

# Check Frontend
echo -n "Frontend (port 5173): "
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ RUNNING"
else
    echo "❌ DOWN"
fi

echo "======================="
