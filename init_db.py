#!/usr/bin/env python3
"""Database initialization script"""

import sqlite3
import os
from src.config import Config

def init_database():
    """Initialize the database with schema"""
    print("🗄️ Checking database...")
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(Config.DATABASE), exist_ok=True)
    
    # Check if database already exists
    db_exists = os.path.exists(Config.DATABASE)
    
    if db_exists:
        print("📊 Database already exists, checking schema...")
        
        # Connect and check if tables exist
        conn = sqlite3.connect(Config.DATABASE)
        try:
            # Check for essential tables
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
            if cursor.fetchone():
                # Check for fasting tables
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fasting_sessions'")
                if cursor.fetchone():
                    print("✅ Database schema is up to date")
                    
                    # Show current data count
                    cursor = conn.execute("SELECT COUNT(*) FROM products")
                    count = cursor.fetchone()[0]
                    print(f"📊 Products in database: {count}")
                    
                    cursor = conn.execute("SELECT COUNT(*) FROM log_entries")
                    log_count = cursor.fetchone()[0]
                    print(f"📊 Log entries: {log_count}")
                    
                    return  # Database is fine, no need to recreate
                else:
                    print("⚠️ Database exists but fasting tables are missing, updating schema...")
            else:
                print("⚠️ Database exists but schema is missing, recreating...")
        except Exception as e:
            print(f"⚠️ Database check failed: {e}, recreating...")
        finally:
            conn.close()
    
    # Create or recreate database
    print("🔄 Creating/updating database schema...")
    conn = sqlite3.connect(Config.DATABASE)
    
    try:
        # Read and execute schema v2
        with open('schema_v2.sql', 'r') as f:
            schema = f.read()
        
        conn.executescript(schema)
        conn.commit()
        
        print("✅ Database initialized successfully")
        
        # Show sample data count
        cursor = conn.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        print(f"📊 Sample products loaded: {count}")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()
