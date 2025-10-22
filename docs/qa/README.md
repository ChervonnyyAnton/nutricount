# QA Documentation

**Target Audience:** QA Engineers, Test Automation Engineers, Manual Testers  
**Status:** ✅ Complete (Week 3)  
**Last Updated:** October 22, 2025

## Overview

This section provides comprehensive testing guides and strategies for QA engineers working on the Nutricount project.

## Documentation

### Testing Strategy
📄 **[Testing Strategy Guide](testing-strategy.md)** - Complete testing methodology
- Test Pyramid Strategy
- Testing Infrastructure Setup
- Manual Testing Checklists
- Automated Testing Best Practices
- Coverage Goals & Metrics
- Bug Reporting Process

## Quick Start for QA Engineers

### Backend Testing

```bash
# Install dependencies
pip install -r requirements-minimal.txt

# Setup environment
export PYTHONPATH=/home/runner/work/nutricount/nutricount
mkdir -p logs

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov=routes --cov-report=html
```

**Current Status:**
- ✅ 759 tests passing, 1 skipped
- ✅ 94% code coverage
- ✅ 0 linting errors
- ✅ ~30 second execution time

### Frontend Testing

```bash
cd frontend

# Install dependencies
npm install

# Run all tests
npm test

# Run with coverage
npm run test:coverage
```

**Current Status:**
- ✅ 80 tests passing
- ✅ 67% code coverage
- ✅ ~0.5 second execution time

## Test Organization

```
tests/
├── conftest.py              # Test configuration and fixtures
├── unit/                    # Unit tests (70% of tests)
│   ├── test_security.py     # Security & authentication tests
│   ├── test_fasting_manager.py
│   ├── test_cache_manager.py
│   └── test_nutrition_calculator.py
├── integration/             # Integration tests (20% of tests)
│   ├── test_api.py          # API endpoint tests
│   ├── test_auth_routes.py
│   ├── test_products_routes.py
│   └── test_stats_routes.py
└── e2e/                     # End-to-end tests (10% of tests)
    └── test_workflows.py    # Complete user workflows
```

## Quality Metrics Dashboard

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Test Pass Rate | 100% | 100% | ✅ |
| Backend Coverage | 90% | 94% | ✅ |
| Frontend Coverage | 80% | 67% | 🔄 In Progress |
| Linting Errors | 0 | 0 | ✅ |
| Test Execution Time | <60s | <35s | ✅ |
| Critical Bugs | 0 | 0 | ✅ |

## Key Testing Areas

### 1. Authentication & Security (Critical)
- User registration and login
- JWT token management
- Password hashing and validation
- Rate limiting
- **Coverage:** 97% ✅

### 2. Nutrition Calculations (High Priority)
- Calorie calculations from macros
- Keto index calculation
- Net carbs calculation
- BMR/TDEE calculations
- **Coverage:** 95% ✅

### 3. Data Management (High Priority)
- Products CRUD operations
- Daily log management
- Dishes/recipes management
- Statistics calculation
- **Coverage:** 90-100% ✅

### 4. Intermittent Fasting (Medium Priority)
- Fasting session tracking
- Goals management
- Statistics calculation
- **Coverage:** 100% ✅

## Testing Best Practices

### Do's ✅
- Write tests before fixing bugs (TDD)
- Follow AAA pattern (Arrange, Act, Assert)
- Use descriptive test names
- Test edge cases and error conditions
- Mock external dependencies
- Keep tests isolated and independent
- Maintain test data fixtures

### Don'ts ❌
- Don't test third-party library code
- Don't write flaky tests
- Don't skip test cleanup
- Don't test implementation details
- Don't write tests that depend on execution order
- Don't commit commented-out tests

## Common Testing Scenarios

### Testing API Endpoints

```python
def test_create_product_success(client, app):
    """Test successful product creation"""
    product_data = {
        "name": "Avocado",
        "calories": 160,
        "protein": 2,
        "fats": 15,
        "carbs": 9
    }
    
    response = client.post('/api/products', json=product_data)
    
    assert response.status_code == 201
    assert response.json['success'] is True
    assert response.json['data']['name'] == "Avocado"
```

### Testing Error Handling

```python
def test_create_product_duplicate_name(client, app):
    """Test error handling for duplicate product name"""
    product_data = {"name": "Avocado", "calories": 160}
    
    # Create first product
    client.post('/api/products', json=product_data)
    
    # Try to create duplicate
    response = client.post('/api/products', json=product_data)
    
    assert response.status_code == 400
    assert 'already exists' in response.json['error']
```

## Continuous Integration

Tests are automatically run on:
- Every pull request
- Every commit to main branch
- Nightly builds (mutation testing)

**CI Pipeline:**
1. Lint code (flake8)
2. Run unit tests
3. Run integration tests
4. Generate coverage report
5. Security scan (bandit)
6. Build Docker image
7. Run E2E tests (on PR merge)

## Resources

- [Testing Strategy Guide](testing-strategy.md) - Detailed testing methodology
- [PROJECT_SETUP.md](../../PROJECT_SETUP.md) - Project setup and development
- [ARCHITECTURE.md](../../ARCHITECTURE.md) - System architecture
- [CODE_QUALITY.md](../../CODE_QUALITY.md) - Code quality standards

## Support

For questions or issues with testing:
1. Check the [Testing Strategy Guide](testing-strategy.md)
2. Review existing tests for examples
3. Contact the development team
4. Refer to [pytest documentation](https://docs.pytest.org/)

---

**Educational Expansion:** See [EDUCATIONAL_EXPANSION_PLAN.md](../../EDUCATIONAL_EXPANSION_PLAN.md) for the complete QA learning path.

**Status:** ✅ Complete (Week 3 - QA Testing Strategy)

