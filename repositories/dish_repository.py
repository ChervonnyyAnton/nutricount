"""
Dish Repository - Data access layer for dishes (recipes).

Implements Repository Pattern for dish entities.
"""

from typing import Any, Dict, List, Optional

from repositories.base_repository import BaseRepository
from src.nutrition_calculator import (
    KETO_INDEX_CATEGORIES,
    RecipeIngredient,
    calculate_recipe_nutrition,
)


class DishRepository(BaseRepository):
    """
    Repository for dish data access.

    Handles CRUD operations for dishes (recipes) and their ingredients.
    Includes advanced recipe nutrition calculations.
    """

    def find_all(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Get all dishes with pre-calculated nutrition.

        Returns:
            List of dish dictionaries with nutrition data
        """
        dishes = self.db.execute(
            """
            SELECT d.*,
                   COUNT(di.id) as ingredient_count,
                   d.calories_per_100g * d.cooked_weight_grams / 100.0 as total_calories,
                   d.protein_per_100g * d.cooked_weight_grams / 100.0 as total_protein,
                   d.fat_per_100g * d.cooked_weight_grams / 100.0 as total_fat,
                   d.carbs_per_100g * d.cooked_weight_grams / 100.0 as total_carbs,
                   d.net_carbs_per_100g * d.cooked_weight_grams / 100.0 as total_net_carbs
            FROM dishes d
            LEFT JOIN dish_ingredients di ON d.id = di.dish_id
            GROUP BY d.id
            ORDER BY d.name COLLATE NOCASE
        """
        ).fetchall()

        return [dict(row) for row in dishes]

    def find_by_id(self, dish_id: int) -> Optional[Dict[str, Any]]:
        """
        Get dish by ID with ingredients.

        Args:
            dish_id: Dish ID

        Returns:
            Dish dictionary with ingredients or None if not found
        """
        # Get dish data
        dish_row = self.db.execute(
            """
            SELECT d.*,
                   COUNT(di.id) as ingredient_count,
                   d.calories_per_100g * d.cooked_weight_grams / 100.0 as total_calories,
                   d.protein_per_100g * d.cooked_weight_grams / 100.0 as total_protein,
                   d.fat_per_100g * d.cooked_weight_grams / 100.0 as total_fat,
                   d.carbs_per_100g * d.cooked_weight_grams / 100.0 as total_carbs,
                   d.net_carbs_per_100g * d.cooked_weight_grams / 100.0 as total_net_carbs
            FROM dishes d
            LEFT JOIN dish_ingredients di ON d.id = di.dish_id
            WHERE d.id = ?
            GROUP BY d.id
        """,
            (dish_id,),
        ).fetchone()

        if not dish_row:
            return None

        dish = dict(dish_row)

        # Get ingredients
        ingredients = self.db.execute(
            """
            SELECT di.*, p.name as product_name
            FROM dish_ingredients di
            JOIN products p ON di.product_id = p.id
            WHERE di.dish_id = ?
            ORDER BY p.name
        """,
            (dish_id,),
        ).fetchall()

        dish["ingredients"] = [dict(row) for row in ingredients]

        return dish

    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find dish by exact name.

        Args:
            name: Dish name

        Returns:
            Dish dictionary or None
        """
        row = self.db.execute("SELECT id FROM dishes WHERE name = ?", (name,)).fetchone()
        return dict(row) if row else None

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new dish with ingredients and calculated nutrition.

        Args:
            data: Dish data with ingredients

        Returns:
            Created dish dictionary
        """
        # Insert dish
        cursor = self.db.execute(
            "INSERT INTO dishes (name, description) VALUES (?, ?)",
            (data["name"], data.get("description", "")),
        )
        dish_id = cursor.lastrowid

        # Process ingredients and calculate nutrition
        recipe_ingredients = []

        for ingredient in data["ingredients"]:
            # Get product data
            product = self.db.execute(
                "SELECT * FROM products WHERE id = ?", (ingredient["product_id"],)
            ).fetchone()

            if product:
                # Create RecipeIngredient for calculation
                recipe_ingredient = RecipeIngredient(
                    name=product["name"],
                    raw_weight=ingredient["quantity_grams"],
                    nutrition_per_100g={
                        "protein": product["protein_per_100g"],
                        "fats": product["fat_per_100g"],
                        "carbs": product["carbs_per_100g"],
                        "fiber": product.get("fiber_per_100g", 0),
                        "sugars": product.get("sugars_per_100g", 0),
                    },
                    category=product.get("category", "unknown"),
                    preparation=ingredient.get("preparation_method", "raw"),
                    edible_portion=ingredient.get("edible_portion", 1.0),
                )

                recipe_ingredients.append(recipe_ingredient)

                # Store ingredient
                self.db.execute(
                    """INSERT INTO dish_ingredients
                       (dish_id, product_id, quantity_grams, preparation_method, edible_portion)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        dish_id,
                        ingredient["product_id"],
                        ingredient["quantity_grams"],
                        ingredient.get("preparation_method", "raw"),
                        ingredient.get("edible_portion", 1.0),
                    ),
                )

        # Calculate recipe nutrition
        recipe_result = calculate_recipe_nutrition(recipe_ingredients, data["name"], servings=1)

        # Determine keto category
        keto_index = recipe_result.get("keto_index", 0)
        keto_category = "Исключить"  # Default
        for (min_val, max_val), category_name in KETO_INDEX_CATEGORIES.items():
            if min_val <= keto_index <= max_val:
                keto_category = category_name
                break

        # Update dish with calculated nutrition
        self.db.execute(
            """UPDATE dishes SET
                total_weight_grams = ?,
                cooked_weight_grams = ?,
                calories_per_100g = ?,
                protein_per_100g = ?,
                fat_per_100g = ?,
                carbs_per_100g = ?,
                net_carbs_per_100g = ?,
                fiber_per_100g = ?,
                sugars_per_100g = ?,
                keto_index = ?,
                keto_category = ?
            WHERE id = ?""",
            (
                recipe_result["total_raw_weight"],
                recipe_result["total_cooked_weight"],
                recipe_result["per_100g"]["calories"],
                recipe_result["per_100g"]["protein"],
                recipe_result["per_100g"]["fats"],
                recipe_result["per_100g"]["carbs"],
                recipe_result["per_100g"]["net_carbs"],
                recipe_result["per_100g"].get("fiber", 0),
                recipe_result["per_100g"].get("sugars", 0),
                keto_index,
                keto_category,
                dish_id,
            ),
        )

        self.db.commit()

        # Return created dish
        return self.find_by_id(dish_id)

    def update(self, dish_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update existing dish.

        Args:
            dish_id: Dish ID
            data: Updated dish data

        Returns:
            Updated dish dictionary or None if not found
        """
        # Check if dish exists
        existing = self.find_by_id(dish_id)
        if not existing:
            return None

        # Delete existing ingredients if updating ingredients
        if "ingredients" in data:
            self.db.execute("DELETE FROM dish_ingredients WHERE dish_id = ?", (dish_id,))

        # Update dish basic info
        self.db.execute(
            "UPDATE dishes SET name = ?, description = ? WHERE id = ?",
            (data.get("name", existing["name"]), data.get("description", existing.get("description", "")), dish_id),
        )

        # If ingredients provided, recalculate nutrition
        if "ingredients" in data:
            recipe_ingredients = []

            for ingredient in data["ingredients"]:
                product = self.db.execute(
                    "SELECT * FROM products WHERE id = ?", (ingredient["product_id"],)
                ).fetchone()

                if product:
                    recipe_ingredient = RecipeIngredient(
                        name=product["name"],
                        raw_weight=ingredient["quantity_grams"],
                        nutrition_per_100g={
                            "protein": product["protein_per_100g"],
                            "fats": product["fat_per_100g"],
                            "carbs": product["carbs_per_100g"],
                            "fiber": product.get("fiber_per_100g", 0),
                            "sugars": product.get("sugars_per_100g", 0),
                        },
                        category=product.get("category", "unknown"),
                        preparation=ingredient.get("preparation_method", "raw"),
                        edible_portion=ingredient.get("edible_portion", 1.0),
                    )

                    recipe_ingredients.append(recipe_ingredient)

                    self.db.execute(
                        """INSERT INTO dish_ingredients
                           (dish_id, product_id, quantity_grams, preparation_method, edible_portion)
                           VALUES (?, ?, ?, ?, ?)""",
                        (
                            dish_id,
                            ingredient["product_id"],
                            ingredient["quantity_grams"],
                            ingredient.get("preparation_method", "raw"),
                            ingredient.get("edible_portion", 1.0),
                        ),
                    )

            # Recalculate nutrition
            recipe_result = calculate_recipe_nutrition(
                recipe_ingredients, data.get("name", existing["name"]), servings=1
            )

            keto_index = recipe_result.get("keto_index", 0)
            keto_category = "Исключить"
            for (min_val, max_val), category_name in KETO_INDEX_CATEGORIES.items():
                if min_val <= keto_index <= max_val:
                    keto_category = category_name
                    break

            self.db.execute(
                """UPDATE dishes SET
                    total_weight_grams = ?,
                    cooked_weight_grams = ?,
                    calories_per_100g = ?,
                    protein_per_100g = ?,
                    fat_per_100g = ?,
                    carbs_per_100g = ?,
                    net_carbs_per_100g = ?,
                    fiber_per_100g = ?,
                    sugars_per_100g = ?,
                    keto_index = ?,
                    keto_category = ?
                WHERE id = ?""",
                (
                    recipe_result["total_raw_weight"],
                    recipe_result["total_cooked_weight"],
                    recipe_result["per_100g"]["calories"],
                    recipe_result["per_100g"]["protein"],
                    recipe_result["per_100g"]["fats"],
                    recipe_result["per_100g"]["carbs"],
                    recipe_result["per_100g"]["net_carbs"],
                    recipe_result["per_100g"].get("fiber", 0),
                    recipe_result["per_100g"].get("sugars", 0),
                    keto_index,
                    keto_category,
                    dish_id,
                ),
            )

        self.db.commit()

        return self.find_by_id(dish_id)

    def delete(self, dish_id: int) -> bool:
        """
        Delete dish and its ingredients.

        Args:
            dish_id: Dish ID

        Returns:
            True if deleted, False if not found
        """
        # Check if exists
        if not self.find_by_id(dish_id):
            return False

        # Delete ingredients first
        self.db.execute("DELETE FROM dish_ingredients WHERE dish_id = ?", (dish_id,))

        # Delete dish
        self.db.execute("DELETE FROM dishes WHERE id = ?", (dish_id,))
        self.db.commit()

        return True

    def exists(self, dish_id: int) -> bool:
        """Check if dish exists."""
        row = self.db.execute("SELECT 1 FROM dishes WHERE id = ?", (dish_id,)).fetchone()
        return row is not None

    def count(self, **kwargs) -> int:
        """Count total dishes."""
        row = self.db.execute("SELECT COUNT(*) FROM dishes").fetchone()
        return row[0] if row else 0

    def is_used_in_logs(self, dish_id: int) -> tuple[bool, int]:
        """
        Check if dish is used in any log entries.

        Args:
            dish_id: Dish ID

        Returns:
            Tuple of (is_used, count)
        """
        row = self.db.execute(
            "SELECT COUNT(*) FROM food_log WHERE item_type = 'dish' AND item_id = ?", (dish_id,)
        ).fetchone()
        count = row[0] if row else 0
        return (count > 0, count)

    def verify_products_exist(self, product_ids: List[int]) -> tuple[bool, List[int]]:
        """
        Verify that all product IDs exist.

        Args:
            product_ids: List of product IDs

        Returns:
            Tuple of (all_exist, missing_ids)
        """
        if not product_ids:
            return (True, [])

        existing_products = self.db.execute(
            f"SELECT id FROM products WHERE id IN ({','.join('?' * len(product_ids))})",
            product_ids,
        ).fetchall()
        existing_product_ids = [row[0] for row in existing_products]

        missing_products = list(set(product_ids) - set(existing_product_ids))
        all_exist = len(missing_products) == 0

        return (all_exist, missing_products)
