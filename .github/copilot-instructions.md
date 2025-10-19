# GitHub Copilot Custom Instructions for Nutricount Project

## Project Context

This is a production-ready nutrition tracking application optimized for Raspberry Pi 4 Model B 2018. It's a Flask-based web application with JWT authentication, Redis caching, background task processing, and comprehensive monitoring.

## Technology Stack

- **Backend**: Flask 2.3.3, Python 3.11
- **Database**: SQLite with WAL mode
- **Cache**: Redis (with fallback to in-memory)
- **Authentication**: JWT (PyJWT 2.8.0), bcrypt password hashing
- **Testing**: pytest 7.4.3, pytest-cov
- **Linting**: flake8 6.1.0 (max-line-length=100, ignore=E501,W503,E226)
- **Containerization**: Docker (ARM64 optimized)
- **Target Platform**: Raspberry Pi 4 Model B 2018, ARM64, Raspberry Pi OS Lite 64-bit

## Code Style Guidelines

- Maximum line length: 100 characters
- Ignore flake8 codes: E501 (line too long), W503 (line break before binary operator), E226 (missing whitespace around arithmetic operator)
- Use type hints where appropriate
- Follow PEP 8 conventions except for the ignores above
- Prefer explicit over implicit
- Use descriptive variable names

## Project Structure

```
nutricount/
├── app.py                          # Main Flask application (DON'T break this file!)
├── src/                           # Core modules
│   ├── config.py                  # Application configuration
│   ├── constants.py               # Application constants
│   ├── utils.py                   # Utility functions
│   ├── security.py                # JWT auth, bcrypt (requires PyJWT, bcrypt)
│   ├── fasting_manager.py         # Intermittent fasting tracking
│   ├── cache_manager.py           # Redis caching with fallback
│   ├── task_manager.py            # Background tasks (Celery with fallback)
│   ├── monitoring.py              # Prometheus metrics
│   ├── advanced_logging.py        # Structured logging
│   └── nutrition_calculator.py    # Nutrition calculations
├── tests/                         # Test suite (pytest)
│   ├── conftest.py               # Test configuration (imports from app.py)
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── e2e/                     # End-to-end tests
├── requirements.txt              # Full production deps (103 packages)
└── requirements-minimal.txt      # CI/CD minimal deps (11 packages)
```

## Critical Dependencies

### Minimal Dependencies (requirements-minimal.txt)
These are REQUIRED for CI/CD and must be kept minimal:

```
Flask==2.3.3              # Web framework
flask-cors==6.0.1         # CORS support (imported in app.py)
PyJWT==2.8.0              # JWT auth (imported in src/security.py)
bcrypt==4.1.2             # Password hashing (imported in src/security.py)
pytest==7.4.3             # Testing framework
pytest-cov==4.1.0         # Coverage reporting
flake8==6.1.0             # Linting
black==25.9.0             # Code formatting
isort==5.13.2             # Import sorting
mypy==1.11.2              # Type checking
bandit==1.7.5             # Security scanning
```

### When Adding New Dependencies

1. **Check if the import is direct**: Only add packages directly imported in `app.py`, `src/*.py`, or `tests/conftest.py`
2. **Add to both files**: Add to both `requirements.txt` AND `requirements-minimal.txt`
3. **Use specific versions**: Always pin to specific versions (e.g., `Flask==2.3.3`)
4. **Check compatibility**: Verify no version conflicts with existing packages
5. **Common pitfall**: Forgetting transitive dependencies (e.g., flask-cors is imported but was missing)

## Common Patterns to Follow

### Import Order
```python
# Standard library imports
import os
import sys
from datetime import datetime

# Third-party imports
from flask import Flask, request, jsonify
import jwt
import bcrypt

# Local application imports
from src.config import Config
from src.utils import some_function
```

### Error Handling
```python
try:
    # Operation
    result = some_function()
except SpecificException as e:
    # Log the error
    logger.error(f"Operation failed: {e}")
    # Return user-friendly error
    return jsonify({"error": "User-friendly message"}), 500
```

### API Response Format
```python
# Success
return jsonify({"success": True, "data": result}), 200

# Error
return jsonify({"error": "Error message"}), 400
```

### Testing Pattern
```python
def test_feature(client, app):
    """Test feature with descriptive docstring"""
    # Arrange
    data = {"key": "value"}
    
    # Act
    response = client.post('/api/endpoint', json=data)
    
    # Assert
    assert response.status_code == 200
    assert response.json['success'] is True
```

## Dos and Don'ts

### DO
- ✅ Check imports before adding dependencies
- ✅ Run `flake8 src/ --max-line-length=100 --ignore=E501,W503,E226` before committing
- ✅ Run `pytest tests/ -v` to verify tests pass
- ✅ Use mocks for external services (Redis, Celery) in tests
- ✅ Keep requirements-minimal.txt minimal (only direct imports)
- ✅ Use type hints for function signatures
- ✅ Add docstrings to public functions
- ✅ Handle errors gracefully with user-friendly messages
- ✅ Use environment variables for configuration
- ✅ Follow the existing code structure and patterns

