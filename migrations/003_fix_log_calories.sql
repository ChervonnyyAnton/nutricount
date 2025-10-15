-- Migration: Update log_entries_with_details view to include product nutrition data
-- This fixes the issue where calories_per_100g was null in log entries

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
    END as carbs_per_100g
FROM log_entries le
LEFT JOIN products p ON le.item_type = 'product' AND le.item_id = p.id
LEFT JOIN dishes d ON le.item_type = 'dish' AND le.item_id = d.id;
