#!/usr/bin/env python3
"""Database initialization script"""

import sqlite3
import os
from src.config import Config

def init_database():
    """Initialize the database with schema"""
    print("🗄️ Initializing database...")
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(Config.DATABASE), exist_ok=True)
    
    # Connect and initialize
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
