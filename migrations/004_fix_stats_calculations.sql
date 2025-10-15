-- Migration: Update log_entries_with_details view to include macro calculations for dishes
-- This ensures statistics API gets accurate macro calculations

DROP VIEW IF EXISTS log_entries_with_details;

CREATE VIEW log_entries_with_details AS
SELECT 
    le.*,
    CASE 
        WHEN le.item_type = 'product' THEN p.name
        WHEN le.item_type = 'dish' THEN d.name
    END as item_name,
    CASE 
        WHEN le.item_type = 'product' THEN (p.calories_per_100g * le.quantity_grams / 100.0)
        WHEN le.item_type = 'dish' THEN (
            SELECT COALESCE(SUM(p2.calories_per_100g * di.quantity_grams / 100.0), 0) * le.quantity_grams / 100.0
            FROM dish_ingredients di
            JOIN products p2 ON di.product_id = p2.id
            WHERE di.dish_id = le.item_id
        )
        ELSE 0
    END as calculated_calories,
    -- Product nutrition data (for products only)
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
    -- Calculated macros per 100g for dishes (for statistics)
    CASE 
        WHEN le.item_type = 'dish' THEN (
            SELECT COALESCE(SUM(p2.protein_per_100g * di.quantity_grams / 100.0), 0) / d.total_weight_grams * 100.0
            FROM dish_ingredients di
            JOIN products p2 ON di.product_id = p2.id
            WHERE di.dish_id = le.item_id AND d.total_weight_grams > 0
        )
        ELSE NULL
    END as dish_protein_per_100g,
    CASE 
        WHEN le.item_type = 'dish' THEN (
            SELECT COALESCE(SUM(p2.fat_per_100g * di.quantity_grams / 100.0), 0) / d.total_weight_grams * 100.0
            FROM dish_ingredients di
            JOIN products p2 ON di.product_id = p2.id
            WHERE di.dish_id = le.item_id AND d.total_weight_grams > 0
        )
        ELSE NULL
    END as dish_fat_per_100g,
    CASE 
        WHEN le.item_type = 'dish' THEN (
            SELECT COALESCE(SUM(p2.carbs_per_100g * di.quantity_grams / 100.0), 0) / d.total_weight_grams * 100.0
            FROM dish_ingredients di
            JOIN products p2 ON di.product_id = p2.id
            WHERE di.dish_id = le.item_id AND d.total_weight_grams > 0
        )
        ELSE NULL
    END as dish_carbs_per_100g
FROM log_entries le
LEFT JOIN products p ON le.item_type = 'product' AND le.item_id = p.id
LEFT JOIN dishes d ON le.item_type = 'dish' AND le.item_id = d.id;
