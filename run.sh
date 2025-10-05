#!/bin/bash

# TraWell Monorepo Runner for Replit
# This script starts both backend and frontend services

set -e

echo "🚀 Starting TraWell Application..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if first run
if [ ! -f ".initialized" ]; then
    echo -e "${YELLOW}📦 First run detected - running setup...${NC}"
    bash setup.sh
    touch .initialized
fi

# Function to cleanup background processes on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Start Backend
echo -e "${BLUE}🐍 Starting Backend (FastAPI)...${NC}"
cd Trawell-BE
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo -e "${YELLOW}⏳ Waiting for backend to initialize...${NC}"
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is running on port 8000${NC}"
else
    echo -e "${RED}❌ Backend failed to start${NC}"
    exit 1
fi

# Start Frontend
echo -e "${BLUE}⚛️  Starting Frontend (Vite + React)...${NC}"
cd Trawell-FE
npm run dev -- --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo -e "${YELLOW}⏳ Waiting for frontend to initialize...${NC}"
sleep 5

echo ""
echo -e "${GREEN}=================================="
echo -e "✨ TraWell is ready!"
echo -e "=================================="
echo -e "📡 Backend API:  ${BLUE}http://localhost:8000${NC}"
echo -e "🌐 Frontend UI:  ${BLUE}http://localhost:5173${NC}"
echo -e "📚 API Docs:     ${BLUE}http://localhost:8000/docs${NC}"
echo -e "=================================="
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Wait for all background processes
wait
