# Unit Test Instructions

**Applies to**: `**/*.test.py`, `**/test_*.py` in `/tests/unit/` directory

## Unit Test Requirements

### Follow AAA Pattern (Arrange-Act-Assert)

All unit tests must follow the AAA pattern for clarity and maintainability:

```python
def test_validate_input_with_missing_required_field(app):
    """Test that validation fails when a required field is missing"""
    # Arrange - Set up test data and preconditions
    data = {"name": "Test Product"}
    required_fields = ["name", "calories"]
    
    # Act - Execute the function being tested
    is_valid, error = validate_input(data, required_fields)
    
    # Assert - Verify the expected outcome
    assert is_valid is False
    assert "calories" in error.lower()
```

### Test Naming Convention

Use descriptive names following the pattern:
**`test_<function>_<scenario>_<expected_outcome>`**

Examples:
- `test_validate_input_with_valid_data_returns_true`
- `test_create_product_with_missing_calories_returns_error`
- `test_start_fasting_when_already_active_returns_error`
- `test_cache_get_with_expired_key_returns_none`

### Mock All External Dependencies

**Always mock**:
- Database connections
- API calls
- File system access
- Time/date functions
- External services (Redis, Celery)

```python
from unittest.mock import patch, MagicMock

@patch('src.cache_manager.redis')
def test_cache_get_from_redis(mock_redis, app):
    mock_redis.get.return_value = b'cached_value'
    result = cache_manager.get('test_key')
    assert result == 'cached_value'
```

### Tests Must Be Independent

No shared state between tests. Use fixtures for setup:

```python
@pytest.fixture
def sample_product():
    return {"name": "Test", "calories": 100}

def test_with_fixture(sample_product):
    assert sample_product["calories"] == 100
```

### Coverage >80%

Run: `pytest tests/unit/ --cov=src --cov-report=html`
