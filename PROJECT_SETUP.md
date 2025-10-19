# Nutricount Project Setup & Custom Instructions

## Project Overview

**Nutricount** is a production-ready nutrition tracking application optimized for Raspberry Pi 4 Model B 2018 with Raspberry Pi OS Lite 64-bit. It's a Flask-based web application with modern features including JWT authentication, Redis caching, background task processing, intermittent fasting tracking, and comprehensive monitoring.

## Technology Stack

- **Backend**: Flask 2.3.3, Python 3.11
- **Database**: SQLite with WAL mode
- **Cache**: Redis (with fallback to in-memory)
- **Task Queue**: Celery (with fallback to synchronous execution)
- **Authentication**: JWT (PyJWT), bcrypt password hashing
- **Testing**: pytest, pytest-cov, pytest-mock
- **Linting**: flake8, black, isort, mypy, bandit
- **Containerization**: Docker (ARM64 optimized), docker-compose
- **Web Server**: Gunicorn + Nginx
- **Monitoring**: Prometheus metrics, structured logging (loguru)
- **CI/CD**: GitHub Actions

## Project Structure

```
nutricount/
├── app.py                          # Main Flask application
├── init_db.py                      # Database initialization
├── webhook_server.py               # Webhook server for CI/CD
├── gunicorn.conf.py               # Gunicorn configuration
├── locustfile.py                   # Load testing configuration
│
├── src/                           # Core application modules
│   ├── config.py                  # Application configuration
│   ├── constants.py               # Application constants
│   ├── utils.py                   # Utility functions
│   ├── security.py                # Authentication & authorization (JWT, bcrypt)
│   ├── fasting_manager.py         # Intermittent fasting tracking
│   ├── cache_manager.py           # Redis caching layer
│   ├── task_manager.py            # Background task processing (Celery)
│   ├── monitoring.py              # Prometheus metrics & monitoring
│   ├── advanced_logging.py        # Structured logging with loguru
│   ├── ssl_config.py              # SSL/TLS configuration
│   └── nutrition_calculator.py    # Nutrition calculations
│
├── templates/                     # Jinja2 HTML templates
│   ├── index.html                 # Main application page
│   └── admin-modal.html           # Admin panel modal
│
├── static/                        # Static assets (CSS, JS, images)
│   ├── css/
│   │   └── final-polish.css       # Application styles
│   └── js/
│       ├── app.js                 # Main application logic
│       ├── admin.js               # Admin panel functionality
│       ├── shortcuts.js           # Keyboard shortcuts
│       ├── notifications.js       # Toast notifications
│       └── offline.js             # PWA offline support
│
├── tests/                         # Test suite
│   ├── conftest.py               # Pytest configuration & fixtures
│   ├── test_app.py               # Main app tests
│   ├── unit/                     # Unit tests
│   │   ├── test_fasting_manager.py
│   │   ├── test_cache_manager.py
│   │   ├── test_security.py
│   │   ├── test_monitoring.py
│   │   ├── test_nutrition_calculator.py
│   │   ├── test_task_manager.py
│   │   ├── test_utils.py
│   │   ├── test_advanced_logging.py
│   │   ├── test_ssl_config.py
│   │   └── test_init_db.py
│   ├── integration/              # Integration tests
│   │   ├── test_api.py
│   │   └── test_api_extended.py
│   └── e2e/                     # End-to-end tests
│       ├── test_workflows.py
│       ├── test_enhanced_workflows.py
│       └── test_ui_api_workflows.py
│
├── scripts/                       # Utility scripts
│   ├── setup.sh                  # Automatic Raspberry Pi setup
│   ├── temp_monitor.sh           # Temperature monitoring (critical for Pi 4)
│   ├── monitor.sh                # System monitoring
│   ├── backup.sh                 # Database backup
│   ├── setup_ssl.sh              # SSL certificate generation
│   └── run_tests.sh              # Test runner
│
├── .github/workflows/            # CI/CD workflows
│   └── test.yml                  # GitHub Actions pipeline
│
├── requirements.txt              # Full production dependencies (103 packages)
├── requirements-minimal.txt      # CI/CD minimal dependencies (11 packages)
├── docker-compose.yml           # Docker services configuration
├── dockerfile                    # Multi-stage Docker build
├── nginx.conf                    # Nginx reverse proxy config
├── pytest.ini                    # Pytest configuration
├── .bandit                       # Bandit security config
├── .env.example                  # Environment variables template
└── schema_v2.sql                # Database schema
```

