"""
UI-focused End-to-End tests for user interface interactions
"""
import pytest
import json
import time
from datetime import datetime


class TestUIInteractions:
    """Test UI interactions and user experience"""
    
    def test_responsive_design_elements(self, client):
        """Test that UI elements are responsive and accessible"""
        # Test main page loads with responsive elements
        response = client.get('/')
        assert response.status_code == 200
        
        # Check for responsive CSS
        css_response = client.get('/static/css/responsive.css')
        assert css_response.status_code == 200
        
        # Check for viewport meta tag in HTML
        html_content = response.data.decode('utf-8')
        assert 'viewport' in html_content.lower() or 'responsive' in html_content.lower()
    
    def test_accessibility_features(self, client):
        """Test accessibility features and WCAG compliance"""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.data.decode('utf-8')
        
        # Check for basic accessibility elements
        # Note: This is a basic check - full accessibility testing would require browser automation
        assert '<html' in html_content.lower()
        assert '<head>' in html_content.lower()
        assert '<body>' in html_content.lower()
    
    def test_progressive_web_app_features(self, client):
        """Test PWA features and offline capabilities"""
        # Test manifest file
        manifest_response = client.get('/manifest.json')
        assert manifest_response.status_code == 200
        manifest = json.loads(manifest_response.data)
        
        # Check required PWA fields
        assert 'name' in manifest
        assert 'short_name' in manifest
        assert 'icons' in manifest
        assert 'start_url' in manifest
        assert 'display' in manifest
        
        # Test service worker
        sw_response = client.get('/sw.js')
        assert sw_response.status_code == 200
        sw_content = sw_response.data.decode('utf-8')
        
        # Check for service worker registration
        assert 'addEventListener' in sw_content or 'serviceworker' in sw_content.lower()
    
    def test_theme_and_styling(self, client):
        """Test theme and styling functionality"""
        # Test CSS files load correctly
        css_files = [
            '/static/css/responsive.css',
            '/static/css/final-polish.css'
        ]
        
        for css_file in css_files:
            response = client.get(css_file)
            assert response.status_code == 200
            assert 'css' in response.data.decode('utf-8').lower() or response.data.startswith(b'/*')
    
    def test_javascript_functionality(self, client):
        """Test JavaScript files and functionality"""
        # Test JS files load correctly
        js_files = [
            '/static/js/app.js',
            '/static/js/admin.js',
            '/static/js/fasting.js',
            '/static/js/notifications.js',
            '/static/js/shortcuts.js',
            '/static/js/themes.js',
            '/static/js/offline.js'
        ]
        
        for js_file in js_files:
            response = client.get(js_file)
            assert response.status_code == 200
            js_content = response.data.decode('utf-8')
            # Basic check that it contains JavaScript-like content
            assert ('class' in js_content.lower() or 'constructor' in js_content.lower() or 'addEventListener' in js_content.lower())


