-- Migration: Fix dish calculations
-- Update total_weight_grams for existing dishes based on ingredients

UPDATE dishes 
SET total_weight_grams = (
    SELECT COALESCE(SUM(di.quantity_grams), 0)
    FROM dish_ingredients di
    WHERE di.dish_id = dishes.id
)
WHERE total_weight_grams = 0 OR total_weight_grams IS NULL;

-- Update the view to use total_weight_grams for proper calculations
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
            CASE 
                WHEN d.total_weight_grams > 0 THEN (
                    SELECT COALESCE(SUM(p2.calories_per_100g * di.quantity_grams / 100.0), 0) * le.quantity_grams / d.total_weight_grams
                    FROM dish_ingredients di
                    JOIN products p2 ON di.product_id = p2.id
                    WHERE di.dish_id = le.item_id
                )
                ELSE (
                    SELECT COALESCE(SUM(p2.calories_per_100g * di.quantity_grams / 100.0), 0) * le.quantity_grams / 100.0
                    FROM dish_ingredients di
                    JOIN products p2 ON di.product_id = p2.id
                    WHERE di.dish_id = le.item_id
                )
            END
        )
        ELSE 0
    END as calculated_calories
FROM log_entries le
LEFT JOIN products p ON le.item_type = 'product' AND le.item_id = p.id
LEFT JOIN dishes d ON le.item_type = 'dish' AND le.item_id = d.id;
