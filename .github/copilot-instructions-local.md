# GitHub Copilot Instructions for Local Development Setup

## Local Development Environment

This guide provides instructions for setting up the Nutricount project for local development on your machine (not CI/CD environments).

## Prerequisites

### Required Software
- **Python 3.11** (exact version required)
- **Git** (latest version)
- **Docker** (latest version) + **docker-compose**
- **Redis** (optional, app has fallback)
- **Text Editor/IDE** with GitHub Copilot extension

### Optional Software
- **pyenv** - Python version management
- **virtualenv** or **venv** - Virtual environment management
- **pre-commit** - Git hooks for automatic linting

## Quick Start Guide

### 1. Clone Repository
```bash
git clone https://github.com/ChervonnyyAnton/nutricount.git
cd nutricount
```

### 2. Set Up Python Environment
```bash
# Using venv (recommended)
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# OR using virtualenv
virtualenv -p python3.11 venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install all production dependencies
pip install --upgrade pip
pip install -r requirements.txt

# OR install minimal dependencies (for testing only)
pip install -r requirements-minimal.txt
```

### 4. Set Up Environment Variables
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

### 5. Initialize Database
```bash
# Create logs directory
mkdir -p logs

# Set PYTHONPATH
export PYTHONPATH=$(pwd)

# Initialize database
python init_db.py
```

### 6. Run Application
```bash
# Development mode (Flask built-in server)
python app.py

# OR Production mode (with Gunicorn)
gunicorn -c gunicorn.conf.py app:app

# OR Docker mode
docker-compose up -d
```

### 7. Access Application
- **Web Interface**: http://localhost:5000
- **API**: http://localhost:5000/api/
- **Health Check**: http://localhost:5000/health

## Development Workflow

### Before Making Changes

1. **Pull latest changes**
```bash
git pull origin main
```

2. **Activate virtual environment**
```bash
source venv/bin/activate
```

3. **Update dependencies if needed**
```bash
pip install -r requirements.txt
```

4. **Run tests to ensure everything works**
```bash
export PYTHONPATH=$(pwd)
pytest tests/ -v
```

### Making Changes

1. **Create feature branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes** following the code style guidelines

3. **Run linter**
```bash
flake8 src/ --max-line-length=100 --ignore=E501,W503,E226
```

4. **Run tests**
```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

5. **Commit changes**
```bash
git add .
git commit -m "Description of changes"
```

6. **Push to GitHub**
```bash
git push origin feature/your-feature-name
```

### After Making Changes

1. **Create Pull Request** on GitHub
2. **Wait for CI/CD pipeline** to pass
3. **Request review** if needed
4. **Merge** when approved

## Common Development Tasks

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/unit/test_security.py -v

# Specific test function
pytest tests/unit/test_security.py::test_password_hashing -v

# With coverage
pytest tests/ -v --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # On macOS
xdg-open htmlcov/index.html  # On Linux
```

### Code Quality Checks

```bash
# Linting
flake8 src/ --max-line-length=100 --ignore=E501,W503,E226

# Type checking
mypy src/ --ignore-missing-imports

# Security scanning
bandit -r src/ -f json -o bandit-report.json

# Code formatting (check only)
black --check src/
isort --check-only src/

# Code formatting (apply)
black src/
isort src/
```

### Database Operations

```bash
# Initialize database
python init_db.py

# Backup database
python -c "from src.utils import backup_database; backup_database()"

# View database
sqlite3 nutrition_tracker.db
.tables
.schema products
SELECT * FROM products LIMIT 5;
.quit
```

### Docker Operations

```bash
# Build image
docker build -t nutrition-tracker:local .

# Run container
docker run -d -p 5000:5000 --name nutricount nutrition-tracker:local

# View logs
docker logs -f nutricount

# Stop container
docker stop nutricount
docker rm nutricount

# Docker Compose
docker-compose up -d          # Start all services
docker-compose down           # Stop all services
docker-compose logs -f        # View logs
docker-compose restart        # Restart services
```

### Working with Redis (Optional)

```bash
# Start Redis (if installed locally)
redis-server

# OR start Redis with Docker
docker run -d -p 6379:6379 --name redis redis:7-alpine

# Test Redis connection
redis-cli ping  # Should return "PONG"

# View cached data
redis-cli
KEYS *
GET cache_key
QUIT
```

## IDE Setup

### VS Code Configuration

Create `.vscode/settings.json`:
```json
{
  "python.pythonPath": "venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": [
    "--max-line-length=100",
    "--ignore=E501,W503,E226"
  ],
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": [
    "--line-length=100"
  ],
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "editor.formatOnSave": false,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    ".pytest_cache": true,
    "htmlcov": true,
    "*.egg-info": true
  }
}
```

### PyCharm Configuration

1. **Set Python Interpreter**: File → Settings → Project → Python Interpreter → Add → Virtualenv Environment → Existing → `venv/bin/python`
2. **Configure pytest**: File → Settings → Tools → Python Integrated Tools → Testing → pytest
3. **Configure flake8**: File → Settings → Tools → External Tools → Add flake8
4. **Enable type hints**: File → Settings → Editor → Inspections → Python → Type Checker

