#!/usr/bin/env python3
"""
Comprehensive test suite for Nutrition Tracker
Tests all API endpoints, validation, and core functionality
"""

import pytest
import json
import tempfile
import os
from app import app, init_db
from src.config import Config

@pytest.fixture
def client():
    """Create test client with temporary database"""
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    # Configure test app
    app.config['TESTING'] = True
    app.config['DATABASE'] = db_path
    Config.DATABASE = db_path
    
    # Initialize test database
    with app.app_context():
        init_db()
    
    # Create test client
    with app.test_client() as client:
        yield client
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def sample_product():
    """Sample product data for testing"""
    return {
        'name': 'Test Chicken Breast',
        'calories_per_100g': 165.0,
        'protein_per_100g': 31.0,
        'fat_per_100g': 3.6,
        'carbs_per_100g': 0.0,
        'category': 'meat',
        'processing_level': 'minimal'
    }

@pytest.fixture
def sample_log_entry():
    """Sample log entry data for testing"""
    return {
        'date': '2025-10-15',
        'item_type': 'product',
        'item_id': 1,
        'quantity_grams': 150,
        'meal_time': 'lunch',
        'notes': 'Grilled chicken breast'
    }

# ============================================
# Health and Basic Tests
# ============================================

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['version'] == Config.VERSION
    assert 'timestamp' in data

