# GitHub Copilot Custom Instructions for Nutricount Project

## Project Overview

### Purpose
**Nutricount** is a production-ready nutrition tracking application designed for health-conscious individuals and Raspberry Pi enthusiasts. It provides comprehensive nutrition management with products, dishes, daily logging, intermittent fasting tracking, and detailed statistics. The application is optimized for Raspberry Pi 4 Model B 2018 with resource-efficient design, thermal monitoring, and edge computing capabilities.

### Technology Stack
- **Backend**: Flask 2.3.3, Python 3.11
- **Database**: SQLite with WAL mode (concurrent access support)
- **Cache**: Redis 5.0.1 (with fallback to in-memory)
- **Task Queue**: Celery 5.3.4 (with fallback to synchronous execution)
- **Authentication**: JWT (PyJWT 2.8.0), bcrypt 4.1.2 password hashing
- **Testing**: pytest 7.4.3, pytest-cov 4.1.0, pytest-mock 3.12.0, pytest-xdist 3.5.0
- **Linting**: flake8 6.1.0, black 25.9.0, isort 5.13.2, mypy 1.11.2
- **Security**: bandit 1.7.5, safety 3.6.2
- **Monitoring**: Prometheus (prometheus-client 0.19.0), loguru 0.7.3
- **Frontend**: Vanilla JavaScript, HTML5, CSS3, Bootstrap 5
- **Containerization**: Docker (ARM64 optimized), docker-compose
- **Web Server**: Gunicorn 23.0.0 + Nginx
- **CI/CD**: GitHub Actions
- **Target Platform**: Raspberry Pi 4 Model B 2018, ARM64, Raspberry Pi OS Lite 64-bit

### Architecture Pattern
**Monolithic with Modular Components** (Blueprint-based architecture)
- Entry point: `app.py` (Flask application)
- Business logic: Organized in `src/` modules
- API routes: Blueprint modules in `routes/` directory
- Frontend: Templates in `templates/`, static assets in `static/`
- Progressive Web App (PWA) support with Service Worker

### Component Dependencies
```
app.py (Main Entry)
    ├── routes/ (Blueprint Modules)
    │   ├── auth_bp → src/security.py
    │   ├── products_bp → src/utils.py
    │   ├── dishes_bp → src/utils.py
    │   ├── log_bp → src/utils.py
    │   ├── stats_bp → src/cache_manager.py
    │   ├── fasting_bp → src/fasting_manager.py
    │   ├── metrics_bp → src/monitoring.py
    │   ├── profile_bp → src/utils.py
    │   └── system_bp → src/task_manager.py
    │
    ├── src/ (Core Modules)
    │   ├── config.py (Configuration)
    │   ├── constants.py (Application constants)
    │   ├── utils.py (Utility functions)
    │   ├── security.py → PyJWT, bcrypt
    │   ├── fasting_manager.py → SQLite
    │   ├── cache_manager.py → Redis, fallback
    │   ├── task_manager.py → Celery, fallback
    │   ├── monitoring.py → prometheus-client
    │   ├── advanced_logging.py → loguru
    │   └── nutrition_calculator.py
    │
    └── Database (SQLite)
        └── schema_v2.sql (Database schema)
```

### Business Domain
**Health & Nutrition Tracking**
- **Products**: Individual food items with nutritional information (calories, protein, carbs, fat, fiber)
- **Dishes**: Recipes composed of multiple products with portion calculations
- **Daily Log**: Track consumed products/dishes with timestamps and portions
- **Statistics**: Daily, weekly, monthly nutrition summaries and trends
- **Intermittent Fasting**: Track fasting sessions with types (16:8, 18:6, 20:4, OMAD, custom)
- **GKI Calculator**: Glucose Ketone Index calculation for ketogenic diet tracking
- **User Profiles**: Personalization, themes, preferences
- **Admin Operations**: Database backup, optimization, export/import

### External Integrations
- **Redis**: Caching layer (optional, falls back to in-memory)
- **Celery**: Background task processing (optional, falls back to synchronous)
- **Prometheus**: Metrics collection endpoint (`/metrics`)
- **GitHub Actions**: CI/CD pipeline for testing and deployment
- **Docker Hub**: Container image hosting (optional)

