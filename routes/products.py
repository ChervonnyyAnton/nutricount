"""
Products routes for Nutricount application.
Handles CRUD operations for products (food items).
"""

import sqlite3

from flask import Blueprint, current_app, jsonify, request
from werkzeug.exceptions import BadRequest

from src.cache_manager import cache_invalidate, cache_manager
from src.config import Config
from src.constants import (
    ERROR_MESSAGES,
    HTTP_BAD_REQUEST,
    HTTP_CREATED,
    HTTP_NOT_FOUND,
    HTTP_OK,
    SUCCESS_MESSAGES,
)
from src.monitoring import monitor_http_request
from src.nutrition_calculator import (
    calculate_calories_from_macros,
    calculate_keto_index_advanced,
    calculate_net_carbs_advanced,
)
from src.security import rate_limit
from src.utils import (
    clean_string,
    json_response,
    safe_float,
    validate_nutrition_values,
    validate_product_data,
)


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

    db.execute("PRAGMA foreign_keys = ON")

    return db


# Create products blueprint
products_bp = Blueprint("products", __name__, url_prefix="/api/products")


@products_bp.route("", methods=["GET", "POST"])
@monitor_http_request
@rate_limit("api")
def products_api():
    """Products CRUD endpoint"""
    db = get_db()

    try:
        if request.method == "GET":
            # Search and pagination
            search = request.args.get("search", "").strip()
            limit = min(int(request.args.get("limit", 50)), Config.API_MAX_PER_PAGE)
            offset = max(0, int(request.args.get("offset", 0)))

            # Create cache key
            cache_key = f"products:{search}:{limit}:{offset}"

            # Try to get from cache first
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return (
                    jsonify(json_response(cached_result, "Products retrieved from cache", HTTP_OK)),
                    HTTP_OK,
                )

            query = """
                SELECT * FROM products
                WHERE name LIKE ?
                ORDER BY name COLLATE NOCASE
                LIMIT ? OFFSET ?
            """

            products = []
            for row in db.execute(query, (f"%{search}%", limit, offset)).fetchall():
                product = dict(row)

                # Calculate enhanced fields for each product using advanced algorithms
                try:
                    # Calculate net carbs using advanced algorithm
                    net_carbs_result = calculate_net_carbs_advanced(
                        product["carbs_per_100g"],
                        product["fiber_per_100g"] if "fiber_per_100g" in product.keys() else None,
                        product["category"] if "category" in product.keys() else None,
                        product["region"] if "region" in product.keys() else "US",
                    )

                    # Calculate keto index using advanced algorithm
                    keto_result = calculate_keto_index_advanced(
                        product["protein_per_100g"],
                        product["fat_per_100g"],
                        product["carbs_per_100g"],
                        product["fiber_per_100g"] if "fiber_per_100g" in product.keys() else None,
                        product["category"] if "category" in product.keys() else None,
                        product["glycemic_index"] if "glycemic_index" in product.keys() else None,
                        (
                            product["processing_level"]
                            if "processing_level" in product.keys()
                            else None
                        ),
                    )

                    # Add calculated fields
                    product["net_carbs"] = net_carbs_result["net_carbs"]
                    product["fiber_estimated"] = net_carbs_result["fiber_estimated"]
                    product["fiber_deduction_coefficient"] = net_carbs_result[
                        "fiber_deduction_coefficient"
                    ]
                    product["keto_index"] = keto_result["keto_index"]
                    product["keto_category"] = keto_result["keto_category"]
                    product["carbs_score"] = keto_result["carbs_score"]
                    product["fat_score"] = keto_result["fat_score"]
                    product["quality_score"] = keto_result["quality_score"]
                    product["gi_score"] = keto_result["gi_score"]

                except Exception as e:
                    current_app.logger.warning(
                        f"Error calculating enhanced fields for product {product['id']}: {e}"
                    )
                    # Add default values if calculation fails
                    product["net_carbs"] = product["carbs_per_100g"]
                    product["fiber_estimated"] = True
                    product["keto_index"] = 0
                    product["keto_category"] = "Не для кето"
                    product["carbs_score"] = 0
                    product["fat_score"] = 0
                    product["gi_score"] = 50

                products.append(product)

            # Cache the result
            cache_manager.set(cache_key, products, 300)  # Cache for 5 minutes

            return jsonify(json_response(products))

        else:  # POST
            data = safe_get_json()
            if data is None:
                return (
                    jsonify(json_response(None, "Invalid JSON", status=HTTP_BAD_REQUEST)),
                    HTTP_BAD_REQUEST,
                )

            # Validate product data
            is_valid, errors, cleaned_data = validate_product_data(data)
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
                "SELECT id FROM products WHERE name = ?", (cleaned_data["name"],)
            ).fetchone()
            if existing:
                return (
                    jsonify(
                        json_response(
                            None,
                            "Validation failed",
                            status=HTTP_BAD_REQUEST,
                            errors=[f"Product '{cleaned_data['name']}' already exists"],
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Insert product with enhanced calculations
            try:
                # Extract additional fields
                fiber_per_100g = safe_float(data.get("fiber_per_100g"))
                sugars_per_100g = safe_float(data.get("sugars_per_100g"))
                category = data.get("category") if data.get("category") else None
                processing_level = (
                    data.get("processing_level") if data.get("processing_level") else None
                )
                glycemic_index = safe_float(data.get("glycemic_index"))
                region = clean_string(data.get("region", "US"))

                # Calculate calories using Atwater system
                calculated_calories = calculate_calories_from_macros(
                    cleaned_data["protein_per_100g"],
                    cleaned_data["fat_per_100g"],
                    cleaned_data["carbs_per_100g"],
                )

                # Calculate net carbs using advanced algorithm
                net_carbs_result = calculate_net_carbs_advanced(
                    cleaned_data["carbs_per_100g"], fiber_per_100g, category, region
                )

                # Calculate keto index using advanced algorithm
                keto_result = calculate_keto_index_advanced(
                    cleaned_data["protein_per_100g"],
                    cleaned_data["fat_per_100g"],
                    cleaned_data["carbs_per_100g"],
                    fiber_per_100g,
                    category,
                    glycemic_index,
                    processing_level,
                )

                cursor = db.execute(
                    """
                    INSERT INTO products (name, calories_per_100g, protein_per_100g, fat_per_100g, carbs_per_100g,
                                        fiber_per_100g, sugars_per_100g, category, processing_level, glycemic_index, region,
                                        net_carbs_per_100g, keto_index, keto_category, carbs_score, fat_score,
                                        quality_score, gi_score, fiber_estimated, fiber_deduction_coefficient)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        cleaned_data["name"],
                        calculated_calories,  # Use calculated calories
                        cleaned_data["protein_per_100g"],
                        cleaned_data["fat_per_100g"],
                        cleaned_data["carbs_per_100g"],
                        fiber_per_100g,
                        sugars_per_100g,
                        category,
                        processing_level,
                        glycemic_index,
                        region,
                        net_carbs_result["net_carbs"],
                        keto_result["keto_index"],
                        keto_result["keto_category"],
                        keto_result["carbs_score"],
                        keto_result["fat_score"],
                        keto_result["quality_score"],
                        keto_result["gi_score"],
                        net_carbs_result["fiber_estimated"],
                        net_carbs_result["fiber_deduction_coefficient"],
                    ),
                )

                db.commit()

                # Invalidate products cache
                cache_invalidate("products:*")

                # Return created product with enhanced data
                product_id = cursor.lastrowid
                created_product = dict(
                    db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
                )

                # Add calculated fields
                created_product["net_carbs"] = net_carbs_result["net_carbs"]
                created_product["fiber_estimated"] = net_carbs_result["fiber_estimated"]
                created_product["fiber_deduction_coefficient"] = net_carbs_result[
                    "fiber_deduction_coefficient"
                ]
                created_product["keto_index"] = keto_result["keto_index"]
                created_product["keto_category"] = keto_result["keto_category"]
                created_product["carbs_score"] = keto_result["carbs_score"]
                created_product["fat_score"] = keto_result["fat_score"]
                created_product["quality_score"] = keto_result["quality_score"]
                created_product["gi_score"] = keto_result["gi_score"]

                return (
                    jsonify(
                        json_response(
                            created_product, SUCCESS_MESSAGES["product_created"], HTTP_CREATED
                        )
                    ),
                    HTTP_CREATED,
                )

            except sqlite3.IntegrityError as e:
                current_app.logger.error(f"Product creation integrity error: {e}")
                return (
                    jsonify(
                        json_response(
                            None,
                            "Database error",
                            status=HTTP_BAD_REQUEST,
                            errors=["Failed to create product due to database constraint"],
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

    except sqlite3.IntegrityError as e:
        error_msg = str(e)
        if "UNIQUE constraint failed" in error_msg:
            return (
                jsonify(json_response(None, "❌ Product with this name already exists", 400)),
                400,
            )
        elif "CHECK constraint failed" in error_msg:
            return jsonify(json_response(None, "❌ Invalid data values provided", 400)), 400
        else:
            return jsonify(json_response(None, ERROR_MESSAGES["constraint_violation"], 400)), 400
    except sqlite3.Error as e:
        current_app.logger.error(f"Database error in products API: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["database_error"], 500)), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error in products API: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


@products_bp.route("/<int:product_id>", methods=["GET", "DELETE", "PUT"])
def product_detail_api(product_id):
    """Individual product operations"""
    db = get_db()

    try:
        if request.method == "GET":
            product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
            if not product:
                return (
                    jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)),
                    HTTP_NOT_FOUND,
                )

            return jsonify(json_response(dict(product)))

        elif request.method == "DELETE":
            # Check if product is used in log entries
            usage_count = db.execute(
                "SELECT COUNT(*) as count FROM log_entries WHERE item_type = 'product' AND item_id = ?",
                (product_id,),
            ).fetchone()["count"]

            if usage_count > 0:
                return (
                    jsonify(
                        json_response(
                            None,
                            f"Cannot delete product: used in {usage_count} log entries",
                            HTTP_BAD_REQUEST,
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Delete product
            cursor = db.execute("DELETE FROM products WHERE id = ?", (product_id,))
            if cursor.rowcount == 0:
                return (
                    jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)),
                    HTTP_NOT_FOUND,
                )

            db.commit()

            # Invalidate products cache
            cache_invalidate("products:*")

            return jsonify(json_response({}, SUCCESS_MESSAGES["product_deleted"]))

        elif request.method == "PUT":
            # Update product
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
                            errors=["Product name is required"],
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            calories = safe_float(data.get("calories_per_100g", 0))
            protein = safe_float(data.get("protein_per_100g", 0))
            fat = safe_float(data.get("fat_per_100g", 0))
            carbs = safe_float(data.get("carbs_per_100g", 0))

            # Calculate calories from macros if not provided or if provided calories are 0
            if calories == 0:
                calories = calculate_calories_from_macros(protein, fat, carbs)

            # Validate nutrition values (calories are now optional)
            validation_errors = validate_nutrition_values(
                calories, protein, fat, carbs, calories_optional=True
            )
            if validation_errors:
                return (
                    jsonify(
                        json_response(
                            None,
                            ERROR_MESSAGES["validation_error"],
                            status=HTTP_BAD_REQUEST,
                            errors=validation_errors,
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Check if product exists
            existing = db.execute("SELECT id FROM products WHERE id = ?", (product_id,)).fetchone()
            if not existing:
                return (
                    jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)),
                    HTTP_NOT_FOUND,
                )

            # Check for name conflicts (excluding current product)
            name_conflict = db.execute(
                "SELECT id FROM products WHERE name = ? AND id != ?", (name, product_id)
            ).fetchone()

            if name_conflict:
                return (
                    jsonify(
                        json_response(
                            None,
                            ERROR_MESSAGES["validation_error"],
                            status=HTTP_BAD_REQUEST,
                            errors=["Product with this name already exists"],
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Update product
            cursor = db.execute(
                """
                UPDATE products
                SET name = ?, calories_per_100g = ?, protein_per_100g = ?,
                    fat_per_100g = ?, carbs_per_100g = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (name, calories, protein, fat, carbs, product_id),
            )

            db.commit()

            # Invalidate products cache
            cache_invalidate("products:*")

            # Return updated product
            updated_product = db.execute(
                "SELECT * FROM products WHERE id = ?", (product_id,)
            ).fetchone()
            return jsonify(json_response(dict(updated_product), "Product updated successfully!"))

    except Exception as e:
        current_app.logger.error(f"Product detail API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()
