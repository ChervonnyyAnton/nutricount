#!/usr/bin/env python3
"""
Basic tests for Nutrition Tracker
"""

import os
import sys
import tempfile
import pytest

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, get_db, init_db
import app as app_module


@pytest.fixture
def client():
    """Create a test client"""
    import tempfile
    import os
    
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    # Configure app for testing
    app.config['DATABASE'] = db_path
    app.config['TESTING'] = True

    # Clear cache before each test
    app_module._cache.clear()

    # Initialize database
    with app.app_context():
        init_db()

    with app.test_client() as client:
        yield client
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


def test_health_endpoint(client):
    """Test health endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'timestamp' in data
    assert 'version' in data


def test_index_page(client):
    """Test main page loads"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Nutrition Tracker' in response.data


def test_products_api(client):
    """Test products API endpoint"""
    response = client.get('/api/products')
    assert response.status_code == 200
    data = response.get_json()
    assert 'data' in data
    assert isinstance(data['data'], list)


def test_stats_api(client):
    """Test stats API endpoint"""
    response = client.get('/api/stats/2025-01-01')
    assert response.status_code == 200
    data = response.get_json()
    assert 'data' in data


def test_database_connection(client):
    """Test database connection"""
    with app.app_context():
        db = get_db()
        assert db is not None

        # Test basic query
        cursor = db.execute('SELECT COUNT(*) FROM products')
        count = cursor.fetchone()[0]
        assert count >= 0

        db.close()


def test_create_product(client):
    """Test product creation"""
    product_data = {
        'name': 'Test Product',
        'protein_per_100g': 20.0,
        'fat_per_100g': 10.0,
        'carbs_per_100g': 5.0,
        'category': 'meat',  # Use valid category
        'processing_level': 'raw'  # Use valid processing level
    }
    
    response = client.post('/api/products', json=product_data)
    assert response.status_code == 201
    
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'data' in data
    assert data['data']['name'] == 'Test Product'


def test_invalid_product_data(client):
    """Test product creation with invalid data"""
    invalid_data = {
        'name': '',  # Empty name should fail
        'protein_per_100g': -1,  # Negative protein should fail
    }
    
    response = client.post('/api/products', json=invalid_data)
    assert response.status_code == 400


def test_log_food_entry(client):
    """Test food logging"""
    # First create a product
    product_data = {
        'name': 'Test Food',
        'protein_per_100g': 15.0,
        'fat_per_100g': 8.0,
        'carbs_per_100g': 3.0,
        'category': 'meat',  # Use valid category
        'processing_level': 'raw'  # Use valid processing level
    }
    response = client.post('/api/products', json=product_data)
    assert response.status_code == 201
    product_result = response.get_json()
    product_id = product_result['data']['id']
    
    # Then log it
    log_data = {
        'date': '2025-01-01',
        'meal_type': 'breakfast',
        'item_type': 'product',
        'item_id': product_id,
        'quantity_grams': 100  # Use correct field name
    }
    
    response = client.post('/api/log', json=log_data)
    assert response.status_code == 201
    
    data = response.get_json()
    assert data['status'] == 'success'


def test_api_error_handling(client):
    """Test API error handling"""
    # Test non-existent endpoint
    response = client.get('/api/nonexistent')
    assert response.status_code == 404
    
    # Test invalid JSON - expect 500 for malformed JSON
    response = client.post('/api/products', 
                          data='invalid json',
                          content_type='application/json')
    assert response.status_code == 500


if __name__ == '__main__':
    pytest.main([__file__])
