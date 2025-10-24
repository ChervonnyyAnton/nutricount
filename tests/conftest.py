"""
Test configuration and fixtures for Nutrition Tracker
"""
import os
import tempfile
import pytest
from flask import Flask
from unittest.mock import Mock, patch

# Add src to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app as flask_app
from src.config import Config


@pytest.fixture
def app():
    """Create application for testing"""
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp()
    
    # Override config for testing
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': db_path,
        'SECRET_KEY': 'test-secret-key',
        'REDIS_URL': 'redis://localhost:6379/1',  # Use different Redis DB
        'CELERY_BROKER_URL': 'redis://localhost:6379/2',
        'CELERY_RESULT_BACKEND': 'redis://localhost:6379/2',
    })
    
    # Initialize database with schema
    with flask_app.app_context():
        from app import init_db
        init_db()
        
        # Clear test data that might be inserted by schema
        db = flask_app.config['DATABASE']
        import sqlite3
        conn = sqlite3.connect(db)
        # Clear all tables to ensure clean state
        conn.execute("DELETE FROM products")
        conn.execute("DELETE FROM user_profile")
        conn.execute("DELETE FROM dishes")
        conn.execute("DELETE FROM dish_ingredients")
        conn.execute("DELETE FROM log_entries")
        conn.execute("DELETE FROM gki_measurements")
        conn.execute("DELETE FROM fasting_sessions")
        conn.execute("DELETE FROM fasting_goals")
        conn.execute("DELETE FROM fasting_settings")
        conn.commit()
        conn.close()

        # Clear cache to ensure clean state
        from src.cache_manager import cache_manager
        cache_manager.clear()

    yield flask_app

    # Clear cache after test
    from src.cache_manager import cache_manager
    cache_manager.clear()

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def mock_redis():
    """Mock Redis for testing"""
    with patch('src.cache_manager.redis.Redis') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        mock_instance.get.return_value = None
        mock_instance.set.return_value = True
        mock_instance.delete.return_value = True
        mock_instance.ping.return_value = True
        yield mock_instance


@pytest.fixture
def mock_celery():
    """Mock Celery for testing"""
    with patch('src.task_manager.celery') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        mock_instance.send_task.return_value = Mock(id='test-task-id')
        yield mock_instance


@pytest.fixture
def sample_product():
    """Sample product data for testing"""
    return {
        'name': 'Test Product',
        'calories_per_100g': 100.0,
        'protein_per_100g': 10.0,
        'fat_per_100g': 5.0,
        'carbs_per_100g': 15.0,
        'fiber_per_100g': 3.0,
        'sugars_per_100g': 2.0,
        'category': 'meat',
        'processing_level': 'raw',
        'glycemic_index': 50,
        'region': 'US'
    }


@pytest.fixture
def sample_dish():
    """Sample dish data for testing"""
    return {
        'name': 'Test Dish',
        'description': 'Test dish description',
        'ingredients': [
            {'product_id': 1, 'quantity_grams': 100.0}
        ]
    }


@pytest.fixture
def sample_log_entry():
    """Sample log entry data for testing"""
    return {
        'date': '2025-01-01',
        'item_type': 'product',
        'item_id': 1,
        'quantity_grams': 150.0,
        'meal_time': 'breakfast',
        'notes': 'Test log entry'
    }


@pytest.fixture
def sample_fasting_session():
    """Sample fasting session data for testing"""
    return {
        'fasting_type': '16:8',
        'notes': 'Test fasting session'
    }


@pytest.fixture
def auth_headers():
    """Authentication headers for testing"""
    return {
        'Authorization': 'Bearer test-token'
    }


@pytest.fixture
def mock_jwt():
    """Mock JWT for testing"""
    with patch('src.security.jwt') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        mock_instance.encode.return_value = 'test-token'
        mock_instance.decode.return_value = {
            'user_id': 1,
            'username': 'testuser',
            'is_admin': False
        }
        yield mock_instance


@pytest.fixture
def isolated_db():
    """Fixture to create isolated database for tests that need it"""
    import tempfile
    import os
    import sqlite3
    
    # Create a new temporary database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    # Store original database path
    original_db = flask_app.config.get('DATABASE')
    
    # Set new database path
    flask_app.config['DATABASE'] = db_path
    
    # Initialize database with schema
    with flask_app.app_context():
        from app import init_db
        init_db()
    
    yield db_path
    
    # Cleanup: close file descriptor and remove temporary file
    os.close(db_fd)
    try:
        os.unlink(db_path)
    except OSError:
        pass  # File might already be deleted
    
    # Restore original database path
    if original_db:
        flask_app.config['DATABASE'] = original_db
