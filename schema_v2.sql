-- Nutrition Tracker Database Schema v2.1
-- SQLite with WAL mode for better concurrency
-- Updated according to NUTRIENTS.md specifications

PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 1000;
PRAGMA foreign_keys = ON;

-- Products table with enhanced fields for advanced calculations
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    calories_per_100g REAL NOT NULL DEFAULT 0,
    protein_per_100g REAL NOT NULL DEFAULT 0,
    fat_per_100g REAL NOT NULL DEFAULT 0,
    carbs_per_100g REAL NOT NULL DEFAULT 0,
    -- New fields according to NUTRIENTS.md
    fiber_per_100g REAL DEFAULT NULL,
    sugars_per_100g REAL DEFAULT NULL,
    category TEXT DEFAULT NULL,  -- leafy_vegetables, cruciferous, nuts_seeds, etc.
    processing_level TEXT DEFAULT NULL,  -- raw, minimal, processed, ultra_processed
    glycemic_index REAL DEFAULT NULL,
    region TEXT DEFAULT 'US',  -- US, EU, AU for labeling differences
    -- Calculated fields (cached for performance)
    net_carbs_per_100g REAL DEFAULT NULL,
    keto_index REAL DEFAULT NULL,
    keto_category TEXT DEFAULT NULL,
    carbs_score REAL DEFAULT NULL,
    fat_score REAL DEFAULT NULL,
    quality_score REAL DEFAULT NULL,
    gi_score REAL DEFAULT NULL,
    fiber_estimated BOOLEAN DEFAULT FALSE,
    fiber_deduction_coefficient REAL DEFAULT NULL,
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    -- Constraints
    CONSTRAINT chk_calories CHECK (calories_per_100g >= 0 AND calories_per_100g <= 9999),
    CONSTRAINT chk_protein CHECK (protein_per_100g >= 0 AND protein_per_100g <= 100),
    CONSTRAINT chk_fat CHECK (fat_per_100g >= 0 AND fat_per_100g <= 100),
    CONSTRAINT chk_carbs CHECK (carbs_per_100g >= 0 AND carbs_per_100g <= 100),
    CONSTRAINT chk_fiber CHECK (fiber_per_100g IS NULL OR (fiber_per_100g >= 0 AND fiber_per_100g <= carbs_per_100g)),
    CONSTRAINT chk_sugars CHECK (sugars_per_100g IS NULL OR (sugars_per_100g >= 0 AND sugars_per_100g <= carbs_per_100g)),
    CONSTRAINT chk_glycemic_index CHECK (glycemic_index IS NULL OR (glycemic_index >= 0 AND glycemic_index <= 100)),
    CONSTRAINT chk_keto_index CHECK (keto_index IS NULL OR (keto_index >= 0 AND keto_index <= 100)),
    CONSTRAINT chk_category CHECK (category IS NULL OR category IN (
        'leafy_vegetables', 'cruciferous', 'root_vegetables', 'nuts_seeds', 
        'berries', 'avocado_olives', 'processed', 'dairy', 'meat', 'fish', 'oil'
    )),
    CONSTRAINT chk_processing_level CHECK (processing_level IS NULL OR processing_level IN (
        'raw', 'minimal', 'processed', 'ultra_processed'
    )),
    CONSTRAINT chk_region CHECK (region IN ('US', 'EU', 'AU', 'UK'))
);

