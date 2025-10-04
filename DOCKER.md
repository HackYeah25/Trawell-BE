# Docker Deployment Guide

## Quick Start with Docker

### Prerequisites

- Docker installed (version 20.10+)
- Docker Compose installed (version 2.0+)

### 1. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

Required environment variables:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` - LLM API key
- `SECRET_KEY` - JWT secret (generate with `openssl rand -hex 32`)

### 2. Build and Run

```bash
# Build the Docker image
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
```

### 3. Access the Application

- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### 4. Verify Running Services

```bash
# Check running containers
docker-compose ps

# Expected output:
# NAME                     STATUS    PORTS
# travel-ai-backend        Up        0.0.0.0:8000->8000/tcp
# travel-ai-redis          Up        0.0.0.0:6379->6379/tcp
# travel-ai-celery-worker  Up
# travel-ai-celery-beat    Up
```

## Docker Services

### Backend (FastAPI)
- **Port**: 8000
- **Container**: travel-ai-backend
- **Health Check**: Built-in at `/health`

### Redis
- **Port**: 6379
- **Container**: travel-ai-redis
- **Purpose**: Celery message broker

### Celery Worker
- **Container**: travel-ai-celery-worker
- **Purpose**: Background task processing

### Celery Beat
- **Container**: travel-ai-celery-beat
- **Purpose**: Scheduled task execution

## Common Docker Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery-worker
```

### Execute Commands in Container
```bash
# Open shell in backend container
docker-compose exec backend /bin/bash

# Run Python commands
docker-compose exec backend python -c "print('Hello')"

# Run tests
docker-compose exec backend pytest
```

### Rebuild After Code Changes
```bash
# Rebuild and restart
docker-compose up -d --build
```

### Clean Up
```bash
# Stop and remove containers, networks
docker-compose down

# Also remove volumes (WARNING: deletes data!)
docker-compose down -v
```

## Development with Docker

### Hot Reload

The `docker-compose.yml` mounts the `./app` directory for hot reload:

```yaml
volumes:
  - ./app:/app/app
```

Changes to your code will automatically reload the server.

### Using Makefile

```bash
# Build Docker images
make docker-build

# Start services
make docker-up

# Stop services
make docker-down

# View logs
make docker-logs

# Open shell in container
make docker-shell

# Restart services
make docker-restart
```

## Production Deployment

### 1. Update docker-compose.yml

For production, modify environment variables:

```yaml
environment:
  - ENVIRONMENT=production
  - DEBUG=False
```

### 2. Use Production Image

Build optimized production image:

```bash
docker build -t travel-ai-backend:prod \
  --build-arg ENVIRONMENT=production \
  -f Dockerfile .
```

### 3. Security Considerations

- Use secrets management (Docker Secrets, Kubernetes Secrets)
- Don't expose unnecessary ports
- Run as non-root user (already configured)
- Use HTTPS/TLS termination (nginx, traefik)
- Set proper resource limits

### 4. Example Production docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    image: travel-ai-backend:prod
    restart: always
    environment:
      - ENVIRONMENT=production
      - DEBUG=False
    env_file:
      - .env.production
    ports:
      - "8000:8000"
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 512M
```

## Kubernetes Deployment

### Basic Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: travel-ai-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: travel-ai-backend
  template:
    metadata:
      labels:
        app: travel-ai-backend
    spec:
      containers:
      - name: backend
        image: travel-ai-backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: travel-ai-secrets
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Missing .env file
# 2. Invalid API keys
# 3. Port already in use
```

### Database Connection Issues

```bash
# Check if services can communicate
docker-compose exec backend ping redis

# Verify environment variables
docker-compose exec backend env | grep SUPABASE
```

### Performance Issues

```bash
# Check container stats
docker stats

# Increase resources in docker-compose.yml:
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

### Clean Installation

```bash
# Complete cleanup and fresh start
docker-compose down -v
docker system prune -a
docker-compose up -d --build
```

## Monitoring

### Health Checks

The Dockerfile includes a health check:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"
```

### Logs

```bash
# Follow logs
docker-compose logs -f

# Save logs to file
docker-compose logs > logs.txt
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