---

## Repository Structure

### Core Application Code
```
/app.py                           # Main Flask application entry point (DON'T BREAK!)
/init_db.py                       # Database initialization script
/webhook_server.py                # CI/CD webhook server
/gunicorn.conf.py                 # Gunicorn configuration
```

### Core Modules
```
/src/                            # Core application modules
├── config.py                     # Application configuration (Config class)
├── constants.py                  # Application constants (ERROR_MESSAGES, etc.)
├── utils.py                      # Utility functions (json_response, validate_input)
├── security.py                   # JWT auth, bcrypt, SecurityHeaders
├── fasting_manager.py            # Intermittent fasting tracking
├── cache_manager.py              # Redis caching with fallback
├── task_manager.py               # Background tasks (Celery with fallback)
├── monitoring.py                 # Prometheus metrics
├── advanced_logging.py           # Structured logging (loguru)
├── ssl_config.py                 # SSL/TLS configuration
└── nutrition_calculator.py       # Nutrition calculations
```

### API Routes (Blueprints)
```
/routes/                         # API endpoint blueprints
├── auth.py                       # Authentication (/api/auth/*)
├── products.py                   # Products CRUD (/api/products/*)
├── dishes.py                     # Dishes CRUD (/api/dishes/*)
├── log.py                        # Daily log (/api/log/*)
├── stats.py                      # Statistics (/api/stats/*)
├── fasting.py                    # Fasting tracking (/api/fasting/*)
├── metrics.py                    # Prometheus metrics (/metrics)
├── profile.py                    # User profiles (/api/profile/*)
└── system.py                     # System operations (/api/system/*)
```

### Frontend
```
/templates/                      # Jinja2 HTML templates
├── index.html                    # Main application page
└── admin-modal.html              # Admin panel modal

/static/                         # Static assets
├── css/
│   └── final-polish.css          # Application styles
└── js/
    ├── app.js                    # Main application logic
    ├── admin.js                  # Admin panel functionality
    ├── shortcuts.js              # Keyboard shortcuts
    ├── notifications.js          # Toast notifications
    └── offline.js                # PWA offline support
```

### Tests
```
/tests/                          # Test suite (567 tests, 93% coverage)
├── conftest.py                   # Test configuration (imports from app.py)
├── test_app.py                   # Main app tests
├── unit/                         # Unit tests (330+ tests)
│   ├── test_fasting_manager.py
│   ├── test_cache_manager.py
│   ├── test_security.py
│   ├── test_monitoring.py
│   ├── test_nutrition_calculator.py
│   ├── test_task_manager.py
│   ├── test_utils.py
│   ├── test_advanced_logging.py
│   ├── test_ssl_config.py
│   └── test_init_db.py
├── integration/                  # Integration tests (125+ tests)
│   ├── test_api.py
│   └── test_api_extended.py
└── e2e/                         # End-to-end tests (100+ tests)
    ├── test_workflows.py
    ├── test_enhanced_workflows.py
    └── test_ui_api_workflows.py
```

### Utilities & Scripts
```
/scripts/                        # Utility scripts
├── setup.sh                      # Automatic Raspberry Pi setup
├── temp_monitor.sh               # Temperature monitoring (CRITICAL for Pi 4!)
├── monitor.sh                    # System monitoring
├── backup.sh                     # Database backup
├── setup_ssl.sh                  # SSL certificate generation
├── run_tests.sh                  # Test runner
└── mutation_test.sh              # Mutation testing
```

### Configuration Files
```
/requirements.txt                # Full production deps (103 packages)
/requirements-minimal.txt        # CI/CD minimal deps (17 packages)
/docker-compose.yml              # Docker services configuration
/dockerfile                      # Multi-stage Docker build (ARM64 optimized)
/nginx.conf                      # Nginx reverse proxy config
/pytest.ini                      # Pytest configuration
/.bandit                         # Bandit security config
/.env.example                    # Environment variables template
/schema_v2.sql                   # Database schema
/Makefile                        # Development commands
```

