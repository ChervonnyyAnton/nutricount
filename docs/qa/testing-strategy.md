# QA Testing Strategy Guide

**Target Audience:** QA Engineers, Test Automation Engineers, Manual Testers  
**Status:** ✅ Complete (Week 3)  
**Last Updated:** October 22, 2025

## Table of Contents

1. [Overview](#overview)
2. [Test Pyramid Strategy](#test-pyramid-strategy)
3. [Testing Infrastructure](#testing-infrastructure)
4. [Manual Testing Guide](#manual-testing-guide)
5. [Automated Testing](#automated-testing)
6. [Test Coverage Goals](#test-coverage-goals)
7. [Quality Metrics](#quality-metrics)
8. [Bug Reporting Process](#bug-reporting-process)
9. [Testing Checklists](#testing-checklists)

## Overview

Nutricount uses a comprehensive testing strategy that combines:
- **Unit Tests** (70%): Test individual functions and classes
- **Integration Tests** (20%): Test API endpoints and module interactions
- **E2E Tests** (10%): Test complete user workflows

### Current Test Status

**Backend Testing:**
- **Framework:** pytest 7.4.3
- **Tests:** 759 passing, 1 skipped
- **Coverage:** 94% overall
- **Execution Time:** ~30 seconds
- **Linting:** flake8 (0 errors)

**Frontend Testing:**
- **Framework:** Jest 29.7.0
- **Tests:** 80 passing
- **Coverage:** 67% overall
- **Business Logic:** 87.6% coverage
- **Execution Time:** ~0.5 seconds

## Test Pyramid Strategy

```
        /\
       /  \      E2E Tests (10%)
      /____\     - Full user workflows
     /      \    - Browser automation
    /________\   - Critical paths only
   /          \  
  /____________\ Integration Tests (20%)
 /              \- API endpoint testing
/________________\- Component integration
                  - Database operations
                  
Unit Tests (70%)
- Business logic
- Utility functions
- Data validation
- Edge cases
```

### Why This Ratio?

- **Fast Feedback:** Unit tests run in seconds, providing immediate feedback
- **High Coverage:** Unit tests cover edge cases and error conditions
- **Stable:** Unit tests are less flaky than E2E tests
- **Maintainable:** Easier to debug and maintain than E2E tests

## Testing Infrastructure

### Backend Testing Setup

```bash
# Install dependencies
pip install -r requirements-minimal.txt

# Set environment
export PYTHONPATH=/home/runner/work/nutricount/nutricount
mkdir -p logs

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov=routes --cov-report=html

# Run specific test file
pytest tests/unit/test_security.py -v

# Run specific test
pytest tests/unit/test_security.py::test_generate_token -v
```

### Frontend Testing Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode (for development)
npm run test:watch
```

### Test Database Setup

All tests use an in-memory SQLite database that is:
- Created fresh for each test
- Automatically cleaned up after each test
- Isolated from production data

## Manual Testing Guide

### Pre-Release Testing Checklist

#### Authentication & Security
- [ ] User can register with valid email
- [ ] User cannot register with duplicate email
- [ ] User can login with correct credentials
- [ ] User cannot login with incorrect credentials
- [ ] Password reset flow works correctly
- [ ] JWT tokens expire correctly
- [ ] Rate limiting prevents abuse

#### Products Management
- [ ] Create new product with all fields
- [ ] Create product with minimal fields (name, calories)
- [ ] Update existing product
- [ ] Cannot create product with duplicate name
- [ ] Delete unused product
- [ ] Cannot delete product used in log entries
- [ ] Search and filter products work correctly
- [ ] Keto index is calculated correctly

#### Daily Log
- [ ] Add product to daily log
- [ ] Update log entry quantity
- [ ] Delete log entry
- [ ] View daily totals (calories, macros)
- [ ] Navigate between days
- [ ] Export daily log as CSV

#### Dishes/Recipes
- [ ] Create new dish with ingredients
- [ ] Update dish ingredients
- [ ] Delete dish
- [ ] Add dish to daily log
- [ ] View dish nutritional values

#### Statistics & Reports
- [ ] Daily statistics display correctly
- [ ] Weekly statistics calculate accurately
- [ ] Monthly trends show data
- [ ] Charts render properly
- [ ] Export reports as PDF/CSV

#### Intermittent Fasting
- [ ] Start fasting session
- [ ] Pause/resume fasting session
- [ ] End fasting session
- [ ] View fasting history
- [ ] View fasting statistics
- [ ] Set fasting goals

#### User Interface
- [ ] Responsive on mobile (320px+)
- [ ] Responsive on tablet (768px+)
- [ ] Responsive on desktop (1024px+)
- [ ] Dark theme works correctly
- [ ] Light theme works correctly
- [ ] Keyboard navigation works
- [ ] Screen reader accessibility

#### Performance
- [ ] Page loads in < 2 seconds
- [ ] API responses in < 200ms
- [ ] No memory leaks during use
- [ ] Works with slow 3G connection

### Browser Compatibility Matrix

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | Latest | ✅ Fully Supported |
| Firefox | Latest | ✅ Fully Supported |
| Safari | Latest | ✅ Fully Supported |
| Edge | Latest | ✅ Fully Supported |
| Mobile Safari | iOS 14+ | ✅ Fully Supported |
| Chrome Mobile | Latest | ✅ Fully Supported |

### Device Testing Matrix

| Device Type | Screen Size | Status |
|------------|-------------|--------|
| Mobile (Portrait) | 320px - 480px | ✅ Tested |
| Mobile (Landscape) | 480px - 768px | ✅ Tested |
| Tablet (Portrait) | 768px - 1024px | ✅ Tested |
| Tablet (Landscape) | 1024px - 1366px | ✅ Tested |
| Desktop | 1366px+ | ✅ Tested |

## Automated Testing

### Unit Testing Best Practices

**Good Unit Test:**
```python
def test_calculate_calories_from_macros():
    """Test calorie calculation using Atwater system"""
    # Arrange
    protein = 10
    fats = 10
    carbs = 10
    
    # Act
    result = calculate_calories_from_macros(protein, fats, carbs)
    
    # Assert
    expected = (10 * 4) + (10 * 9) + (10 * 4)  # 170 calories
    assert result == expected
```

**What Makes It Good:**
- ✅ Clear, descriptive name
- ✅ Tests one thing
- ✅ Follows AAA pattern (Arrange, Act, Assert)
- ✅ Has explanatory comments
- ✅ Uses meaningful variable names

**Bad Unit Test:**
```python
def test_1():  # ❌ Unclear name
    # ❌ No arrange section
    # ❌ Tests multiple things
    assert calculate_calories_from_macros(10, 10, 10) == 170
    assert calculate_keto_index(10, 10, 10) > 0
    assert validate_nutrition_data(10, 10, 10).valid
```

### Integration Testing Best Practices

**Good Integration Test:**
```python
def test_create_product_api(client, app):
    """Test POST /api/products endpoint"""
    # Arrange
    product_data = {
        "name": "Chicken Breast",
        "calories": 165,
        "protein": 31,
        "fats": 3.6,
        "carbs": 0
    }
    
    # Act
    response = client.post('/api/products', json=product_data)
    
    # Assert
    assert response.status_code == 201
    assert response.json['success'] is True
    assert response.json['data']['name'] == "Chicken Breast"
    
    # Verify persistence
    response = client.get('/api/products')
    products = response.json['data']
    assert len(products) == 1
```

### E2E Testing Strategy

**When to Write E2E Tests:**
- ✅ Critical user workflows (login, add to log, view stats)
- ✅ Multi-step processes (create dish with ingredients)
- ✅ Payment or security-critical flows
- ❌ Simple CRUD operations (covered by integration tests)
- ❌ Edge cases (covered by unit tests)

**E2E Test Example:**
```javascript
test('User can log food and view daily totals', async () => {
    // Login
    await page.goto('http://localhost:5000');
    await page.fill('#email', 'test@example.com');
    await page.fill('#password', 'password123');
    await page.click('#login-btn');
    
    // Add food to log
    await page.click('#add-food-btn');
    await page.selectOption('#product-select', 'Chicken Breast');
    await page.fill('#quantity', '100');
    await page.click('#save-log-btn');
    
    // Verify totals updated
    const calories = await page.textContent('#daily-calories');
    expect(calories).toBe('165 kcal');
});
```

## Test Coverage Goals

### Current Coverage

| Module | Coverage | Goal | Status |
|--------|----------|------|--------|
| src/security.py | 97% | 95% | ✅ Exceeded |
| src/fasting_manager.py | 100% | 95% | ✅ Exceeded |
| src/monitoring.py | 98% | 90% | ✅ Exceeded |
| routes/auth.py | 95% | 90% | ✅ Exceeded |
| routes/products.py | 90% | 90% | ✅ Met |
| routes/log.py | 100% | 90% | ✅ Exceeded |
| **Overall** | **94%** | **90%** | **✅ Exceeded** |

### Coverage Guidelines

**What to Prioritize:**
1. **Critical Paths** (100% coverage required)
   - Authentication and authorization
   - Payment processing (if applicable)
   - Data validation and sanitization
   - Security-critical operations

2. **Business Logic** (95% coverage goal)
   - Nutrition calculations
   - Keto index calculations
   - BMR/TDEE calculations
   - Fasting tracking

3. **API Endpoints** (90% coverage goal)
   - All CRUD operations
   - Error handling
   - Input validation

4. **Utility Functions** (85% coverage acceptable)
   - Helper functions
   - Formatters
   - Converters

**What Not to Test:**
- ❌ Third-party library code
- ❌ Generated code (migration files)
- ❌ Simple getters/setters without logic
- ❌ Configuration files

## Quality Metrics

### Key Quality Indicators (KQIs)

**Test Health:**
- ✅ Pass Rate: 100% (759/759 backend, 80/80 frontend)
- ✅ Coverage: 94% backend, 67% frontend
- ✅ Execution Time: <35 seconds total
- ✅ Flaky Tests: 0

**Code Quality:**
- ✅ Linting Errors: 0
- ✅ Security Vulnerabilities: 0 critical, 0 high
- ✅ Code Smells: Minimal
- ✅ Duplication: <3%

**Defect Metrics:**
- Target: <5 bugs per release
- Severity breakdown: 0 critical, 0 high, <3 medium, <5 low
- Escaped defects: <1 per release

### Mutation Testing

**Status:** Infrastructure ready, baseline in progress

**What is Mutation Testing?**
Mutation testing introduces small changes (mutations) to your code to verify that tests catch the changes.

**Example:**
```python
# Original code
def calculate_bmi(weight, height):
    return weight / (height ** 2)

# Mutation 1: Change operator
def calculate_bmi(weight, height):
    return weight * (height ** 2)  # Should be caught by tests

# Mutation 2: Change constant
def calculate_bmi(weight, height):
    return weight / (height ** 3)  # Should be caught by tests
```

**Goal:** 80%+ mutation score for critical modules

## Bug Reporting Process

### Bug Report Template

```markdown
## Bug Report

**Title:** Clear, descriptive one-liner

**Severity:** Critical / High / Medium / Low

**Priority:** P0 / P1 / P2 / P3

**Environment:**
- OS: [e.g., Ubuntu 22.04, macOS 13.0]
- Browser: [e.g., Chrome 118, Firefox 119]
- Device: [e.g., Desktop, iPhone 14]
- Version: [e.g., v1.2.3]

**Steps to Reproduce:**
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Screenshots/Logs:**
If applicable, add screenshots or error logs

**Additional Context:**
Any other context about the problem
```

### Severity Definitions

**Critical (P0):**
- Complete system outage
- Data loss or corruption
- Security vulnerability
- **SLA:** Fix within 4 hours

**High (P1):**
- Major feature broken
- Affects multiple users
- No workaround available
- **SLA:** Fix within 24 hours

**Medium (P2):**
- Feature partially broken
- Workaround available
- Affects some users
- **SLA:** Fix within 1 week

**Low (P3):**
- Minor UI issues
- Cosmetic problems
- Feature enhancement
- **SLA:** Fix in next release

## Testing Checklists

### Pre-Commit Checklist

- [ ] All tests pass locally
- [ ] New code has tests (unit + integration)
- [ ] Coverage maintained or improved
- [ ] No linting errors
- [ ] No security vulnerabilities added
- [ ] Documentation updated

### Pre-Release Checklist

- [ ] All automated tests pass
- [ ] Manual smoke tests completed
- [ ] Regression tests passed
- [ ] Performance tests passed
- [ ] Security scan completed
- [ ] Browser compatibility verified
- [ ] Mobile responsiveness verified
- [ ] Accessibility checks passed
- [ ] Release notes written
- [ ] Rollback plan prepared

### Post-Release Checklist

- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify user analytics
- [ ] Review user feedback
- [ ] Update documentation
- [ ] Close resolved issues

## Resources

### Testing Tools

**Backend:**
- pytest: https://docs.pytest.org/
- pytest-cov: https://pytest-cov.readthedocs.io/
- mutmut: https://mutmut.readthedocs.io/

**Frontend:**
- Jest: https://jestjs.io/
- Playwright: https://playwright.dev/
- Cypress: https://www.cypress.io/

### Learning Resources

- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [JavaScript Testing Best Practices](https://github.com/goldbergyoni/javascript-testing-best-practices)
- [Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html)
- [Mutation Testing](https://en.wikipedia.org/wiki/Mutation_testing)

---

**Questions?** Contact the development team or refer to [PROJECT_SETUP.md](../../PROJECT_SETUP.md) for more details.

**Status:** ✅ Complete (Week 3)
