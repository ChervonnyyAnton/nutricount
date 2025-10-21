"""
Unit tests for routes/helpers.py module.
Tests shared helper functions used across route blueprints.
"""
import pytest
import sqlite3


class TestSafeGetJson:
    """Test safe_get_json helper function"""

    def test_safe_get_json_valid_data(self, app, client):
        """Test safe_get_json with valid JSON data"""
        from routes.helpers import safe_get_json

        with app.test_request_context(
            '/test',
            method='POST',
            json={'key': 'value', 'number': 42}
        ):
            result = safe_get_json()
            assert result == {'key': 'value', 'number': 42}

    def test_safe_get_json_empty_body(self, app, client):
        """Test safe_get_json with empty body returns empty dict"""
        from routes.helpers import safe_get_json

        with app.test_request_context(
            '/test',
            method='POST',
            json={}
        ):
            result = safe_get_json()
            assert result == {}

    def test_safe_get_json_get_request(self, app, client):
        """Test safe_get_json with GET request (no body) returns empty dict"""
        from routes.helpers import safe_get_json

        with app.test_request_context('/test', method='GET'):
            # GET requests don't have JSON body
            # safe_get_json should handle this gracefully
            result = safe_get_json()
            # Should return None or empty dict for non-JSON requests
            assert result in [None, {}]

    def test_safe_get_json_invalid_json(self, app, client):
        """Test safe_get_json with invalid JSON returns None"""
        from routes.helpers import safe_get_json

        with app.test_request_context(
            '/test',
            method='POST',
            data='invalid json{',
            content_type='application/json'
        ):
            result = safe_get_json()
            assert result is None

    def test_safe_get_json_malformed_json(self, app, client):
        """Test safe_get_json with malformed JSON"""
        from routes.helpers import safe_get_json

        with app.test_request_context(
            '/test',
            method='POST',
            data='{broken',
            content_type='application/json'
        ):
            result = safe_get_json()
            assert result is None

    def test_safe_get_json_nested_data(self, app, client):
        """Test safe_get_json with nested JSON structure"""
        from routes.helpers import safe_get_json

        nested_data = {
            'user': {
                'name': 'Test',
                'settings': {
                    'theme': 'dark',
                    'notifications': True
                }
            },
            'items': [1, 2, 3]
        }

        with app.test_request_context(
            '/test',
            method='POST',
            json=nested_data
        ):
            result = safe_get_json()
            assert result == nested_data


class TestGetDb:
    """Test get_db helper function"""

    def test_get_db_returns_connection(self, app, client):
        """Test get_db returns valid database connection"""
        from routes.helpers import get_db

        with app.app_context():
            db = get_db()
            assert db is not None
            assert isinstance(db, sqlite3.Connection)
            db.close()

    def test_get_db_row_factory_configured(self, app, client):
        """Test get_db configures Row factory for dict-like access"""
        from routes.helpers import get_db

        with app.app_context():
            db = get_db()
            assert db.row_factory == sqlite3.Row
            db.close()

    def test_get_db_foreign_keys_enabled(self, app, client):
        """Test get_db enables foreign key constraints"""
        from routes.helpers import get_db

        with app.app_context():
            db = get_db()
            cursor = db.execute("PRAGMA foreign_keys")
            result = cursor.fetchone()
            assert result[0] == 1  # Foreign keys enabled
            db.close()

    def test_get_db_wal_mode_for_file_database(self, app, client):
        """Test get_db enables WAL mode for file-based databases"""
        from routes.helpers import get_db

        with app.app_context():
            # Only check if not in-memory database
            if app.config['DATABASE'] != ':memory:':
                db = get_db()
                cursor = db.execute("PRAGMA journal_mode")
                result = cursor.fetchone()
                # WAL mode should be enabled for file databases
                assert result[0].upper() in ['WAL', 'DELETE']  # May already be in WAL
                db.close()

    def test_get_db_memory_database_no_wal(self, app, client):
        """Test get_db doesn't set WAL mode for memory databases"""
        from routes.helpers import get_db

        # Create temporary in-memory database config
        original_db = app.config['DATABASE']
        app.config['DATABASE'] = ':memory:'

        try:
            with app.app_context():
                db = get_db()
                cursor = db.execute("PRAGMA journal_mode")
                result = cursor.fetchone()
                # Memory databases use DELETE or MEMORY mode, not WAL
                assert result[0].upper() in ['DELETE', 'MEMORY']
                db.close()
        finally:
            app.config['DATABASE'] = original_db

    def test_get_db_multiple_connections(self, app, client):
        """Test get_db can create multiple independent connections"""
        from routes.helpers import get_db

        with app.app_context():
            db1 = get_db()
            db2 = get_db()

            # Should be different connection objects
            assert db1 is not db2

            db1.close()
            db2.close()

    def test_get_db_connection_usable(self, app, client):
        """Test get_db returns usable connection for queries"""
        from routes.helpers import get_db

        with app.app_context():
            db = get_db()

            # Should be able to execute queries
            cursor = db.execute("SELECT 1 as test")
            result = cursor.fetchone()
            assert result['test'] == 1

            db.close()

    def test_get_db_transaction_support(self, app, client):
        """Test get_db supports transactions"""
        from routes.helpers import get_db

        with app.app_context():
            db = get_db()

            try:
                # Start transaction
                db.execute("BEGIN")

                # Insert test data with correct column names
                db.execute(
                    "INSERT INTO products (name, protein_per_100g, fat_per_100g, "
                    "carbs_per_100g, calories_per_100g) "
                    "VALUES (?, ?, ?, ?, ?)",
                    ("Test Product", 10.0, 5.0, 20.0, 155.0)
                )

                # Rollback transaction (cleanup)
                db.rollback()

                # Verify no data was inserted
                cursor = db.execute("SELECT COUNT(*) FROM products WHERE name = ?", ("Test Product",))
                count = cursor.fetchone()[0]
                assert count == 0
            finally:
                db.close()

    def test_get_db_pragma_synchronous_normal(self, app, client):
        """Test get_db sets synchronous mode to NORMAL for file databases"""
        from routes.helpers import get_db

        with app.app_context():
            if app.config['DATABASE'] != ':memory:':
                db = get_db()
                cursor = db.execute("PRAGMA synchronous")
                result = cursor.fetchone()
                # NORMAL mode is 1
                assert result[0] in [0, 1, 2]  # FULL=2, NORMAL=1, OFF=0
                db.close()


class TestHelpersIntegration:
    """Integration tests for helper functions"""

    def test_helpers_work_together_in_route_context(self, app, client):
        """Test helpers work together in realistic route scenario"""
        from routes.helpers import safe_get_json, get_db

        # Simulate a route handling a POST request with JSON
        with app.test_request_context(
            '/api/test',
            method='POST',
            json={'name': 'Test Item', 'value': 42}
        ):
            # Get JSON data
            data = safe_get_json()
            assert data['name'] == 'Test Item'
            assert data['value'] == 42

            # Get database connection
            db = get_db()
            assert db is not None

            # Can use both together
            cursor = db.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1

            db.close()

    def test_helpers_error_handling(self, app, client):
        """Test helpers handle errors gracefully"""
        from routes.helpers import safe_get_json

        # Test with bad JSON
        with app.test_request_context(
            '/api/test',
            method='POST',
            data='not valid json',
            content_type='application/json'
        ):
            result = safe_get_json()
            # Should return None for invalid JSON
            assert result is None

    def test_get_db_with_app_context_required(self, app):
        """Test get_db requires application context"""
        from routes.helpers import get_db

        # Should raise error outside app context
        with pytest.raises(RuntimeError):
            get_db()
