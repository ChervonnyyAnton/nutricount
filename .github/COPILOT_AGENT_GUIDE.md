# GitHub Copilot Coding Agent Complete Guide

This guide provides comprehensive instructions for using GitHub Copilot coding agent effectively in the Nutricount project.

---

## Table of Contents

1. [Issue Management Best Practices](#issue-management-best-practices)
2. [PDCA Workflow (Plan-Do-Check-Act)](#pdca-workflow-plan-do-check-act)
3. [Quality Metrics and Monitoring](#quality-metrics-and-monitoring)
4. [Code Review Guidelines](#code-review-guidelines)

---

## Issue Management Best Practices

### Writing Issues for Copilot Coding Agent

Think of issues as prompts for an AI agent. Essential components:

#### 1. Clear, Descriptive Title

**Good titles:**
- `[BUG] Fasting session not ending when time expires`
- `[FEATURE] Add export functionality for nutrition data`
- `[TASK] Implement Redis caching for product list`

**Bad titles:**
- `Fix bug`
- `Improve performance`
- `Update feature`

#### 2. Problem Description

Clearly explain **what** is wrong or **what** needs to be built:

```markdown
### Problem
Users cannot export their nutrition data to CSV format for external analysis.
This limits the ability to use data with other tools like Excel or Google Sheets.

### Current Behavior
The application only displays data in the web interface with no export option.

### Desired Behavior
Users should be able to export:
- Daily logs to CSV
- Product database to CSV
- Dish database to CSV
- Fasting history to CSV
```

#### 3. Acceptance Criteria

Specific, measurable criteria for completion:

```markdown
## Acceptance Criteria
- [ ] Add "Export to CSV" button on each major page
- [ ] Clicking button downloads CSV file with proper formatting
- [ ] CSV includes all relevant fields for each data type
- [ ] File naming follows pattern: `nutricount_<type>_<date>.csv`
- [ ] Export works for datasets with 1000+ rows
- [ ] Tests pass with >80% coverage
- [ ] Documentation updated with export instructions
```

#### 4. File Locations

Tell the agent exactly where to work:

```markdown
## Files to Modify

### Backend
- `/routes/system.py` - Add export endpoints
  - `GET /api/export/products` - Export products
  - `GET /api/export/dishes` - Export dishes
  - `GET /api/export/log?date=YYYY-MM-DD` - Export daily log

### Frontend
- `/static/js/app.js` - Add export button click handlers
- `/templates/index.html` - Add export buttons to UI

### Tests
- `/tests/integration/test_api_extended.py` - Test export endpoints
- `/tests/unit/test_utils.py` - Test CSV generation helpers

### Utilities
- `/src/utils.py` - Add CSV generation helper functions
```

#### 5. Implementation Hints

Guide the agent with patterns and examples:

```markdown
## Implementation Guidance

### Similar Pattern
See `/routes/stats.py` for example of data aggregation and response formatting.

### Reusable Components
- Use `src/utils.py::json_response()` for consistent API responses
- Use Python's `csv` module for CSV generation
- Follow existing route pattern in `routes/system.py`

### Example Implementation
\```python
import csv
import io
from flask import Response

@system_bp.route('/api/export/products', methods=['GET'])
def export_products():
    """Export all products to CSV"""
    products = fetch_all_products()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['id', 'name', 'calories', ...])
    writer.writeheader()
    writer.writerows(products)
    
    # Return as downloadable file
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=products.csv'}
    )
\```
```

#### 6. Testing Requirements

Specify exactly what to test:

```markdown
## Testing Requirements

### Unit Tests
- [ ] Test CSV generation with empty dataset
- [ ] Test CSV generation with single row
- [ ] Test CSV generation with 1000+ rows
- [ ] Test proper field quoting and escaping
- [ ] Test date formatting in CSV

### Integration Tests
- [ ] Test GET /api/export/products returns valid CSV
- [ ] Test GET /api/export/dishes returns valid CSV
- [ ] Test CSV can be parsed by standard CSV readers
- [ ] Test proper HTTP headers (Content-Type, Content-Disposition)
- [ ] Test export with authentication required

### Example Test
\```python
def test_export_products_returns_valid_csv(client, app):
    """Test that product export returns valid CSV"""
    # Arrange - Create test products
    create_test_product(app, name="Apple", calories=52)
    create_test_product(app, name="Banana", calories=89)
    
    # Act - Export products
    response = client.get('/api/export/products')
    
    # Assert - Verify CSV
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/csv'
    
    # Parse CSV
    csv_reader = csv.DictReader(io.StringIO(response.data.decode()))
    rows = list(csv_reader)
    
    assert len(rows) == 2
    assert rows[0]['name'] == 'Apple'
    assert rows[1]['name'] == 'Banana'
\```
```

#### 7. Related Issues

Link dependencies and relationships:

```markdown
## Related Issues
- Depends on: #123 (Database optimization for large exports)
- Related to: #456 (Import functionality)
- Blocks: #789 (Data backup feature)
```

### Bug Report Best Practices

For bugs, include:

1. **Steps to Reproduce**: Exact steps to trigger the bug
2. **Expected Behavior**: What should happen
3. **Actual Behavior**: What actually happens
4. **Environment**: OS, browser, Python version
5. **Error Logs**: Stack traces, console output
6. **Impact**: Severity and users affected
7. **Workaround**: If available

### Feature Request Best Practices

For features, include:

1. **Problem Statement**: What problem does this solve?
2. **Proposed Solution**: Detailed description
3. **Use Cases**: Who benefits and how?
4. **Success Criteria**: How to measure success
5. **Technical Considerations**: Architecture impact
6. **Alternatives Considered**: Other approaches and why rejected

---

## PDCA Workflow (Plan-Do-Check-Act)

The PDCA cycle ensures high-quality, iterative development.

### PLAN Phase: Before Writing Code

#### 1. High-Level Analysis

- [ ] Understand issue description completely
- [ ] Review acceptance criteria
- [ ] Identify affected components
- [ ] Check for similar implementations

**Questions to answer:**
- What is the core problem to solve?
- What are the expected outcomes?
- Which modules/files are involved?
- Are there existing patterns to follow?

#### 2. Pattern Research

Find 2-3 similar implementations in the codebase:

```bash
# Find similar route patterns
grep -r "@.*_bp.route" routes/

# Find similar functions
grep -r "def fetch_" src/

# Find similar tests
grep -r "def test_" tests/
```

Document findings:
```markdown
## Similar Implementations Found
1. `/routes/stats.py::get_daily_stats()` - Similar data aggregation
2. `/src/cache_manager.py::get_cached_data()` - Similar caching pattern
3. `/tests/integration/test_api.py::test_get_products()` - Similar test structure
```

#### 3. Architecture Documentation

Map the changes:

```markdown
## Affected Layers

### API Layer
- Route: `/api/export/products`
- Blueprint: `system_bp` in `/routes/system.py`
- Method: GET
- Response: CSV file download

### Business Logic Layer
- Module: `/src/utils.py`
- Function: `generate_csv(data, fields)`
- Purpose: Convert list of dicts to CSV string

### Database Layer
- Function: `fetch_all_products()`
- Query: `SELECT * FROM products ORDER BY name`

### Integration Points
- Uses existing `get_db()` for database access
- Uses existing `json_response()` pattern (adapted for CSV)
- No caching needed (export is one-time operation)
```

#### 4. Task Decomposition

Break into atomic steps:

```markdown
## Implementation Steps

1. [ ] Add CSV generation helper to src/utils.py (30 min)
2. [ ] Add export endpoint to routes/system.py (20 min)
3. [ ] Write unit tests for CSV generation (30 min)
4. [ ] Write integration tests for export endpoint (30 min)
5. [ ] Add frontend button and click handler (20 min)
6. [ ] Test manually with browser (15 min)
7. [ ] Update documentation (15 min)

Total estimate: 2.5 hours
```

#### 5. Risk Identification

List potential issues:

```markdown
## Risks and Edge Cases

### Memory Issues
- **Risk**: Large datasets (10,000+ rows) may cause memory issues
- **Mitigation**: Use streaming response or pagination

### Security
- **Risk**: Unauthenticated users could export data
- **Mitigation**: Add `@require_auth` decorator

### Performance
- **Risk**: Export query may be slow for large datasets
- **Mitigation**: Add database index on frequently filtered columns

### Edge Cases
- Empty dataset
- Special characters in product names (quotes, commas)
- Very long text fields
- Null values in optional fields
```

#### 6. Test Strategy

Plan what to test:

```markdown
## Test Strategy

### Unit Tests (tests/unit/test_utils.py)
- CSV generation with various data types
- Special character handling
- Empty dataset handling
- Field quoting and escaping

### Integration Tests (tests/integration/test_api_extended.py)
- Export endpoint returns correct status codes
- CSV format validation
- HTTP headers validation
- Authentication required

### Manual Tests
- Download CSV in browser
- Open in Excel/Google Sheets
- Verify all fields present
- Test with 100+ products
```

#### Planning Checklist

- [ ] Fully understand the scope
- [ ] Found 2-3 similar patterns in codebase
- [ ] Identified all files to modify
- [ ] Documented dependencies
- [ ] Broken down into small steps (<1 hour each)
- [ ] Identified risks and edge cases
- [ ] Planned comprehensive testing
- [ ] Estimated <8 hours total

### DO Phase: Implementation

#### 1. Test-Driven Development (TDD)

**Always write tests first:**

```python
# Step 1: Write failing test (RED)
def test_generate_csv_with_products():
    """Test CSV generation from product list"""
    products = [
        {"id": 1, "name": "Apple", "calories": 52},
        {"id": 2, "name": "Banana", "calories": 89}
    ]
    
    csv_output = generate_csv(products, ["id", "name", "calories"])
    
    assert "id,name,calories" in csv_output
    assert "1,Apple,52" in csv_output
    assert "2,Banana,89" in csv_output

# Step 2: Run test (should fail)
$ pytest tests/unit/test_utils.py::test_generate_csv_with_products -v
# FAILED - NameError: name 'generate_csv' is not defined

# Step 3: Implement minimal code (GREEN)
def generate_csv(data, fields):
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()

# Step 4: Run test (should pass)
$ pytest tests/unit/test_utils.py::test_generate_csv_with_products -v
# PASSED

# Step 5: Refactor if needed (keep tests green)
```

#### 2. Incremental Development

Work in small batches (30-90 minutes):

**Batch 1: Core functionality**
- Write tests for CSV generation
- Implement CSV generation helper
- Verify tests pass

**Batch 2: API endpoint**
- Write tests for export endpoint
- Implement export route
- Verify tests pass

**Batch 3: Frontend integration**
- Add export button
- Add click handler
- Manual testing

**Batch 4: Documentation and polish**
- Update README
- Add code comments
- Final testing

#### 3. Code Quality Standards

Follow project conventions:

```python
# Good - Follows conventions
def generate_csv(data: list, fields: list) -> str:
    """
    Generate CSV string from list of dictionaries.
    
    Args:
        data: List of dictionaries to convert
        fields: List of field names to include in CSV
        
    Returns:
        CSV formatted string
        
    Example:
        >>> data = [{"name": "Apple", "calories": 52}]
        >>> generate_csv(data, ["name", "calories"])
        'name,calories\\nApple,52\\n'
    """
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()

# Bad - Lacks documentation, type hints
def gen_csv(d, f):
    import csv, io
    o = io.StringIO()
    w = csv.DictWriter(o, fieldnames=f)
    w.writeheader()
    w.writerows(d)
    return o.getvalue()
```

#### 4. Version Control Best Practices

**Branch naming:**
```bash
feature/PROJ-123-add-csv-export
bugfix/PROJ-456-fix-fasting-timer
refactor/improve-caching
docs/update-api-documentation
```

**Commit messages:**
```bash
feat(system): add CSV export functionality

- Add generate_csv() helper to src/utils.py
- Add /api/export/products endpoint
- Add /api/export/dishes endpoint
- Include comprehensive tests
- Update API documentation

Closes #123
```

**Commit format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

#### 5. Progressive Testing

Test continuously:

```bash
# After each function
pytest tests/unit/test_utils.py::test_generate_csv -v

# After each endpoint
pytest tests/integration/test_api_extended.py::test_export_products -v

# Before committing
pytest tests/ -v

# Check coverage
pytest tests/ --cov=src --cov-report=term-missing
```

### CHECK Phase: Validation and Review

#### 1. Test Execution

Run complete test suite:

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Expected: >80% coverage, all tests pass
```

#### 2. Code Quality Checks

```bash
# Linting
flake8 src/ app.py routes/ --max-line-length=100 --ignore=E501,W503,E226

# Formatting
black --check src/ app.py routes/
isort --check-only src/ app.py routes/

# Type checking
mypy src/ --ignore-missing-imports

# Security scan
bandit -r src/ app.py routes/ -ll
```

#### 3. Security Review

Check for:
- [ ] No SQL injection vulnerabilities (use parameterized queries)
- [ ] Input validation on all endpoints
- [ ] No sensitive data in logs
- [ ] Authentication/authorization properly implemented
- [ ] No hardcoded secrets

#### 4. Performance Validation

```bash
# Profile critical paths
python -m cProfile -o profile.stats app.py

# Check query efficiency
# Use EXPLAIN QUERY PLAN in SQLite

# Test with realistic data
# Create 1000+ test products and measure export time
```

#### 5. Documentation Review

- [ ] Updated API documentation (docstrings)
- [ ] Added code comments for complex logic
- [ ] Updated README.md if user-facing
- [ ] Updated CHANGELOG.md
- [ ] Created/updated ADRs if needed

#### 6. Acceptance Criteria Verification

Review each criterion from the issue:

```markdown
## Acceptance Criteria Review
- [x] Add "Export to CSV" button on each major page
- [x] Clicking button downloads CSV file with proper formatting
- [x] CSV includes all relevant fields for each data type
- [x] File naming follows pattern: `nutricount_<type>_<date>.csv`
- [x] Export works for datasets with 1000+ rows
- [x] Tests pass with >80% coverage (Current: 92%)
- [x] Documentation updated with export instructions
```

#### Validation Checklist

- [ ] All tests pass locally and in CI
- [ ] Coverage meets requirements (>80%)
- [ ] Linter passes with no errors
- [ ] Type checking passes
- [ ] Security scan passes
- [ ] Performance acceptable
- [ ] Documentation up to date
- [ ] All acceptance criteria met
- [ ] Edge cases tested
- [ ] Error scenarios handled

### ACT Phase: Retrospective and Improvement

#### 1. Micro-Retrospective (5-10 minutes)

**What Went Well:**
- TDD approach caught edge cases early
- Found similar pattern in stats.py that saved time
- Tests were comprehensive and caught a bug

**What Could Be Improved:**
- Initial estimate was too optimistic (took 3.5 hours instead of 2.5)
- Didn't account for special character handling in CSV
- Could have used streaming response for large datasets

**What to Do Differently Next Time:**
- Add 30% buffer to estimates
- Review CSV RFC 4180 spec before implementing
- Consider scalability earlier in planning phase

#### 2. Learning Documentation

Update project documentation with learnings:

```markdown
## New Patterns Added

### CSV Export Pattern
Location: `/src/utils.py::generate_csv()`

Usage:
\```python
from src.utils import generate_csv

data = [{"name": "Apple", "calories": 52}]
fields = ["name", "calories"]
csv_string = generate_csv(data, fields)
\```

Notes:
- Automatically handles special characters
- Includes proper header row
- Compatible with Excel and Google Sheets
- For datasets >1000 rows, consider streaming
```

#### 3. Process Refinement

Suggest improvements:

```markdown
## Process Improvements

### Estimation
- Add 30% buffer for unknowns
- Account for testing time (usually 40% of development)
- Include documentation time

### Testing
- Always write tests first (TDD)
- Test edge cases early
- Include performance tests for data operations

### Documentation
- Update docs in same commit as code
- Include examples in docstrings
- Add troubleshooting section for common issues
```

---

## Quality Metrics and Monitoring

### Commit Quality Metrics

**Target Metrics:**
- Large commits (>100 lines): <20%
- Sprawling commits (>5 files): <10%
- Average lines per commit: <100
- Average files per commit: <5
- Test-first commits: >50%

**Check your commits:**
```bash
# Lines changed in last commit
git show --stat

# Files changed in last commit
git show --name-only

# Should be small, focused changes
```

### Code Quality Metrics

**Current Project Stats:**
- Overall Coverage: 93% ✅ (target: >80%)
- Critical Path Coverage: 95%+ ✅
- New Code Coverage: Target >90%
- Total Tests: 567 ✅

**Check coverage:**
```bash
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

**Target Metrics:**
- Cyclomatic Complexity: <10 per function
- Max Function Length: <50 lines
- Max File Length: <500 lines
- Nesting Depth: Max 4 levels
- Code Duplication: <5%
- Dead Code: Zero commented blocks

### Build and CI Metrics

**Target Metrics:**
- Build Success Rate: >95%
- Test Success Rate: >98%
- Average Build Time: <10 minutes
- Flaky Test Rate: <1%
- Critical Vulnerabilities: Zero
- High Vulnerabilities: Fix within 7 days

**Check CI status:**
```bash
# View workflow runs
gh run list

# View specific run
gh run view <run-id>
```

### Performance Metrics

**Backend Targets:**
- API Response p50: <200ms
- API Response p95: <500ms
- Database Query: <100ms
- Error Rate: <0.1%

**Test performance:**
```bash
# Use locust for load testing
locust -f locustfile.py --host=http://localhost:5000
```

---

## Code Review Guidelines

### For Authors

**Before requesting review:**
- [ ] All tests pass
- [ ] Coverage >80%
- [ ] Linting passes
- [ ] Security scan clean
- [ ] Documentation updated
- [ ] Self-reviewed code
- [ ] Commits are small and logical

**PR Description should include:**
- Clear summary of changes
- Why changes were made
- How to test
- Screenshots (if UI changes)
- Migration notes (if breaking changes)

### For Reviewers

**Check for:**
- [ ] Functionality works as described
- [ ] All acceptance criteria met
- [ ] Code follows style guide
- [ ] No code duplication
- [ ] Complex logic is commented
- [ ] No commented-out code
- [ ] Tests are meaningful and pass
- [ ] Edge cases covered
- [ ] No security vulnerabilities
- [ ] Performance is acceptable
- [ ] Documentation updated

**Review checklist:**
```markdown
## Code Review Checklist

### Functionality
- [ ] All acceptance criteria met
- [ ] Feature works as described
- [ ] Edge cases handled
- [ ] No regressions

### Code Quality
- [ ] Follows style guide
- [ ] Functions are small and focused
- [ ] No duplication
- [ ] Well-documented

### Testing
- [ ] Tests pass
- [ ] Coverage >80%
- [ ] Meaningful tests
- [ ] Edge cases tested

### Security
- [ ] No vulnerabilities
- [ ] Input validated
- [ ] No secrets in code
- [ ] Proper auth/authz

### Performance
- [ ] No obvious issues
- [ ] Queries optimized
- [ ] Appropriate caching

### Documentation
- [ ] Code documented
- [ ] README updated
- [ ] API docs updated
```

---

## Quick Reference

### Common Commands

```bash
# Setup
export PYTHONPATH=$(pwd)
pip install -r requirements-minimal.txt
mkdir -p logs

# Testing
pytest tests/ -v                          # All tests
pytest tests/unit/ -v                     # Unit only
pytest tests/ --cov=src --cov-report=html # With coverage

# Linting
flake8 src/ app.py routes/ --max-line-length=100 --ignore=E501,W503,E226
black src/ app.py routes/                 # Format
isort src/ app.py routes/                 # Sort imports

# Security
bandit -r src/ app.py routes/ -ll

# Running
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

### File Locations Quick Reference

```
/app.py                     - Main Flask application
/src/*.py                   - Core business logic
/routes/*.py                - API endpoints
/tests/unit/*.py            - Unit tests
/tests/integration/*.py     - Integration tests
/tests/e2e/*.py             - E2E tests
/.github/copilot-instructions.md          - Main instructions
/.github/instructions/*.instructions.md   - Path-specific instructions
```

---

**Remember**: Quality over speed. Take time to plan, test thoroughly, and document well.