### Documentation
```
/docs/                           # Documentation
README.md                        # User documentation
PROJECT_SETUP.md                 # Setup guide
ARCHITECTURE.md                  # Architecture documentation
CODE_QUALITY.md                  # Code quality standards
CONTRIBUTING.md                  # Contributing guidelines
COMMUNITY_GUIDELINES.md          # Community guidelines
CODE_OF_CONDUCT.md               # Code of conduct
```

### Critical Components

**Authentication Logic**: `/src/security.py`
- JWT token generation and validation
- Bcrypt password hashing
- Security headers middleware
- Requires: PyJWT 2.8.0, bcrypt 4.1.2

**Database Access Layer**: Direct SQLite access in blueprints + `/src/utils.py`
- Database connection via `get_db()` function
- WAL mode for concurrent access
- Schema: `schema_v2.sql`

**API Endpoints**: `/routes/*.py` (9 blueprint modules)
- RESTful API design
- JSON request/response format
- Error handling with json_response()

**Business Logic**: `/src/*.py` modules
- Fasting tracking: `fasting_manager.py`
- Caching: `cache_manager.py`
- Background tasks: `task_manager.py`
- Monitoring: `monitoring.py`

**Integration Points**:
- `/routes/stats.py` → `/src/cache_manager.py` (caching)
- `/routes/fasting.py` → `/src/fasting_manager.py` (fasting logic)
- `/routes/system.py` → `/src/task_manager.py` (background tasks)
- `/routes/metrics.py` → `/src/monitoring.py` (Prometheus metrics)
- All routes → `/src/security.py` (authentication middleware)

---

## Build, Test, and Deploy Commands

### Build Commands

**Development build**:
```bash
# No build required for Python Flask
export PYTHONPATH=/home/runner/work/nutricount/nutricount
export FLASK_ENV=development
```

**Production build**:
```bash
docker-compose build --no-cache
```

**Watch mode** (for development):
```bash
export FLASK_DEBUG=1
export FLASK_ENV=development
python app.py  # Auto-reloads on file changes
```

### Test Commands

**Run all tests**:
```bash
pytest tests/ -v
# or
make test
# or
./scripts/run_tests.sh all
```

**Unit tests only**:
```bash
pytest tests/unit/ -v
# or
./scripts/run_tests.sh unit
```

**Integration tests**:
```bash
pytest tests/integration/ -v
# or
./scripts/run_tests.sh integration
```

**E2E tests**:
```bash
pytest tests/e2e/ -v
# or
./scripts/run_tests.sh e2e
```

**Test with coverage**:
```bash
pytest tests/ -v --cov=src --cov-report=html --cov-report=xml
# or
./scripts/run_tests.sh report
```

**Watch mode for tests**:
```bash
pytest-watch tests/
# or
pytest tests/ -v --looponfail
```

### Code Quality Commands

**Format code (run before every commit)**:
```bash
black app.py src/ routes/
isort app.py src/ routes/
# or
make format
```

**Lint code**:
```bash
flake8 src/ app.py routes/ --max-line-length=100 --ignore=E501,W503,E226
# or
make lint
```

**Type checking**:
```bash
mypy src/ --ignore-missing-imports
```

**Security scan**:
```bash
bandit -r src/ app.py routes/ -ll
# or
safety check --json
```

### Development Workflow

**Start development server**:
```bash
# Local development
export FLASK_ENV=development
export FLASK_DEBUG=1
export PYTHONPATH=/home/runner/work/nutricount/nutricount
mkdir -p logs
python app.py

# Docker development
docker-compose up
```

**Generate API documentation**:
```bash
# API documentation is in route docstrings
# View with: grep -r "@app.route\|@.*_bp.route" routes/ app.py
```

**Database migrations**:
```bash
# Initialize database
python init_db.py

# Backup database
./scripts/backup.sh

# Database is SQLite - no formal migrations
# Schema changes are manual via schema_v2.sql
```

**Seed test data**:
```bash
# Test data is created via fixtures in tests/conftest.py
# Use pytest fixtures for test data
```

