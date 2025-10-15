#!/usr/bin/env python3
"""
Comprehensive integration test for Nutrition Tracker
Tests complete workflow: products -> dishes -> logging -> statistics -> modifications -> cleanup
"""

import os
import sys
import tempfile
import pytest
import json

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, get_db, init_db


@pytest.fixture
def client():
    """Create a test client with fresh database"""
    # Create a temporary database
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
    
    # Clean up
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


def test_complete_workflow(client):
    """Test complete workflow from products to cleanup"""
    
    # 1-4. Create products
    products_data = [
        {
            'name': 'хлеб',
            'protein_per_100g': 8.0,
            'fat_per_100g': 2.0,
            'carbs_per_100g': 45.0,
            'category': 'processed',
            'processing_level': 'processed'
        },
        {
            'name': 'колбаса',
            'protein_per_100g': 15.0,
            'fat_per_100g': 25.0,
            'carbs_per_100g': 1.0,
            'category': 'processed',
            'processing_level': 'processed'
        },
        {
            'name': 'сливочное масло',
            'protein_per_100g': 1.0,
            'fat_per_100g': 82.0,
            'carbs_per_100g': 0.5,
            'category': 'dairy',
            'processing_level': 'minimal'
        },
        {
            'name': 'сыр',
            'protein_per_100g': 25.0,
            'fat_per_100g': 30.0,
            'carbs_per_100g': 0.5,
            'category': 'dairy',
            'processing_level': 'minimal'
        }
    ]
    
    product_ids = {}
    for product_data in products_data:
        response = client.post('/api/products', json=product_data)
        assert response.status_code == 201
        data = response.get_json()
        product_ids[product_data['name']] = data['data']['id']
    
    # 5. Create dish "бутерброд"
    dish_data = {
        'name': 'бутерброд',
        'description': 'Классический бутерброд',
        'ingredients': [
            {'product_id': product_ids['хлеб'], 'quantity_grams': 50, 'preparation_method': 'raw', 'edible_portion': 1.0},
            {'product_id': product_ids['колбаса'], 'quantity_grams': 30, 'preparation_method': 'raw', 'edible_portion': 1.0},
            {'product_id': product_ids['сливочное масло'], 'quantity_grams': 10, 'preparation_method': 'raw', 'edible_portion': 1.0},
            {'product_id': product_ids['сыр'], 'quantity_grams': 20, 'preparation_method': 'raw', 'edible_portion': 1.0}
        ]
    }
    
    response = client.post('/api/dishes', json=dish_data)
    assert response.status_code == 201
    dish_data_response = response.get_json()
    dish_id = dish_data_response['data']['id']
    
    # 6. Add products to log one by one
    log_date = '2025-01-01'
    meal_time = 'breakfast'
    
    log_entries = [
        {'item_type': 'product', 'item_id': product_ids['хлеб'], 'quantity_grams': 100},
        {'item_type': 'product', 'item_id': product_ids['колбаса'], 'quantity_grams': 50},
        {'item_type': 'product', 'item_id': product_ids['сливочное масло'], 'quantity_grams': 20},
        {'item_type': 'product', 'item_id': product_ids['сыр'], 'quantity_grams': 30}
    ]
    
    log_entry_ids = []
    for log_entry in log_entries:
        log_data = {
            'date': log_date,
            'meal_time': meal_time,
            **log_entry
        }
        response = client.post('/api/log', json=log_data)
        assert response.status_code == 201
        log_data_response = response.get_json()
        log_entry_ids.append(log_data_response['data']['id'])
    
    # 7-8. Check statistics display and calculations
    response = client.get(f'/api/stats/{log_date}')
    assert response.status_code == 200
    stats_data = response.get_json()
    
    # Verify statistics structure
    assert 'data' in stats_data
    assert 'calories' in stats_data['data']
    assert 'protein' in stats_data['data']
    assert 'fat' in stats_data['data']
    assert 'carbs' in stats_data['data']
    assert 'entries_count' in stats_data['data']
    
    # Verify calculations (approximate values)
    total_calories = stats_data['data']['calories']
    assert total_calories > 0
    assert total_calories < 2000  # Reasonable upper bound
    
    # 9. Add dish to log
    dish_log_data = {
        'date': log_date,
        'meal_time': 'lunch',
        'item_type': 'dish',
        'item_id': dish_id,
        'quantity_grams': 150
    }
    
    response = client.post('/api/log', json=dish_log_data)
    assert response.status_code == 201
    dish_log_response = response.get_json()
    dish_log_id = dish_log_response['data']['id']
    
    # 10. Re-check statistics
    response = client.get(f'/api/stats/{log_date}')
    assert response.status_code == 200
    stats_data_after_dish = response.get_json()
    
    # Statistics should have increased
    assert stats_data_after_dish['data']['calories'] > total_calories
    
    # 11. Modify bread data
    updated_bread_data = {
        'name': 'хлеб',
        'protein_per_100g': 10.0,  # Increased from 8.0
        'fat_per_100g': 3.0,       # Increased from 2.0
        'carbs_per_100g': 50.0,    # Increased from 45.0
        'category': 'processed',
        'processing_level': 'processed'
    }
    
    response = client.put(f'/api/products/{product_ids["хлеб"]}', json=updated_bread_data)
    assert response.status_code == 200
    
    # 12. Re-check statistics (should reflect updated bread data)
    response = client.get(f'/api/stats/{log_date}')
    assert response.status_code == 200
    stats_data_after_bread_update = response.get_json()
    
    # Statistics should have changed due to updated bread
    assert stats_data_after_bread_update['data']['calories'] != stats_data_after_dish['data']['calories']
    
    # 13. Modify dish data
    updated_dish_data = {
        'name': 'бутерброд',
        'description': 'Обновленный бутерброд',
        'ingredients': [
            {'product_id': product_ids['хлеб'], 'quantity_grams': 60, 'preparation_method': 'raw', 'edible_portion': 1.0},  # Increased
            {'product_id': product_ids['колбаса'], 'quantity_grams': 35, 'preparation_method': 'raw', 'edible_portion': 1.0},  # Increased
            {'product_id': product_ids['сливочное масло'], 'quantity_grams': 15, 'preparation_method': 'raw', 'edible_portion': 1.0},  # Increased
            {'product_id': product_ids['сыр'], 'quantity_grams': 25, 'preparation_method': 'raw', 'edible_portion': 1.0}  # Increased
        ]
    }
    
    response = client.put(f'/api/dishes/{dish_id}', json=updated_dish_data)
    assert response.status_code == 200
    
    # 14. Re-check statistics
    response = client.get(f'/api/stats/{log_date}')
    assert response.status_code == 200
    stats_data_after_dish_update = response.get_json()
    
    # Statistics should have changed due to updated dish
    assert stats_data_after_dish_update['data']['calories'] != stats_data_after_bread_update['data']['calories']
    
    # 15. Modify logged bread quantity
    updated_bread_log_data = {
        'date': log_date,
        'meal_time': meal_time,
        'item_type': 'product',
        'item_id': product_ids['хлеб'],
        'quantity_grams': 150  # Increased from 100
    }
    
    response = client.put(f'/api/log/{log_entry_ids[0]}', json=updated_bread_log_data)
    assert response.status_code == 200
    
    # 16. Re-check statistics
    response = client.get(f'/api/stats/{log_date}')
    assert response.status_code == 200
    stats_data_after_log_update = response.get_json()
    
    # Statistics should have increased due to more bread
    assert stats_data_after_log_update['data']['calories'] > stats_data_after_dish_update['data']['calories']
    
    # 17. Modify logged dish quantity
    updated_dish_log_data = {
        'date': log_date,
        'meal_time': 'lunch',
        'item_type': 'dish',
        'item_id': dish_id,
        'quantity_grams': 200  # Increased from 150
    }
    
    response = client.put(f'/api/log/{dish_log_id}', json=updated_dish_log_data)
    assert response.status_code == 200
    
    # 18. Re-check statistics
    response = client.get(f'/api/stats/{log_date}')
    assert response.status_code == 200
    stats_data_after_dish_log_update = response.get_json()
    
    # Statistics should have increased due to more dish
    assert stats_data_after_dish_log_update['data']['calories'] > stats_data_after_log_update['data']['calories']
    
    # 19. Delete logged bread
    response = client.delete(f'/api/log/{log_entry_ids[0]}')
    assert response.status_code == 200
    
    # 20. Re-check statistics
    response = client.get(f'/api/stats/{log_date}')
    assert response.status_code == 200
    stats_data_after_bread_deletion = response.get_json()
    
    # Statistics should have decreased due to deleted bread
    assert stats_data_after_bread_deletion['data']['calories'] < stats_data_after_dish_log_update['data']['calories']
    
    # 21. Delete logged dish
    response = client.delete(f'/api/log/{dish_log_id}')
    assert response.status_code == 200
    
    # 22. Re-check statistics
    response = client.get(f'/api/stats/{log_date}')
    assert response.status_code == 200
    stats_data_after_dish_deletion = response.get_json()
    
    # Statistics should have decreased due to deleted dish
    assert stats_data_after_dish_deletion['data']['calories'] < stats_data_after_bread_deletion['data']['calories']
    
    # 23. Delete bread from products database
    response = client.delete(f'/api/products/{product_ids["хлеб"]}')
    assert response.status_code == 200
    
    # 24. Delete dish from dishes database
    response = client.delete(f'/api/dishes/{dish_id}')
    assert response.status_code == 200
    
    # 25. Test admin panel access (check if maintenance endpoint exists)
    response = client.get('/api/maintenance/stats')
    # This might not exist, so we'll skip if it returns 404
    if response.status_code == 404:
        # Skip admin panel test if endpoint doesn't exist
        pass
    else:
        assert response.status_code == 200
        admin_stats = response.get_json()
        assert 'data' in admin_stats
    
    # 26. Test database wipe (admin function)
    response = client.post('/api/maintenance/wipe-database')
    assert response.status_code == 200
    wipe_response = response.get_json()
    assert wipe_response['status'] == 'success'
    
    # 27. Verify everything is empty
    # Check products
    response = client.get('/api/products')
    assert response.status_code == 200
    products_response = response.get_json()
    assert len(products_response['data']) == 0
    
    # Check dishes
    response = client.get('/api/dishes')
    assert response.status_code == 200
    dishes_response = response.get_json()
    assert len(dishes_response['data']) == 0
    
    # Check log entries
    response = client.get(f'/api/log?date={log_date}')
    assert response.status_code == 200
    log_response = response.get_json()
    assert len(log_response['data']) == 0
    
    # Check statistics (should be zero)
    response = client.get(f'/api/stats/{log_date}')
    assert response.status_code == 200
    final_stats = response.get_json()
    assert final_stats['data']['calories'] == 0
    assert final_stats['data']['protein'] == 0
    assert final_stats['data']['fat'] == 0
    assert final_stats['data']['carbs'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
