#!/usr/bin/env python3
"""
Basic tests for Nutrition Tracker
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test health endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'

def test_products_api(client):
    """Test products API"""
    response = client.get('/api/products')
    assert response.status_code == 200
    data = response.get_json()
    assert 'data' in data
    assert isinstance(data['data'], list)

def test_stats_api(client):
    """Test stats API"""
    response = client.get('/api/stats/2025-01-01')
    assert response.status_code == 200
    data = response.get_json()
    assert 'data' in data

def test_main_page(client):
    """Test main page loads"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Nutrition Tracker' in response.data

def test_create_product(client):
    """Test product creation"""
    product_data = {
        'name': 'Test Product',
        'calories_per_100g': 100,
        'protein_per_100g': 10,
        'fat_per_100g': 5,
        'carbs_per_100g': 20,
        'fiber_per_100g': 0,
        'sugars_per_100g': 0,
        'category': 'berries',
        'processing_level': 'raw',
        'glycemic_index': 0,
        'region': 'US'
    }
    
    response = client.post('/api/products', 
                          json=product_data,
                          content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['data']['name'] == 'Test Product'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
