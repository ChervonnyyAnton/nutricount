# Integration and E2E Test Instructions

**Applies to**: `**/integration/**/*.py`, `**/e2e/**/*.py`

## Integration Test Requirements

### Use Real Test Databases

```python
@pytest.fixture
def app():
    """Create test app with in-memory database"""
    os.environ['DATABASE'] = ':memory:'
    test_app = create_app()
    with test_app.app_context():
        init_db()
        yield test_app
```

### Setup and Teardown

Use setup/teardown patterns with pytest fixtures:

```python
@pytest.fixture(autouse=True)
def setup_teardown(app):
    # Setup
    with app.app_context():
        db = get_db()
        insert_test_data(db)
    
    yield
    
    # Teardown
    with app.app_context():
        db = get_db()
        db.execute("DELETE FROM products")
        db.commit()
```

### Transaction Rollback

Use transactions for cleanup:

```python
@pytest.fixture
def db_transaction(app):
    with app.app_context():
        db = get_db()
        db.execute("BEGIN")
        yield db
        db.execute("ROLLBACK")
```

### Mock External Services

Mock Redis and Celery, but use real SQLite:

```python
@patch('src.cache_manager.redis', None)  # Force fallback
def test_api_works_without_redis(client):
    response = client.get('/api/products')
    assert response.status_code == 200
```

### Test Complete Flows

```python
def test_complete_product_lifecycle(client, app):
    """Test create, read, update, delete flow"""
    # Create
    response = client.post('/api/products', json={
        'name': 'Test Product',
        'calories': 100
    })
    assert response.status_code == 200
    product_id = response.json['id']
    
    # Read
    response = client.get(f'/api/products/{product_id}')
    assert response.json['name'] == 'Test Product'
    
    # Update
    response = client.put(f'/api/products/{product_id}', json={
        'name': 'Updated Product'
    })
    assert response.status_code == 200
    
    # Delete
    response = client.delete(f'/api/products/{product_id}')
    assert response.status_code == 200
```

## E2E Test Requirements

### Stable Locators

Prefer semantic selectors:
- **Good**: `page.get_by_role('button', name='Submit')`
- **Good**: `page.get_by_label('Product Name')`
- **Acceptable**: `page.get_by_test_id('submit-button')`
- **Avoid**: CSS selectors, XPath

### Proper Async Handling

```python
# Wait for elements
await page.wait_for_selector('[data-testid="product-list"]')

# Wait for API responses
async with page.expect_response('**/api/products') as response_info:
    await page.click('button[name="refresh"]')
    response = await response_info.value

# Avoid hardcoded waits
# BAD: await page.wait_for_timeout(1000)
```

### Test Data Management

Each test creates its own data:

```python
async def test_create_product(page, app):
    # Create unique test data
    product_name = f"Test Product {uuid.uuid4()}"
    
    await page.fill('[name="name"]', product_name)
    await page.fill('[name="calories"]', '100')
    await page.click('button[type="submit"]')
    
    # Verify
    await page.wait_for_selector(f'text={product_name}')
```

### Cleanup After Tests

```python
@pytest.fixture(autouse=True)
async def cleanup(app):
    yield
    # Clean up test data
    with app.app_context():
        db = get_db()
        db.execute("DELETE FROM products WHERE name LIKE 'Test Product%'")
        db.commit()
```

### Screenshots on Failure

Configure in `playwright.config.js`:

```javascript
use: {
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'on-first-retry',
}
```

### Cross-Browser Testing

Test on major browsers:

```python
@pytest.mark.parametrize('browser_name', ['chromium', 'firefox', 'webkit'])
async def test_cross_browser(browser_name, app):
    # Test will run on all browsers
    pass
```

## Quick Checklist

- [ ] Use real test database (in-memory SQLite)
- [ ] Setup/teardown in fixtures
- [ ] Mock external services (Redis, Celery)
- [ ] Test complete user journeys
- [ ] Use stable locators (getByRole, getByLabel)
- [ ] Proper async handling (no hardcoded waits)
- [ ] Each test creates own data
- [ ] Cleanup after tests
- [ ] Screenshots on failure
- [ ] Tests pass: `pytest tests/integration/ tests/e2e/ -v`
