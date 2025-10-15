#!/usr/bin/env python3
"""Database migration script"""

import sqlite3
import os
import glob
from datetime import datetime

def get_db_connection():
    """Get database connection"""
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.config import Config
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_migrations_table():
    """Create migrations tracking table"""
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            executed_at DATETIME NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_executed_migrations():
    """Get list of executed migrations"""
    conn = get_db_connection()
    try:
        result = conn.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        ).fetchall()
        return [row['version'] for row in result]
    except sqlite3.OperationalError:
        # Table doesn't exist yet
        return []
    finally:
        conn.close()

def run_migration(migration_file):
    """Run a single migration file"""
    print(f"  Running {migration_file}...")
    
    with open(migration_file, 'r') as f:
        sql = f.read()
    
    conn = get_db_connection()
    try:
        conn.executescript(sql)
        
        # Record migration as executed
        filename = os.path.basename(migration_file)
        version = int(filename.split('_')[0])
        name = filename.replace('.sql', '')
        
        conn.execute(
            "INSERT INTO schema_migrations (version, name, executed_at) VALUES (?, ?, datetime('now'))",
            (version, name)
        )
        
        conn.commit()
        print(f"  ✅ {migration_file} completed")
    except Exception as e:
        conn.rollback()
        print(f"  ❌ {migration_file} failed: {e}")
        raise
    finally:
        conn.close()

def main():
    """Run database migrations"""
    print("🔄 Running database migrations...")
    
    # Create migrations table
    create_migrations_table()
    
    # Get executed migrations
    executed = get_executed_migrations()
    print(f"Already executed migrations: {executed}")
    
    # Find migration files
    migration_files = sorted(glob.glob('migrations/*.sql'))
    
    if not migration_files:
        print("No migration files found.")
        return
    
    # Run pending migrations
    pending = 0
    for migration_file in migration_files:
        # Extract version from filename (e.g., "001_initial.sql" -> 1)
        filename = os.path.basename(migration_file)
        try:
            version = int(filename.split('_')[0])
        except (IndexError, ValueError):
            print(f"⚠️  Skipping {migration_file} - invalid filename format")
            continue
        
        if version not in executed:
            run_migration(migration_file)
            pending += 1
    
    if pending == 0:
        print("✅ Database is up to date!")
    else:
        print(f"✅ Applied {pending} migration(s)")

if __name__ == "__main__":
    main()
