-- Migration 009: Update schema to v2.1 according to NUTRIENTS.md
-- This migration adds new fields and tables for advanced nutrition calculations

-- Add new columns to products table
ALTER TABLE products ADD COLUMN fiber_per_100g REAL DEFAULT NULL;
ALTER TABLE products ADD COLUMN sugars_per_100g REAL DEFAULT NULL;
ALTER TABLE products ADD COLUMN category TEXT DEFAULT NULL;
ALTER TABLE products ADD COLUMN processing_level TEXT DEFAULT NULL;
ALTER TABLE products ADD COLUMN glycemic_index REAL DEFAULT NULL;
ALTER TABLE products ADD COLUMN region TEXT DEFAULT 'US';
ALTER TABLE products ADD COLUMN net_carbs_per_100g REAL DEFAULT NULL;
ALTER TABLE products ADD COLUMN keto_index REAL DEFAULT NULL;
ALTER TABLE products ADD COLUMN keto_category TEXT DEFAULT NULL;
ALTER TABLE products ADD COLUMN carbs_score REAL DEFAULT NULL;
ALTER TABLE products ADD COLUMN fat_score REAL DEFAULT NULL;
ALTER TABLE products ADD COLUMN quality_score REAL DEFAULT NULL;
ALTER TABLE products ADD COLUMN gi_score REAL DEFAULT NULL;
ALTER TABLE products ADD COLUMN fiber_estimated BOOLEAN DEFAULT FALSE;
ALTER TABLE products ADD COLUMN fiber_deduction_coefficient REAL DEFAULT NULL;

-- Add new columns to dishes table
ALTER TABLE dishes ADD COLUMN servings INTEGER DEFAULT 1;
ALTER TABLE dishes ADD COLUMN calories_per_100g REAL DEFAULT 0;
ALTER TABLE dishes ADD COLUMN protein_per_100g REAL DEFAULT 0;
ALTER TABLE dishes ADD COLUMN fat_per_100g REAL DEFAULT 0;
ALTER TABLE dishes ADD COLUMN carbs_per_100g REAL DEFAULT 0;
ALTER TABLE dishes ADD COLUMN fiber_per_100g REAL DEFAULT NULL;
ALTER TABLE dishes ADD COLUMN net_carbs_per_100g REAL DEFAULT NULL;
ALTER TABLE dishes ADD COLUMN keto_index REAL DEFAULT NULL;
ALTER TABLE dishes ADD COLUMN keto_category TEXT DEFAULT NULL;
ALTER TABLE dishes ADD COLUMN cooking_method TEXT DEFAULT NULL;
ALTER TABLE dishes ADD COLUMN yield_factor REAL DEFAULT 1.0;

-- Add new columns to dish_ingredients table
ALTER TABLE dish_ingredients ADD COLUMN preparation_method TEXT DEFAULT 'raw';
ALTER TABLE dish_ingredients ADD COLUMN edible_portion REAL DEFAULT 1.0;
ALTER TABLE dish_ingredients ADD COLUMN calories_contribution REAL DEFAULT 0;
ALTER TABLE dish_ingredients ADD COLUMN protein_contribution REAL DEFAULT 0;
ALTER TABLE dish_ingredients ADD COLUMN fat_contribution REAL DEFAULT 0;
ALTER TABLE dish_ingredients ADD COLUMN carbs_contribution REAL DEFAULT 0;

-- Add new columns to log_entries table
ALTER TABLE log_entries ADD COLUMN calories REAL DEFAULT 0;
ALTER TABLE log_entries ADD COLUMN protein REAL DEFAULT 0;
ALTER TABLE log_entries ADD COLUMN fat REAL DEFAULT 0;
ALTER TABLE log_entries ADD COLUMN carbs REAL DEFAULT 0;
ALTER TABLE log_entries ADD COLUMN net_carbs REAL DEFAULT NULL;
ALTER TABLE log_entries ADD COLUMN keto_index REAL DEFAULT NULL;