-- User profiles table for personalized calculations
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
    -- Optional body composition data
    body_fat_percentage REAL DEFAULT NULL CHECK (body_fat_percentage IS NULL OR (body_fat_percentage >= 5 AND body_fat_percentage <= 50)),
    lean_body_mass_kg REAL DEFAULT NULL CHECK (lean_body_mass_kg IS NULL OR lean_body_mass_kg >= 20),
    -- Calculated fields
    bmr REAL DEFAULT NULL,
    tdee REAL DEFAULT NULL,
    target_calories REAL DEFAULT NULL,
    keto_type TEXT DEFAULT 'standard' CHECK (keto_type IN ('strict', 'standard', 'moderate')),
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Dishes table with enhanced nutrition tracking
CREATE TABLE IF NOT EXISTS dishes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    description TEXT,
    total_weight_grams REAL DEFAULT 0,
    cooked_weight_grams REAL DEFAULT NULL,
    servings INTEGER DEFAULT 1 CHECK (servings > 0),
    -- Calculated nutrition per 100g
    calories_per_100g REAL DEFAULT 0,
    protein_per_100g REAL DEFAULT 0,
    fat_per_100g REAL DEFAULT 0,
    carbs_per_100g REAL DEFAULT 0,
    fiber_per_100g REAL DEFAULT NULL,
    net_carbs_per_100g REAL DEFAULT NULL,
    -- Keto analysis
    keto_index REAL DEFAULT NULL,
    keto_category TEXT DEFAULT NULL,
    -- Cooking information
    cooking_method TEXT DEFAULT NULL CHECK (cooking_method IS NULL OR cooking_method IN (
        'raw', 'boiled', 'steamed', 'grilled', 'fried', 'baked', 'mixed'
    )),
    yield_factor REAL DEFAULT 1.0 CHECK (yield_factor > 0 AND yield_factor <= 5.0),
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Dish ingredients relationship with enhanced tracking
CREATE TABLE IF NOT EXISTS dish_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dish_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity_grams REAL NOT NULL CHECK (quantity_grams > 0),
    -- Cooking preparation details
    preparation_method TEXT DEFAULT 'raw' CHECK (preparation_method IN (
        'raw', 'boiled', 'steamed', 'grilled', 'fried', 'baked'
    )),
    edible_portion REAL DEFAULT 1.0 CHECK (edible_portion > 0 AND edible_portion <= 1.0),
    -- Calculated nutrition contribution
    calories_contribution REAL DEFAULT 0,
    protein_contribution REAL DEFAULT 0,
    fat_contribution REAL DEFAULT 0,
    carbs_contribution REAL DEFAULT 0,
    FOREIGN KEY (dish_id) REFERENCES dishes(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Food log entries with enhanced tracking
CREATE TABLE IF NOT EXISTS log_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    item_type TEXT NOT NULL CHECK (item_type IN ('product', 'dish')),
    item_id INTEGER NOT NULL,
    quantity_grams REAL NOT NULL CHECK (quantity_grams > 0),
    meal_time TEXT CHECK (meal_time IN ('breakfast', 'lunch', 'dinner', 'snack')),
    notes TEXT,
    -- Calculated nutrition for this entry
    calories REAL DEFAULT 0,
    protein REAL DEFAULT 0,
    fat REAL DEFAULT 0,
    carbs REAL DEFAULT 0,
    net_carbs REAL DEFAULT NULL,
    keto_index REAL DEFAULT NULL,
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_log_quantity CHECK (quantity_grams > 0)
);

-- GKI measurements table for ketosis tracking
CREATE TABLE IF NOT EXISTS gki_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,  -- HH:MM format
    glucose_mgdl REAL NOT NULL CHECK (glucose_mgdl > 0 AND glucose_mgdl <= 500),
    ketones_mgdl REAL NOT NULL CHECK (ketones_mgdl > 0 AND ketones_mgdl <= 10),
    -- Calculated values
    glucose_mmol REAL NOT NULL,
    ketones_mmol REAL NOT NULL,
    gki REAL NOT NULL,
    gki_category TEXT NOT NULL,
    -- Context
    measurement_context TEXT DEFAULT 'fasting' CHECK (measurement_context IN (
        'fasting', 'post_meal', 'post_exercise', 'bedtime', 'other'
    )),
    notes TEXT,
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_keto_index ON products(keto_index);
CREATE INDEX IF NOT EXISTS idx_dishes_name ON dishes(name);
CREATE INDEX IF NOT EXISTS idx_dishes_keto_index ON dishes(keto_index);
CREATE INDEX IF NOT EXISTS idx_log_date ON log_entries(date);
CREATE INDEX IF NOT EXISTS idx_log_date_meal ON log_entries(date, meal_time);
CREATE INDEX IF NOT EXISTS idx_log_item ON log_entries(item_type, item_id);
CREATE INDEX IF NOT EXISTS idx_dish_ingredients_dish ON dish_ingredients(dish_id);
CREATE INDEX IF NOT EXISTS idx_dish_ingredients_product ON dish_ingredients(product_id);
CREATE INDEX IF NOT EXISTS idx_gki_date ON gki_measurements(date);
CREATE INDEX IF NOT EXISTS idx_user_profile_updated ON user_profile(updated_at);

