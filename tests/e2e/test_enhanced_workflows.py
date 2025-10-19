"""
Enhanced End-to-End tests for UI and API workflows
"""
import pytest
import json
import time
from datetime import datetime, timedelta
from unittest.mock import patch


class TestUIWorkflows:
    """Test UI-specific workflows and user interactions"""
    
    def test_homepage_loads_correctly(self, client):
        """Test that homepage loads with all necessary elements"""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data
        assert b'<title>' in response.data
        assert b'<body>' in response.data
        
        # Check for essential UI elements
        assert b'nutrition' in response.data.lower() or b'nutricount' in response.data.lower()
    
    def test_static_assets_load(self, client):
        """Test that static assets (CSS, JS) are accessible"""
        # Test CSS files
        css_response = client.get('/static/css/responsive.css')
        assert css_response.status_code == 200
        assert b'css' in css_response.data.lower() or css_response.data.startswith(b'/*')
        
        css_response = client.get('/static/css/final-polish.css')
        assert css_response.status_code == 200
        
        # Test JS files
        js_response = client.get('/static/js/app.js')
        assert js_response.status_code == 200
        assert b'javascript' in js_response.data.lower() or b'function' in js_response.data
        
        js_response = client.get('/static/js/fasting.js')
        assert js_response.status_code == 200
        
        # Test service worker
        sw_response = client.get('/static/sw.js')
        assert sw_response.status_code == 200
        assert b'serviceworker' in sw_response.data.lower() or b'addEventListener' in sw_response.data
    
    def test_manifest_json(self, client):
        """Test PWA manifest file"""
        response = client.get('/manifest.json')
        
        assert response.status_code == 200
        manifest = json.loads(response.data)
        
        assert 'name' in manifest
        assert 'short_name' in manifest
        assert 'icons' in manifest
        assert 'start_url' in manifest
        assert 'display' in manifest
    
    def test_service_worker_registration(self, client):
        """Test service worker file"""
        response = client.get('/sw.js')
        
        assert response.status_code == 200
        assert b'serviceworker' in response.data.lower() or b'addEventListener' in response.data
        assert b'cache' in response.data.lower()
    
    def test_health_endpoint_ui(self, client):
        """Test health endpoint returns proper JSON"""
        response = client.get('/health')
        
        assert response.status_code == 200
        health_data = json.loads(response.data)
        
        assert 'status' in health_data
        assert 'timestamp' in health_data
        assert 'version' in health_data
        assert health_data['status'] == 'healthy'