### CI/CD Pipeline

**Trigger**: 
- Automatically on `pull_request` to `main` or `develop` branches
- Automatically on `push` to `main` branch
- Manually via `workflow_dispatch`

**Steps** (in `.github/workflows/test.yml`):
1. **Setup**: Checkout code, setup Python 3.11, install dependencies
2. **Lint**: Run flake8 with project-specific rules
3. **Security Scan**: Run bandit for security vulnerabilities
4. **Test**: Run pytest with coverage reporting
5. **Upload Coverage**: Send coverage to Codecov
6. **Build**: Build Docker image (ARM64 optimized)
7. **Health Check**: Test Docker container with `/health` endpoint
8. **Deploy**: Authorize deployment (only on main branch push)

**Required Checks**:
- ✅ Linting must pass (flake8)
- ✅ Security scan must not find critical issues (bandit)
- ✅ All tests must pass (pytest)
- ✅ Coverage must be >80%
- ✅ Docker build must succeed
- ✅ Health check must pass

**Deployment Process**:
1. All checks pass on main branch
2. Deploy authorization step runs
3. Manual deployment to Raspberry Pi (webhook-based)
4. GitHub Pages demo deployment (automated)

---

## Code Standards and Conventions

### Naming Conventions

**Files**: `snake_case.py`
- Examples: `fasting_manager.py`, `cache_manager.py`, `test_api.py`

**Classes**: `PascalCase`
- Examples: `FastingManager`, `CacheManager`, `SecurityHeaders`

**Functions/Methods**: `snake_case`
- Examples: `get_fasting_status()`, `validate_input()`, `json_response()`

**Variables**: `snake_case`
- Examples: `user_id`, `fasting_session`, `cached_data`

**Constants**: `UPPER_SNAKE_CASE`
- Examples: `ERROR_MESSAGES`, `DEFAULT_CACHE_TTL`, `MAX_RETRY_ATTEMPTS`

**Test Files**: `test_*.py`
- Examples: `test_fasting_manager.py`, `test_api.py`, `test_workflows.py`

**Blueprint Variables**: `*_bp`
- Examples: `auth_bp`, `products_bp`, `fasting_bp`

### File Organization

- **One blueprint per file**: Each route file contains one blueprint
- **Related functionality grouped**: All auth routes in `routes/auth.py`
- **Maximum file length**: 500 lines (prefer smaller, focused files)
- **Export patterns**: Use blueprints for routes, named imports for functions

### Code Style

**Indentation**: 4 spaces (Python standard)

**Line Length**: Maximum 100 characters
- Exception: Can exceed for URLs, long strings if breaking reduces readability

**Quotes**: Double quotes for strings (consistent with existing code)
- Example: `return jsonify({"error": "Invalid input"})`

**Trailing Commas**: Required for multi-line collections
```python
data = {
    "key1": "value1",
    "key2": "value2",  # ← Required
}
```

**Import Order** (enforced by isort):
```python
# 1. Standard library imports
import os
import sys
from datetime import datetime

# 2. Third-party imports
from flask import Flask, request, jsonify
import jwt
import bcrypt

# 3. Local application imports
from src.config import Config
from src.utils import some_function
```

### Comments and Documentation

**Public APIs**: Must include docstrings with parameters, return types, and examples
```python
def validate_input(data: dict, required_fields: list) -> tuple:
    """
    Validate input data for required fields.
    
    Args:
        data: Dictionary containing input data
        required_fields: List of required field names
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
        
    Example:
        is_valid, error = validate_input({"name": "Test"}, ["name", "value"])
    """
    pass
```

**Complex Logic**: Comment the "why," not the "what"
```python
# Cache with shorter TTL during fasting to show real-time updates
cache_ttl = 60 if is_fasting else 300
```

**TODO Comments**: Must include ticket number or context
```python
# TODO(#123): Implement Redis Cluster support for high availability
```

**FIXME Comments**: Require immediate attention with ticket reference
```python
# FIXME(#456): Memory leak in long-running fasting sessions
```

**Documentation Updates**: Required when public interfaces change

### Error Handling Patterns

