-- Migration 010: Add cooked_weight_grams to dishes table
-- This field stores the weight of the dish after cooking, accounting for yield factors

-- Add cooked_weight_grams column to dishes table
ALTER TABLE dishes ADD COLUMN cooked_weight_grams REAL DEFAULT NULL;

-- Update existing dishes to have cooked_weight_grams = total_weight_grams (assuming no cooking)
UPDATE dishes SET cooked_weight_grams = total_weight_grams WHERE cooked_weight_grams IS NULL;

-- Add constraint to ensure cooked_weight_grams is reasonable
-- (should be between 0.1 and 10 times the raw weight)
-- Note: SQLite doesn't support complex CHECK constraints with subqueries,
-- so we'll rely on application logic for validation