-- Enhanced views for easier querying
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

-- View for daily nutrition summary with keto analysis
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

-- Triggers for automatic calculations
-- Trigger to calculate calories from macros when product is inserted/updated
CREATE TRIGGER IF NOT EXISTS calculate_product_calories 
AFTER INSERT ON products
BEGIN
    UPDATE products 
    SET calories_per_100g = (protein_per_100g * 4.0) + (fat_per_100g * 9.0) + (carbs_per_100g * 4.0)
    WHERE id = NEW.id AND calories_per_100g = 0;
END;

CREATE TRIGGER IF NOT EXISTS update_product_calories 
AFTER UPDATE ON products
WHEN NEW.calories_per_100g = 0 OR (OLD.protein_per_100g != NEW.protein_per_100g OR 
                                   OLD.fat_per_100g != NEW.fat_per_100g OR 
                                   OLD.carbs_per_100g != NEW.carbs_per_100g)
BEGIN
    UPDATE products 
    SET calories_per_100g = (NEW.protein_per_100g * 4.0) + (NEW.fat_per_100g * 9.0) + (NEW.carbs_per_100g * 4.0)
    WHERE id = NEW.id AND NEW.calories_per_100g = 0;
END;

-- Trigger to update dish nutrition when ingredients change
CREATE TRIGGER IF NOT EXISTS update_dish_nutrition 
AFTER INSERT ON dish_ingredients
BEGIN
    UPDATE dishes 
    SET 
        total_weight_grams = (
            SELECT SUM(quantity_grams) 
            FROM dish_ingredients 
            WHERE dish_id = NEW.dish_id
        ),
        calories_per_100g = (
            SELECT SUM(p.calories_per_100g * di.quantity_grams / 100.0) * 100.0 / SUM(di.quantity_grams)
            FROM dish_ingredients di
            JOIN products p ON di.product_id = p.id
            WHERE di.dish_id = NEW.dish_id
        ),
        protein_per_100g = (
            SELECT SUM(p.protein_per_100g * di.quantity_grams / 100.0) * 100.0 / SUM(di.quantity_grams)
            FROM dish_ingredients di
            JOIN products p ON di.product_id = p.id
            WHERE di.dish_id = NEW.dish_id
        ),
        fat_per_100g = (
            SELECT SUM(p.fat_per_100g * di.quantity_grams / 100.0) * 100.0 / SUM(di.quantity_grams)
            FROM dish_ingredients di
            JOIN products p ON di.product_id = p.id
            WHERE di.dish_id = NEW.dish_id
        ),
        carbs_per_100g = (
            SELECT SUM(p.carbs_per_100g * di.quantity_grams / 100.0) * 100.0 / SUM(di.quantity_grams)
            FROM dish_ingredients di
            JOIN products p ON di.product_id = p.id
            WHERE di.dish_id = NEW.dish_id
        )
    WHERE id = NEW.dish_id;
END;

-- Sample data with enhanced fields
INSERT OR IGNORE INTO products (name, calories_per_100g, protein_per_100g, fat_per_100g, carbs_per_100g, fiber_per_100g, category, glycemic_index, processing_level) VALUES
('Chicken Breast', 165, 31, 3.6, 0, 0, 'meat', 0, 'minimal'),
('Avocado', 160, 2, 14.7, 8.5, 6.7, 'avocado_olives', 15, 'raw'),
('Broccoli', 34, 2.8, 0.4, 7, 2.6, 'cruciferous', 15, 'raw'),
('Olive Oil', 884, 0, 100, 0, 0, 'oil', 0, 'minimal'),
('Almonds', 579, 21.2, 49.9, 21.6, 12.5, 'nuts_seeds', 15, 'minimal'),
('Spinach', 23, 2.9, 0.4, 3.6, 2.2, 'leafy_vegetables', 15, 'raw'),
('Blueberries', 57, 0.7, 0.3, 14.5, 2.4, 'berries', 25, 'raw'),
('Sweet Potato', 86, 1.6, 0.1, 20.1, 3.0, 'root_vegetables', 70, 'minimal');