## Critical Dependencies

### Core Dependencies (requirements-minimal.txt)
These are the **MINIMUM** dependencies required for CI/CD testing:

```txt
Flask==2.3.3              # Web framework
flask-cors==6.0.1         # CORS support
PyJWT==2.8.0              # JWT authentication
bcrypt==4.1.2             # Password hashing
pytest==7.4.3             # Testing framework
pytest-cov==4.1.0         # Coverage reporting
flake8==6.1.0             # Linting
black==25.9.0             # Code formatting
isort==5.13.2             # Import sorting
mypy==1.11.2              # Type checking
bandit==1.7.5             # Security scanning
```

### Full Production Dependencies (requirements.txt)
The full application requires 103 packages including:
- **Database**: peewee (ORM), psutil (system monitoring)
- **Caching**: redis, hiredis
- **Task Queue**: celery, billiard, amqp, kombu, vine
- **Security**: cryptography, Authlib
- **Monitoring**: prometheus-client, structlog, loguru
- **Web Server**: gunicorn, uvicorn
- **Testing**: pytest-flask, pytest-mock, pytest-xdist, factory-boy, faker, freezegun
- **API**: elasticsearch (ELK stack), requests

### Dependency Management Rules

1. **Always keep requirements-minimal.txt minimal** - Only add packages that are DIRECTLY imported in:
   - `app.py`
   - `src/*.py` modules
   - `tests/conftest.py`

2. **Check imports before adding** - Use this command to see what's imported:
   ```bash
   grep -h "^import\|^from" src/*.py app.py tests/conftest.py | grep -v "^from src\|^from app" | sort -u
   ```

3. **Common missing dependencies** that break CI/CD:
   - `flask-cors` - Used in app.py for CORS
   - `PyJWT` - Used in src/security.py for JWT tokens
   - `bcrypt` - Used in src/security.py for password hashing
   - `redis` - If tests use Redis (check if mocked)
   - `celery` - If tests use Celery (check if mocked)

## Environment Setup for Ephemeral CI/CD Environments

### 1. Initial Setup (Run Once)
```bash
cd /home/runner/work/nutricount/nutricount

# Create logs directory (required by app)
mkdir -p logs

# Set PYTHONPATH
export PYTHONPATH=/home/runner/work/nutricount/nutricount

# Install minimal dependencies
pip install -r requirements-minimal.txt
```

### 2. Running Tests
```bash
# Lint code
flake8 src/ --max-line-length=100 --ignore=E501,W503,E226

# Run tests with coverage
pytest tests/ -v --cov=src --cov-report=xml

# Type checking (optional, removed from CI)
# mypy src/ --ignore-missing-imports

# Security scanning (optional, removed from CI)
# bandit -r src/ -f json -o bandit-report.json
```

### 3. Common Issues in CI/CD

#### Issue: ModuleNotFoundError
**Symptom**: `ModuleNotFoundError: No module named 'X'`
**Solution**: 
1. Check if module is imported in `src/*.py` or `app.py`
2. Add to `requirements-minimal.txt`
3. Common culprits: flask-cors, PyJWT, bcrypt, redis, celery

