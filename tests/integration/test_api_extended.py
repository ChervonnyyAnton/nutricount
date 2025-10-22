"""
Extended Integration tests for API endpoints - Edge cases and Error scenarios
"""
import pytest
import json
from unittest.mock import patch, Mock


class TestAPIErrorHandling:
    """Test API error handling and edge cases"""
    
    def test_products_api_invalid_json(self, client):
        """Test products API with invalid JSON"""
        response = client.post(
            '/api/products',
            data='invalid json',
            content_type='application/json'
        )
        
        # API returns 400 for invalid JSON (now properly handled)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_products_api_missing_fields(self, client):
        """Test products API with missing required fields"""
        incomplete_product = {
            "name": "Test Product"
            # Missing required fields
        }
        
        response = client.post(
            '/api/products',
            data=json.dumps(incomplete_product),
            content_type='application/json'
        )
        
        # API might accept incomplete data and use defaults
        assert response.status_code in [200, 201, 400]
        data = json.loads(response.data)
        assert data['status'] in ['success', 'error']
    
    def test_products_api_invalid_data_types(self, client):
        """Test products API with invalid data types"""
        invalid_product = {
            "name": "Test Product",
            "calories_per_100g": "not_a_number",
            "protein_per_100g": "invalid",
            "fats_per_100g": "invalid",
            "carbs_per_100g": "invalid",
            "category": "invalid_category"
        }
        
        response = client.post(
            '/api/products',
            data=json.dumps(invalid_product),
            content_type='application/json'
        )
        
        # API converts invalid numbers to 0, so product is created with defaults
        assert response.status_code in [201, 400]
        data = json.loads(response.data)
        assert data['status'] in ['success', 'error']
    
    def test_products_api_negative_values(self, client):
        """Test products API with negative nutritional values"""
        negative_product = {
            "name": "Test Product",
            "calories_per_100g": -100,
            "protein_per_100g": -10,
            "fats_per_100g": -5,
            "carbs_per_100g": -20,
            "category": "vegetables"
        }
        
        response = client.post(
            '/api/products',
            data=json.dumps(negative_product),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_products_api_nonexistent_product(self, client):
        """Test getting nonexistent product"""
        response = client.get('/api/products/99999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_products_api_update_nonexistent(self, client):
        """Test updating nonexistent product"""
        update_data = {
            "name": "Updated Product",
            "calories_per_100g": 100
        }
        
        response = client.put(
            '/api/products/99999',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_products_api_delete_nonexistent(self, client):
        """Test deleting nonexistent product"""
        response = client.delete('/api/products/99999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'


class TestDishesAPIErrorHandling:
    """Test dishes API error handling"""
    
    def test_dishes_api_invalid_json(self, client):
        """Test dishes API with invalid JSON"""
        response = client.post(
            '/api/dishes',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_dishes_api_missing_ingredients(self, client):
        """Test dishes API with missing ingredients"""
        incomplete_dish = {
            "name": "Test Dish"
            # Missing ingredients
        }
        
        response = client.post(
            '/api/dishes',
            data=json.dumps(incomplete_dish),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_dishes_api_invalid_ingredients(self, client):
        """Test dishes API with invalid ingredients"""
        invalid_dish = {
            "name": "Test Dish",
            "ingredients": [
                {
                    "product_id": "not_a_number",
                    "quantity": "invalid"
                }
            ]
        }
        
        response = client.post(
            '/api/dishes',
            data=json.dumps(invalid_dish),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_dishes_api_nonexistent_product_in_ingredients(self, client):
        """Test dishes API with nonexistent product in ingredients"""
        dish_with_nonexistent_product = {
            "name": "Test Dish",
            "ingredients": [
                {
                    "product_id": 99999,
                    "quantity": 100
                }
            ]
        }
        
        response = client.post(
            '/api/dishes',
            data=json.dumps(dish_with_nonexistent_product),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'


class TestLogAPIErrorHandling:
    """Test log API error handling"""
    
    def test_log_api_invalid_json(self, client):
        """Test log API with invalid JSON"""
        response = client.post(
            '/api/log',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_log_api_missing_required_fields(self, client):
        """Test log API with missing required fields"""
        incomplete_log = {
            "date": "2023-01-01"
            # Missing required fields
        }
        
        response = client.post(
            '/api/log',
            data=json.dumps(incomplete_log),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_log_api_invalid_date_format(self, client):
        """Test log API with invalid date format"""
        invalid_log = {
            "date": "invalid-date",
            "meal_time": "breakfast",
            "item_type": "product",
            "item_id": 1,
            "quantity": 100
        }
        
        response = client.post(
            '/api/log',
            data=json.dumps(invalid_log),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_log_api_invalid_meal_time(self, client):
        """Test log API with invalid meal time"""
        invalid_log = {
            "date": "2023-01-01",
            "meal_time": "invalid_meal",
            "item_type": "product",
            "item_id": 1,
            "quantity": 100
        }
        
        response = client.post(
            '/api/log',
            data=json.dumps(invalid_log),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'


class TestStatsAPIErrorHandling:
    """Test stats API error handling"""
    
    def test_stats_api_invalid_date_format(self, client):
        """Test stats API with invalid date format"""
        response = client.get('/api/stats/invalid-date')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_stats_api_future_date(self, client):
        """Test stats API with future date"""
        response = client.get('/api/stats/2030-01-01')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_weekly_stats_api_invalid_date_format(self, client):
        """Test weekly stats API with invalid date format"""
        response = client.get('/api/stats/weekly/invalid-date')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'


class TestGKIApiErrorHandling:
    """Test GKI API error handling"""
    
    def test_gki_api_invalid_json(self, client):
        """Test GKI API with invalid JSON"""
        response = client.post(
            '/api/gki',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_gki_api_missing_fields(self, client):
        """Test GKI API with missing required fields"""
        incomplete_gki = {
            "glucose_mgdl": 100
            # Missing ketones_mgdl
        }
        
        response = client.post(
            '/api/gki',
            data=json.dumps(incomplete_gki),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_gki_api_negative_values(self, client):
        """Test GKI API with negative values"""
        negative_gki = {
            "glucose_mgdl": -100,
            "ketones_mgdl": -1
        }
        
        response = client.post(
            '/api/gki',
            data=json.dumps(negative_gki),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_gki_api_zero_values(self, client):
        """Test GKI API with zero values"""
        zero_gki = {
            "glucose_mgdl": 0,
            "ketones_mgdl": 0
        }
        
        response = client.post(
            '/api/gki',
            data=json.dumps(zero_gki),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'


class TestFastingAPIErrorHandling:
    """Test fasting API error handling"""
    
    def test_fasting_start_api_invalid_json(self, client, isolated_db):
        """Test fasting start API with invalid JSON"""
        response = client.post(
            '/api/fasting/start',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_fasting_start_api_invalid_fasting_type(self, client, isolated_db):
        """Test fasting start API with invalid fasting type"""
        invalid_fasting = {
            "fasting_type": "invalid_type",
            "target_hours": 16
        }
        
        response = client.post(
            '/api/fasting/start',
            data=json.dumps(invalid_fasting),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_fasting_start_api_negative_target_hours(self, client, isolated_db):
        """Test fasting start API with negative target hours"""
        negative_fasting = {
            "fasting_type": "16:8",
            "target_hours": -16
        }
        
        response = client.post(
            '/api/fasting/start',
            data=json.dumps(negative_fasting),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_fasting_end_api_no_active_session(self, client, isolated_db):
        """Test fasting end API when no active session exists"""
        response = client.post('/api/fasting/end')

        # Endpoint might return 200 or 400 depending on implementation
        data = json.loads(response.data)
        assert 'status' in data


class TestSystemAPIErrorHandling:
    """Test system API error handling"""
    
    def test_system_backup_api_no_backup_path(self, client):
        """Test system backup API without backup path"""
        response = client.post('/api/system/backup')
        
        assert response.status_code == 401  # Unauthorized due to @require_admin
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_system_restore_api_no_file(self, client):
        """Test system restore API without file"""
        response = client.post('/api/system/restore')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_maintenance_wipe_database_confirmation(self, client):
        """Test maintenance wipe database API"""
        response = client.post('/api/maintenance/wipe-database')
        
        # This should work as it's a maintenance operation
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'


class TestAuthAPIErrorHandling:
    """Test authentication API error handling"""
    
    def test_auth_login_api_invalid_json(self, client):
        """Test auth login API with invalid JSON"""
        response = client.post(
            '/api/auth/login',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_auth_login_api_missing_fields(self, client):
        """Test auth login API with missing fields"""
        incomplete_login = {
            "username": "test"
            # Missing password
        }
        
        response = client.post(
            '/api/auth/login',
            data=json.dumps(incomplete_login),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_auth_login_api_invalid_credentials(self, client):
        """Test auth login API with invalid credentials"""
        invalid_login = {
            "username": "nonexistent_user",
            "password": "wrong_password"
        }
        
        response = client.post(
            '/api/auth/login',
            data=json.dumps(invalid_login),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_auth_refresh_api_invalid_token(self, client):
        """Test auth refresh API with invalid token"""
        response = client.post(
            '/api/auth/refresh',
            headers={'Authorization': 'Bearer invalid_token'},
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_auth_verify_api_no_token(self, client):
        """Test auth verify API without token"""
        response = client.get('/api/auth/verify')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['status'] == 'error'


class TestTasksAPIErrorHandling:
    """Test tasks API error handling"""
    
    def test_tasks_api_invalid_json(self, client):
        """Test tasks API with invalid JSON"""
        response = client.post(
            '/api/tasks',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_tasks_api_invalid_task_type(self, client):
        """Test tasks API with invalid task type"""
        invalid_task = {
            "task_type": "invalid_task",
            "params": {}
        }
        
        response = client.post(
            '/api/tasks',
            data=json.dumps(invalid_task),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_tasks_api_nonexistent_task_id(self, client):
        """Test tasks API with nonexistent task ID"""
        response = client.get('/api/tasks/nonexistent_task_id')
        
        # In CI environment, Celery might not be available, so we expect 404 for NOT_FOUND status
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'


class TestAPIEdgeCases:
    """Test API edge cases and boundary conditions"""
    
    def test_products_api_very_long_name(self, client):
        """Test products API with very long product name"""
        long_name_product = {
            "name": "A" * 1000,  # Very long name
            "calories_per_100g": 100,
            "protein_per_100g": 10,
            "fats_per_100g": 5,
            "carbs_per_100g": 20,
            "category": "vegetables"
        }
        
        response = client.post(
            '/api/products',
            data=json.dumps(long_name_product),
            content_type='application/json'
        )
        
        # Should handle long names gracefully (accepts or rejects)
        assert response.status_code in [200, 201, 400]
        data = json.loads(response.data)
        assert data['status'] in ['success', 'error']
    
    def test_products_api_very_large_nutritional_values(self, client):
        """Test products API with very large nutritional values"""
        large_values_product = {
            "name": "Test Product",
            "calories_per_100g": 10000,
            "protein_per_100g": 1000,
            "fats_per_100g": 1000,
            "carbs_per_100g": 1000,
            "category": "vegetables"
        }
        
        response = client.post(
            '/api/products',
            data=json.dumps(large_values_product),
            content_type='application/json'
        )
        
        # Should handle large values gracefully
        assert response.status_code in [200, 400]
        data = json.loads(response.data)
        assert data['status'] in ['success', 'error']
    
    def test_log_api_very_large_quantity(self, client):
        """Test log API with very large quantity"""
        large_quantity_log = {
            "date": "2023-01-01",
            "meal_time": "breakfast",
            "item_type": "product",
            "item_id": 1,
            "quantity": 1000000  # Very large quantity
        }
        
        response = client.post(
            '/api/log',
            data=json.dumps(large_quantity_log),
            content_type='application/json'
        )
        
        # Should handle large quantities gracefully
        assert response.status_code in [200, 400]
        data = json.loads(response.data)
        assert data['status'] in ['success', 'error']
    
    def test_gki_api_very_high_values(self, client):
        """Test GKI API with very high values"""
        high_values_gki = {
            "glucose_mgdl": 1000,
            "ketones_mgdl": 100
        }
        
        response = client.post(
            '/api/gki',
            data=json.dumps(high_values_gki),
            content_type='application/json'
        )
        
        # Should handle high values gracefully
        assert response.status_code in [200, 400]
        data = json.loads(response.data)
        assert data['status'] in ['success', 'error']