**Async Operations**: Not applicable (Flask uses sync by default)

**Error Types**: Use standard exceptions with json_response helper
```python
from src.utils import json_response

try:
    result = operation()
    return json_response({"data": result}, 200)
except ValueError as e:
    return json_response({"error": str(e)}, 400)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return json_response({"error": "Internal server error"}, 500)
```

**Logging**: Use loguru with structured logging
```python
from src.advanced_logging import structured_logger as logger

logger.info("User logged in", user_id=user_id, ip=request.remote_addr)
logger.error("Database error", exc_info=True, query=query)
```

**User-Facing Errors**: Must be user-friendly, never expose stack traces
```python
# Good
return json_response({"error": "Product not found"}, 404)

# Bad
return json_response({"error": str(exception)}, 500)  # May expose internals
```

**Error Boundaries**: Not applicable (no React, backend error handling only)

### Dependency Management

**Adding Dependencies**:
1. Check if functionality exists in stdlib or existing deps
2. Add to `requirements.txt` with exact version: `package==1.2.3`
3. If directly imported in `app.py`, `src/*.py`, `routes/*.py`, or `tests/conftest.py`, also add to `requirements-minimal.txt`
4. Test locally: `pip install -r requirements-minimal.txt`
5. Verify CI passes

**Version Pinning**: Exact versions required
- Example: `Flask==2.3.3` not `Flask>=2.3.0`

**Dependency Updates**: 
- Security updates: Immediate
- Major version updates: Test thoroughly, update in separate PR
- Minor/patch updates: Monthly batch update

**Security Scanning**: 
- Automated via `bandit` in CI
- Manual: `safety check`

### Performance Considerations

**Database Queries**: Always use parameterized queries, avoid N+1 problems
```python
# Good: Single query with JOIN
cursor.execute("""
    SELECT p.*, d.dish_name 
    FROM products p 
    JOIN dish_products dp ON p.id = dp.product_id 
    JOIN dishes d ON dp.dish_id = d.id 
    WHERE d.id = ?
""", (dish_id,))

# Bad: N+1 query
products = cursor.execute("SELECT * FROM products").fetchall()
for product in products:
    dish = cursor.execute("SELECT * FROM dishes WHERE id = ?", (product['dish_id'],))
```

**Caching Strategy**: 
- Use Redis cache for frequently accessed data (products, dishes, stats)
- TTL: 300s for products/dishes, 60s for real-time data
- Invalidation: On create/update/delete operations
```python
from src.cache_manager import cache_manager

cached_data = cache_manager.get('products')
if not cached_data:
    cached_data = fetch_from_db()
    cache_manager.set('products', cached_data, ttl=300)
```

**Lazy Loading**: Load data on-demand, not upfront
- Use generators for large datasets
- Implement pagination for API endpoints

**Bundle Size**: Not applicable (no bundler, vanilla JS)

**Memory Management**: 
- Be mindful of Raspberry Pi's 4GB RAM limit
- Close database connections properly
- Avoid loading large datasets into memory
- Use generators and streaming for large files

### Security Best Practices

**Input Validation**: All user inputs must be validated and sanitized
```python
from src.utils import validate_input

is_valid, error = validate_input(data, ['name', 'calories'])
if not is_valid:
    return json_response({"error": error}, 400)
```

**Authentication**: JWT tokens with proper expiration
```python
from src.security import generate_jwt_token, verify_jwt_token

token = generate_jwt_token(user_id, expiry=3600)  # 1 hour
is_valid, payload = verify_jwt_token(token)
```

**Authorization**: Role-based access control (admin/user)
```python
from src.security import require_auth, require_admin

@products_bp.route('/api/products', methods=['POST'])
@require_auth
def create_product():
    pass

@system_bp.route('/api/system/backup', methods=['POST'])
@require_admin
def backup_database():
    pass
```

**Secrets Management**: Never commit secrets, use environment variables
```python
import os
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
```

**SQL Injection**: Always use parameterized queries
```python
# Good
cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))

# Bad
cursor.execute(f"SELECT * FROM products WHERE id = {product_id}")
```

