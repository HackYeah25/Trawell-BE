# 🚀 Quick Start Guide

Get the Travel AI Assistant backend up and running in 5 minutes!

## Prerequisites

- Python 3.11+ OR Docker
- Supabase account (free tier works!)
- OpenAI or Anthropic API key

## 🐳 Option 1: Docker (Easiest)

### 1. Clone and Configure

```bash
# Clone the repository
git clone <repo-url>
cd Trawell-BE

# Copy environment file
cp .env.example .env
```

### 2. Edit .env

Open `.env` and add your API keys:

```bash
# Required
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_key  # or ANTHROPIC_API_KEY
SECRET_KEY=generate_with_openssl_rand_hex_32
```

### 3. Set up Supabase

Run the SQL in `supabase_schema.sql` in your Supabase SQL Editor.

### 4. Start with Docker

```bash
# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f backend
```

### 5. Test the API

Visit http://localhost:8000/docs

You should see the Swagger UI with all endpoints!

---

## 🐍 Option 2: Local Python

### 1. Setup Virtual Environment

```bash
# Clone the repository
git clone <repo-url>
cd Trawell-BE

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your API keys (same as Docker option)
nano .env
```

### 3. Set up Supabase

Run the SQL in `supabase_schema.sql` in your Supabase SQL Editor.

### 4. Run the Server

```bash
# Start development server
uvicorn app.main:app --reload --port 8000

# Or use the run script
./run.sh
```

### 5. Test the API

Visit http://localhost:8000/docs

---

## 🧪 Verify Installation

### Test Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "travel-ai-backend",
  "version": "1.0.0"
}
```

### Test Root Endpoint

Visit http://localhost:8000 in your browser.

Expected response:
```json
{
  "name": "Travel AI Assistant",
  "version": "1.0.0",
  "status": "running",
  "environment": "development",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

---

## 📚 Next Steps

### 1. Explore the API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 2. Test Brainstorm Flow

1. Create a user profile (TODO: implement auth)
2. Start a brainstorm session: `POST /api/brainstorm/start`
3. Send a message: `POST /api/brainstorm/{id}/message`
4. Get suggestions: `GET /api/brainstorm/{id}/suggestions`

### 3. Customize Prompts

Edit the YAML files in `app/prompts/`:
- `system.yaml` - System prompts and user profile
- `brainstorm.yaml` - Destination discovery prompts
- `planning.yaml` - Trip planning prompts
- `support.yaml` - On-site support prompts

### 4. Read the Documentation

- [README.md](README.md) - Main documentation
- [API.md](API.md) - API reference
- [DOCKER.md](DOCKER.md) - Docker deployment guide

---

## 🔧 Using the Makefile

The project includes a Makefile with helpful commands:

```bash
# Show all available commands
make help

# Install dependencies
make install

# Run development server
make run

# Run tests
make test

# Docker commands
make docker-up       # Start Docker containers
make docker-down     # Stop Docker containers
make docker-logs     # View logs
make docker-shell    # Open shell in container

# Code quality
make format          # Format code
make lint            # Run linters
make clean           # Clean up cache files
```

---

## ⚡ Quick Commands Cheat Sheet

### Docker
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f backend

# Restart
docker-compose restart backend
```

### Local Development
```bash
# Activate venv
source venv/bin/activate

# Run server
uvicorn app.main:app --reload

# Run tests
pytest

# Format code
black app/
```

---

## 🐛 Troubleshooting

### Port 8000 already in use

```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### Database connection error

1. Check Supabase credentials in `.env`
2. Verify you ran `supabase_schema.sql`
3. Check Supabase dashboard for errors

### LLM API errors

1. Verify API key in `.env`
2. Check API key has credits/quota
3. Try different model in `config.py`

### Docker issues

```bash
# Clean rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

## 🎯 Development Workflow

### 1. Make Changes

Edit files in `app/` directory

### 2. Test Locally

```bash
# Run server
make run

# In another terminal, run tests
make test
```

### 3. Format Code

```bash
make format
make lint
```

### 4. Commit Changes

```bash
git add .
git commit -m "Description of changes"
git push
```

### 5. Deploy

```bash
# Build production image
docker build -t travel-ai-backend:prod .

# Deploy to your platform
# (AWS, GCP, Azure, etc.)
```

---

## 📞 Getting Help

- **Documentation**: See [README.md](README.md)
- **API Reference**: See [API.md](API.md)
- **Issues**: Open an issue on GitHub
- **Questions**: Check existing issues or create new one

---

## ✅ Checklist

Before you start developing:

- [ ] Supabase account created
- [ ] Supabase schema deployed (`supabase_schema.sql`)
- [ ] `.env` file configured with all keys
- [ ] API keys have credits/quota
- [ ] Server running and accessible
- [ ] Swagger UI working at `/docs`
- [ ] Health check returns `healthy`

You're ready to build! 🎉
