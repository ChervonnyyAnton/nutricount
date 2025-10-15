-- Migration to add fiber and category fields to products table (with existence checks)

-- Add fiber_per_100g column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pragma_table_info('products') WHERE name = 'fiber_per_100g') THEN
        ALTER TABLE products ADD COLUMN fiber_per_100g REAL DEFAULT NULL;
    END IF;
END $$;

-- Add category column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pragma_table_info('products') WHERE name = 'category') THEN
        ALTER TABLE products ADD COLUMN category TEXT DEFAULT NULL;
    END IF;
END $$;

-- Add glycemic_index column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pragma_table_info('products') WHERE name = 'glycemic_index') THEN
        ALTER TABLE products ADD COLUMN glycemic_index REAL DEFAULT NULL;
    END IF;
END $$;

-- Add check constraints (SQLite doesn't support IF NOT EXISTS for constraints, so we'll skip if they exist)
-- Note: SQLite has limited ALTER TABLE support, so we'll handle constraints differently

-- Update existing products with estimated fiber based on carbs (conservative approach)
UPDATE products 
SET fiber_per_100g = CASE 
    WHEN carbs_per_100g > 0 THEN carbs_per_100g * 0.1  -- 10% conservative estimate
    ELSE 0
END,
category = 'unknown'
WHERE fiber_per_100g IS NULL;

-- Create index for category for faster queries
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