**XSS Prevention**: Jinja2 auto-escapes, but sanitize JSON responses
```python
import html
name = html.escape(user_input)
```

**CSRF Protection**: Not implemented (API uses JWT, not cookies)

**Rate Limiting**: Required for all public endpoints (Flask-Limiter)
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per hour")
def login():
    pass
```

**Data Privacy**: No PII collected, GDPR not applicable

---

## Testing Requirements and Standards

### Test Coverage Targets

- **Overall Coverage**: Minimum 80% (Current: 93%)
- **Critical Paths**: Minimum 95% (auth, fasting, data operations)
- **New Code**: Minimum 90%
- **Branches**: Minimum 75%

### Unit Testing

**Structure**: Follow Arrange-Act-Assert (AAA) pattern
```python
def test_validate_input_with_missing_field(app):
    """Test validation fails when required field is missing"""
    # Arrange
    data = {"name": "Test Product"}
    required_fields = ["name", "calories"]
    
    # Act
    is_valid, error = validate_input(data, required_fields)
    
    # Assert
    assert is_valid is False
    assert "calories" in error
```

**Test Naming**: Use descriptive names following pattern:
- `test_<function>_<scenario>_<expected_outcome>`
- Examples:
  - `test_validate_input_with_valid_data_returns_true`
  - `test_create_product_with_missing_calories_returns_400`
  - `test_start_fasting_when_already_active_returns_error`

**One Test File per Source File**: Mirror source structure
- `src/utils.py` → `tests/unit/test_utils.py`
- `src/fasting_manager.py` → `tests/unit/test_fasting_manager.py`

**Isolation**: Each test must be independent
- Use fixtures for setup (`@pytest.fixture`)
- Clean up in teardown or use `autouse` fixtures
- No shared state between tests

**Mocking**: Mock all external dependencies
```python
from unittest.mock import patch, MagicMock

@patch('src.cache_manager.redis')
def test_cache_get_from_redis(mock_redis, app):
    mock_redis.get.return_value = b'cached_value'
    result = cache_manager.get('key')
    assert result == 'cached_value'
```

**Table-Driven Tests**: Use parametrize for multiple scenarios
```python
@pytest.mark.parametrize("input,expected", [
    ({"name": "Test", "calories": 100}, True),
    ({"name": "Test"}, False),
    ({}, False),
])
def test_validate_input(input, expected, app):
    is_valid, _ = validate_input(input, ["name", "calories"])
    assert is_valid == expected
```

**Fast Execution**: Unit tests should complete in milliseconds
- Mock database, Redis, Celery
- No network calls
- No file I/O

**Test Data**: Use factories or builders (pytest fixtures)
```python
@pytest.fixture
def sample_product():
    return {
        "name": "Test Product",
        "calories": 100,
        "protein": 10,
        "carbs": 15,
        "fat": 5
    }
```

### Integration Testing

**Real Dependencies**: Test with real databases (use test instances)
```python
@pytest.fixture
def app():
    """Create test app with test database"""
    os.environ['DATABASE'] = ':memory:'
    test_app = create_app()
    with test_app.app_context():
        init_test_db()
        yield test_app
```

**Test Data Setup**: Use beforeEach/afterEach for setup/cleanup
```python
@pytest.fixture(autouse=True)
def setup_teardown(app):
    # Setup
    with app.app_context():
        db = get_db()
        # Insert test data
    
    yield
    
    # Teardown
    with app.app_context():
        db = get_db()
        db.execute("DELETE FROM products")
        db.commit()
```

**Transaction Rollback**: Use SQLite transactions for cleanup
```python
@pytest.fixture
def db_transaction(app):
    with app.app_context():
        db = get_db()
        db.execute("BEGIN")
        yield db
        db.execute("ROLLBACK")
```

**External Service Mocking**: Mock third-party APIs (Redis, Celery)
```python
@patch('src.cache_manager.redis', None)  # Force fallback mode
def test_api_works_without_redis(client):
    response = client.get('/api/products')
    assert response.status_code == 200