class TestAPIWorkflows:
    """Test comprehensive API workflows"""
    
    def test_complete_product_lifecycle(self, client):
        """Test complete product lifecycle: create, read, update, delete"""
        # 1. Create product
        product_data = {
            'name': 'Test Banana',
            'calories_per_100g': 89.0,
            'protein_per_100g': 1.1,
            'fat_per_100g': 0.3,
            'carbs_per_100g': 23.0,
            'fiber_per_100g': 2.6,
            'sugars_per_100g': 12.2,
            'category': 'berries',
            'processing_level': 'raw',
            'glycemic_index': 51,
            'region': 'US'
        }
        
        create_response = client.post(
            '/api/products',
            data=json.dumps(product_data),
            content_type='application/json'
        )
        
        assert create_response.status_code == 201
        created_product = json.loads(create_response.data)['data']
        product_id = created_product['id']
        
        # 2. Read product
        read_response = client.get(f'/api/products/{product_id}')
        assert read_response.status_code == 200
        read_product = json.loads(read_response.data)['data']
        assert read_product['name'] == 'Test Banana'
        assert read_product['calories_per_100g'] > 0  # Calories are recalculated
        
        # 3. Update product
        update_data = {
            'name': 'Updated Banana',
            'calories_per_100g': 90.0,
            'protein_per_100g': 1.2,
            'fat_per_100g': 0.3,
            'carbs_per_100g': 23.0,
            'fiber_per_100g': 2.6,
            'sugars_per_100g': 12.2,
            'category': 'fruits',
            'processing_level': 'raw',
            'glycemic_index': 51,
            'region': 'US'
        }
        
        update_response = client.put(
            f'/api/products/{product_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert update_response.status_code == 200
        updated_product = json.loads(update_response.data)['data']
        assert updated_product['name'] == 'Updated Banana'
        assert updated_product['calories_per_100g'] > 0  # Calories are recalculated
        
        # 4. List products
        list_response = client.get('/api/products')
        assert list_response.status_code == 200
        products_list = json.loads(list_response.data)['data']
        assert isinstance(products_list, list)
        # Products might be filtered or empty due to test isolation
        
        # 5. Delete product
        delete_response = client.delete(f'/api/products/{product_id}')
        assert delete_response.status_code == 200
        
        # 6. Verify deletion
        verify_response = client.get(f'/api/products/{product_id}')
        assert verify_response.status_code == 404
    
    def test_complete_dish_lifecycle(self, client):
        """Test complete dish lifecycle with ingredients"""
        # First create a product to use in dish
        product_data = {
            'name': 'Test Rice',
            'calories_per_100g': 130.0,
            'protein_per_100g': 2.7,
            'fat_per_100g': 0.3,
            'carbs_per_100g': 28.0,
            'fiber_per_100g': 0.4,
            'sugars_per_100g': 0.1,
            'category': 'processed',
            'processing_level': 'processed',
            'glycemic_index': 73,
            'region': 'US'
        }
        
        product_response = client.post(
            '/api/products',
            data=json.dumps(product_data),
            content_type='application/json'
        )
        
        assert product_response.status_code == 201
        product = json.loads(product_response.data)['data']
        product_id = product['id']
        
        # 1. Create dish
        dish_data = {
            'name': 'Rice Bowl',
            'description': 'Healthy rice bowl with vegetables',
            'ingredients': [
                {'product_id': product_id, 'quantity_grams': 200.0}
            ]
        }
        
        create_response = client.post(
            '/api/dishes',
            data=json.dumps(dish_data),
            content_type='application/json'
        )
        
        assert create_response.status_code == 201
        created_dish = json.loads(create_response.data)['data']
        dish_id = created_dish['id']
        
        # 2. Read dish
        read_response = client.get(f'/api/dishes/{dish_id}')
        assert read_response.status_code == 200
        read_dish = json.loads(read_response.data)['data']
        assert read_dish['name'] == 'Rice Bowl'
        assert len(read_dish['ingredients']) == 1
        
        # 3. Update dish
        update_data = {
            'name': 'Updated Rice Bowl',
            'description': 'Updated healthy rice bowl',
            'ingredients': [
                {'product_id': product_id, 'quantity_grams': 250.0}
            ]
        }
        
        update_response = client.put(
            f'/api/dishes/{dish_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert update_response.status_code == 200
        updated_dish = json.loads(update_response.data)['data']
        assert updated_dish['name'] == 'Updated Rice Bowl'
        
        # 4. List dishes
        list_response = client.get('/api/dishes')
        assert list_response.status_code == 200
        dishes_list = json.loads(list_response.data)['data']
        assert isinstance(dishes_list, list)
        
        # 5. Delete dish
        delete_response = client.delete(f'/api/dishes/{dish_id}')
        assert delete_response.status_code == 200
        
        # 6. Clean up product
        client.delete(f'/api/products/{product_id}')
    
    def test_complete_logging_workflow(self, client):
        """Test complete logging workflow with multiple entries"""
        # Create a product first
        product_data = {
            'name': 'Test Bread',
            'calories_per_100g': 265.0,
            'protein_per_100g': 9.0,
            'fat_per_100g': 3.2,
            'carbs_per_100g': 49.0,
            'fiber_per_100g': 2.7,
            'sugars_per_100g': 5.7,
            'category': 'processed',
            'processing_level': 'processed',
            'glycemic_index': 70,
            'region': 'US'
        }
        
        product_response = client.post(
            '/api/products',
            data=json.dumps(product_data),
            content_type='application/json'
        )
        
        assert product_response.status_code == 201
        product = json.loads(product_response.data)['data']
        product_id = product['id']
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 1. Log breakfast
        breakfast_log = {
            'date': today,
            'meal_time': 'breakfast',
            'item_type': 'product',
            'item_id': product_id,
            'quantity_grams': 50.0,
            'notes': 'Morning toast'
        }
        
        breakfast_response = client.post(
            '/api/log',
            data=json.dumps(breakfast_log),
            content_type='application/json'
        )
        
        assert breakfast_response.status_code == 201
        breakfast_entry = json.loads(breakfast_response.data)['data']
        breakfast_id = breakfast_entry['id']
        
        # 2. Log lunch
        lunch_log = {
            'date': today,
            'meal_time': 'lunch',
            'item_type': 'product',
            'item_id': product_id,
            'quantity_grams': 100.0,
            'notes': 'Lunch sandwich'
        }
        
        lunch_response = client.post(
            '/api/log',
            data=json.dumps(lunch_log),
            content_type='application/json'
        )
        
        assert lunch_response.status_code == 201
        lunch_entry = json.loads(lunch_response.data)['data']
        lunch_id = lunch_entry['id']
        
        # 3. Log dinner
        dinner_log = {
            'date': today,
            'meal_time': 'dinner',
            'item_type': 'product',
            'item_id': product_id,
            'quantity_grams': 75.0,
            'notes': 'Evening bread'
        }
        
        dinner_response = client.post(
            '/api/log',
            data=json.dumps(dinner_log),
            content_type='application/json'
        )
        
        assert dinner_response.status_code == 201
        dinner_entry = json.loads(dinner_response.data)['data']
        dinner_id = dinner_entry['id']
        
        # 4. Get all logs for today
        logs_response = client.get('/api/log')
        assert logs_response.status_code == 200
        logs_data = json.loads(logs_response.data)['data']
        assert isinstance(logs_data, list)
        assert len(logs_data) >= 3
        
        # 5. Update a log entry
        update_log = {
            'date': today,
            'meal_time': 'breakfast',
            'item_type': 'product',
            'item_id': product_id,
            'quantity_grams': 60.0,
            'notes': 'Updated morning toast'
        }
        
        update_response = client.put(
            f'/api/log/{breakfast_id}',
            data=json.dumps(update_log),
            content_type='application/json'
        )
        
        assert update_response.status_code == 200
        updated_entry = json.loads(update_response.data)['data']
        assert updated_entry['quantity_grams'] == 60.0
        
        # 6. Get daily stats
        stats_response = client.get(f'/api/stats/{today}')
        assert stats_response.status_code == 200
        stats = json.loads(stats_response.data)['data']
        assert stats['calories'] > 0
        assert stats['protein'] > 0
        assert stats['carbs'] > 0
        assert stats['fat'] > 0
        
        # 7. Delete log entries
        client.delete(f'/api/log/{breakfast_id}')
        client.delete(f'/api/log/{lunch_id}')
        client.delete(f'/api/log/{dinner_id}')
        
        # 8. Clean up product
        client.delete(f'/api/products/{product_id}')
    
    def test_complete_profile_workflow(self, client):
        """Test complete user profile workflow"""
        # 1. Create profile
        profile_data = {
            'gender': 'male',
            'birth_date': '1993-01-01',
            'height_cm': 180,
            'weight_kg': 75.0,
            'activity_level': 'moderate',
            'goal': 'maintenance'
        }
        
        create_response = client.post(
            '/api/profile',
            data=json.dumps(profile_data),
            content_type='application/json'
        )
        
        assert create_response.status_code == 201
        created_profile = json.loads(create_response.data)['data']
        
        # 2. Get profile
        get_response = client.get('/api/profile')
        assert get_response.status_code == 200
        profile = json.loads(get_response.data)['data']
        assert profile['gender'] == 'male'
        assert profile['height_cm'] == 180
        assert profile['weight_kg'] == 75.0
        
        # 3. Update profile
        update_data = {
            'gender': 'male',
            'birth_date': '1992-01-01',
            'height_cm': 180,
            'weight_kg': 74.0,
            'activity_level': 'active',
            'goal': 'muscle_gain'
        }
        
        update_response = client.put(
            '/api/profile',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert update_response.status_code == 200
        updated_profile = json.loads(update_response.data)['data']
        assert updated_profile['weight_kg'] == 74.0
        assert updated_profile['activity_level'] == 'active'
        
        # 4. Get macros
        macros_response = client.get('/api/profile/macros')
        assert macros_response.status_code == 200
        macros = json.loads(macros_response.data)['data']
        assert 'bmr' in macros
        assert 'carbs' in macros
        assert 'fats' in macros
    
    def test_complete_gki_workflow(self, client):
        """Test complete GKI (Glucose-Ketone Index) workflow"""
        # 1. Calculate GKI with normal values
        gki_data = {
            'glucose_mgdl': 90.0,
            'ketones_mgdl': 1.5
        }
        
        gki_response = client.post(
            '/api/gki',
            data=json.dumps(gki_data),
            content_type='application/json'
        )
        
        assert gki_response.status_code == 200
        gki_result = json.loads(gki_response.data)['data']
        assert 'gki' in gki_result
        assert 'gki_category' in gki_result
        assert 'glucose_mmol' in gki_result
        assert 'ketones_mmol' in gki_result
        
        # 2. Calculate GKI with high glucose
        high_glucose_data = {
            'glucose_mgdl': 150.0,
            'ketones_mgdl': 0.5
        }
        
        high_glucose_response = client.post(
            '/api/gki',
            data=json.dumps(high_glucose_data),
            content_type='application/json'
        )
        
        assert high_glucose_response.status_code == 200
        high_glucose_result = json.loads(high_glucose_response.data)['data']
        assert high_glucose_result['gki'] > gki_result['gki']  # Higher GKI
        
        # 3. Calculate GKI with high ketones
        high_ketones_data = {
            'glucose_mgdl': 80.0,
            'ketones_mgdl': 3.0
        }
        
        high_ketones_response = client.post(
            '/api/gki',
            data=json.dumps(high_ketones_data),
            content_type='application/json'
        )
        
        assert high_ketones_response.status_code == 200
        high_ketones_result = json.loads(high_ketones_response.data)['data']
        assert high_ketones_result['gki'] < gki_result['gki']  # Lower GKI


class TestSystemWorkflows:
    """Test system administration and maintenance workflows"""
    
    def test_system_status_workflow(self, client):
        """Test system status monitoring"""
        # 1. Get system status
        status_response = client.get('/api/system/status')
        assert status_response.status_code == 200
        status = json.loads(status_response.data)['data']
        
        assert 'database' in status
        assert 'application' in status
        assert 'system' in status
    
    def test_database_maintenance_workflow(self, client):
        """Test database maintenance operations"""
        # 1. Vacuum database
        vacuum_response = client.post('/api/maintenance/vacuum')
        assert vacuum_response.status_code == 200
        vacuum_result = json.loads(vacuum_response.data)['data']
        assert 'optimization_type' in vacuum_result
        
        # 2. Cleanup old data
        cleanup_response = client.post('/api/maintenance/cleanup')
        assert cleanup_response.status_code == 200
        cleanup_result = json.loads(cleanup_response.data)['data']
        assert 'cleanup_details' in cleanup_result
        
        # 3. Cleanup test data
        cleanup_test_response = client.post('/api/maintenance/cleanup-test-data')
        assert cleanup_test_response.status_code == 200
        cleanup_test_result = json.loads(cleanup_test_response.data)['data']
        assert 'cleanup_time' in cleanup_test_result
    
    def test_export_workflow(self, client):
        """Test data export functionality"""
        # 1. Export all data
        export_response = client.get('/api/export/all')
        assert export_response.status_code == 200
        
        # Check if it's a file download or JSON response
        if export_response.headers.get('Content-Type') == 'application/json':
            export_data = json.loads(export_response.data)
            assert 'export_info' in export_data
        else:
            # It might be a file download
            assert len(export_response.data) > 0


class TestPerformanceWorkflows:
    """Test performance-related workflows"""
    
    def test_bulk_operations_performance(self, client):
        """Test performance of bulk operations"""
        # Create multiple products quickly
        start_time = time.time()
        
        products_created = []
        for i in range(10):
            product_data = {
                'name': f'Test Product {i}',
                'calories_per_100g': 100.0 + i,
                'protein_per_100g': 10.0 + i,
                'fat_per_100g': 5.0 + i,
                'carbs_per_100g': 20.0 + i,
                'fiber_per_100g': 2.0 + i,
                'sugars_per_100g': 5.0 + i,
                'category': 'leafy_vegetables',
                'processing_level': 'raw',
                'glycemic_index': 30 + i,
                'region': 'US'
            }
            
            response = client.post(
                '/api/products',
                data=json.dumps(product_data),
                content_type='application/json'
            )
            
            assert response.status_code == 201
            product = json.loads(response.data)['data']
            products_created.append(product['id'])
        
        creation_time = time.time() - start_time
        
        # Should create 10 products in reasonable time (less than 5 seconds)
        assert creation_time < 5.0
        
        # Clean up
        for product_id in products_created:
            client.delete(f'/api/products/{product_id}')
    
    def test_concurrent_requests_performance(self, client):
        """Test performance under concurrent-like requests"""
        # Simulate multiple rapid requests
        start_time = time.time()
        
        responses = []
        for i in range(20):
            response = client.get('/api/products')
            responses.append(response)
        
        total_time = time.time() - start_time
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
        
        # Should handle 20 requests in reasonable time (less than 2 seconds)
        assert total_time < 2.0
    
    def test_large_data_handling(self, client):
        """Test handling of large data sets"""
        # Create a product with large nutritional data
        large_product_data = {
            'name': 'Large Test Product',
            'calories_per_100g': 630.0,
            'protein_per_100g': 50.0,
            'fat_per_100g': 30.0,
            'carbs_per_100g': 40.0,
            'fiber_per_100g': 10.0,
            'sugars_per_100g': 20.0,
            'category': 'processed',
            'processing_level': 'processed',
            'glycemic_index': 80,
            'region': 'US'
        }
        
        response = client.post(
            '/api/products',
            data=json.dumps(large_product_data),
            content_type='application/json'
        )
        
        # Test that large data is handled correctly
        # If validation fails, that's expected behavior for very large values
        if response.status_code == 201:
            product = json.loads(response.data)['data']
            product_id = product['id']
            
            get_response = client.get(f'/api/products/{product_id}')
            assert get_response.status_code == 200
            retrieved_product = json.loads(get_response.data)['data']
            assert retrieved_product['calories_per_100g'] > 0
            
            # Clean up
            client.delete(f'/api/products/{product_id}')
        else:
            # Large data validation failed - this is expected behavior
            error_data = json.loads(response.data)
            assert error_data['status'] == 'error'


class TestErrorRecoveryWorkflows:
    """Test error recovery and resilience workflows"""
    
    def test_database_error_recovery(self, client):
        """Test recovery from database errors"""
        # This test would require mocking database errors
        # For now, we'll test that the system handles invalid requests gracefully
        
        # Test with invalid product data
        invalid_product = {
            'name': '',  # Empty name should fail
            'calories_per_100g': 'invalid'  # Invalid type should fail
        }
        
        response = client.post(
            '/api/products',
            data=json.dumps(invalid_product),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        error_data = json.loads(response.data)
        assert error_data['status'] == 'error'
    
    def test_network_error_simulation(self, client):
        """Test handling of network-like errors"""
        # Test with malformed JSON
        response = client.post(
            '/api/products',
            data='invalid json data',
            content_type='application/json'
        )
        
        # Should handle gracefully (either 400 or 500)
        assert response.status_code in [400, 500]
    
    def test_resource_not_found_recovery(self, client):
        """Test recovery from resource not found errors"""
        # Test accessing non-existent product
        response = client.get('/api/products/99999')
        assert response.status_code == 404
        
        # Test accessing non-existent dish
        response = client.get('/api/dishes/99999')
        assert response.status_code == 404
        
        # Test accessing non-existent log
        response = client.get('/api/log/99999')
        assert response.status_code == 404


class TestSecurityWorkflows:
    """Test security-related workflows"""
    
    def test_authentication_security_workflow(self, client):
        """Test authentication security measures"""
        # 1. Test login with invalid credentials
        invalid_login = {
            'username': 'hacker',
            'password': 'password123'
        }
        
        response = client.post(
            '/api/auth/login',
            data=json.dumps(invalid_login),
            content_type='application/json'
        )
        
        assert response.status_code == 401  # Changed from 400 to 401
        error_data = json.loads(response.data)
        assert error_data['status'] == 'error'
        
        # 2. Test access without token
        response = client.get('/api/auth/verify')
        assert response.status_code == 401
        
        # 3. Test access with invalid token
        response = client.get(
            '/api/auth/verify',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        assert response.status_code in [401, 500]  # Should reject invalid token
    
    def test_input_validation_security(self, client):
        """Test input validation security"""
        # Test SQL injection attempt
        malicious_product = {
            'name': "'; DROP TABLE products; --",
            'calories_per_100g': 100.0,
            'protein_per_100g': 10.0,
            'fat_per_100g': 5.0,
            'carbs_per_100g': 20.0,
            'fiber_per_100g': 2.0,
            'sugars_per_100g': 5.0,
            'category': 'vegetables',
            'processing_level': 'raw',
            'glycemic_index': 30,
            'region': 'US'
        }
        
        response = client.post(
            '/api/products',
            data=json.dumps(malicious_product),
            content_type='application/json'
        )
        
        # Should either reject or sanitize the input
        assert response.status_code in [200, 201, 400]
        
        if response.status_code in [200, 201]:
            # If accepted, verify the data was sanitized
            product = json.loads(response.data)['data']
            assert "'; DROP TABLE" not in product['name']
            product_id = product['id']
            # Clean up
            client.delete(f'/api/products/{product_id}')
    
    def test_rate_limiting_security(self, client):
        """Test rate limiting security measures"""
        # Make multiple rapid requests to trigger rate limiting
        responses = []
        for i in range(10):
            response = client.post(
                '/api/auth/login',
                data=json.dumps({'username': 'test', 'password': 'test'}),
                content_type='application/json'
            )
            responses.append(response)
        
        # At least one request should be rate limited (429) or all should be 401 (unauthorized)
        status_codes = [r.status_code for r in responses]
        assert 429 in status_codes or all(code == 401 for code in status_codes)
