# CI/CD Pipeline Guide

**Target Audience:** DevOps Engineers, Site Reliability Engineers, Platform Engineers  
**Status:** ✅ Complete (Week 3)  
**Last Updated:** October 22, 2025

## Table of Contents

1. [Overview](#overview)
2. [Pipeline Architecture](#pipeline-architecture)
3. [GitHub Actions Workflows](#github-actions-workflows)
4. [Deployment Process](#deployment-process)
5. [Docker Configuration](#docker-configuration)
6. [Monitoring & Alerts](#monitoring--alerts)
7. [Rollback Procedures](#rollback-procedures)
8. [Environment Management](#environment-management)
9. [Troubleshooting](#troubleshooting)

## Overview

Nutricount uses GitHub Actions for CI/CD with the following goals:
- **Automated Testing:** Run all tests on every PR and commit
- **Code Quality:** Enforce linting, security scanning, and coverage thresholds
- **Continuous Deployment:** Deploy to production on successful main branch merges
- **Raspberry Pi Optimized:** ARM64-specific Docker builds
- **Fast Feedback:** Complete pipeline in <10 minutes

### Current CI/CD Status

- ✅ Automated testing on every PR
- ✅ Security scanning with bandit
- ✅ Code quality checks with flake8
- ✅ Docker image builds for ARM64
- ✅ Coverage reporting
- 🔄 Automated deployment (in progress)
- 🔄 Rollback mechanism (planned Week 5)

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Repository                        │
│                                                              │
│  Pull Request / Push to Main                                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions                            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Lint & Test │──▶│ Security Scan│──▶│ Build Docker │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ✅ Pass/Fail       ✅ Pass/Fail       ✅ Pass/Fail        │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Deploy (Main Branch Only)                   │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Docker Hub   │──▶│  Raspberry   │──▶│ Health Check │     │
│  │ ARM64 Image  │  │  Pi Deploy   │  │  & Verify    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## GitHub Actions Workflows

### Main CI/CD Workflow

**File:** `.github/workflows/ci-cd.yml`

**Triggers:**
- Pull requests to `main` or `develop`
- Direct pushes to `main` branch only (not on PR commits to avoid duplication)

**Jobs:**

#### 1. Lint & Test Job

```yaml
jobs:
  test:
    name: Lint and Test
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install -r requirements-minimal.txt
          
      - name: Lint with flake8
        run: |
          flake8 src/ routes/ --max-line-length=100 --ignore=E501,W503,E226
          
      - name: Test with pytest
        run: |
          export PYTHONPATH=$PWD
          mkdir -p logs
          pytest tests/ -v --cov=src --cov=routes --cov-report=xml
          
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

**Why This Works:**
- ✅ Fast: Runs in ~3 minutes
- ✅ Reliable: Uses minimal dependencies
- ✅ Comprehensive: Covers linting, testing, and coverage
- ✅ Isolated: Each PR gets its own test environment

#### 2. Security Scan Job

```yaml
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        
      - name: Run bandit security scan
        run: |
          pip install bandit
          bandit -r src/ -f json -o bandit-report.json
          
      - name: Upload security report
        uses: actions/upload-artifact@v3
        with:
          name: security-report
          path: bandit-report.json
```

**Security Checks:**
- 🔒 Hardcoded secrets detection
- 🔒 SQL injection vulnerabilities
- 🔒 Command injection risks
- 🔒 Insecure cryptography usage
- 🔒 Weak password hashing

#### 3. Build & Deploy Job

```yaml
  build-deploy:
    name: Build and Deploy
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    steps:
      - name: Set up QEMU
        uses: docker/setup-qemu-action@v2
        
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
        
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
          
      - name: Build and push ARM64 image
        uses: docker/build-push-action@v4
        with:
          context: .
          platforms: linux/arm64
          push: true
          tags: |
            ${{ secrets.DOCKER_USERNAME }}/nutricount:latest
            ${{ secrets.DOCKER_USERNAME }}/nutricount:${{ github.sha }}
          cache-from: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/nutricount:buildcache
          cache-to: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/nutricount:buildcache,mode=max
```

**Build Features:**
- 🐳 Multi-arch support (ARM64 for Raspberry Pi)
- 🚀 Layer caching for faster builds
- 🏷️ Semantic versioning with git SHA
- 📦 Docker Hub registry

### Frontend CI Workflow

**File:** `.github/workflows/frontend-ci.yml`

```yaml
jobs:
  test-frontend:
    name: Frontend Tests
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
          
      - name: Install dependencies
        working-directory: frontend
        run: npm ci
        
      - name: Run tests with coverage
        working-directory: frontend
        run: npm run test:coverage
        
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./frontend/coverage/coverage-final.json
          flags: frontend
```

## Deployment Process

### Deployment Pipeline

```
1. Code Merge to Main
   │
   ├─▶ Trigger GitHub Actions
   │
2. Run CI Pipeline
   │
   ├─▶ Lint & Test (3 min)
   ├─▶ Security Scan (1 min)
   ├─▶ Build Docker Image (5 min)
   │
3. Deploy to Registry
   │
   ├─▶ Push to Docker Hub
   ├─▶ Tag with version
   │
4. Deploy to Production
   │
   ├─▶ SSH to Raspberry Pi
   ├─▶ Pull latest image
   ├─▶ Update docker-compose
   ├─▶ Rolling restart
   │
5. Health Check
   │
   ├─▶ Check /health endpoint
   ├─▶ Verify metrics
   ├─▶ Monitor errors
```

### Deployment Commands

**Manual Deployment (Raspberry Pi):**

```bash
# SSH to Raspberry Pi
ssh pi@raspberry-pi-ip

# Navigate to project
cd /opt/nutricount

# Pull latest changes
git pull origin main

# Pull latest Docker image
docker-compose pull

# Restart services
docker-compose down
docker-compose up -d

# Verify deployment
curl http://localhost/health
docker-compose ps
docker-compose logs -f --tail=50
```

**Automated Deployment (via GitHub Actions - Week 5):**

```yaml
- name: Deploy to Raspberry Pi
  uses: appleboy/ssh-action@master
  with:
    host: ${{ secrets.PI_HOST }}
    username: ${{ secrets.PI_USER }}
    key: ${{ secrets.PI_SSH_KEY }}
    script: |
      cd /opt/nutricount
      docker-compose pull
      docker-compose up -d
      curl -f http://localhost/health || exit 1
```

## Docker Configuration

### Multi-Stage Dockerfile

**Optimized for Raspberry Pi ARM64:**

```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim-bookworm

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 nutricount && \
    chown -R nutricount:nutricount /app

USER nutricount

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD curl -f http://localhost:5000/health || exit 1

# Run application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
```

**Benefits:**
- 🔒 Non-root user for security
- 📦 Multi-stage build reduces image size
- 🏥 Built-in health check
- ⚡ Optimized for ARM64

### docker-compose.yml

```yaml
version: '3.8'

services:
  nutricount:
    image: chervonnyyanton/nutricount:latest
    container_name: nutricount-app
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE=/data/nutricount.db
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./data:/data
      - ./logs:/app/logs
    depends_on:
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    container_name: nutricount-redis
    restart: unless-stopped
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: nutricount-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - nutricount
    restart: unless-stopped

volumes:
  redis-data:
```

## Monitoring & Alerts

### Prometheus Metrics

**Endpoint:** `http://raspberry-pi:5000/metrics`

**Key Metrics:**
```
# HTTP Request Metrics
http_requests_total{method="GET",endpoint="/api/products",status="200"}
http_request_duration_seconds{endpoint="/api/products"}

# Application Metrics
nutricount_products_total
nutricount_log_entries_total
nutricount_fasting_sessions_active

# System Metrics
process_cpu_seconds_total
process_resident_memory_bytes
```

### Health Check Endpoint

**Endpoint:** `http://raspberry-pi:5000/health`

**Response:**
```json
{
  "status": "healthy",
  "database": "ok",
  "redis": "ok",
  "temperature": 65.2,
  "uptime": 86400,
  "version": "1.0.0"
}
```

### Temperature Monitoring (Raspberry Pi Specific)

```bash
# Monitor temperature continuously
./scripts/temp_monitor.sh --continuous

# Alert thresholds:
# 70°C - Warning
# 80°C - Critical (throttling starts)
# 85°C - Maximum safe
```

## Rollback Procedures

### Quick Rollback (Manual)

```bash
# SSH to Raspberry Pi
ssh pi@raspberry-pi-ip

# Navigate to project
cd /opt/nutricount

# Stop current containers
docker-compose down

# Rollback to previous image
docker-compose pull $DOCKER_USERNAME/nutricount:previous-sha

# Start with previous version
docker-compose up -d

# Verify
curl http://localhost/health
```

### Automated Rollback (Week 5 - Planned)

```yaml
- name: Rollback on failure
  if: failure()
  uses: appleboy/ssh-action@master
  with:
    host: ${{ secrets.PI_HOST }}
    username: ${{ secrets.PI_USER }}
    key: ${{ secrets.PI_SSH_KEY }}
    script: |
      cd /opt/nutricount
      docker-compose down
      docker-compose pull $PREVIOUS_IMAGE
      docker-compose up -d
```

## Environment Management

### Environment Variables

**Production (.env):**
```bash
# Flask
FLASK_ENV=production
SECRET_KEY=<strong-random-key>

# Database
DATABASE=/data/nutricount.db

# Redis
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/1

# Security
JWT_SECRET_KEY=<strong-random-key>
RATE_LIMIT_ENABLED=true

# Monitoring
PROMETHEUS_ENABLED=true
```

**Development (.env.development):**
```bash
FLASK_ENV=development
SECRET_KEY=dev-secret-key
DATABASE=nutricount.db
REDIS_URL=redis://localhost:6379/0
DEBUG=true
```

### Secrets Management

**GitHub Secrets:**
- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub password
- `PI_HOST` - Raspberry Pi IP address
- `PI_USER` - SSH username
- `PI_SSH_KEY` - SSH private key
- `JWT_SECRET_KEY` - JWT signing key

**Setting Secrets:**
```bash
# Via GitHub CLI
gh secret set DOCKER_USERNAME
gh secret set DOCKER_PASSWORD
gh secret set PI_SSH_KEY < ~/.ssh/id_rsa
```

## Troubleshooting

### Common Issues

#### 1. Tests Failing in CI But Pass Locally

**Cause:** Environment differences (Python version, dependencies)

**Solution:**
```bash
# Use same Python version as CI
pyenv install 3.11
pyenv local 3.11

# Install exact dependencies
pip install -r requirements-minimal.txt

# Run tests with same settings
export PYTHONPATH=$PWD
mkdir -p logs
pytest tests/ -v
```

#### 2. Docker Build Fails on ARM64

**Cause:** Missing QEMU emulation

**Solution:**
```bash
# Install QEMU
sudo apt-get install qemu-user-static

# Enable buildx
docker buildx create --use

# Build with specific platform
docker buildx build --platform linux/arm64 -t nutricount:latest .
```

#### 3. Deployment Health Check Fails

**Cause:** Database not ready, Redis not connected

**Solution:**
```bash
# Check container logs
docker-compose logs nutricount

# Check dependencies
docker-compose ps

# Restart with proper order
docker-compose down
docker-compose up -d redis
sleep 5
docker-compose up -d nutricount
```

#### 4. High Temperature on Raspberry Pi

**Cause:** Inadequate cooling, high load

**Solution:**
```bash
# Check temperature
vcgencmd measure_temp

# Check throttling
vcgencmd get_throttled

# Solutions:
# 1. Add/improve cooling fan
# 2. Reduce CPU frequency in /boot/config.txt
# 3. Optimize application (reduce workers)
# 4. Check thermal paste
```

### CI/CD Pipeline Debugging

**View Logs:**
```bash
# GitHub Actions logs are in the Actions tab

# For local debugging:
# 1. Use act (GitHub Actions local runner)
act pull_request

# 2. Or reproduce locally:
./scripts/ci-test.sh
```

**Common CI Failures:**

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError` | Missing dependency | Add to requirements-minimal.txt |
| `flake8 errors` | Code style issues | Run `flake8 src/ routes/` locally |
| `pytest failed` | Test failures | Run `pytest tests/ -v` locally |
| `Docker build timeout` | Slow build | Use build cache, reduce layers |
| `Permission denied` | User permissions | Use non-root user in Dockerfile |

## Best Practices

### Do's ✅
- ✅ Test CI changes in a fork first
- ✅ Use caching to speed up builds
- ✅ Keep workflows DRY (reusable workflows)
- ✅ Monitor build times and optimize
- ✅ Use semantic versioning for releases
- ✅ Document all environment variables
- ✅ Test rollback procedures regularly

### Don'ts ❌
- ❌ Don't commit secrets to repository
- ❌ Don't skip security scans
- ❌ Don't deploy without health checks
- ❌ Don't ignore failing tests
- ❌ Don't build every architecture unnecessarily
- ❌ Don't use `latest` tag in production

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Raspberry Pi Optimization Guide](../../PROJECT_SETUP.md)
- [Monitoring Setup](../../docs/devops/monitoring.md)

---

**Next Steps (Week 4-5):**
- [ ] Implement automated deployment to Raspberry Pi
- [ ] Add E2E tests to pipeline
- [ ] Implement automated rollback on failures
- [ ] Set up performance monitoring

**Status:** ✅ Complete (Week 3 - CI/CD Pipeline)