```

**End-to-End Flows**: Test complete user journeys
```python
def test_complete_fasting_session(client, app):
    """Test starting, pausing, resuming, and ending a fasting session"""
    # Start fasting
    response = client.post('/api/fasting/start', json={'type': '16:8'})
    assert response.status_code == 200
    
    # Pause
    response = client.post('/api/fasting/pause')
    assert response.status_code == 200
    
    # Resume
    response = client.post('/api/fasting/resume')
    assert response.status_code == 200
    
    # End
    response = client.post('/api/fasting/end')
    assert response.status_code == 200
```

### E2E Testing

**Stable Locators**: Prefer semantic selectors
- Good: `getByRole('button')`, `getByLabel('Product Name')`
- Acceptable: `data-testid` attributes
- Avoid: CSS selectors, XPath

**Async Handling**: Use proper wait mechanisms
- Wait for elements to appear
- Wait for API responses
- Avoid `time.sleep()` or hardcoded waits

**Test Data**: Each test creates its own data
```python
def test_e2e_create_product(client, app):
    # Create unique test data
    product_name = f"Test Product {uuid.uuid4()}"
    response = client.post('/api/products', json={
        'name': product_name,
        'calories': 100
    })
    assert response.status_code == 200
    
    # Verify
    response = client.get('/api/products')
    products = response.json['products']
    assert any(p['name'] == product_name for p in products)
```

**Cleanup**: Tests must clean up after themselves
```python
@pytest.fixture(autouse=True)
def cleanup_test_data(app):
    yield
    # Clean up after test
    with app.app_context():
        db = get_db()
        db.execute("DELETE FROM products WHERE name LIKE 'Test Product%'")
        db.commit()
```

**Screenshots on Failure**: Capture screenshots when tests fail (Playwright)
```python
# In playwright.config.js
screenshot: 'only-on-failure',
video: 'retain-on-failure',
```

**Cross-Browser**: Test on major browsers (Chrome, Firefox, Safari via Playwright)

### Test Organization

```
tests/
├── conftest.py              # Test configuration and shared fixtures
├── test_app.py              # Main app tests
├── unit/                    # Unit tests (mirror src/ structure)
│   ├── test_fasting_manager.py
│   ├── test_cache_manager.py
│   ├── test_security.py
│   ├── test_monitoring.py
│   ├── test_nutrition_calculator.py
│   ├── test_task_manager.py
│   ├── test_utils.py
│   ├── test_advanced_logging.py
│   ├── test_ssl_config.py
│   └── test_init_db.py
├── integration/             # Integration tests (by feature)
│   ├── test_api.py
│   └── test_api_extended.py
├── e2e/                    # E2E tests (by user journey)
│   ├── test_workflows.py
│   ├── test_enhanced_workflows.py
│   └── test_ui_api_workflows.py
└── e2e-playwright/         # Playwright E2E tests
    └── test_*.spec.js
```

### Test-Driven Development (TDD) Workflow

1. **Write failing tests first** (RED)
```python
def test_new_feature():
    result = new_feature()
    assert result == expected_value
```

2. **Run tests to confirm they fail**
```bash
pytest tests/unit/test_new_feature.py -v
# Should fail with: AttributeError or ImportError
```

3. **Implement minimal code to pass** (GREEN)
```python
def new_feature():
    return expected_value
```

4. **Refactor while keeping tests passing**
```python
def new_feature():
    # Improved implementation
    return calculate_expected_value()
```

5. **Commit tests and implementation separately**
```bash
git add tests/unit/test_new_feature.py
git commit -m "test: add tests for new feature"

git add src/new_feature.py
git commit -m "feat: implement new feature"
```

---

## Documentation Standards

### Code-Level Documentation

**Public Functions/Methods**: Docstring required
```python
def calculate_nutrition(products: list, portions: dict) -> dict:
    """
    Calculate total nutrition from products and portions.
    
    Args:
        products: List of product dictionaries with nutrition info
        portions: Dictionary mapping product_id to portion size
        
    Returns:
        Dictionary with total calories, protein, carbs, fat, fiber
        
    Raises:
        ValueError: If product_id not found in products list
        
    Example:
        products = [{"id": 1, "calories": 100, "protein": 10}]
        portions = {1: 2.0}
        result = calculate_nutrition(products, portions)
        # Returns: {"calories": 200, "protein": 20, ...}
    """
    pass
