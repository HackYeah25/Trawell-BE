#!/bin/bash

# Travel AI Assistant - Development Server Runner

echo "🚀 Starting Travel AI Assistant Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env with your API keys before running again."
    exit 1
fi

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Run the application
echo "✨ Starting FastAPI server..."
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
