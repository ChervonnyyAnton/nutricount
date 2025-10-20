"""
Unit tests for config.py
"""

from unittest.mock import patch
from src.config import Config


class TestConfigMethods:
    """Test Config class methods"""

    def test_is_development_when_development(self):
        """Test is_development returns True in development mode"""
        with patch.object(Config, 'FLASK_ENV', 'development'):
            assert Config.is_development() is True

    def test_is_development_when_production(self):
        """Test is_development returns False in production mode"""
        with patch.object(Config, 'FLASK_ENV', 'production'):
            assert Config.is_development() is False

    def test_is_production_when_production(self):
        """Test is_production returns True in production mode"""
        with patch.object(Config, 'FLASK_ENV', 'production'):
            assert Config.is_production() is True

    def test_is_production_when_development(self):
        """Test is_production returns False in development mode"""
        with patch.object(Config, 'FLASK_ENV', 'development'):
            assert Config.is_production() is False
