"""
Shared helper functions for route blueprints.
Provides common utilities for database access and request handling.
"""

import sqlite3

from flask import current_app, request
from werkzeug.exceptions import BadRequest, UnsupportedMediaType


def safe_get_json():
    """Safely get JSON data from request, handling invalid JSON gracefully

    Returns:
        dict: Parsed JSON data or empty dict if invalid/missing
        None: If JSON parsing completely fails or content-type is not JSON
    """
    try:
        return request.get_json() or {}
    except (BadRequest, UnsupportedMediaType):
        return None


def get_db():
    """Get database connection with proper configuration

    Returns:
        sqlite3.Connection: Configured database connection with:
            - Row factory for dict-like access
            - WAL mode for better concurrency (file databases only)
            - Foreign key constraints enabled
    """
    db = sqlite3.connect(current_app.config["DATABASE"])
    db.row_factory = sqlite3.Row

    # Enable WAL mode for better concurrency (only for file databases)
    if current_app.config["DATABASE"] != ":memory:":
        db.execute("PRAGMA journal_mode = WAL")
        db.execute("PRAGMA synchronous = NORMAL")

    db.execute("PRAGMA foreign_keys = ON")

    return db
