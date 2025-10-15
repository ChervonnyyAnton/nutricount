#!/usr/bin/env python3
"""
Migration script to safely add fiber and category fields to products table
"""

import sqlite3
import os

def column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def main():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'nutrition.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check and add fiber_per_100g column
        if not column_exists(cursor, 'products', 'fiber_per_100g'):
            print("  Adding fiber_per_100g column...")
            cursor.execute("ALTER TABLE products ADD COLUMN fiber_per_100g REAL DEFAULT NULL")
        else:
            print("  fiber_per_100g column already exists")
        
        # Check and add category column
        if not column_exists(cursor, 'products', 'category'):
            print("  Adding category column...")
            cursor.execute("ALTER TABLE products ADD COLUMN category TEXT DEFAULT NULL")
        else:
            print("  category column already exists")
        
        # Check and add glycemic_index column
        if not column_exists(cursor, 'products', 'glycemic_index'):
            print("  Adding glycemic_index column...")
            cursor.execute("ALTER TABLE products ADD COLUMN glycemic_index REAL DEFAULT NULL")
        else:
            print("  glycemic_index column already exists")
        
        # Update existing products with estimated fiber
        print("  Updating existing products with estimated fiber...")
        cursor.execute("""
            UPDATE products 
            SET fiber_per_100g = CASE 
                WHEN carbs_per_100g > 0 THEN carbs_per_100g * 0.1
                ELSE 0
            END,
            category = 'unknown'
            WHERE fiber_per_100g IS NULL
        """)
        
        # Create index for category
        print("  Creating index for category...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
        
        conn.commit()
        print("✅ Migration 007 completed successfully")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
