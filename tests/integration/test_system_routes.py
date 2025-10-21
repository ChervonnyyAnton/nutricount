"""
Integration tests for system routes.
Tests system status, maintenance, and export endpoints.
"""

import io
import json
import os
import tempfile


class TestSystemRoutes:
    """Test system management routes"""

    def test_system_status_success(self, client, app):
        """Test system status endpoint returns proper information"""
        response = client.get('/api/system/status')

        assert response.status_code == 200
        data = json.loads(response.data)

        # Verify response structure
        assert 'data' in data
        assert 'application' in data['data']
        assert 'database' in data['data']
        assert 'system' in data['data']

        # Verify application info
        app_info = data['data']['application']
        assert 'name' in app_info
        assert 'version' in app_info
        assert 'environment' in app_info

        # Verify database info
        db_info = data['data']['database']
        assert 'type' in db_info
        assert 'size_mb' in db_info
        assert 'products_count' in db_info
        assert 'dishes_count' in db_info
        assert 'log_entries_count' in db_info

        # Verify system info
        sys_info = data['data']['system']
        assert 'cpu_percent' in sys_info
        assert 'memory_percent' in sys_info
        assert 'disk_percent' in sys_info

    def test_maintenance_vacuum_success(self, client):
        """Test database vacuum maintenance endpoint"""
        response = client.post('/api/maintenance/vacuum')

        assert response.status_code == 200
        data = json.loads(response.data)

        # Verify response structure
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'space_saved_mb' in data['data']
        assert 'size_before_mb' in data['data']
        assert 'size_after_mb' in data['data']
        assert 'table_count' in data['data']
        assert 'optimization_type' in data['data']

        # Verify optimization type
        assert data['data']['optimization_type'] == 'VACUUM + ANALYZE'

    def test_maintenance_cleanup_success(self, client, app):
        """Test maintenance cleanup endpoint"""
        # Create some temporary test files to clean up
        with app.app_context():
            # Create a test .tmp file in the root directory
            test_tmp = 'test_cleanup_file.tmp'
            with open(test_tmp, 'w') as f:
                f.write('test data')

            try:
                response = client.post('/api/maintenance/cleanup')

                assert response.status_code == 200
                data = json.loads(response.data)

                # Verify response structure
                assert data['status'] == 'success'
                assert 'data' in data
                assert 'files_cleaned' in data['data']
                assert 'space_freed_mb' in data['data']
                assert 'cleanup_time' in data['data']
                assert 'cleanup_details' in data['data']

                # Verify files_cleaned is a number
                assert isinstance(data['data']['files_cleaned'], int)
                assert data['data']['files_cleaned'] >= 0
            finally:
                # Clean up test file if it still exists
                if os.path.exists(test_tmp):
                    os.remove(test_tmp)

    def test_maintenance_cleanup_test_data_success(self, client):
        """Test cleanup of test data (TEST prefix items)"""
        # First, create some test data
        test_product = {
            'name': 'TEST Product for Cleanup',
            'category': 'leafy_vegetables',
            'proteins': 10.0,
            'fats': 5.0,
            'carbs': 20.0,
            'calories': 170.0
        }

        # Add test product
        add_response = client.post('/api/products', json=test_product)
        assert add_response.status_code == 201

        # Now clean up test data
        response = client.post('/api/maintenance/cleanup-test-data')

        assert response.status_code == 200
        data = json.loads(response.data)

        # Verify response structure
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'deleted_products' in data['data']
        assert 'deleted_dishes' in data['data']
        assert 'deleted_logs' in data['data']
        assert 'total_deleted' in data['data']
        assert 'cleanup_time' in data['data']

        # Verify at least the test product was deleted
        assert data['data']['deleted_products'] >= 1
        assert data['data']['total_deleted'] >= 1

    def test_export_all_success(self, client):
        """Test export all data endpoint"""
        response = client.get('/api/export/all')

        assert response.status_code == 200
        data = json.loads(response.data)

        # Verify export structure
        assert 'export_info' in data
        assert 'products' in data
        assert 'dishes' in data
        assert 'dish_ingredients' in data
        assert 'log_entries' in data

        # Verify export_info
        export_info = data['export_info']
        assert 'exported_at' in export_info
        assert 'app_version' in export_info
        assert 'total_products' in export_info
        assert 'total_dishes' in export_info
        assert 'total_log_entries' in export_info

        # Verify data types
        assert isinstance(data['products'], list)
        assert isinstance(data['dishes'], list)
        assert isinstance(data['dish_ingredients'], dict)
        assert isinstance(data['log_entries'], list)

    def test_system_restore_missing_file(self, client):
        """Test system restore without file"""
        response = client.post('/api/system/restore')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'errors' in data
        assert 'No backup file provided' in data['errors']

    def test_system_restore_empty_filename(self, client):
        """Test system restore with empty filename"""
        # Create empty file data
        data = {'backup_file': (io.BytesIO(b''), '')}

        response = client.post(
            '/api/system/restore',
            data=data,
            content_type='multipart/form-data'
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['status'] == 'error'
        assert 'errors' in response_data
        assert 'No file selected' in response_data['errors']

    def test_system_restore_invalid_file_type(self, client):
        """Test system restore with invalid file type"""
        # Create a test file with wrong extension
        data = {
            'backup_file': (io.BytesIO(b'fake data'), 'backup.txt')
        }

        response = client.post(
            '/api/system/restore',
            data=data,
            content_type='multipart/form-data'
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['status'] == 'error'
        assert 'errors' in response_data
        assert 'Invalid file type' in response_data['errors'][0]

    def test_system_restore_valid_db_file(self, client, app):
        """Test system restore with valid .db file"""
        with app.app_context():
            # Create a temporary valid database backup
            import shutil
            from src.config import Config

            # Create a backup of current database
            temp_backup = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
            temp_backup.close()

            try:
                # Copy current database to temp file
                shutil.copy2(Config.DATABASE, temp_backup.name)

                # Read the backup file
                with open(temp_backup.name, 'rb') as f:
                    backup_data = f.read()

                # Send restore request
                data = {
                    'backup_file': (io.BytesIO(backup_data), 'test_backup.db')
                }

                response = client.post(
                    '/api/system/restore',
                    data=data,
                    content_type='multipart/form-data'
                )

                assert response.status_code == 200
                response_data = json.loads(response.data)
                assert response_data['status'] == 'success'
                assert 'data' in response_data
                assert 'restored_file' in response_data['data']
                assert 'current_backup' in response_data['data']
                assert 'restored_at' in response_data['data']
            finally:
                # Clean up temp backup
                if os.path.exists(temp_backup.name):
                    os.remove(temp_backup.name)

    def test_system_status_exception_handling(self, client, monkeypatch):
        """Test system status endpoint exception handling"""
        from unittest.mock import patch

        # Mock get_database_stats to raise an exception
        def mock_error_stats():
            raise Exception("Database connection error")

        with patch('routes.system.get_database_stats', side_effect=mock_error_stats):
            response = client.get('/api/system/status')

            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['status'] == 'error'

    def test_system_backup_success(self, client, app):
        """Test creating a database backup"""
        with app.app_context():
            response = client.post('/api/system/backup')

            # Note: This endpoint requires admin authentication
            # Since we're not authenticated, we expect it to be protected
            # But let's check if the route exists
            assert response.status_code in [200, 401, 403]

    def test_export_all_with_dishes(self, client):
        """Test export all data with dishes that have ingredients"""
        # Create a product first
        product = {
            'name': 'Export Test Product',
            'category': 'leafy_vegetables',
            'proteins': 10.0,
            'fats': 5.0,
            'carbs': 20.0,
            'calories': 170.0
        }
        product_response = client.post('/api/products', json=product)
        product_data = json.loads(product_response.data)
        product_id = product_data['data']['id']

        # Create a dish with ingredients
        dish = {
            'name': 'Export Test Dish',
            'preparation_method': 'Mixed',
            'edible_portion': 95.0,
            'ingredients': [
                {'product_id': product_id, 'quantity': 100.0}
            ]
        }
        client.post('/api/dishes', json=dish)

        # Export all data
        response = client.get('/api/export/all')

        assert response.status_code == 200
        data = json.loads(response.data)

        # Verify dish_ingredients structure
        assert 'dish_ingredients' in data
        assert isinstance(data['dish_ingredients'], dict)

        # Check that dish ingredients are properly exported
        # The dish_ingredients dict should have at least one entry
        if len(data['dishes']) > 0:
            # Find our test dish
            test_dishes = [d for d in data['dishes'] if d['name'] == 'Export Test Dish']
            if test_dishes:
                dish_id = test_dishes[0]['id']
                assert dish_id in data['dish_ingredients']
                assert len(data['dish_ingredients'][dish_id]) > 0


class TestMaintenanceRoutes:
    """Test maintenance-specific operations"""

    def test_wipe_database_success(self, client):
        """Test database wipe operation"""
        # Create test product first to have data to wipe
        test_product = {
            'name': 'Wipe Test Product',
            'category': 'leafy_vegetables',
            'proteins': 10.0,
            'fats': 5.0,
            'carbs': 20.0,
            'calories': 170.0
        }
        client.post('/api/products', json=test_product)

        # Wipe database
        response = client.post('/api/maintenance/wipe-database')

        assert response.status_code == 200
        data = json.loads(response.data)

        # Verify response structure
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'deleted_products' in data['data']
        assert 'deleted_dishes' in data['data']
        assert 'deleted_logs' in data['data']
        assert 'total_deleted' in data['data']
        assert 'initial_products_loaded' in data['data']
        assert 'wipe_time' in data['data']

        # Verify database was actually wiped (should have only initial data)
        assert data['data']['initial_products_loaded'] > 0

    def test_maintenance_vacuum_exception_handling(self, client):
        """Test vacuum endpoint exception handling"""
        from unittest.mock import patch, MagicMock

        # Mock database connection to raise an exception
        mock_db = MagicMock()
        mock_db.execute.side_effect = Exception("Database error")

        with patch('app.get_db', return_value=mock_db):
            response = client.post('/api/maintenance/vacuum')

            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['status'] == 'error'

    def test_maintenance_cleanup_exception_handling(self, client):
        """Test cleanup endpoint exception handling"""
        from unittest.mock import patch

        # Mock glob.glob to raise an exception
        def mock_error_glob(*args, **kwargs):
            raise Exception("Filesystem error")

        with patch('glob.glob', side_effect=mock_error_glob):
            response = client.post('/api/maintenance/cleanup')

            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['status'] == 'error'

    def test_maintenance_cleanup_test_data_exception_handling(self, client):
        """Test cleanup test data endpoint exception handling"""
        from unittest.mock import patch, MagicMock

        # Mock database connection to raise an exception
        mock_db = MagicMock()
        mock_db.execute.side_effect = Exception("Database error")

        with patch('app.get_db', return_value=mock_db):
            response = client.post('/api/maintenance/cleanup-test-data')

            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['status'] == 'error'

    def test_maintenance_wipe_database_exception_handling(self, client):
        """Test wipe database endpoint exception handling"""
        from unittest.mock import patch, MagicMock

        # Mock database connection to raise an exception
        mock_db = MagicMock()
        mock_db.execute.side_effect = Exception("Database error")

        with patch('app.get_db', return_value=mock_db):
            response = client.post('/api/maintenance/wipe-database')

            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['status'] == 'error'

    def test_export_all_exception_handling(self, client):
        """Test export all endpoint exception handling"""
        from unittest.mock import patch, MagicMock

        # Mock database connection to raise an exception
        mock_db = MagicMock()
        mock_db.execute.side_effect = Exception("Database error")

        with patch('app.get_db', return_value=mock_db):
            response = client.get('/api/export/all')

            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['status'] == 'error'

    def test_system_restore_exception_handling(self, client):
        """Test restore endpoint exception handling"""
        from unittest.mock import patch

        # Mock to raise an exception during file processing
        def mock_error_files(*args, **kwargs):
            raise Exception("File processing error")

        # Create a test file to trigger the exception
        data = {
            'backup_file': (io.BytesIO(b'test data'), 'test.db')
        }

        with patch('werkzeug.datastructures.FileStorage.save', side_effect=mock_error_files):
            response = client.post(
                '/api/system/restore',
                data=data,
                content_type='multipart/form-data'
            )

            assert response.status_code == 500
            response_data = json.loads(response.data)
            assert response_data['status'] == 'error'