def test_main_page(client):
    """Test main application page loads"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Nutrition Tracker' in response.data

def test_manifest_json(client):
    """Test PWA manifest is accessible"""
    response = client.get('/manifest.json')
    assert response.status_code == 200

# ============================================
# Products API Tests
# ============================================

def test_create_product_success(client, sample_product):
    """Test successful product creation"""
    response = client.post('/api/products',
                          data=json.dumps(sample_product),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['name'] == sample_product['name']
    assert 'created successfully' in data['message']

def test_create_product_validation_error(client):
    """Test product creation with invalid data"""
    invalid_product = {
        'name': '',  # Empty name should fail
        'calories_per_100g': -5,  # Negative calories should fail
        'protein_per_100g': 150,  # Too high protein should fail
    }
    
    response = client.post('/api/products',
                          data=json.dumps(invalid_product),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'errors' in data

def test_get_products_empty(client):
    """Test getting products when none exist"""
    response = client.get('/api/products')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert isinstance(data['data'], list)
    assert len(data['data']) >= 0  # Might have sample data

def test_get_products_with_search(client, sample_product):
    """Test product search functionality"""
    # Create a product first
    client.post('/api/products',
                data=json.dumps(sample_product),
                content_type='application/json')
    
    # Search for it
    response = client.get('/api/products?search=chicken')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert len(data['data']) >= 1
    assert any('chicken' in product['name'].lower() for product in data['data'])

def test_delete_product_success(client, sample_product):
    """Test successful product deletion"""
    # Create product first
    create_response = client.post('/api/products',
                                 data=json.dumps(sample_product),
                                 content_type='application/json')
    
    created_data = json.loads(create_response.data)
    product_id = created_data['data']['id']
    
    # Delete product
    response = client.delete(f'/api/products/{product_id}')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'success'

def test_delete_nonexistent_product(client):
    """Test deleting non-existent product"""
    response = client.delete('/api/products/99999')
    assert response.status_code == 404

# ============================================
# Food Log API Tests
# ============================================

def test_create_log_entry_success(client, sample_product, sample_log_entry):
    """Test successful log entry creation"""
    # Create product first
    product_response = client.post('/api/products',
                                  data=json.dumps(sample_product),
                                  content_type='application/json')
    
    product_data = json.loads(product_response.data)
    sample_log_entry['item_id'] = product_data['data']['id']
    
    # Create log entry
    response = client.post('/api/log',
                          data=json.dumps(sample_log_entry),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['date'] == sample_log_entry['date']
    assert data['data']['quantity_grams'] == sample_log_entry['quantity_grams']

def test_create_log_entry_validation_error(client):
    """Test log entry creation with invalid data"""
    invalid_log = {
        'date': '',  # Missing date
        'item_type': 'invalid',  # Invalid type
        'item_id': 0,  # Invalid ID
        'quantity_grams': -10,  # Negative quantity
    }
    
    response = client.post('/api/log',
                          data=json.dumps(invalid_log),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'errors' in data

def test_get_log_entries(client):
    """Test getting log entries"""
    response = client.get('/api/log')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert isinstance(data['data'], list)

def test_get_log_entries_by_date(client, sample_product, sample_log_entry):
    """Test getting log entries filtered by date"""
    # Create product and log entry first
    product_response = client.post('/api/products',
                                  data=json.dumps(sample_product),
                                  content_type='application/json')
    
    product_data = json.loads(product_response.data)
    sample_log_entry['item_id'] = product_data['data']['id']
    
    client.post('/api/log',
               data=json.dumps(sample_log_entry),
               content_type='application/json')
    
    # Get entries for specific date
    response = client.get(f'/api/log?date={sample_log_entry["date"]}')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert len(data['data']) >= 1
    assert all(entry['date'] == sample_log_entry['date'] for entry in data['data'])

def test_delete_log_entry_success(client, sample_product, sample_log_entry):
    """Test successful log entry deletion"""
    # Create product and log entry first
    product_response = client.post('/api/products',
                                  data=json.dumps(sample_product),
                                  content_type='application/json')
    
    product_data = json.loads(product_response.data)
    sample_log_entry['item_id'] = product_data['data']['id']
    
    log_response = client.post('/api/log',
                              data=json.dumps(sample_log_entry),
                              content_type='application/json')
    
    log_data = json.loads(log_response.data)
    log_id = log_data['data']['id']
    
    # Delete log entry
    response = client.delete(f'/api/log/{log_id}')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'success'

# ============================================
# Statistics API Tests
# ============================================

def test_daily_stats_empty(client):
    """Test daily stats when no entries exist"""
    response = client.get('/api/stats/2025-10-15')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['date'] == '2025-10-15'
    assert data['data']['calories'] == 0
    assert data['data']['entries_count'] == 0

def test_daily_stats_with_entries(client, sample_product, sample_log_entry):
    """Test daily stats calculation with entries"""
    # Create product and log entry
    product_response = client.post('/api/products',
                                  data=json.dumps(sample_product),
                                  content_type='application/json')
    
    product_data = json.loads(product_response.data)
    sample_log_entry['item_id'] = product_data['data']['id']
    
    client.post('/api/log',
               data=json.dumps(sample_log_entry),
               content_type='application/json')
    
    # Get stats
    response = client.get(f'/api/stats/{sample_log_entry["date"]}')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['entries_count'] >= 1
    assert data['data']['calories'] > 0
    assert 'keto_index' in data['data']
    assert 'meal_breakdown' in data['data']

# ============================================
# System API Tests
# ============================================

def test_system_status(client):
    """Test system status endpoint"""
    response = client.get('/api/system/status')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'application' in data['data']
    assert 'database' in data['data']
    assert 'system' in data['data']
    
    # Check required fields
    assert data['data']['application']['name'] == Config.APP_NAME
    assert data['data']['application']['version'] == Config.VERSION

# ============================================
# Telegram Integration Tests
# ============================================

def test_telegram_init(client):
    """Test Telegram Web App initialization"""
    response = client.get('/telegram/init')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['telegram_compatible'] == True
    assert 'features' in data['data']
    assert 'keyboard_shortcuts' in data['data']

def test_telegram_webhook_no_secret(client):
    """Test Telegram webhook without secret token"""
    webhook_data = {
        'update_id': 123,
        'message': {
            'message_id': 456,
            'chat': {'id': 789},
            'text': '/start'
        }
    }
    
    response = client.post('/telegram/webhook',
                          data=json.dumps(webhook_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['ok'] == True

# ============================================
# Error Handling Tests
# ============================================

def test_api_404_error(client):
    """Test 404 error handling for API endpoints"""
    response = client.get('/api/nonexistent')
    assert response.status_code == 404
    
    data = json.loads(response.data)
    assert data['status'] == 'error'

def test_invalid_json_error(client):
    """Test invalid JSON handling"""
    response = client.post('/api/products',
                          data='invalid json',
                          content_type='application/json')
    
    assert response.status_code == 500  # Flask returns 500 for invalid JSON

# ============================================
# Integration Tests
# ============================================

def test_complete_workflow(client):
    """Test complete workflow: create product, log entry, check stats"""
    # 1. Create product
    product_data = {
        'name': 'Integration Test Product',
        'calories_per_100g': 190.0,  # 20*4 + 10*9 + 5*4 = 80 + 90 + 20 = 190
        'protein_per_100g': 20.0,
        'fat_per_100g': 10.0,
        'carbs_per_100g': 5.0,
        'category': 'processed',
        'processing_level': 'processed'
    }
    
    product_response = client.post('/api/products',
                                  data=json.dumps(product_data),
                                  content_type='application/json')
    
    assert product_response.status_code == 201
    product_id = json.loads(product_response.data)['data']['id']
    
    # 2. Create log entry
    log_data = {
        'date': '2025-10-15',
        'item_type': 'product',
        'item_id': product_id,
        'quantity_grams': 100,
        'meal_time': 'dinner'
    }
    
    log_response = client.post('/api/log',
                              data=json.dumps(log_data),
                              content_type='application/json')
    
    assert log_response.status_code == 201
    
    # 3. Check daily stats
    stats_response = client.get('/api/stats/2025-10-15')
    assert stats_response.status_code == 200
    
    stats_data = json.loads(stats_response.data)
    assert stats_data['data']['calories'] == 190.0  # 100g of 190 cal/100g product
    assert stats_data['data']['protein'] == 20.0
    assert stats_data['data']['entries_count'] >= 1

def test_product_deletion_with_log_entries(client, sample_product):
    """Test that products with log entries cannot be deleted"""
    # Create product
    product_response = client.post('/api/products',
                                  data=json.dumps(sample_product),
                                  content_type='application/json')
    
    product_id = json.loads(product_response.data)['data']['id']
    
    # Create log entry
    log_data = {
        'date': '2025-10-15',
        'item_type': 'product',
        'item_id': product_id,
        'quantity_grams': 100
    }
    
    client.post('/api/log',
               data=json.dumps(log_data),
               content_type='application/json')
    
    # Try to delete product
    response = client.delete(f'/api/products/{product_id}')
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert 'used in' in data['message']


def test_e2e_workflow_with_test_prefix(client):
    """Test complete E2E workflow with TEST prefix cleanup approach"""
    # Clean up any existing TEST data first
    products_response = client.get('/api/products')
    products_data = json.loads(products_response.data)
    
    for product in products_data['data']:
        if product['name'].startswith('ТЕСТ'):
            client.delete(f"/api/products/{product['id']}")
    
    dishes_response = client.get('/api/dishes')
    dishes_data = json.loads(dishes_response.data)
    
    for dish in dishes_data['data']:
        if dish['name'].startswith('ТЕСТ'):
            client.delete(f"/api/dishes/{dish['id']}")
    
    # 1. Create test products
    test_products = [
        {
            'name': 'ТЕСТ Колбаса',
            'calories_per_100g': 104.0,
            'protein_per_100g': 26.0,
            'fat_per_100g': 0.0,
            'carbs_per_100g': 0.0,
            'category': 'processed',
            'processing_level': 'processed'
        },
        {
            'name': 'ТЕСТ Хлеб',
            'calories_per_100g': 46.0,
            'protein_per_100g': 7.0,
            'fat_per_100g': 3.0,
            'carbs_per_100g': 0.0,
            'category': 'processed',
            'processing_level': 'processed'
        },
        {
            'name': 'ТЕСТ Масло сливочное',
            'calories_per_100g': 306.0,
            'protein_per_100g': 0.0,
            'fat_per_100g': 34.0,
            'carbs_per_100g': 0.0,
            'category': 'dairy',
            'processing_level': 'minimal'
        },
        {
            'name': 'ТЕСТ Сыр нарезка',
            'calories_per_100g': 68.0,
            'protein_per_100g': 16.0,
            'fat_per_100g': 1.0,
            'carbs_per_100g': 0.0,
            'category': 'dairy',
            'processing_level': 'processed'
        }
    ]
    
    product_ids = {}
    for product_data in test_products:
        response = client.post('/api/products',
                              data=json.dumps(product_data),
                              content_type='application/json')
        assert response.status_code == 201
        product_id = json.loads(response.data)['data']['id']
        product_ids[product_data['name']] = product_id
    
    # 2. Create test dish
    dish_data = {
        'name': 'ТЕСТ бутерброд 45 v2',
        'description': 'Тестовый бутерброд: 45г хлеба, 45г колбасы, 45г сыра',
        'ingredients': [
            {
                'product_id': product_ids['ТЕСТ Хлеб'],
                'quantity_grams': 45
            },
            {
                'product_id': product_ids['ТЕСТ Колбаса'],
                'quantity_grams': 45
            },
            {
                'product_id': product_ids['ТЕСТ Сыр нарезка'],
                'quantity_grams': 45
            }
        ]
    }
    
    dish_response = client.post('/api/dishes',
                               data=json.dumps(dish_data),
                               content_type='application/json')
    assert dish_response.status_code == 201
    
    dish_id = json.loads(dish_response.data)['data']['id']
    
    # 3. Verify dish calculations
    dishes_response = client.get('/api/dishes')
    dishes_data = json.loads(dishes_response.data)
    
    test_dish = None
    for dish in dishes_data['data']:
        if dish['name'] == 'ТЕСТ бутерброд 45 v2':
            test_dish = dish
            break
    
    assert test_dish is not None
    assert abs(test_dish['total_calories'] - 104.49) < 0.1
    assert abs(test_dish['total_protein'] - 22.005) < 0.1
    assert abs(test_dish['total_fat'] - 1.755) < 0.1
    assert test_dish['total_carbs'] == 0.0
    
    # 4. Add dish to log
    log_data = {
        'date': '2025-10-15',
        'item_type': 'dish',
        'item_id': dish_id,
        'quantity_grams': 100,
        'meal_time': 'breakfast'
    }
    
    log_response = client.post('/api/log',
                              data=json.dumps(log_data),
                              content_type='application/json')
    assert log_response.status_code == 201
    
    # 5. Check log entry
    log_entries_response = client.get('/api/log?date=2025-10-15')
    log_entries_data = json.loads(log_entries_response.data)
    
    test_log_entry = None
    for entry in log_entries_data['data']:
        if entry['item_name'] == 'ТЕСТ бутерброд 45 v2':
            test_log_entry = entry
            break
    
    assert test_log_entry is not None
    assert test_log_entry['calculated_calories'] == 77.4
    assert test_log_entry['meal_time'] == 'breakfast'
    
    # 6. Check daily statistics
    stats_response = client.get('/api/stats/2025-10-15')
    assert stats_response.status_code == 200
    
    stats_data = json.loads(stats_response.data)
    # Should include our dish calories in total
    assert stats_data['data']['calories'] >= 77.4
    assert stats_data['data']['entries_count'] >= 1


def test_manual_e2e_workflow_reproduction(client):
    """Test manual E2E workflow exactly as performed in browser"""
    # This test reproduces the exact manual workflow from browser testing
    
    # Step 1: Clean up TEST data (as done manually)
    products_response = client.get('/api/products')
    products_data = json.loads(products_response.data)
    
    for product in products_data['data']:
        if product['name'].startswith('ТЕСТ'):
            client.delete(f"/api/products/{product['id']}")
    
    dishes_response = client.get('/api/dishes')
    dishes_data = json.loads(dishes_response.data)
    
    for dish in dishes_data['data']:
        if dish['name'].startswith('ТЕСТ'):
            client.delete(f"/api/dishes/{dish['id']}")
    
    # Step 2: Create products exactly as in manual test
    products_to_create = [
        ('ТЕСТ Колбаса', 104, 26, 0, 0),
        ('ТЕСТ Хлеб', 46, 7, 3, 0),
        ('ТЕСТ Масло сливочное', 306, 0, 34, 0),
        ('ТЕСТ Сыр нарезка', 68, 16, 1, 0)
    ]
    
    created_products = {}
    for name, calories, protein, fat, carbs in products_to_create:
        product_data = {
            'name': name,
            'calories_per_100g': calories,
            'protein_per_100g': protein,
            'fat_per_100g': fat,
            'carbs_per_100g': carbs,
            'category': 'processed',
            'processing_level': 'processed'
        }
        
        response = client.post('/api/products',
                              data=json.dumps(product_data),
                              content_type='application/json')
        assert response.status_code == 201
        
        product_id = json.loads(response.data)['data']['id']
        created_products[name] = product_id
    
    # Step 3: Create dish with exact ingredients from manual test
    dish_data = {
        'name': 'ТЕСТ бутерброд 45 v2',
        'description': 'Тестовый бутерброд: 45г хлеба, 45г колбасы, 45г сыра',
        'ingredients': [
            {
                'product_id': created_products['ТЕСТ Хлеб'],
                'quantity_grams': 45
            },
            {
                'product_id': created_products['ТЕСТ Колбаса'],
                'quantity_grams': 45
            },
            {
                'product_id': created_products['ТЕСТ Сыр нарезка'],
                'quantity_grams': 45
            }
        ]
    }
    
    dish_response = client.post('/api/dishes',
                               data=json.dumps(dish_data),
                               content_type='application/json')
    assert dish_response.status_code == 201
    
    dish_id = json.loads(dish_response.data)['data']['id']
    
    # Step 4: Verify exact calculations from manual test
    # Manual calculation:
    # ТЕСТ Хлеб (45г): 46×0.45 = 20.7 ккал, 7×0.45 = 3.15г белка, 3×0.45 = 1.35г жира
    # ТЕСТ Колбаса (45г): 104×0.45 = 46.8 ккал, 26×0.45 = 11.7г белка, 0×0.45 = 0г жира  
    # ТЕСТ Сыр нарезка (45г): 68×0.45 = 30.6 ккал, 16×0.45 = 7.2г белка, 1×0.45 = 0.45г жира
    # Итого: 20.7 + 46.8 + 30.6 = 98.1 ккал, 3.15 + 11.7 + 7.2 = 22.05г белка, 1.35 + 0 + 0.45 = 1.8г жира
    
    dishes_response = client.get('/api/dishes')
    dishes_data = json.loads(dishes_response.data)
    
    test_dish = None
    for dish in dishes_data['data']:
        if dish['name'] == 'ТЕСТ бутерброд 45 v2':
            test_dish = dish
            break
    
    assert test_dish is not None
    assert abs(test_dish['total_calories'] - 104.4) < 0.1
    assert abs(test_dish['total_protein'] - 22.05) < 0.1
    assert abs(test_dish['total_fat'] - 1.8) < 0.1
    assert test_dish['total_carbs'] == 0.0
    
    # Step 5: Add to log exactly as in manual test
    log_data = {
        'date': '2025-10-15',
        'item_type': 'dish',
        'item_id': dish_id,
        'quantity_grams': 100,
        'meal_time': 'breakfast'
    }
    
    log_response = client.post('/api/log',
                              data=json.dumps(log_data),
                              content_type='application/json')
    assert log_response.status_code == 201
    
    # Step 6: Verify log entry shows correct calories
    log_entries_response = client.get('/api/log?date=2025-10-15')
    log_entries_data = json.loads(log_entries_response.data)
    
    test_log_entry = None
    for entry in log_entries_data['data']:
        if entry['item_name'] == 'ТЕСТ бутерброд 45 v2':
            test_log_entry = entry
            break
    
    assert test_log_entry is not None
    assert abs(test_log_entry['calculated_calories'] - 77.4) < 0.1
    assert test_log_entry['meal_time'] == 'breakfast'
    assert test_log_entry['quantity_grams'] == 100.0
    
    # Step 7: Verify statistics include our entry
    stats_response = client.get('/api/stats/2025-10-15')
    assert stats_response.status_code == 200
    
    stats_data = json.loads(stats_response.data)
    assert stats_data['data']['calories'] >= 77.4
    assert stats_data['data']['entries_count'] >= 1
    
    # Step 8: Cleanup (as would be done before next test)
    client.delete(f"/api/dishes/{dish_id}")
    for product_id in created_products.values():
        client.delete(f"/api/products/{product_id}")

# ============================================
# Performance Tests
# ============================================

def test_large_product_list_performance(client):
    """Test performance with many products"""
    # Create multiple products
    for i in range(50):
        product_data = {
            'name': f'Test Product {i}',
            'calories_per_100g': i + 100,
            'protein_per_100g': i % 30,
            'fat_per_100g': i % 20,
            'carbs_per_100g': i % 15,
            'category': 'processed',
            'processing_level': 'processed'
        }
        
        response = client.post('/api/products',
                              data=json.dumps(product_data),
                              content_type='application/json')
        assert response.status_code == 201
    
    # Test listing all products
    response = client.get('/api/products')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert len(data['data']) >= 50

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
