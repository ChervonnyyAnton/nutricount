"""
Dishes routes for Nutricount application.
Handles CRUD operations for dishes (recipes).
"""

import sqlite3

from flask import Blueprint, current_app, jsonify, request
from werkzeug.exceptions import BadRequest

from src.constants import (
    ERROR_MESSAGES,
    HTTP_BAD_REQUEST,
    HTTP_CREATED,
    HTTP_NOT_FOUND,
    SUCCESS_MESSAGES,
)
from src.monitoring import monitor_http_request
from src.nutrition_calculator import (
    KETO_INDEX_CATEGORIES,
    RecipeIngredient,
    calculate_recipe_nutrition,
)
from src.security import rate_limit
from src.utils import clean_string, json_response, safe_float, validate_dish_data


def safe_get_json():
    """Safely get JSON data from request, handling invalid JSON gracefully"""
    try:
        return request.get_json() or {}
    except BadRequest:
        return None


def get_db():
    """Get database connection with proper configuration"""
    db = sqlite3.connect(current_app.config["DATABASE"])
    db.row_factory = sqlite3.Row

    # Enable WAL mode for better concurrency (only for file databases)
    if current_app.config["DATABASE"] != ":memory:":
        db.execute("PRAGMA journal_mode = WAL")
        db.execute("PRAGMA synchronous = NORMAL")

    # Enable foreign key constraints
    db.execute("PRAGMA foreign_keys = ON")

    return db


# Create blueprint
dishes_bp = Blueprint("dishes", __name__, url_prefix="/api/dishes")