#### Issue: Import Errors in conftest.py
**Symptom**: Tests fail during conftest import
**Solution**:
1. Check what `tests/conftest.py` imports from `app.py`
2. Trace the import chain: app.py → src/* → dependencies
3. Add all transitive dependencies

#### Issue: Redis/Celery Not Available
**Symptom**: Warnings about Redis/Celery
**Solution**: These are expected in CI. The app has fallback modes:
- Redis → In-memory cache fallback
- Celery → Synchronous task execution fallback

#### Issue: Database Errors
**Symptom**: SQLite errors
**Solution**:
1. Ensure logs/ directory exists
2. Check if init_db.py needs to be run first
3. SQLite WAL mode may not work in some CI environments

### 4. Docker Build (Local Testing)
```bash
# Build Docker image
docker build -t nutrition-tracker:test .

# Test Docker image
docker run -d --name test-container -p 5000:5000 nutrition-tracker:test
sleep 10
curl -f http://localhost:5000/health || exit 1
docker stop test-container
docker rm test-container
```

## GitHub Actions Pipeline

### Current Workflow (.github/workflows/test.yml)

**Trigger Configuration**:
```yaml
on:
  pull_request:
    branches: [ main, develop ]
  push:
    branches: [ main ]
  workflow_dispatch:
```

**Important**: Triggers are configured to avoid duplicate runs:
- `pull_request` events fire for PR commits
- `push` events ONLY for direct commits to main branch
- This prevents the double-run issue where both events fire for the same commit

### Pipeline Jobs

**1. Test Job**
- Install minimal dependencies
- Run flake8 linting
- Run pytest with coverage
- Upload coverage to Codecov

**2. Build Job** (depends on test)
- Build Docker image
- Test Docker image health endpoint

**3. Deploy Job** (depends on build, only on main branch push)
- Deployment notification
- Webhook trigger for Raspberry Pi deployment

### Pipeline Optimization

The pipeline has been simplified from 4 complex jobs (200+ lines) to 3 essential jobs (~86 lines):

**Removed**:
- Python version matrix (now single version 3.11)
- Separate security-scan job (bandit, safety, semgrep)
- Separate performance-test job (locust)
- Multiple test type runs (unit/integration/e2e - now runs all together)
- Black/isort formatting checks (kept flake8 only)
- Type checking with mypy
- Redis service containers
- Artifact uploads
- Docker Compose testing

**Kept**:
- Essential linting (flake8)
- All tests (pytest runs all test types)
- Docker build & health check
- Coverage reporting

## Custom Instructions for AI Agents

### When Working on This Project

1. **Always check dependencies first** when encountering import errors:
   ```bash
   grep -rh "^import\|^from" src/ app.py | grep -v "^from src" | sort -u
   ```

2. **Test locally before pushing**:
   ```bash
   pip install -r requirements-minimal.txt
   export PYTHONPATH=$(pwd)
   mkdir -p logs
   flake8 src/ --max-line-length=100 --ignore=E501,W503,E226
   pytest tests/ -v
   ```

3. **When adding new features**:
   - Add imports to existing modules (don't create new dependencies if possible)
   - If new dependency needed, add to BOTH requirements.txt and requirements-minimal.txt
   - Update this documentation

4. **When fixing pipeline failures**:
   - Check GitHub Actions logs for the actual error
   - Look for ModuleNotFoundError or ImportError
   - Add missing package to requirements-minimal.txt
   - Verify package exists in requirements.txt

5. **Code Style Guidelines**:
   - Max line length: 100 characters
   - Ignore: E501 (line too long), W503 (line break before binary operator), E226 (missing whitespace around arithmetic operator)
   - Use flake8 for linting (no black/isort enforcement in CI)

6. **Testing Guidelines**:
   - All tests run with pytest (no separation of unit/integration/e2e in CI)
   - Use mocks for external services (Redis, Celery) in tests
   - Maintain >80% code coverage
   - Tests should work without Redis/Celery available

7. **Documentation**:
   - Keep README.md user-focused (deployment, features, usage)
   - Keep this file (PROJECT_SETUP.md) developer-focused (setup, troubleshooting)
   - Update both when making significant changes

## Troubleshooting Guide

### Pipeline Failure Checklist

1. ✅ Check if it's a dependency issue (ModuleNotFoundError)
2. ✅ Verify requirements-minimal.txt has all direct imports
3. ✅ Check if new code added new imports
4. ✅ Verify flake8 passes locally
5. ✅ Verify pytest passes locally
6. ✅ Check Docker builds locally
7. ✅ Review GitHub Actions logs for actual error

### Common Fixes

**Missing flask-cors**:
```bash
echo "flask-cors==6.0.1" >> requirements-minimal.txt
```

**Missing PyJWT**:
```bash
echo "PyJWT==2.8.0" >> requirements-minimal.txt
```

**Missing bcrypt**:
```bash
echo "bcrypt==4.1.2" >> requirements-minimal.txt
```

**Dependency version conflicts**:
- Check requirements.txt for the correct version
- Ensure minimal and full requirements don't conflict
- Common conflicts: pycodestyle with flake8, pyflakes with flake8

**Duplicate pipeline runs**:
- Verify workflow triggers are correct (pull_request + push: [main] only)
- Check that other workflow files don't exist (.github/workflows/*.yml)

### Health Check Commands

```bash
# Check Python version
python --version  # Should be 3.11

# Check installed packages
pip list | grep -E "flask|pytest|jwt|bcrypt|cors"

# Check PYTHONPATH
echo $PYTHONPATH

# Check directory structure
ls -la logs/  # Should exist

# Test imports manually
python -c "import flask; import flask_cors; import jwt; import bcrypt; print('All imports OK')"

# Run single test
pytest tests/test_app.py -v

# Run with debugging
pytest tests/ -vv --tb=short
```

## Quick Reference

### Essential Files
- `app.py` - Main application (DON'T break this)
- `src/security.py` - Authentication (requires PyJWT, bcrypt)
- `requirements-minimal.txt` - CI dependencies (keep minimal!)
- `.github/workflows/test.yml` - CI/CD pipeline
- `tests/conftest.py` - Test configuration (imports from app.py)

### Essential Commands
```bash
# Setup
export PYTHONPATH=$(pwd)
mkdir -p logs
pip install -r requirements-minimal.txt

# Test
flake8 src/ --max-line-length=100 --ignore=E501,W503,E226
pytest tests/ -v --cov=src

# Docker
docker build -t nutrition-tracker:test .
docker run -d -p 5000:5000 nutrition-tracker:test
curl http://localhost:5000/health
```

### Package Version References
```python
# Core web framework
Flask==2.3.3
flask-cors==6.0.1
Werkzeug==3.1.3
Jinja2==3.1.6

# Authentication
PyJWT==2.8.0
bcrypt==4.1.2
cryptography==46.0.3

# Testing
pytest==7.4.3
pytest-cov==4.1.0

# Linting
flake8==6.1.0
pycodestyle==2.11.1
pyflakes==3.1.0
mccabe==0.7.0

# Type checking
mypy==1.11.2

# Security scanning
bandit==1.7.5
pbr==7.0.1
```

## Version History

- **v1.0**: Initial project setup
- **v2.0**: Added fasting tracking, Redis caching, Celery tasks
- **v2.1**: Added security features (JWT, rate limiting, HTTPS)
- **v2.2**: Added monitoring (Prometheus, structured logging)
- **v2.3**: Pipeline optimization (from 4 jobs to 3, removed duplicates)
- **v2.4**: Dependency fixes (flask-cors, PyJWT, bcrypt)

## Maintenance Notes

- **Last Updated**: 2025-10-19
- **Python Version**: 3.11
- **Target Platform**: Raspberry Pi 4 Model B 2018, ARM64
- **CI/CD**: GitHub Actions
- **Production**: Docker + docker-compose

---

**For questions or issues, refer to:**
- README.md - User documentation
- This file - Developer setup
- GitHub Issues - Bug reports
- GitHub Actions logs - CI/CD debugging