-- Sample user profile
INSERT OR IGNORE INTO user_profile (gender, birth_date, height_cm, weight_kg, activity_level, goal, keto_type) VALUES
('male', '1993-01-01', 185, 121.8, 'moderate', 'weight_loss', 'standard');

-- Performance indexes (only for tables, not views)
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_log_entries_date ON log_entries(date);
CREATE INDEX IF NOT EXISTS idx_log_entries_item ON log_entries(item_type, item_id);
CREATE INDEX IF NOT EXISTS idx_log_entries_date_meal ON log_entries(date, meal_time);
CREATE INDEX IF NOT EXISTS idx_dish_ingredients_dish ON dish_ingredients(dish_id);
CREATE INDEX IF NOT EXISTS idx_dish_ingredients_product ON dish_ingredients(product_id);
CREATE INDEX IF NOT EXISTS idx_dishes_name ON dishes(name);

-- ============================================
-- FASTING TABLES
-- ============================================

-- Fasting sessions table
CREATE TABLE IF NOT EXISTS fasting_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1, -- For future multi-user support
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    duration_hours REAL,
    fasting_type TEXT DEFAULT '16:8', -- 16:8, 18:6, 20:4, OMAD, Custom
    status TEXT DEFAULT 'active', -- active, completed, paused, cancelled
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_duration CHECK (duration_hours IS NULL OR duration_hours >= 0),
    CONSTRAINT chk_status CHECK (status IN ('active', 'completed', 'paused', 'cancelled'))
);

-- Fasting goals table
CREATE TABLE IF NOT EXISTS fasting_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    goal_type TEXT NOT NULL, -- daily_hours, weekly_sessions, monthly_hours
    target_value REAL NOT NULL,
    current_value REAL DEFAULT 0,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    status TEXT DEFAULT 'active', -- active, completed, paused
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_target_value CHECK (target_value > 0),
    CONSTRAINT chk_current_value CHECK (current_value >= 0)
);

-- Fasting statistics view
CREATE VIEW IF NOT EXISTS fasting_stats AS
SELECT 
    DATE(start_time) as fasting_date,
    COUNT(*) as sessions_count,
    AVG(duration_hours) as avg_duration_hours,
    SUM(duration_hours) as total_hours,
    MAX(duration_hours) as longest_session
FROM fasting_sessions 
WHERE status = 'completed'
GROUP BY DATE(start_time)
ORDER BY fasting_date DESC;

-- Fasting indexes
CREATE INDEX IF NOT EXISTS idx_fasting_sessions_user ON fasting_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_fasting_sessions_start ON fasting_sessions(start_time);
CREATE INDEX IF NOT EXISTS idx_fasting_sessions_status ON fasting_sessions(status);
CREATE INDEX IF NOT EXISTS idx_fasting_goals_user ON fasting_goals(user_id);
CREATE INDEX IF NOT EXISTS idx_fasting_goals_period ON fasting_goals(period_start, period_end);

-- Fasting settings table
CREATE TABLE IF NOT EXISTS fasting_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    fasting_goal TEXT NOT NULL DEFAULT '16:8', -- 16:8, 18:6, 20:4, OMAD
    preferred_start_time TIME, -- Preferred time to start fasting
    enable_reminders BOOLEAN DEFAULT 0, -- Enable fasting reminders
    enable_notifications BOOLEAN DEFAULT 0, -- Enable completion notifications
    default_notes TEXT, -- Default notes for fasting sessions
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_fasting_goal CHECK (fasting_goal IN ('16:8', '18:6', '20:4', 'OMAD')),
    CONSTRAINT chk_reminders CHECK (enable_reminders IN (0, 1)),
    CONSTRAINT chk_notifications CHECK (enable_notifications IN (0, 1))
);

-- Fasting settings indexes
CREATE INDEX IF NOT EXISTS idx_fasting_settings_user ON fasting_settings(user_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_fasting_settings_user_unique ON fasting_settings(user_id);