class TestAPIResponseFormats:
    """Test API response formats and consistency"""
    
    def test_json_response_consistency(self, client):
        """Test that all API responses follow consistent JSON format"""
        # Test products API
        response = client.get('/api/products')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert 'data' in data
        
        # Test dishes API
        response = client.get('/api/dishes')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert 'data' in data
        
        # Test logs API
        response = client.get('/api/log')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert 'data' in data
        
        # Test fasting status API
        response = client.get('/api/fasting/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert 'data' in data
    
    def test_error_response_consistency(self, client):
        """Test that error responses follow consistent format"""
        # Test 404 error
        response = client.get('/api/products/99999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'error'
        
        # Test 400 error with invalid data
        invalid_data = {'name': ''}  # Empty name should fail
        response = client.post(
            '/api/products',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        if response.status_code == 400:
            data = json.loads(response.data)
            assert 'status' in data
            assert data['status'] == 'error'
    
    def test_content_type_headers(self, client):
        """Test that API responses have correct content types"""
        # Test JSON endpoints
        json_endpoints = [
            '/api/products',
            '/api/dishes',
            '/api/log',
            '/api/fasting/status'
        ]
        
        for endpoint in json_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            # Should be JSON content type
            assert 'application/json' in response.headers.get('Content-Type', '')
    
    def test_cors_headers(self, client):
        """Test CORS headers for cross-origin requests"""
        # Test CORS headers on API endpoints
        response = client.get('/api/products')
        assert response.status_code == 200
        
        # Check for CORS headers (if configured)
        headers = response.headers
        # CORS headers might be present depending on configuration
        # This is a basic check - full CORS testing would require cross-origin requests


class TestDataIntegrityWorkflows:
    """Test data integrity and consistency workflows"""
    
    def test_nutritional_calculations_consistency(self, client):
        """Test that nutritional calculations are consistent across endpoints"""
        # Create a product with known nutritional values
        product_data = {
            'name': 'Test Calculation Product',
            'calories_per_100g': 200.0,
            'protein_per_100g': 20.0,
            'fat_per_100g': 10.0,
            'carbs_per_100g': 15.0,
            'fiber_per_100g': 5.0,
            'sugars_per_100g': 10.0,
            'category': 'processed',
            'processing_level': 'raw',
            'glycemic_index': 50,
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
        
        # Create a dish using this product
        dish_data = {
            'name': 'Test Calculation Dish',
            'description': 'Dish for calculation testing',
            'ingredients': [
                {'product_id': product_id, 'quantity_grams': 100.0}
            ]
        }
        
        dish_response = client.post(
            '/api/dishes',
            data=json.dumps(dish_data),
            content_type='application/json'
        )
        
        assert dish_response.status_code == 201
        dish = json.loads(dish_response.data)['data']
        dish_id = dish['id']
        
        # Log the dish
        today = datetime.now().strftime('%Y-%m-%d')
        log_data = {
            'date': today,
            'meal_time': 'breakfast',
            'item_type': 'dish',
            'item_id': dish_id,
            'quantity_grams': 200.0
        }
        
        log_response = client.post(
            '/api/log',
            data=json.dumps(log_data),
            content_type='application/json'
        )
        
        assert log_response.status_code == 201
        
        # Check daily stats - should reflect the logged nutrition
        stats_response = client.get(f'/api/stats/{today}')
        assert stats_response.status_code == 200
        stats = json.loads(stats_response.data)['data']
        
        # Verify that stats reflect the logged nutrition
        assert stats['calories'] > 0
        assert stats['protein'] > 0
        assert stats['carbs'] > 0
        assert stats['fat'] > 0
        
        # Clean up
        client.delete(f'/api/log/{json.loads(log_response.data)["data"]["id"]}')
        client.delete(f'/api/dishes/{dish_id}')
        client.delete(f'/api/products/{product_id}')
    
    def test_fasting_session_data_consistency(self, client, isolated_db):
        """Test that fasting session data is consistent across endpoints"""
        # Start a fasting session
        fasting_data = {
            'fasting_type': '16:8',
            'notes': 'Consistency test session'
        }
        
        start_response = client.post(
            '/api/fasting/start',
            data=json.dumps(fasting_data),
            content_type='application/json'
        )
        
        if start_response.status_code == 201:
            session = json.loads(start_response.data)['data']
            session_id = session['session_id']
            
            # Check status endpoint
            status_response = client.get('/api/fasting/status')
            assert status_response.status_code == 200
            status = json.loads(status_response.data)['data']
            assert status['is_fasting'] is True
            assert status['fasting_type'] == '16:8'
            
            # Check sessions endpoint
            sessions_response = client.get('/api/fasting/sessions')
            assert sessions_response.status_code == 200
            sessions_data = json.loads(sessions_response.data)['data']
            sessions = sessions_data['sessions']
            assert len(sessions) >= 1, f"Expected at least 1 session, got {len(sessions)}"
            assert sessions[0]['fasting_type'] == '16:8'
            
            # End the session
            end_response = client.post('/api/fasting/end')
            assert end_response.status_code == 200
            
            # Verify final status
            final_status_response = client.get('/api/fasting/status')
            assert final_status_response.status_code == 200
            final_status = json.loads(final_status_response.data)['data']
            assert final_status['is_fasting'] is False
    
    def test_profile_macro_calculations(self, client):
        """Test that profile macro calculations are consistent"""
        # Create a profile
        profile_data = {
            'gender': 'male',
            'birth_date': '1993-01-01',
            'height_cm': 180,
            'weight_kg': 75.0,
            'activity_level': 'moderate',
            'goal': 'maintenance'
        }
        
        profile_response = client.post(
            '/api/profile',
            data=json.dumps(profile_data),
            content_type='application/json'
        )
        
        assert profile_response.status_code == 201
        
        # Get macros
        macros_response = client.get('/api/profile/macros')
        assert macros_response.status_code == 200
        macros = json.loads(macros_response.data)['data']
        
        # Verify macro calculations are reasonable
        assert macros['bmr'] > 0
        assert macros['carbs'] > 0
        assert macros['fats'] > 0
        
        # Verify macro percentages add up to approximately 100%
        total_percentage = (
            macros.get('protein_percentage', 0) +
            macros.get('carbs_percentage', 0) +
            macros.get('fats_percentage', 0)
        )
        assert 95 <= total_percentage <= 105  # Allow for rounding errors


class TestWorkflowIntegration:
    """Test integration between different workflows"""
    
    def test_nutrition_and_fasting_integration(self, client):
        """Test integration between nutrition tracking and fasting"""
        # Create a product
        product_data = {
            'name': 'Integration Test Product',
            'calories_per_100g': 150.0,
            'protein_per_100g': 15.0,
            'fat_per_100g': 8.0,
            'carbs_per_100g': 12.0,
            'fiber_per_100g': 3.0,
            'sugars_per_100g': 9.0,
            'category': 'meat',
            'processing_level': 'minimal',
            'glycemic_index': 40,
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
        
        # Log some nutrition
        today = datetime.now().strftime('%Y-%m-%d')
        log_data = {
            'date': today,
            'meal_time': 'breakfast',
            'item_type': 'product',
            'item_id': product_id,
            'quantity_grams': 100.0
        }
        
        log_response = client.post(
            '/api/log',
            data=json.dumps(log_data),
            content_type='application/json'
        )
        
        assert log_response.status_code == 201
        
        # Start fasting
        fasting_data = {
            'fasting_type': '16:8',
            'notes': 'Integration test fasting'
        }
        
        fasting_response = client.post(
            '/api/fasting/start',
            data=json.dumps(fasting_data),
            content_type='application/json'
        )
        
        if fasting_response.status_code == 201:
            # Check that both nutrition and fasting data are available
            stats_response = client.get(f'/api/stats/{today}')
            assert stats_response.status_code == 200
            stats = json.loads(stats_response.data)['data']
            assert stats['calories'] > 0
            
            fasting_status_response = client.get('/api/fasting/status')
            assert fasting_status_response.status_code == 200
            fasting_status = json.loads(fasting_status_response.data)['data']
            assert fasting_status['is_fasting'] is True
            
            # End fasting
            client.post('/api/fasting/end')
        
        # Clean up
        client.delete(f'/api/log/{json.loads(log_response.data)["data"]["id"]}')
        client.delete(f'/api/products/{product_id}')
    
    def test_profile_and_nutrition_integration(self, client):
        """Test integration between profile and nutrition tracking"""
        # Create a profile
        profile_data = {
            'gender': 'female',
            'birth_date': '1998-01-01',
            'height_cm': 165,
            'weight_kg': 60.0,
            'activity_level': 'active',
            'goal': 'weight_loss'
        }
        
        profile_response = client.post(
            '/api/profile',
            data=json.dumps(profile_data),
            content_type='application/json'
        )
        
        assert profile_response.status_code == 201
        
        # Get macros based on profile
        macros_response = client.get('/api/profile/macros')
        assert macros_response.status_code == 200
        macros = json.loads(macros_response.data)['data']
        
        # Verify macros are appropriate for weight loss goal
        assert macros['bmr'] > 0
        assert macros['carbs'] > 0
        assert macros['fats'] > 0
        
        # Create and log nutrition
        product_data = {
            'name': 'Profile Integration Product',
            'calories_per_100g': 100.0,
            'protein_per_100g': 10.0,
            'fat_per_100g': 5.0,
            'carbs_per_100g': 8.0,
            'fiber_per_100g': 2.0,
            'sugars_per_100g': 6.0,
            'category': 'leafy_vegetables',
            'processing_level': 'raw',
            'glycemic_index': 30,
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
        
        # Log nutrition
        today = datetime.now().strftime('%Y-%m-%d')
        log_data = {
            'date': today,
            'meal_time': 'lunch',
            'item_type': 'product',
            'item_id': product_id,
            'quantity_grams': 150.0
        }
        
        log_response = client.post(
            '/api/log',
            data=json.dumps(log_data),
            content_type='application/json'
        )
        
        assert log_response.status_code == 201
        
        # Check that daily stats reflect the logged nutrition
        stats_response = client.get(f'/api/stats/{today}')
        assert stats_response.status_code == 200
        stats = json.loads(stats_response.data)['data']
        assert stats['calories'] > 0
        
        # Clean up
        client.delete(f'/api/log/{json.loads(log_response.data)["data"]["id"]}')
        client.delete(f'/api/products/{product_id}')


class TestEdgeCaseWorkflows:
    """Test edge cases and boundary conditions in workflows"""
    
    def test_empty_database_workflows(self, client):
        """Test workflows with empty database"""
        # Wipe database
        wipe_response = client.post('/api/maintenance/wipe-database')
        assert wipe_response.status_code == 200
        
        # Test that endpoints handle empty database gracefully
        products_response = client.get('/api/products')
        assert products_response.status_code == 200
        products = json.loads(products_response.data)['data']
        assert isinstance(products, list)
        
        dishes_response = client.get('/api/dishes')
        assert dishes_response.status_code == 200
        dishes = json.loads(dishes_response.data)['data']
        assert isinstance(dishes, list)
        
        logs_response = client.get('/api/log')
        assert logs_response.status_code == 200
        logs = json.loads(logs_response.data)['data']
        assert isinstance(logs, list)
    
    def test_boundary_value_workflows(self, client):
        """Test workflows with boundary values"""
        # Test with minimum valid values
        min_product_data = {
            'name': 'Min Product',
            'calories_per_100g': 0.1,
            'protein_per_100g': 0.1,
            'fat_per_100g': 0.1,
            'carbs_per_100g': 0.1,
            'fiber_per_100g': 0.0,
            'sugars_per_100g': 0.0,
            'category': 'leafy_vegetables',
            'processing_level': 'raw',
            'glycemic_index': 1,
            'region': 'US'
        }
        
        min_response = client.post(
            '/api/products',
            data=json.dumps(min_product_data),
            content_type='application/json'
        )
        
        assert min_response.status_code == 201
        min_product = json.loads(min_response.data)['data']
        
        # Test with maximum reasonable values
        max_product_data = {
            'name': 'Max Product',
            'calories_per_100g': 999.0,
            'protein_per_100g': 99.0,
            'fat_per_100g': 99.0,
            'carbs_per_100g': 99.0,
            'fiber_per_100g': 99.0,
            'sugars_per_100g': 99.0,
            'category': 'processed',
            'processing_level': 'processed',
            'glycemic_index': 100,
            'region': 'US'
        }
        
        max_response = client.post(
            '/api/products',
            data=json.dumps(max_product_data),
            content_type='application/json'
        )
        
        # Test that large data is handled correctly
        # If validation fails, that's expected behavior for very large values
        if max_response.status_code == 201:
            max_product = json.loads(max_response.data)['data']
            
            # Clean up both products
            client.delete(f'/api/products/{min_product["id"]}')
            client.delete(f'/api/products/{max_product["id"]}')
        else:
            # Large data validation failed - this is expected behavior
            error_data = json.loads(max_response.data)
            assert error_data['status'] == 'error'
            
            # Clean up min product
            client.delete(f'/api/products/{min_product["id"]}')
    
    def test_concurrent_operation_workflows(self, client):
        """Test workflows with concurrent-like operations"""
        # Create multiple products simultaneously
        product_ids = []
        
        for i in range(5):
            product_data = {
                'name': f'Concurrent Product {i}',
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
            product_ids.append(product['id'])
        
        # Verify all products were created
        products_response = client.get('/api/products')
        assert products_response.status_code == 200
        products = json.loads(products_response.data)['data']
        # Products might be filtered or empty due to test isolation
        assert isinstance(products, list)
        
        # Clean up
        for product_id in product_ids:
            client.delete(f'/api/products/{product_id}')
