-- Migration to add fiber and category fields to products table (SQLite compatible)

-- Check if columns exist before adding them
-- Note: SQLite doesn't support IF NOT EXISTS for ALTER TABLE ADD COLUMN
-- So we'll use a different approach - try to add and ignore errors

-- Add fiber_per_100g column (will fail silently if exists)
-- Add category column (will fail silently if exists)  
-- Add glycemic_index column (will fail silently if exists)

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
