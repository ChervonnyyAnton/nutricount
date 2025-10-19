# Configuration for Nutrition Tracker
# Keep it simple - just constants and basic settings

import os



    class Config:
    # App basics
    APP_NAME = "Nutrition Tracker"
        VERSION = "2.0.0"

    # Flask settings
        SECRET_KEY = os.environ.get("SECRET_KEY") or ""
    FLASK_ENV = os.environ.get("FLASK_ENV") or "development"

    # Database
        DATABASE = (os.environ.get("DATABASE_URL") or \
            "sqlite:///data/nutrition.db").replace("sqlite:///", "")

    # Limits (prevent abuse)
        MAX_PRODUCTS = 1000
    MAX_DISHES = 500
    MAX_LOG_ENTRIES_PER_DAY = 50
        MAX_PRODUCT_NAME_LENGTH = 100
    MAX_DISH_NAME_LENGTH = 100

    # Cache settings
        CACHE_TIMEOUT = 3600  # 1 hour
    STATIC_CACHE_TIMEOUT = 86400  # 24 hours

    # API settings
        API_PER_PAGE = 50
    API_MAX_PER_PAGE = 200

    # File sizes
        MAX_BACKUP_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_LOG_SIZE = 50 * 1024 * 1024  # 50MB

    # Health check
        HEALTH_CHECK_TIMEOUT = 5  # seconds

    @staticmethod
        def is_development():
        return Config.FLASK_ENV == "development"

    @staticmethod
        def is_production():
        return Config.FLASK_ENV == "production"