-- Create user_profile table
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gender TEXT NOT NULL CHECK (gender IN ('male', 'female')),
    birth_date DATE NOT NULL,
    height_cm INTEGER NOT NULL CHECK (height_cm >= 100 AND height_cm <= 250),
    weight_kg REAL NOT NULL CHECK (weight_kg >= 30 AND weight_kg <= 500),
    activity_level TEXT NOT NULL CHECK (activity_level IN (
        'sedentary', 'light', 'moderate', 'active', 'very_active'
    )),
    goal TEXT NOT NULL CHECK (goal IN (
        'weight_loss_aggressive', 'weight_loss', 'maintenance', 'muscle_gain'
    )),
    body_fat_percentage REAL DEFAULT NULL CHECK (body_fat_percentage IS NULL OR (body_fat_percentage >= 5 AND body_fat_percentage <= 50)),
    lean_body_mass_kg REAL DEFAULT NULL CHECK (lean_body_mass_kg IS NULL OR lean_body_mass_kg >= 20),
    bmr REAL DEFAULT NULL,
    tdee REAL DEFAULT NULL,
    target_calories REAL DEFAULT NULL,
    keto_type TEXT DEFAULT 'standard' CHECK (keto_type IN ('strict', 'standard', 'moderate')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create GKI measurements table
CREATE TABLE IF NOT EXISTS gki_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    glucose_mgdl REAL NOT NULL CHECK (glucose_mgdl > 0 AND glucose_mgdl <= 500),
    ketones_mgdl REAL NOT NULL CHECK (ketones_mgdl > 0 AND ketones_mgdl <= 10),
    glucose_mmol REAL NOT NULL,
    ketones_mmol REAL NOT NULL,
    gki REAL NOT NULL,
    gki_category TEXT NOT NULL,
    measurement_context TEXT DEFAULT 'fasting' CHECK (measurement_context IN (
        'fasting', 'post_meal', 'post_exercise', 'bedtime', 'other'
    )),
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create new indexes
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_keto_index ON products(keto_index);
CREATE INDEX IF NOT EXISTS idx_dishes_keto_index ON dishes(keto_index);
CREATE INDEX IF NOT EXISTS idx_log_item ON log_entries(item_type, item_id);
CREATE INDEX IF NOT EXISTS idx_dish_ingredients_product ON dish_ingredients(product_id);
CREATE INDEX IF NOT EXISTS idx_gki_date ON gki_measurements(date);
CREATE INDEX IF NOT EXISTS idx_user_profile_updated ON user_profile(updated_at);

-- Update existing sample data with new fields
UPDATE products SET 
    category = CASE 
        WHEN name = 'Chicken Breast' THEN 'meat'
        WHEN name = 'Avocado' THEN 'avocado_olives'
        WHEN name = 'Broccoli' THEN 'cruciferous'
        WHEN name = 'Olive Oil' THEN 'oil'
        WHEN name = 'Almonds' THEN 'nuts_seeds'
        ELSE 'unknown'
    END,
    processing_level = CASE 
        WHEN name IN ('Chicken Breast', 'Olive Oil', 'Almonds') THEN 'minimal'
        WHEN name IN ('Avocado', 'Broccoli') THEN 'raw'
        ELSE 'processed'
    END,
    glycemic_index = CASE 
        WHEN name IN ('Chicken Breast', 'Olive Oil') THEN 0
        WHEN name IN ('Avocado', 'Broccoli', 'Almonds') THEN 15
        ELSE 50
    END
WHERE category IS NULL;

-- Add fiber data for existing products
UPDATE products SET fiber_per_100g = 6.7 WHERE name = 'Avocado';
UPDATE products SET fiber_per_100g = 2.6 WHERE name = 'Broccoli';
UPDATE products SET fiber_per_100g = 12.5 WHERE name = 'Almonds';

-- Insert sample user profile
INSERT OR IGNORE INTO user_profile (gender, birth_date, height_cm, weight_kg, activity_level, goal, keto_type) VALUES
('male', '1993-01-01', 185, 121.8, 'moderate', 'weight_loss', 'standard');

-- Update the log_entries_with_details view
DROP VIEW IF EXISTS log_entries_with_details;

CREATE VIEW IF NOT EXISTS log_entries_with_details AS
SELECT 
    le.*,
    CASE 
        WHEN le.item_type = 'product' THEN p.name
        WHEN le.item_type = 'dish' THEN d.name
    END as item_name,
    -- Product nutrition data
    CASE 
        WHEN le.item_type = 'product' THEN p.calories_per_100g
        ELSE NULL
    END as calories_per_100g,
    CASE 
        WHEN le.item_type = 'product' THEN p.protein_per_100g
        ELSE NULL
    END as protein_per_100g,
    CASE 
        WHEN le.item_type = 'product' THEN p.fat_per_100g
        ELSE NULL
    END as fat_per_100g,
    CASE 
        WHEN le.item_type = 'product' THEN p.carbs_per_100g
        ELSE NULL
    END as carbs_per_100g,
    CASE 
        WHEN le.item_type = 'product' THEN p.fiber_per_100g
        ELSE NULL
    END as fiber_per_100g,
    CASE 
        WHEN le.item_type = 'product' THEN p.net_carbs_per_100g
        ELSE NULL
    END as net_carbs_per_100g,
    CASE 
        WHEN le.item_type = 'product' THEN p.keto_index
        ELSE NULL
    END as keto_index_per_100g,
    -- Dish nutrition data per 100g
    CASE 
        WHEN le.item_type = 'dish' THEN d.calories_per_100g
        ELSE NULL
    END as dish_calories_per_100g,
    CASE 
        WHEN le.item_type = 'dish' THEN d.protein_per_100g
        ELSE NULL
    END as dish_protein_per_100g,
    CASE 
        WHEN le.item_type = 'dish' THEN d.fat_per_100g
        ELSE NULL
    END as dish_fat_per_100g,
    CASE 
        WHEN le.item_type = 'dish' THEN d.carbs_per_100g
        ELSE NULL
    END as dish_carbs_per_100g,
    CASE 
        WHEN le.item_type = 'dish' THEN d.fiber_per_100g
        ELSE NULL
    END as dish_fiber_per_100g,
    CASE 
        WHEN le.item_type = 'dish' THEN d.net_carbs_per_100g
        ELSE NULL
    END as dish_net_carbs_per_100g,
    CASE 
        WHEN le.item_type = 'dish' THEN d.keto_index
        ELSE NULL
    END as dish_keto_index_per_100g,
    -- Calculated calories for the entry
    CASE 
        WHEN le.item_type = 'product' THEN (p.calories_per_100g * le.quantity_grams / 100.0)
        WHEN le.item_type = 'dish' THEN (d.calories_per_100g * le.quantity_grams / 100.0)
        ELSE 0
    END as calculated_calories
FROM log_entries le
LEFT JOIN products p ON le.item_type = 'product' AND le.item_id = p.id
LEFT JOIN dishes d ON le.item_type = 'dish' AND le.item_id = d.id;

-- Create daily nutrition summary view
CREATE VIEW IF NOT EXISTS daily_nutrition_summary AS
SELECT 
    date,
    COUNT(*) as entries_count,
    SUM(calories) as total_calories,
    SUM(protein) as total_protein,
    SUM(fat) as total_fat,
    SUM(carbs) as total_carbs,
    SUM(net_carbs) as total_net_carbs,
    AVG(keto_index) as avg_keto_index,
    -- Meal breakdown
    SUM(CASE WHEN meal_time = 'breakfast' THEN calories ELSE 0 END) as breakfast_calories,
    SUM(CASE WHEN meal_time = 'lunch' THEN calories ELSE 0 END) as lunch_calories,
    SUM(CASE WHEN meal_time = 'dinner' THEN calories ELSE 0 END) as dinner_calories,
    SUM(CASE WHEN meal_time = 'snack' THEN calories ELSE 0 END) as snack_calories
FROM log_entries
GROUP BY date
ORDER BY date DESC;
