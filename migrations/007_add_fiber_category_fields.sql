-- Migration to add fiber and category fields to products table
ALTER TABLE products ADD COLUMN fiber_per_100g REAL DEFAULT NULL;
ALTER TABLE products ADD COLUMN category TEXT DEFAULT NULL;
ALTER TABLE products ADD COLUMN glycemic_index REAL DEFAULT NULL;

-- Add check constraints
ALTER TABLE products ADD CONSTRAINT check_fiber_valid CHECK (fiber_per_100g IS NULL OR (fiber_per_100g >= 0 AND fiber_per_100g <= carbs_per_100g));
ALTER TABLE products ADD CONSTRAINT check_category_valid CHECK (category IS NULL OR category IN ('leafy_vegetables', 'cruciferous', 'nuts_seeds', 'berries', 'processed', 'unknown'));
ALTER TABLE products ADD CONSTRAINT check_glycemic_index_valid CHECK (glycemic_index IS NULL OR (glycemic_index >= 0 AND glycemic_index <= 100));

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