### DON'T
- ❌ Break `app.py` - it's the main entry point
- ❌ Add dependencies without checking if they're needed
- ❌ Forget to add dependencies to requirements-minimal.txt
- ❌ Use hardcoded values (use config.py or constants.py)
- ❌ Remove existing error handling
- ❌ Add new external services without fallback support
- ❌ Ignore flake8 warnings (except E501, W503, E226)
- ❌ Skip writing tests for new features
- ❌ Use deprecated Python features
- ❌ Modify database schema without migration plan

## Testing Guidelines

### Running Tests Locally
```bash
# Setup environment
export PYTHONPATH=/home/runner/work/nutricount/nutricount
mkdir -p logs

# Install dependencies
pip install -r requirements-minimal.txt

# Run tests
pytest tests/ -v --cov=src --cov-report=xml

# Lint code
flake8 src/ --max-line-length=100 --ignore=E501,W503,E226
```

### Test Structure
- **Unit tests** (`tests/unit/`): Test individual functions/classes in isolation
- **Integration tests** (`tests/integration/`): Test API endpoints and module interactions
- **E2E tests** (`tests/e2e/`): Test complete user workflows

### Mocking External Services
```python
# Mock Redis
@patch('src.cache_manager.redis')
def test_with_redis(mock_redis):
    mock_redis.get.return_value = b'cached_value'
    # Test code

# Mock Celery
@patch('src.task_manager.celery_app')
def test_with_celery(mock_celery):
    mock_celery.send_task.return_value = MagicMock(id='task-id')
    # Test code
```

## CI/CD Pipeline

### Workflow Triggers
- `pull_request`: For PRs to main or develop
- `push`: Only for direct commits to main branch
- This prevents duplicate runs on PR commits

### Pipeline Jobs
1. **Test**: Lint + pytest
2. **Build**: Docker build + health check
3. **Deploy**: Deployment notification (only on main push)

### Pipeline Failures
If the pipeline fails, check:
1. ✅ Is it a `ModuleNotFoundError`? → Add missing package to requirements-minimal.txt
2. ✅ Is it a linting error? → Fix code style or add to ignore list
3. ✅ Is it a test failure? → Fix the failing test
4. ✅ Is it a Docker build error? → Check Dockerfile and dependencies

## Security Considerations

- **Authentication**: Use JWT tokens with proper expiration
- **Passwords**: Always hash with bcrypt (never store plaintext)
- **Input validation**: Sanitize all user inputs
- **Rate limiting**: Enforce rate limits on API endpoints
- **HTTPS**: Use SSL/TLS in production
- **Secrets**: Never commit secrets (use environment variables)
- **SQL injection**: Use parameterized queries
- **XSS protection**: Sanitize output in templates

## Performance Considerations

- **Caching**: Use Redis cache for frequently accessed data
- **Background tasks**: Use Celery for long-running operations
- **Database**: Use SQLite WAL mode for concurrent access
- **Monitoring**: Track metrics with Prometheus
- **Memory**: Be mindful of Raspberry Pi's limited resources (4GB RAM)
- **Temperature**: Monitor CPU temperature (critical for Pi 4)

## When Working on Features

### Adding New API Endpoint
1. Define route in `app.py`
2. Add business logic in appropriate `src/*.py` module
3. Add input validation
4. Add error handling
5. Write unit tests
6. Write integration tests
7. Update API documentation

### Adding New Dependency
1. Check if really needed (can you use existing?)
2. Add to `requirements.txt` with specific version
3. Add to `requirements-minimal.txt` if directly imported
4. Test locally with `pip install -r requirements-minimal.txt`
5. Verify pipeline passes

### Fixing Bugs
1. Write a failing test that reproduces the bug
2. Fix the bug
3. Verify the test passes
4. Verify no other tests broke
5. Run linter

## Troubleshooting Common Issues

### ModuleNotFoundError in CI
**Symptom**: `ModuleNotFoundError: No module named 'X'`
**Fix**: Add `X` to requirements-minimal.txt

### Flake8 Errors
**Symptom**: `E501 line too long`
**Fix**: Break long lines or add to ignore if justified

### Test Import Errors
**Symptom**: Tests can't import from `src/`
**Fix**: Ensure `PYTHONPATH` is set correctly

### Docker Build Fails
**Symptom**: Docker build error
**Fix**: Check dependencies in requirements.txt, verify Dockerfile syntax

## Additional Resources

- Full project documentation: `PROJECT_SETUP.md`
- User documentation: `README.md`
- Database schema: `schema_v2.sql`
- API documentation: Check route decorators in `app.py`

## Remember

1. **Keep it simple**: Don't over-engineer solutions
2. **Test thoroughly**: Write tests for new features
3. **Document changes**: Update documentation when needed
4. **Follow conventions**: Use existing patterns
5. **Ask for help**: Check PROJECT_SETUP.md for detailed guides
