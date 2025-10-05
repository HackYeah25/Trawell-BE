#!/bin/bash

# TraWell Setup Script for Replit
# Installs all dependencies for both backend and frontend

set -e

echo "🔧 Setting up TraWell Development Environment..."
echo "================================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Setup Backend
echo -e "${BLUE}📦 Setting up Backend (Python)...${NC}"
cd Trawell-BE

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip install -r requirements.txt
else
    echo -e "${YELLOW}⚠️  No requirements.txt found, skipping...${NC}"
fi

deactivate
cd ..

echo -e "${GREEN}✅ Backend setup complete${NC}"

# Setup Frontend
echo -e "${BLUE}📦 Setting up Frontend (Node.js)...${NC}"
cd Trawell-FE

# Install dependencies
if [ -f "package.json" ]; then
    echo -e "${YELLOW}Installing Node dependencies...${NC}"
    npm install
else
    echo -e "${YELLOW}⚠️  No package.json found, skipping...${NC}"
fi

cd ..

echo -e "${GREEN}✅ Frontend setup complete${NC}"

# Create .env files if they don't exist
echo -e "${BLUE}🔐 Checking environment files...${NC}"

if [ ! -f "Trawell-BE/.env" ]; then
    echo -e "${YELLOW}Creating backend .env template...${NC}"
    cat > Trawell-BE/.env << 'EOF'
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
AMADEUS_CLIENT_ID=your_amadeus_client_id_here
AMADEUS_CLIENT_SECRET=your_amadeus_client_secret_here
WEATHERAPI_KEY=your_weatherapi_key_here

# Supabase
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# Environment
ENVIRONMENT=development
EOF
    echo -e "${YELLOW}⚠️  Please update Trawell-BE/.env with your API keys${NC}"
fi

if [ ! -f "Trawell-FE/.env" ]; then
    echo -e "${YELLOW}Creating frontend .env template...${NC}"
    cat > Trawell-FE/.env << 'EOF'
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
EOF
fi

echo ""
echo -e "${GREEN}================================================"
echo -e "✨ Setup Complete!"
echo -e "================================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Update ${BLUE}Trawell-BE/.env${NC} with your API keys"
echo -e "  2. Run ${BLUE}bash run.sh${NC} or ${BLUE}npm start${NC} to start the application"
echo ""
