"""
Integration tests for products routes.
Tests for routes/products.py endpoints.
"""

import json
from unittest.mock import patch


class TestProductsRoutes:
    """Test products route endpoints"""

    def test_get_products_with_keto_calculation_error(self, client, app):
        """Test GET products with error in keto calculation"""
        # First create a product
        product_data = {
            'name': 'Test Product for Keto Error',
            'protein_per_100g': 20.0,
            'fat_per_100g': 10.0,
            'carbs_per_100g': 30.0,
            'calories_per_100g': 300
        }

        create_response = client.post(
            '/api/products',
            data=json.dumps(product_data),
            content_type='application/json'
        )
        assert create_response.status_code == 201

        # Mock keto calculation to raise exception
        with patch('routes.products.calculate_net_carbs_advanced', side_effect=Exception('Keto calc error')):
            response = client.get('/api/products')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
            # Product should still be returned with default values
            products = data['data']
            assert len(products) > 0

    def test_post_product_duplicate_name(self, client, app):
        """Test POST product with duplicate name"""
        # Create first product
        product_data = {
            'name': 'Duplicate Product Name',
            'protein_per_100g': 20.0,
            'fat_per_100g': 10.0,
            'carbs_per_100g': 30.0,
            'calories_per_100g': 300
        }

        response1 = client.post(
            '/api/products',
            data=json.dumps(product_data),
            content_type='application/json'
        )
        assert response1.status_code == 201

        # Try to create product with same name
        response2 = client.post(
            '/api/products',
            data=json.dumps(product_data),
            content_type='application/json'
        )

        assert response2.status_code == 400
        data = json.loads(response2.data)
        assert data['status'] == 'error'

    def test_post_product_integrity_error_unique_constraint(self, client, app):
        """Test POST product with IntegrityError for unique constraint"""
        # Create a product
        product_data = {
            'name': 'Product For Integrity Test',
            'protein_per_100g': 20.0,
            'fat_per_100g': 10.0,
            'carbs_per_100g': 30.0,
            'calories_per_100g': 300
        }

        create_response = client.post(
            '/api/products',
            data=json.dumps(product_data),
            content_type='application/json'
        )
        assert create_response.status_code == 201

        # Try to create duplicate (should trigger UNIQUE constraint)
        duplicate_response = client.post(
            '/api/products',
            data=json.dumps(product_data),
            content_type='application/json'
        )

        assert duplicate_response.status_code == 400
        data = json.loads(duplicate_response.data)
        assert data['status'] == 'error'

    def test_post_product_database_error(self, client, app):
        """Test POST product with database error"""
        product_data = {
            'name': 'Product For DB Error',
            'protein_per_100g': 20.0,
            'fat_per_100g': 10.0,
            'carbs_per_100g': 30.0,
            'calories_per_100g': 300
        }

        # Mock database execute to raise sqlite3.Error
        with patch('routes.products.get_db') as mock_get_db:
            import sqlite3
            mock_db = mock_get_db.return_value
            mock_db.execute.side_effect = sqlite3.Error('Database error')

            response = client.post(
                '/api/products',
                data=json.dumps(product_data),
                content_type='application/json'
            )

            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['status'] == 'error'

    def test_post_product_unexpected_error(self, client, app):
        """Test POST product with unexpected error"""
        product_data = {
            'name': 'Product For Unexpected Error',
            'protein_per_100g': 20.0,
            'fat_per_100g': 10.0,
            'carbs_per_100g': 30.0,
            'calories_per_100g': 300
        }

        # Mock validate_product_data to raise unexpected exception
        with patch('routes.products.validate_product_data', side_effect=Exception('Unexpected error')):
            response = client.post(
                '/api/products',
                data=json.dumps(product_data),
                content_type='application/json'
            )

            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['status'] == 'error'

    def test_delete_product_with_log_entries(self, client, app):
        """Test DELETE product that has log entries"""
        # First create a product
        product_data = {
            'name': 'Product To Delete With Logs',
            'protein_per_100g': 20.0,
            'fat_per_100g': 10.0,
            'carbs_per_100g': 30.0,
            'calories_per_100g': 300
        }

        create_response = client.post(
            '/api/products',
            data=json.dumps(product_data),
            content_type='application/json'
        )
        assert create_response.status_code == 201
        product_id = json.loads(create_response.data)['data']['id']

        # Create a log entry using this product
        log_data = {
            'date': '2025-10-21',
            'meal_time': 'breakfast',
            'item_type': 'product',
            'item_id': product_id,
            'quantity_grams': 100
        }

        log_response = client.post(
            '/api/log',
            data=json.dumps(log_data),
            content_type='application/json'
        )
        assert log_response.status_code == 201

        # Try to delete the product
        response = client.delete(f'/api/products/{product_id}')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'used in' in data['message']

    def test_update_product_invalid_json(self, client, app):
        """Test PUT product with invalid JSON"""
        # First create a product
        product_data = {
            'name': 'Product To Update',
            'protein_per_100g': 20.0,
            'fat_per_100g': 10.0,
            'carbs_per_100g': 30.0,
            'calories_per_100g': 300
        }

        create_response = client.post(
            '/api/products',
            data=json.dumps(product_data),
            content_type='application/json'
        )
        assert create_response.status_code == 201
        product_id = json.loads(create_response.data)['data']['id']

        # Try to update with invalid JSON
        response = client.put(
            f'/api/products/{product_id}',
            data='invalid json',
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Invalid JSON' in data['message']

    def test_update_product_missing_name(self, client, app):
        """Test PUT product with missing name"""
        # First create a product
        product_data = {
            'name': 'Product To Update',
            'protein_per_100g': 20.0,
            'fat_per_100g': 10.0,
            'carbs_per_100g': 30.0,
            'calories_per_100g': 300
        }

        create_response = client.post(
            '/api/products',
            data=json.dumps(product_data),
            content_type='application/json'
        )
        assert create_response.status_code == 201
        product_id = json.loads(create_response.data)['data']['id']

        # Try to update with empty name
        update_data = {
            'name': '',
            'protein_per_100g': 25.0,
            'fat_per_100g': 15.0,
            'carbs_per_100g': 35.0
        }

        response = client.put(
            f'/api/products/{product_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'

    def test_update_product_calculate_calories_from_macros(self, client, app):
        """Test PUT product with calories = 0 (should calculate from macros)"""
        # First create a product
        product_data = {
            'name': 'Product For Calorie Calc',
            'protein_per_100g': 20.0,
            'fat_per_100g': 10.0,
            'carbs_per_100g': 30.0,
            'calories_per_100g': 300
        }

        create_response = client.post(
            '/api/products',
            data=json.dumps(product_data),
            content_type='application/json'
        )
        assert create_response.status_code == 201
        product_id = json.loads(create_response.data)['data']['id']

        # Update with calories = 0 (should calculate from macros)
        update_data = {
            'name': 'Updated Product',
            'protein_per_100g': 25.0,
            'fat_per_100g': 15.0,
            'carbs_per_100g': 35.0,
            'calories_per_100g': 0
        }

        response = client.put(
            f'/api/products/{product_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        # Calories should be calculated from macros (protein*4 + fat*9 + carbs*4)
        # 25*4 + 15*9 + 35*4 = 100 + 135 + 140 = 375
        assert data['data']['calories_per_100g'] > 0

    def test_update_product_invalid_nutrition_values(self, client, app):
        """Test PUT product with invalid nutrition values"""
        # First create a product
        product_data = {
            'name': 'Product For Invalid Update',
            'protein_per_100g': 20.0,
            'fat_per_100g': 10.0,
            'carbs_per_100g': 30.0,
            'calories_per_100g': 300
        }

        create_response = client.post(
            '/api/products',
            data=json.dumps(product_data),
            content_type='application/json'
        )
        assert create_response.status_code == 201
        product_id = json.loads(create_response.data)['data']['id']

        # Try to update with invalid nutrition values (protein > 100)
        update_data = {
            'name': 'Updated Product',
            'protein_per_100g': 150.0,  # Invalid: > 100
            'fat_per_100g': 15.0,
            'carbs_per_100g': 35.0,
            'calories_per_100g': 400
        }

        response = client.put(
            f'/api/products/{product_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'

    def test_update_product_duplicate_name(self, client, app):
        """Test PUT product with duplicate name"""
        # Create first product
        product1_data = {
            'name': 'Product One',
            'protein_per_100g': 20.0,
            'fat_per_100g': 10.0,
            'carbs_per_100g': 30.0,
            'calories_per_100g': 300
        }

        response1 = client.post(
            '/api/products',
            data=json.dumps(product1_data),
            content_type='application/json'
        )
        assert response1.status_code == 201

        # Create second product
        product2_data = {
            'name': 'Product Two',
            'protein_per_100g': 25.0,
            'fat_per_100g': 15.0,
            'carbs_per_100g': 35.0,
            'calories_per_100g': 400
        }

        response2 = client.post(
            '/api/products',
            data=json.dumps(product2_data),
            content_type='application/json'
        )
        assert response2.status_code == 201
        product2_id = json.loads(response2.data)['data']['id']

        # Try to update product2 with product1's name
        update_data = {
            'name': 'Product One',  # Duplicate
            'protein_per_100g': 30.0,
            'fat_per_100g': 20.0,
            'carbs_per_100g': 40.0,
            'calories_per_100g': 500
        }

        response = client.put(
            f'/api/products/{product2_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'

    def test_update_product_exception_handling(self, client, app):
        """Test PUT product with exception"""
        # First create a product
        product_data = {
            'name': 'Product For Exception',
            'protein_per_100g': 20.0,
            'fat_per_100g': 10.0,
            'carbs_per_100g': 30.0,
            'calories_per_100g': 300
        }

        create_response = client.post(
            '/api/products',
            data=json.dumps(product_data),
            content_type='application/json'
        )
        assert create_response.status_code == 201
        product_id = json.loads(create_response.data)['data']['id']

        # Mock database to raise exception
        with patch('routes.products.get_db') as mock_get_db:
            mock_db = mock_get_db.return_value
            mock_db.execute.side_effect = Exception('Database error')

            update_data = {
                'name': 'Updated Product',
                'protein_per_100g': 25.0,
                'fat_per_100g': 15.0,
                'carbs_per_100g': 35.0,
                'calories_per_100g': 400
            }

            response = client.put(
                f'/api/products/{product_id}',
                data=json.dumps(update_data),
                content_type='application/json'
            )

            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['status'] == 'error'