@dishes_bp.route("", methods=["GET", "POST"])
@monitor_http_request
@rate_limit("api")
def dishes_api():
    """Dishes CRUD endpoint"""
    db = get_db()

    try:
        if request.method == "GET":
            # Get dishes with pre-calculated nutrition (using advanced recipe calculation)
            dishes = db.execute(
                """
                SELECT d.*,
                       COUNT(di.id) as ingredient_count,
                       -- Use pre-calculated values from advanced recipe calculation
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

            dishes_data = [dict(row) for row in dishes]

            return jsonify(json_response(dishes_data))

        else:  # POST
            data = safe_get_json()
            if data is None:
                return (
                    jsonify(json_response(None, "Invalid JSON", status=HTTP_BAD_REQUEST)),
                    HTTP_BAD_REQUEST,
                )

            # Validate dish data
            is_valid, errors, cleaned_data = validate_dish_data(data)
            if not is_valid:
                return (
                    jsonify(
                        json_response(
                            None, "Validation failed", status=HTTP_BAD_REQUEST, errors=errors
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Check for duplicate name
            existing = db.execute(
                "SELECT id FROM dishes WHERE name = ?", (cleaned_data["name"],)
            ).fetchone()
            if existing:
                return (
                    jsonify(
                        json_response(
                            None,
                            "Validation failed",
                            status=HTTP_BAD_REQUEST,
                            errors=[f"Dish '{cleaned_data['name']}' already exists"],
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Verify all products exist
            product_ids = [ing["product_id"] for ing in cleaned_data["ingredients"]]
            existing_products = db.execute(
                f"SELECT id FROM products WHERE id IN ({','.join('?' * len(product_ids))})",
                product_ids,
            ).fetchall()
            existing_product_ids = [row[0] for row in existing_products]

            missing_products = set(product_ids) - set(existing_product_ids)
            if missing_products:
                return (
                    jsonify(
                        json_response(
                            None,
                            "Validation failed",
                            status=HTTP_BAD_REQUEST,
                            errors=[f"Products with IDs {list(missing_products)} do not exist"],
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Create dish
            try:
                cursor = db.execute(
                    "INSERT INTO dishes (name, description) VALUES (?, ?)",
                    (cleaned_data["name"], cleaned_data.get("description", "")),
                )
                dish_id = cursor.lastrowid

                # Prepare ingredients for advanced recipe calculation
                recipe_ingredients = []
                total_raw_weight = 0

                for ingredient in cleaned_data["ingredients"]:
                    # Get product data
                    product = db.execute(
                        "SELECT * FROM products WHERE id = ?", (ingredient["product_id"],)
                    ).fetchone()

                    if product:
                        # Create RecipeIngredient for advanced calculation
                        recipe_ingredient = RecipeIngredient(
                            name=product["name"],
                            raw_weight=ingredient["quantity_grams"],
                            nutrition_per_100g={
                                "protein": product["protein_per_100g"],
                                "fats": product["fat_per_100g"],
                                "carbs": product["carbs_per_100g"],
                                "fiber": (
                                    product["fiber_per_100g"]
                                    if "fiber_per_100g" in product.keys()
                                    else 0
                                ),
                                "sugars": (
                                    product["sugars_per_100g"]
                                    if "sugars_per_100g" in product.keys()
                                    else 0
                                ),
                            },
                            category=(
                                product["category"] if "category" in product.keys() else "unknown"
                            ),
                            preparation=ingredient.get("preparation_method", "raw"),
                            edible_portion=ingredient.get("edible_portion", 1.0),
                        )

                        recipe_ingredients.append(recipe_ingredient)
                        total_raw_weight += ingredient["quantity_grams"]

                        # Store basic ingredient data
                        db.execute(
                            "INSERT INTO dish_ingredients (dish_id, product_id, quantity_grams, preparation_method, edible_portion) VALUES (?, ?, ?, ?, ?)",
                            (
                                dish_id,
                                ingredient["product_id"],
                                ingredient["quantity_grams"],
                                ingredient.get("preparation_method", "raw"),
                                ingredient.get("edible_portion", 1.0),
                            ),
                        )

                # Calculate advanced recipe nutrition
                recipe_result = calculate_recipe_nutrition(
                    recipe_ingredients, cleaned_data["name"], servings=1
                )

                # Calculate keto category from keto index
                keto_index = recipe_result.get("keto_index", 0)
                keto_category = "Исключить"  # Default
                for (min_val, max_val), category_name in KETO_INDEX_CATEGORIES.items():
                    if min_val <= keto_index <= max_val:
                        keto_category = category_name
                        break

                # Update dish with calculated nutrition and weights
                db.execute(
                    """UPDATE dishes SET
                        total_weight_grams = ?,
                        cooked_weight_grams = ?,
                        calories_per_100g = ?,
                        protein_per_100g = ?,
                        fat_per_100g = ?,
                        carbs_per_100g = ?,
                        net_carbs_per_100g = ?,
                        keto_index = ?,
                        keto_category = ?
                    WHERE id = ?""",
                    (
                        total_raw_weight,
                        recipe_result["weights"]["total_cooked"],
                        recipe_result["nutrition_per_100g"]["calories"],
                        recipe_result["nutrition_per_100g"]["protein"],
                        recipe_result["nutrition_per_100g"]["fats"],
                        recipe_result["nutrition_per_100g"]["carbs"],
                        recipe_result["nutrition_per_100g"].get("net_carbs", 0),
                        keto_index,
                        keto_category,
                        dish_id,
                    ),
                )

                db.commit()

                # Return created dish
                created_dish = dict(
                    db.execute("SELECT * FROM dishes WHERE id = ?", (dish_id,)).fetchone()
                )

                return (
                    jsonify(
                        json_response(created_dish, SUCCESS_MESSAGES["dish_created"], HTTP_CREATED)
                    ),
                    HTTP_CREATED,
                )

            except sqlite3.IntegrityError as e:
                current_app.logger.error(f"Dish creation integrity error: {e}")
                return (
                    jsonify(
                        json_response(
                            None,
                            "Database error",
                            status=HTTP_BAD_REQUEST,
                            errors=["Failed to create dish due to database constraint"],
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

    except Exception as e:
        current_app.logger.error(f"Dishes API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


@dishes_bp.route("/<int:dish_id>", methods=["GET", "PUT", "DELETE"])
def dish_detail_api(dish_id):
    """Dish detail operations (GET, PUT, DELETE)"""
    db = get_db()

    try:
        if request.method == "GET":
            # Get dish details
            dish = db.execute("SELECT * FROM dishes WHERE id = ?", (dish_id,)).fetchone()
            if not dish:
                return (
                    jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)),
                    HTTP_NOT_FOUND,
                )

            # Get ingredients
            ingredients = db.execute(
                """
                SELECT di.*, p.name as product_name, p.calories_per_100g, p.protein_per_100g,
                       p.fat_per_100g, p.carbs_per_100g, p.fiber_per_100g, p.sugars_per_100g,
                       p.category, p.processing_level, p.glycemic_index, p.region
                FROM dish_ingredients di
                JOIN products p ON di.product_id = p.id
                WHERE di.dish_id = ?
                ORDER BY di.id
            """,
                (dish_id,),
            ).fetchall()

            dish_data = dict(dish)
            dish_data["ingredients"] = [dict(ingredient) for ingredient in ingredients]

            return jsonify(json_response(dish_data))

        elif request.method == "PUT":
            # Update dish
            data = safe_get_json()
            if data is None:
                return (
                    jsonify(json_response(None, "Invalid JSON", status=HTTP_BAD_REQUEST)),
                    HTTP_BAD_REQUEST,
                )

            # Validate required fields
            name = clean_string(data.get("name", "").strip())
            if not name:
                return (
                    jsonify(
                        json_response(
                            None,
                            ERROR_MESSAGES["validation_error"],
                            status=HTTP_BAD_REQUEST,
                            errors=["Dish name is required"],
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Check if dish exists
            existing = db.execute("SELECT id FROM dishes WHERE id = ?", (dish_id,)).fetchone()
            if not existing:
                return (
                    jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)),
                    HTTP_NOT_FOUND,
                )

            # Check for name conflicts (excluding current dish)
            name_conflict = db.execute(
                "SELECT id FROM dishes WHERE name = ? AND id != ?", (name, dish_id)
            ).fetchone()

            if name_conflict:
                return (
                    jsonify(
                        json_response(
                            None,
                            ERROR_MESSAGES["validation_error"],
                            status=HTTP_BAD_REQUEST,
                            errors=["Dish with this name already exists"],
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Update dish
            cursor = db.execute(
                """
                UPDATE dishes
                SET name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (name, dish_id),
            )

            # Update ingredients if provided
            ingredients = data.get("ingredients", [])
            if ingredients:
                # Delete existing ingredients
                db.execute("DELETE FROM dish_ingredients WHERE dish_id = ?", (dish_id,))

                # Add new ingredients
                total_weight = 0
                for ingredient in ingredients:
                    product_id = ingredient.get("product_id")
                    quantity_grams = safe_float(ingredient.get("quantity_grams", 0))
                    preparation_method = ingredient.get("preparation_method", "raw")
                    edible_portion = safe_float(ingredient.get("edible_portion", 1.0))

                    if product_id and quantity_grams > 0:
                        db.execute(
                            """
                            INSERT INTO dish_ingredients (dish_id, product_id, quantity_grams, preparation_method, edible_portion)
                            VALUES (?, ?, ?, ?, ?)
                        """,
                            (
                                dish_id,
                                product_id,
                                quantity_grams,
                                preparation_method,
                                edible_portion,
                            ),
                        )
                        total_weight += quantity_grams

                # Update total weight
                db.execute(
                    """
                    UPDATE dishes SET total_weight_grams = ? WHERE id = ?
                """,
                    (total_weight, dish_id),
                )

            db.commit()

            # Return updated dish
            updated_dish = db.execute("SELECT * FROM dishes WHERE id = ?", (dish_id,)).fetchone()
            return jsonify(json_response(dict(updated_dish), "Dish updated successfully!"))

        elif request.method == "DELETE":
            # Check usage in log entries
            usage_count = db.execute(
                "SELECT COUNT(*) as count FROM log_entries WHERE item_type = 'dish' AND item_id = ?",
                (dish_id,),
            ).fetchone()["count"]

            if usage_count > 0:
                return (
                    jsonify(
                        json_response(
                            None,
                            f"Cannot delete dish: used in {usage_count} log entries",
                            HTTP_BAD_REQUEST,
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Delete dish (ingredients will cascade)
            cursor = db.execute("DELETE FROM dishes WHERE id = ?", (dish_id,))
            if cursor.rowcount == 0:
                return (
                    jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)),
                    HTTP_NOT_FOUND,
                )

            db.commit()
            return jsonify(json_response({}, SUCCESS_MESSAGES["dish_deleted"]))

    except Exception as e:
        current_app.logger.error(f"Dish detail API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()
