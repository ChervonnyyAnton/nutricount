-- Nutrition Tracker Database Schema v2.0
-- SQLite with WAL mode for better concurrency

PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 1000;
PRAGMA foreign_keys = ON;

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    calories_per_100g REAL NOT NULL DEFAULT 0,
    protein_per_100g REAL NOT NULL DEFAULT 0,
    fat_per_100g REAL NOT NULL DEFAULT 0,
    carbs_per_100g REAL NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_calories CHECK (calories_per_100g >= 0 AND calories_per_100g <= 9999),
    CONSTRAINT chk_protein CHECK (protein_per_100g >= 0 AND protein_per_100g <= 100),
    CONSTRAINT chk_fat CHECK (fat_per_100g >= 0 AND fat_per_100g <= 100),
    CONSTRAINT chk_carbs CHECK (carbs_per_100g >= 0 AND carbs_per_100g <= 100)
);

-- Dishes table
CREATE TABLE IF NOT EXISTS dishes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    description TEXT,
    total_weight_grams REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Dish ingredients relationship
CREATE TABLE IF NOT EXISTS dish_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dish_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity_grams REAL NOT NULL,
    FOREIGN KEY (dish_id) REFERENCES dishes(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    CONSTRAINT chk_quantity CHECK (quantity_grams > 0)
);

-- Food log entries
CREATE TABLE IF NOT EXISTS log_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    item_type TEXT NOT NULL CHECK (item_type IN ('product', 'dish')),
    item_id INTEGER NOT NULL,
    quantity_grams REAL NOT NULL,
    meal_time TEXT CHECK (meal_time IN ('breakfast', 'lunch', 'dinner', 'snack')),
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_log_quantity CHECK (quantity_grams > 0)
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_dishes_name ON dishes(name);
CREATE INDEX IF NOT EXISTS idx_log_date ON log_entries(date);
CREATE INDEX IF NOT EXISTS idx_log_date_meal ON log_entries(date, meal_time);
CREATE INDEX IF NOT EXISTS idx_dish_ingredients_dish ON dish_ingredients(dish_id);

-- Views for easier querying
CREATE VIEW IF NOT EXISTS log_entries_with_details AS
SELECT 
    le.*,
    CASE 
        WHEN le.item_type = 'product' THEN p.name
        WHEN le.item_type = 'dish' THEN d.name
    END as item_name,
    CASE 
        WHEN le.item_type = 'product' THEN (p.calories_per_100g * le.quantity_grams / 100.0)
        WHEN le.item_type = 'dish' THEN (
            SELECT COALESCE(SUM(p2.calories_per_100g * di.quantity_grams / 100.0), 0) * le.quantity_grams / d.total_weight_grams
            FROM dish_ingredients di
            JOIN products p2 ON di.product_id = p2.id
            WHERE di.dish_id = le.item_id
        )
        ELSE 0
    END as calculated_calories,
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
    -- Dish nutrition data per 100g (calculated based on total weight)
    CASE 
        WHEN le.item_type = 'dish' AND d.total_weight_grams > 0 THEN
            (SELECT COALESCE(SUM(p2.protein_per_100g * di.quantity_grams / 100.0), 0) FROM dish_ingredients di JOIN products p2 ON di.product_id = p2.id WHERE di.dish_id = le.item_id) * 100.0 / d.total_weight_grams
        ELSE NULL
    END as dish_protein_per_100g,
    CASE 
        WHEN le.item_type = 'dish' AND d.total_weight_grams > 0 THEN
            (SELECT COALESCE(SUM(p2.fat_per_100g * di.quantity_grams / 100.0), 0) FROM dish_ingredients di JOIN products p2 ON di.product_id = p2.id WHERE di.dish_id = le.item_id) * 100.0 / d.total_weight_grams
        ELSE NULL
    END as dish_fat_per_100g,
    CASE 
        WHEN le.item_type = 'dish' AND d.total_weight_grams > 0 THEN
            (SELECT COALESCE(SUM(p2.carbs_per_100g * di.quantity_grams / 100.0), 0) FROM dish_ingredients di JOIN products p2 ON di.product_id = p2.id WHERE di.dish_id = le.item_id) * 100.0 / d.total_weight_grams
        ELSE NULL
    END as dish_carbs_per_100g
FROM log_entries le
LEFT JOIN products p ON le.item_type = 'product' AND le.item_id = p.id
LEFT JOIN dishes d ON le.item_type = 'dish' AND le.item_id = d.id;

-- Sample data
INSERT OR IGNORE INTO products (name, calories_per_100g, protein_per_100g, fat_per_100g, carbs_per_100g) VALUES
('Chicken Breast', 165, 31, 3.6, 0),
('Avocado', 160, 2, 14.7, 8.5),
('Broccoli', 34, 2.8, 0.4, 7),
('Olive Oil', 884, 0, 100, 0),
('Almonds', 579, 21.2, 49.9, 21.6);