## Troubleshooting Local Issues

### Python Version Issues

**Problem**: Wrong Python version
```bash
# Check version
python --version  # Should be 3.11.x

# If wrong version, use pyenv
pyenv install 3.11.14
pyenv local 3.11.14
```

### Dependency Issues

**Problem**: ModuleNotFoundError
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Clear cache and reinstall
pip cache purge
pip install --no-cache-dir -r requirements.txt
```

### Database Issues

**Problem**: Database locked or corrupted
```bash
# Delete database and recreate
rm nutrition_tracker.db
python init_db.py
```

### Port Already in Use

**Problem**: Port 5000 already in use
```bash
# Find process using port
lsof -i :5000  # On macOS/Linux
netstat -ano | findstr :5000  # On Windows

# Kill process
kill -9 <PID>  # On macOS/Linux
taskkill /PID <PID> /F  # On Windows

# OR use different port
export FLASK_RUN_PORT=5001
python app.py
```

### Redis Connection Issues

**Problem**: Redis not available
```bash
# The app has fallback mode, this is OK for development
# To fix, start Redis:
redis-server

# OR use Docker:
docker run -d -p 6379:6379 redis:7-alpine
```

### Import Errors

**Problem**: Can't import from src/
```bash
# Set PYTHONPATH
export PYTHONPATH=$(pwd)

# Add to your ~/.bashrc or ~/.zshrc:
echo 'export PYTHONPATH="${PYTHONPATH}:$(pwd)"' >> ~/.bashrc
source ~/.bashrc
```

## Environment Variables

Key environment variables for local development:

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_APP=app.py
SECRET_KEY=your-secret-key-here

# Database
DATABASE_PATH=nutrition_tracker.db

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Celery (optional)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=logs/app.log

# Security
JWT_SECRET_KEY=your-jwt-secret-here
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=86400
```

## Performance Tips for Local Development

1. **Use SQLite for development** (no need for PostgreSQL)
2. **Skip Redis** if not testing cache-specific features (app has fallback)
3. **Skip Celery** if not testing background tasks (app has fallback)
4. **Use pytest-xdist** for parallel test execution:
   ```bash
   pip install pytest-xdist
   pytest tests/ -n auto
   ```
5. **Use watchdog** for auto-reloading:
   ```bash
   pip install watchdog
   flask run --reload
   ```

## Git Workflow Best Practices

### Branch Naming
- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Urgent production fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation changes

### Commit Messages
Follow conventional commits:
```
feat: Add user authentication
fix: Resolve database connection issue
docs: Update API documentation
refactor: Simplify nutrition calculation logic
test: Add tests for fasting manager
```

### Pre-commit Hooks

Install pre-commit hooks (optional but recommended):
```bash
pip install pre-commit
pre-commit install

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black
        args: [--line-length=100]
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: [--max-line-length=100, --ignore=E501,W503,E226]
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
EOF
```

## Debugging Tips

### Flask Debug Mode
```python
# In app.py (for local development only)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### Python Debugger
```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# OR use built-in breakpoint (Python 3.7+)
breakpoint()

# Common pdb commands:
# n - next line
# s - step into function
# c - continue
# p variable - print variable
# l - list code around current line
# q - quit debugger
```

### VS Code Debugging

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Flask",
      "type": "python",
      "request": "launch",
      "module": "flask",
      "env": {
        "FLASK_APP": "app.py",
        "FLASK_ENV": "development",
        "PYTHONPATH": "${workspaceFolder}"
      },
      "args": [
        "run",
        "--no-debugger",
        "--no-reload"
      ],
      "jinja": true
    },
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    },
    {
      "name": "Python: Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": [
        "tests/",
        "-v"
      ],
      "console": "integratedTerminal"
    }
  ]
}
```

## Additional Resources

- **Main Documentation**: `README.md` - User guide and deployment
- **Project Setup**: `PROJECT_SETUP.md` - Comprehensive developer guide
- **API Documentation**: Check `app.py` route decorators
- **Database Schema**: `schema_v2.sql`
- **CI/CD Instructions**: `.github/copilot-instructions.md`

## Quick Reference Commands

```bash
# Setup
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=$(pwd)
mkdir -p logs
python init_db.py

# Development
python app.py                          # Run app
pytest tests/ -v                       # Run tests
flake8 src/ --max-line-length=100 --ignore=E501,W503,E226  # Lint

# Docker
docker-compose up -d                   # Start
docker-compose logs -f                 # View logs
docker-compose down                    # Stop

# Git
git checkout -b feature/my-feature     # New branch
git add .                              # Stage changes
git commit -m "feat: description"      # Commit
git push origin feature/my-feature     # Push
```

## Remember

1. **Always use virtual environment** - Isolate project dependencies
2. **Set PYTHONPATH** - Ensures imports work correctly
3. **Run tests before committing** - Catch issues early
4. **Follow code style** - Use flake8 and existing patterns
5. **Document changes** - Update docs when adding features
6. **Test thoroughly** - Write tests for new code
7. **Keep dependencies minimal** - Only add what's needed
8. **Use Git branches** - Never commit directly to main
