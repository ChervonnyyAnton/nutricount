"""
Unit tests for init_db.py
"""

import pytest
from unittest.mock import patch, Mock, mock_open, MagicMock
import tempfile
import os
import sqlite3
from pathlib import Path
from init_db import init_database


class TestInitDatabase:
    """Test init_database function"""
    
    def test_init_database_new_database(self):
        """Test database initialization for new database"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            
            with patch('init_db.Config') as mock_config, \
                 patch('init_db.os.path.exists', return_value=False), \
                 patch('builtins.open', mock_open(read_data="CREATE TABLE products (id INTEGER PRIMARY KEY);")) as mock_file:
                
                mock_config.DATABASE = db_path
                
                # Mock os.makedirs
                with patch('init_db.os.makedirs') as mock_makedirs:
                    init_database()
                    
                    mock_makedirs.assert_called_once()
                    mock_file.assert_called_once_with('schema_v2.sql', 'r')
    
    def test_init_database_existing_database_up_to_date(self):
        """Test database initialization when database exists and is up to date"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            
            with patch('init_db.Config') as mock_config, \
                 patch('init_db.os.path.exists', return_value=True):
                
                mock_config.DATABASE = db_path
                
                # Mock database connection and queries
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_conn.execute.return_value = mock_cursor
                mock_cursor.fetchone.side_effect = [
                    ('products',),  # products table exists
                    ('fasting_sessions',),  # fasting_sessions table exists
                    (5,),  # products count
                    (10,)  # log_entries count
                ]
                
                with patch('init_db.sqlite3.connect', return_value=mock_conn):
                    init_database()
                    
                    # Verify that the function checked for tables
                    assert mock_conn.execute.call_count >= 2
    
    def test_init_database_existing_database_missing_fasting_tables(self):
        """Test database initialization when database exists but fasting tables are missing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            
            with patch('init_db.Config') as mock_config, \
                 patch('init_db.os.path.exists', return_value=True):
                
                mock_config.DATABASE = db_path
                
                # Mock database connection and queries
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_conn.execute.return_value = mock_cursor
                mock_cursor.fetchone.side_effect = [
                    ('products',),  # products table exists
                    None,  # fasting_sessions table doesn't exist
                    (5,),  # products count after schema recreation
                ]
                
                with patch('init_db.sqlite3.connect', return_value=mock_conn), \
                     patch('builtins.open', mock_open(read_data="CREATE TABLE products (id INTEGER PRIMARY KEY);")) as mock_file:
                    
                    init_database()
                    
                    # Verify that schema was recreated
                    mock_file.assert_called_once_with('schema_v2.sql', 'r')
                    mock_conn.executescript.assert_called_once()
                    mock_conn.commit.assert_called_once()
    
    def test_init_database_existing_database_missing_schema(self):
        """Test database initialization when database exists but schema is missing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            
            with patch('init_db.Config') as mock_config, \
                 patch('init_db.os.path.exists', return_value=True):
                
                mock_config.DATABASE = db_path
                
                # Mock database connection and queries
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_conn.execute.return_value = mock_cursor
                mock_cursor.fetchone.side_effect = [
                    None,  # No products table
                    (5,),  # products count after schema recreation
                ]
                
                with patch('init_db.sqlite3.connect', return_value=mock_conn), \
                     patch('builtins.open', mock_open(read_data="CREATE TABLE products (id INTEGER PRIMARY KEY);")) as mock_file:
                    
                    init_database()
                    
                    # Verify that schema was recreated
                    mock_file.assert_called_once_with('schema_v2.sql', 'r')
                    mock_conn.executescript.assert_called_once()
                    mock_conn.commit.assert_called_once()
    
    def test_init_database_exception_during_check(self):
        """Test database initialization when exception occurs during database check"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            
            with patch('init_db.Config') as mock_config, \
                 patch('init_db.os.path.exists', return_value=True):
                
                mock_config.DATABASE = db_path
                
                # Mock database connection that raises exception during check
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_conn.execute.return_value = mock_cursor
                mock_cursor.fetchone.side_effect = [
                    Exception("Database error"),  # First call raises exception
                    (5,),  # products count after schema recreation
                ]
                
                with patch('init_db.sqlite3.connect', return_value=mock_conn), \
                     patch('builtins.open', mock_open(read_data="CREATE TABLE products (id INTEGER PRIMARY KEY);")) as mock_file:
                    
                    init_database()
                    
                    # Verify that schema was recreated after exception
                    mock_file.assert_called_once_with('schema_v2.sql', 'r')
                    mock_conn.executescript.assert_called_once()
                    mock_conn.commit.assert_called_once()
    
    def test_init_database_schema_file_not_found(self):
        """Test database initialization when schema file is not found"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            
            with patch('init_db.Config') as mock_config, \
                 patch('init_db.os.path.exists', return_value=False):
                
                mock_config.DATABASE = db_path
                
                with patch('init_db.os.makedirs'), \
                     patch('builtins.open', side_effect=FileNotFoundError("Schema file not found")):
                    
                    with pytest.raises(FileNotFoundError):
                        init_database()
    
    def test_init_database_schema_execution_error(self):
        """Test database initialization when schema execution fails"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            
            with patch('init_db.Config') as mock_config, \
                 patch('init_db.os.path.exists', return_value=False):
                
                mock_config.DATABASE = db_path
                
                # Mock database connection that fails on schema execution
                mock_conn = Mock()
                mock_conn.executescript.side_effect = sqlite3.Error("Schema execution failed")
                
                with patch('init_db.os.makedirs'), \
                     patch('builtins.open', mock_open(read_data="INVALID SQL;")), \
                     patch('init_db.sqlite3.connect', return_value=mock_conn):
                    
                    with pytest.raises(sqlite3.Error):
                        init_database()
    
    def test_init_database_success_with_sample_data(self):
        """Test successful database initialization with sample data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            
            with patch('init_db.Config') as mock_config, \
                 patch('init_db.os.path.exists', return_value=False):
                
                mock_config.DATABASE = db_path
                
                # Mock database connection
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_conn.execute.return_value = mock_cursor
                mock_cursor.fetchone.return_value = (15,)  # Sample products count
                
                with patch('init_db.os.makedirs'), \
                     patch('builtins.open', mock_open(read_data="CREATE TABLE products (id INTEGER PRIMARY KEY);")), \
                     patch('init_db.sqlite3.connect', return_value=mock_conn):
                    
                    init_database()
                    
                    # Verify that the function completed successfully
                    mock_conn.commit.assert_called_once()
                    mock_conn.close.assert_called_once()
    
    def test_init_database_directory_creation(self):
        """Test that database directory is created if it doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "nonexistent", "test.db")
            
            with patch('init_db.Config') as mock_config, \
                 patch('init_db.os.path.exists', return_value=False):
                
                mock_config.DATABASE = db_path
                
                with patch('init_db.os.makedirs') as mock_makedirs, \
                     patch('builtins.open', mock_open(read_data="CREATE TABLE products (id INTEGER PRIMARY KEY);")), \
                     patch('init_db.sqlite3.connect') as mock_connect:
                    
                    init_database()
                    
                    # Verify that directory was created
                    mock_makedirs.assert_called_once_with(os.path.dirname(db_path), exist_ok=True)
    
    def test_init_database_connection_closed_on_exception(self):
        """Test that database connection is closed even when exception occurs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            
            with patch('init_db.Config') as mock_config, \
                 patch('init_db.os.path.exists', return_value=True):
                
                mock_config.DATABASE = db_path
                
                # Mock database connection that raises exception during check
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_conn.execute.return_value = mock_cursor
                mock_cursor.fetchone.side_effect = [
                    Exception("Database error"),  # First call raises exception
                    (5,),  # products count after schema recreation
                ]
                
                with patch('init_db.sqlite3.connect', return_value=mock_conn), \
                     patch('builtins.open', mock_open(read_data="CREATE TABLE products (id INTEGER PRIMARY KEY);")):
                    
                    init_database()
                    
                    # Verify that connection was closed even after exception
                    assert mock_conn.close.call_count >= 1