```

**Classes**: Document purpose and responsibilities
```python
class FastingManager:
    """
    Manages intermittent fasting sessions and statistics.
    
    Responsibilities:
    - Start, pause, resume, and end fasting sessions
    - Track fasting duration and progress
    - Calculate fasting statistics and streaks
    - Manage fasting goals
    
    Database Tables:
    - fasting_sessions: Active and historical fasting sessions
    - fasting_goals: User-defined fasting goals
    """
    pass
```

**Modules**: README.md explaining purpose (not required for all modules)

**Complex Algorithms**: Explain approach and complexity
```python
# Binary search for efficient lookups in sorted product list
# Time complexity: O(log n)
# Space complexity: O(1)
def find_product(products, product_id):
    left, right = 0, len(products) - 1
    while left <= right:
        mid = (left + right) // 2
        if products[mid]['id'] == product_id:
            return products[mid]
        elif products[mid]['id'] < product_id:
            left = mid + 1
        else:
            right = mid - 1
    return None
```

### Repository Documentation

**README.md** must include:
- ✅ Project description (what it does, who it's for)
- ✅ Quick start guide (how to run in 5 minutes)
- ✅ Installation instructions (step-by-step)
- ✅ Configuration options (.env variables)
- ✅ Common use cases (typical workflows)
- ✅ Contributing guidelines (link to CONTRIBUTING.md)
- ✅ License information

**PROJECT_SETUP.md** includes:
- Complete setup instructions
- Development environment setup
- Testing procedures
- Deployment instructions
- Troubleshooting guide

**ARCHITECTURE.md** includes:
- System architecture overview
- Component descriptions
- Data flow diagrams
- Integration points
- Technology decisions

### Architecture Decision Records (ADRs)

**Location**: `/docs/adr/`

**Format**: Numbered markdown files
- `001-use-sqlite-for-database.md`
- `002-implement-jwt-authentication.md`

**Required for**: Significant technical decisions
- Architecture changes
- Technology selections
- Design patterns
- Performance optimizations

**Structure**:
```markdown
# ADR-001: Use SQLite for Database

## Status
Accepted

## Context
Need a lightweight, embedded database for Raspberry Pi deployment.
Considerations: resource constraints, backup simplicity, ease of deployment.

## Decision
Use SQLite with WAL mode for concurrent access.

## Consequences
**Positive:**
- No separate database server required
- Simple backup (copy file)
- Low resource usage
- ACID compliance

**Negative:**
- Limited concurrent writes
- Single file storage
- No built-in replication

## Alternatives Considered
1. **PostgreSQL**: Too resource-heavy for Raspberry Pi
2. **MySQL**: Still requires separate server process
3. **MongoDB**: NoSQL not needed for structured nutrition data
```

### Documentation Updates

**When Code Changes**: Update docs in same commit
```bash
git add src/fasting_manager.py docs/api/fasting.md
git commit -m "feat(fasting): add pause/resume functionality

- Added pause() and resume() methods to FastingManager
- Updated API documentation with new endpoints
```

**API Changes**: Require documentation update before merge
- Update docstrings
- Update API documentation
- Add examples

**Breaking Changes**: Document in CHANGELOG with migration guide
```markdown
## [2.0.0] - 2024-03-20

### BREAKING CHANGES

#### Fasting API Endpoints Changed
**Before:**
- POST /api/fasting/toggle

**After:**
- POST /api/fasting/start
- POST /api/fasting/end
- POST /api/fasting/pause
- POST /api/fasting/resume

**Migration Guide:**
Replace `POST /api/fasting/toggle` calls with appropriate start/end calls.
```

**Deprecations**: Document timeline and migration path
```python
@deprecated("Use FastingManager.start() instead. Will be removed in v3.0.0")
def start_fasting(user_id):
    """Legacy method. Use FastingManager.start() instead."""
    return FastingManager().start(user_id)
```

---

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
