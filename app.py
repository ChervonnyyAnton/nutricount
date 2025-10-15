#!/usr/bin/env python3
"""
Nutrition Tracker v2.0 - WCAG 2.2 Compliant Web Application
Local nutrition tracking application optimized for Raspberry Pi Zero 2W
"""

import hashlib
import hmac
import os
import shutil
import sqlite3
import time
from datetime import date, datetime
from functools import wraps

from flask import Flask, jsonify, render_template, request, send_file, send_from_directory
from flask_cors import CORS

# Import our modular components
from src.config import Config
from src.constants import (
    ERROR_MESSAGES,
    HTTP_BAD_REQUEST,
    HTTP_CREATED,
    HTTP_NOT_FOUND,
    HTTP_OK,
    MEAL_TYPES,
    SUCCESS_MESSAGES,
)
from src.nutrition_calculator import (
    calculate_bmr_katch_mcardle,
    calculate_bmr_mifflin_st_jeor,
    calculate_calories_from_macros,
    calculate_gki,
    calculate_keto_index_advanced,
    calculate_keto_macros_advanced,
    calculate_lean_body_mass,
    calculate_net_carbs_advanced,
    calculate_target_calories,
    calculate_tdee,
    KETO_INDEX_CATEGORIES,
)
from src.utils import (
    clean_string,
    get_database_stats,
    json_response,
    safe_float,
    safe_int,
    validate_dish_data,
    validate_log_data,
    validate_nutrition_values,
    validate_product_data,
)

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")
app.config.from_object(Config)

# Enable CORS for API endpoints
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Simple in-memory cache for Pi Zero 2W
_cache = {}
_cache_timeout = 300  # 5 minutes

def cached_response(timeout=300):
    """Simple cache decorator for API responses"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{f.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Check if cached response exists and is not expired
            if cache_key in _cache:
                cached_data, timestamp = _cache[cache_key]
                if time.time() - timestamp < timeout:
                    return cached_data
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            _cache[cache_key] = (result, time.time())
            
            # Clean old cache entries (simple cleanup)
            if len(_cache) > 50:  # Limit cache size
                oldest_key = min(_cache.keys(), key=lambda k: _cache[k][1])
                del _cache[oldest_key]
            
            return result
        return decorated_function
    return decorator

# ============================================
# Database Connection Management
# ============================================


def get_db():
    """Get database connection with proper configuration"""
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row

    # Enable WAL mode for better concurrency (only for file databases)
    if app.config['DATABASE'] != ':memory:':
        db.execute("PRAGMA journal_mode = WAL")
        db.execute("PRAGMA synchronous = NORMAL")
    
    db.execute("PRAGMA foreign_keys = ON")

    return db


def init_db():
    """Initialize database with schema v2"""
    try:
        with open("schema_v2.sql", "r") as f:
            schema = f.read()

        db = get_db()
        db.executescript(schema)
        db.commit()
        db.close()

        print("✅ Database initialized successfully")
        
        # Load sample data only for non-testing environments
        if not app.config.get('TESTING', False) and app.config['DATABASE'] != ':memory:':
            db = get_db()
            sample_products = [
                ('Chicken Breast', 165, 31.0, 3.6, 0.0, 0.0, 'meat', 0, 'raw'),
                ('Salmon', 208, 25.4, 12.4, 0.0, 0.0, 'fish', 0, 'raw'),
                ('Eggs', 155, 13.0, 11.0, 1.1, 0.0, 'dairy', 0, 'raw'),
                ('Avocado', 160, 2.0, 14.7, 8.5, 6.7, 'fruits', 15, 'raw'),
                ('Broccoli', 34, 2.8, 0.4, 6.6, 2.6, 'vegetables', 15, 'raw'),
                ('Almonds', 579, 21.2, 49.9, 21.6, 12.5, 'nuts_seeds', 15, 'minimal'),
                ('Spinach', 23, 2.9, 0.4, 3.6, 2.2, 'leafy_vegetables', 15, 'raw'),
                ('Blueberries', 57, 0.7, 0.3, 14.5, 2.4, 'berries', 25, 'raw'),
                ('Sweet Potato', 86, 1.6, 0.1, 20.1, 3.0, 'root_vegetables', 70, 'minimal')
            ]
            
            for product in sample_products:
                db.execute(
                    "INSERT OR IGNORE INTO products (name, calories_per_100g, protein_per_100g, fat_per_100g, carbs_per_100g, fiber_per_100g, category, glycemic_index, processing_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    product
                )
            
            db.commit()
            db.close()
            
            print(f"📊 Sample products loaded: {len(sample_products)}")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise


# ============================================
# Main Routes
# ============================================


@app.route("/")
def index():
    """Main application page"""
    return render_template("index.html")


@app.route("/health")
def health():
    """Health check endpoint"""
    try:
        db = get_db()
        db.execute("SELECT 1").fetchone()
        db.close()

        return jsonify(
            {
                "status": "healthy",
                "version": Config.VERSION,
                "timestamp": datetime.utcnow().isoformat(),
                "database": "ok",
            }
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "version": Config.VERSION,
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": str(e),
                }
            ),
            500,
        )


# ============================================
# PWA Support
# ============================================


@app.route("/manifest.json")
def manifest():
    """PWA manifest file"""
    return send_from_directory(app.root_path, "manifest.json")


@app.route("/sw.js")
def service_worker():
    """Service worker for offline support"""
    return send_from_directory("static", "sw.js")


# ============================================
# Products API
# ============================================


@app.route("/api/products", methods=["GET", "POST"])
def products_api():
    """Products CRUD endpoint"""
    db = get_db()

    try:
        if request.method == "GET":
            # Search and pagination
            search = request.args.get("search", "").strip()
            limit = min(int(request.args.get("limit", 50)), Config.API_MAX_PER_PAGE)
            offset = max(0, int(request.args.get("offset", 0)))

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
                        product["processing_level"] if "processing_level" in product.keys() else None,
                    )

                    # Add calculated fields
                    product["net_carbs"] = net_carbs_result["net_carbs"]
                    product["fiber_estimated"] = net_carbs_result["fiber_estimated"]
                    product["fiber_deduction_coefficient"] = net_carbs_result["fiber_deduction_coefficient"]
                    product["keto_index"] = keto_result["keto_index"]
                    product["keto_category"] = keto_result["keto_category"]
                    product["carbs_score"] = keto_result["carbs_score"]
                    product["fat_score"] = keto_result["fat_score"]
                    product["quality_score"] = keto_result["quality_score"]
                    product["gi_score"] = keto_result["gi_score"]

                except Exception as e:
                    app.logger.warning(f"Error calculating enhanced fields for product {product['id']}: {e}")
                    # Add default values if calculation fails
                    product["net_carbs"] = product["carbs_per_100g"]
                    product["fiber_estimated"] = True
                    product["keto_index"] = 0
                    product["keto_category"] = "Не для кето"
                    product["carbs_score"] = 0
                    product["fat_score"] = 0
                    product["gi_score"] = 50

                products.append(product)

            return jsonify(json_response(products))

        else:  # POST
            data = request.get_json() or {}

            # Validate product data
            is_valid, errors, cleaned_data = validate_product_data(data)
            if not is_valid:
                return (
                    jsonify(json_response(None, "Validation failed", status=HTTP_BAD_REQUEST, errors=errors)),
                    HTTP_BAD_REQUEST,
                )

            # Check for duplicate name
            existing = db.execute("SELECT id FROM products WHERE name = ?", (cleaned_data["name"],)).fetchone()
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
                category = clean_string(data.get("category"))
                processing_level = clean_string(data.get("processing_level"))
                glycemic_index = safe_float(data.get("glycemic_index"))
                region = clean_string(data.get("region", "US"))

                # Calculate calories using Atwater system
                calculated_calories = calculate_calories_from_macros(
                    cleaned_data["protein_per_100g"], cleaned_data["fat_per_100g"], cleaned_data["carbs_per_100g"]
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

                # Return created product with enhanced data
                product_id = cursor.lastrowid
                created_product = dict(db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone())

                # Add calculated fields
                created_product["net_carbs"] = net_carbs_result["net_carbs"]
                created_product["fiber_estimated"] = net_carbs_result["fiber_estimated"]
                created_product["fiber_deduction_coefficient"] = net_carbs_result["fiber_deduction_coefficient"]
                created_product["keto_index"] = keto_result["keto_index"]
                created_product["keto_category"] = keto_result["keto_category"]
                created_product["carbs_score"] = keto_result["carbs_score"]
                created_product["fat_score"] = keto_result["fat_score"]
                created_product["quality_score"] = keto_result["quality_score"]
                created_product["gi_score"] = keto_result["gi_score"]

                return (
                    jsonify(json_response(created_product, SUCCESS_MESSAGES["product_created"], HTTP_CREATED)),
                    HTTP_CREATED,
                )

            except sqlite3.IntegrityError as e:
                app.logger.error(f"Product creation integrity error: {e}")
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
            return jsonify(json_response(None, "❌ Product with this name already exists", 400)), 400
        elif "CHECK constraint failed" in error_msg:
            return jsonify(json_response(None, "❌ Invalid data values provided", 400)), 400
        else:
            return jsonify(json_response(None, ERROR_MESSAGES["constraint_violation"], 400)), 400
    except sqlite3.Error as e:
        app.logger.error(f"Database error in products API: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["database_error"], 500)), 500
    except Exception as e:
        app.logger.error(f"Unexpected error in products API: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


@app.route("/api/products/<int:product_id>", methods=["GET", "DELETE", "PUT"])
def product_detail_api(product_id):
    """Individual product operations"""
    db = get_db()

    try:
        if request.method == "GET":
            product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
            if not product:
                return jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)), HTTP_NOT_FOUND

            return jsonify(json_response(dict(product)))

        elif request.method == "DELETE":
            # Check if product is used in log entries
            usage_count = db.execute(
                "SELECT COUNT(*) as count FROM log_entries WHERE item_type = 'product' AND item_id = ?", (product_id,)
            ).fetchone()["count"]

            if usage_count > 0:
                return (
                    jsonify(
                        json_response(
                            None, f"Cannot delete product: used in {usage_count} log entries", HTTP_BAD_REQUEST
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Delete product
            cursor = db.execute("DELETE FROM products WHERE id = ?", (product_id,))
            if cursor.rowcount == 0:
                return jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)), HTTP_NOT_FOUND

            db.commit()
            return jsonify(json_response({}, SUCCESS_MESSAGES["product_deleted"]))

        elif request.method == "PUT":
            # Update product
            data = request.get_json() or {}

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
                from src.nutrition_calculator import calculate_calories_from_macros

                calories = calculate_calories_from_macros(protein, fat, carbs)

            # Validate nutrition values (calories are now optional)
            validation_errors = validate_nutrition_values(calories, protein, fat, carbs, calories_optional=True)
            if validation_errors:
                return (
                    jsonify(
                        json_response(
                            None, ERROR_MESSAGES["validation_error"], status=HTTP_BAD_REQUEST, errors=validation_errors
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Check if product exists
            existing = db.execute("SELECT id FROM products WHERE id = ?", (product_id,)).fetchone()
            if not existing:
                return jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)), HTTP_NOT_FOUND

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

            # Return updated product
            updated_product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
            return jsonify(json_response(dict(updated_product), "Product updated successfully!"))

    except Exception as e:
        app.logger.error(f"Product detail API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


# ============================================
# Dishes API
# ============================================


@app.route("/api/dishes", methods=["GET", "POST"])
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
            data = request.get_json() or {}

            # Validate dish data
            is_valid, errors, cleaned_data = validate_dish_data(data)
            if not is_valid:
                return (
                    jsonify(json_response(None, "Validation failed", status=HTTP_BAD_REQUEST, errors=errors)),
                    HTTP_BAD_REQUEST,
                )

            # Check for duplicate name
            existing = db.execute("SELECT id FROM dishes WHERE name = ?", (cleaned_data["name"],)).fetchone()
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
                f"SELECT id FROM products WHERE id IN ({','.join('?' * len(product_ids))})", product_ids
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
                    product = db.execute("SELECT * FROM products WHERE id = ?", (ingredient["product_id"],)).fetchone()

                    if product:
                        # Create RecipeIngredient for advanced calculation
                        from src.nutrition_calculator import RecipeIngredient

                        recipe_ingredient = RecipeIngredient(
                            name=product["name"],
                            raw_weight=ingredient["quantity_grams"],
                            nutrition_per_100g={
                                "protein": product["protein_per_100g"],
                                "fats": product["fat_per_100g"],
                                "carbs": product["carbs_per_100g"],
                                "fiber": product["fiber_per_100g"] if "fiber_per_100g" in product.keys() else 0,
                                "sugars": product["sugars_per_100g"] if "sugars_per_100g" in product.keys() else 0,
                            },
                            category=product["category"] if "category" in product.keys() else "unknown",
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
                from src.nutrition_calculator import calculate_recipe_nutrition

                recipe_result = calculate_recipe_nutrition(recipe_ingredients, cleaned_data["name"], servings=1)

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
                created_dish = dict(db.execute("SELECT * FROM dishes WHERE id = ?", (dish_id,)).fetchone())

                return (
                    jsonify(json_response(created_dish, SUCCESS_MESSAGES["dish_created"], HTTP_CREATED)),
                    HTTP_CREATED,
                )

            except sqlite3.IntegrityError as e:
                app.logger.error(f"Dish creation integrity error: {e}")
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
        app.logger.error(f"Dishes API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


@app.route("/api/dishes/<int:dish_id>", methods=["GET", "PUT", "DELETE"])
def dish_detail_api(dish_id):
    """Dish detail operations (GET, PUT, DELETE)"""
    db = get_db()

    try:
        if request.method == "GET":
            # Get dish details
            dish = db.execute("SELECT * FROM dishes WHERE id = ?", (dish_id,)).fetchone()
            if not dish:
                return jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)), HTTP_NOT_FOUND

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
            data = request.get_json() or {}

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
                return jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)), HTTP_NOT_FOUND

            # Check for name conflicts (excluding current dish)
            name_conflict = db.execute("SELECT id FROM dishes WHERE name = ? AND id != ?", (name, dish_id)).fetchone()

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
                            (dish_id, product_id, quantity_grams, preparation_method, edible_portion),
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
                "SELECT COUNT(*) as count FROM log_entries WHERE item_type = 'dish' AND item_id = ?", (dish_id,)
            ).fetchone()["count"]

            if usage_count > 0:
                return (
                    jsonify(
                        json_response(None, f"Cannot delete dish: used in {usage_count} log entries", HTTP_BAD_REQUEST)
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Delete dish (ingredients will cascade)
            cursor = db.execute("DELETE FROM dishes WHERE id = ?", (dish_id,))
            if cursor.rowcount == 0:
                return jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)), HTTP_NOT_FOUND

            db.commit()
            return jsonify(json_response({}, SUCCESS_MESSAGES["dish_deleted"]))

    except Exception as e:
        app.logger.error(f"Dish detail API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


# ============================================
# Food Log API
# ============================================


@app.route("/api/log", methods=["GET", "POST"])
def log_api():
    """Food log CRUD endpoint"""
    db = get_db()

    try:
        if request.method == "GET":
            date_filter = request.args.get("date")
            limit = min(int(request.args.get("limit", 100)), Config.API_MAX_PER_PAGE)

            if date_filter:
                query = """
                    SELECT * FROM log_entries_with_details 
                    WHERE date = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """
                params = (date_filter, limit)
            else:
                query = """
                    SELECT * FROM log_entries_with_details 
                    ORDER BY date DESC, created_at DESC 
                    LIMIT ?
                """
                params = (limit,)

            log_entries = [dict(row) for row in db.execute(query, params).fetchall()]

            # Process log entries to calculate nutrition values
            processed_entries = []
            for entry in log_entries:
                processed_entry = dict(entry)

                # Calculate nutrition values based on item type
                if entry["item_type"] == "product":
                    # For products, use per_100g values and calculate actual amounts
                    quantity_factor = entry["quantity_grams"] / 100.0
                    processed_entry["calories"] = (
                        entry["calories_per_100g"] * quantity_factor if entry["calories_per_100g"] else None
                    )
                    processed_entry["protein"] = (
                        entry["protein_per_100g"] * quantity_factor if entry["protein_per_100g"] else None
                    )
                    processed_entry["fat"] = entry["fat_per_100g"] * quantity_factor if entry["fat_per_100g"] else None
                    processed_entry["carbs"] = (
                        entry["carbs_per_100g"] * quantity_factor if entry["carbs_per_100g"] else None
                    )
                elif entry["item_type"] == "dish":
                    # For dishes, use dish_per_100g values and calculate actual amounts
                    quantity_factor = entry["quantity_grams"] / 100.0
                    processed_entry["calories"] = entry["calculated_calories"] if entry["calculated_calories"] else None
                    processed_entry["protein"] = (
                        entry["dish_protein_per_100g"] * quantity_factor if entry["dish_protein_per_100g"] else None
                    )
                    processed_entry["fat"] = (
                        entry["dish_fat_per_100g"] * quantity_factor if entry["dish_fat_per_100g"] else None
                    )
                    processed_entry["carbs"] = (
                        entry["dish_carbs_per_100g"] * quantity_factor if entry["dish_carbs_per_100g"] else None
                    )

                processed_entries.append(processed_entry)

            return jsonify(json_response(processed_entries))

        else:  # POST
            data = request.get_json() or {}

            # Validate log data
            is_valid, errors, cleaned_data = validate_log_data(data)
            if not is_valid:
                return (
                    jsonify(json_response(None, "Validation failed", status=HTTP_BAD_REQUEST, errors=errors)),
                    HTTP_BAD_REQUEST,
                )

            # Verify item exists
            if cleaned_data["item_type"] == "product":
                item_exists = db.execute(
                    "SELECT name FROM products WHERE id = ?", (cleaned_data["item_id"],)
                ).fetchone()
            else:
                item_exists = db.execute("SELECT name FROM dishes WHERE id = ?", (cleaned_data["item_id"],)).fetchone()

            if not item_exists:
                return (
                    jsonify(
                        json_response(
                            None,
                            "Validation failed",
                            status=HTTP_BAD_REQUEST,
                            errors=[f"{cleaned_data['item_type'].title()} with ID {cleaned_data['item_id']} not found"],
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Create log entry
            try:
                cursor = db.execute(
                    """
                    INSERT INTO log_entries (date, item_type, item_id, quantity_grams, meal_time, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        cleaned_data["date"],
                        cleaned_data["item_type"],
                        cleaned_data["item_id"],
                        cleaned_data["quantity_grams"],
                        cleaned_data["meal_time"],
                        cleaned_data.get("notes", ""),
                    ),
                )

                db.commit()

                # Return created log entry with details
                log_id = cursor.lastrowid
                log_entry = dict(
                    db.execute("SELECT * FROM log_entries_with_details WHERE id = ?", (log_id,)).fetchone()
                )

                return jsonify(json_response(log_entry, SUCCESS_MESSAGES["log_added"], HTTP_CREATED)), HTTP_CREATED

            except sqlite3.IntegrityError as e:
                app.logger.error(f"Log creation integrity error: {e}")
                return (
                    jsonify(
                        json_response(
                            None,
                            "Database error",
                            status=HTTP_BAD_REQUEST,
                            errors=["Failed to create log entry due to database constraint"],
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

    except Exception as e:
        app.logger.error(f"Log API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


@app.route("/api/log/<int:log_id>", methods=["GET", "PUT", "DELETE"])
def log_detail_api(log_id):
    """Log entry detail operations (GET, PUT, DELETE)"""
    db = get_db()

    try:
        if request.method == "GET":
            # Get log entry details
            log_entry = db.execute(
                """
                SELECT * FROM log_entries_with_details WHERE id = ?
            """,
                (log_id,),
            ).fetchone()

            if not log_entry:
                return jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)), HTTP_NOT_FOUND

            return jsonify(json_response(dict(log_entry)))

        elif request.method == "PUT":
            # Update log entry
            data = request.get_json() or {}

            # Validate required fields
            date = (data.get("date") or "").strip()
            item_type = (data.get("item_type") or "").strip()
            item_id = data.get("item_id")
            quantity_grams = safe_float(data.get("quantity_grams", 0))
            meal_time = (data.get("meal_time") or "").strip()

            if not date or not item_type or not item_id or quantity_grams <= 0 or not meal_time:
                return (
                    jsonify(
                        json_response(
                            None,
                            ERROR_MESSAGES["validation_error"],
                            status=HTTP_BAD_REQUEST,
                            errors=["All fields are required"],
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Check if log entry exists
            existing = db.execute("SELECT id FROM log_entries WHERE id = ?", (log_id,)).fetchone()
            if not existing:
                return jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)), HTTP_NOT_FOUND

            # Validate item exists
            if item_type == "product":
                item_exists = db.execute("SELECT id FROM products WHERE id = ?", (item_id,)).fetchone()
            elif item_type == "dish":
                item_exists = db.execute("SELECT id FROM dishes WHERE id = ?", (item_id,)).fetchone()
            else:
                return (
                    jsonify(
                        json_response(
                            None,
                            ERROR_MESSAGES["validation_error"],
                            status=HTTP_BAD_REQUEST,
                            errors=["Invalid item type"],
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            if not item_exists:
                return (
                    jsonify(
                        json_response(
                            None,
                            ERROR_MESSAGES["validation_error"],
                            status=HTTP_BAD_REQUEST,
                            errors=[f"{item_type.title()} not found"],
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Update log entry
            cursor = db.execute(
                """
                UPDATE log_entries 
                SET date = ?, item_type = ?, item_id = ?, quantity_grams = ?, 
                    meal_time = ?, notes = ?
                WHERE id = ?
            """,
                (date, item_type, item_id, quantity_grams, meal_time, (data.get("notes") or "").strip(), log_id),
            )

            db.commit()

            # Return updated log entry
            updated_entry = db.execute(
                """
                SELECT * FROM log_entries_with_details WHERE id = ?
            """,
                (log_id,),
            ).fetchone()

            return jsonify(json_response(dict(updated_entry), "Log entry updated successfully!"))

        elif request.method == "DELETE":
            cursor = db.execute("DELETE FROM log_entries WHERE id = ?", (log_id,))
            if cursor.rowcount == 0:
                return jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)), HTTP_NOT_FOUND

            db.commit()
            return jsonify(json_response({}, SUCCESS_MESSAGES["log_deleted"]))

    except Exception as e:
        app.logger.error(f"Log detail API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


# ============================================
# Statistics API
# ============================================


@app.route("/api/stats/<date_str>")
@cached_response(timeout=300)  # Cache stats for 5 minutes
def daily_stats_api(date_str):
    """Get daily nutrition statistics"""
    db = get_db()

    try:
        # Calculate nutrition totals for the day (optimized query)
        stats_query = """
            SELECT 
                SUM(calculated_calories) as calories,
                SUM(CASE 
                    WHEN item_type = 'product' THEN protein_per_100g * quantity_grams / 100.0
                    WHEN item_type = 'dish' THEN dish_protein_per_100g * quantity_grams / 100.0
                    ELSE 0 
                END) as protein,
                SUM(CASE 
                    WHEN item_type = 'product' THEN fat_per_100g * quantity_grams / 100.0
                    WHEN item_type = 'dish' THEN dish_fat_per_100g * quantity_grams / 100.0
                    ELSE 0 
                END) as fat,
                SUM(CASE 
                    WHEN item_type = 'product' THEN carbs_per_100g * quantity_grams / 100.0
                    WHEN item_type = 'dish' THEN dish_carbs_per_100g * quantity_grams / 100.0
                    ELSE 0 
                END) as carbs,
                COUNT(*) as entries_count
            FROM log_entries_with_details
            WHERE date = ?
        """

        stats = db.execute(stats_query, (date_str,)).fetchone()

        # Calculate keto index using advanced algorithm
        calories = safe_float(stats["calories"])
        protein = safe_float(stats["protein"])
        fat = safe_float(stats["fat"])
        carbs = safe_float(stats["carbs"])
        entries_count = safe_int(stats["entries_count"])

        # Calculate keto index for daily totals (per 100g equivalent)
        if calories > 0:
            # Convert to per 100g values for keto index calculation
            total_weight = 1000  # Assume 1kg total food weight for calculation
            protein_per_100g = protein * 100 / total_weight
            fat_per_100g = fat * 100 / total_weight
            carbs_per_100g = carbs * 100 / total_weight

            keto_result = calculate_keto_index_advanced(
                protein_per_100g, fat_per_100g, carbs_per_100g, check_total=False
            )
            keto_index = keto_result["keto_index"]
        else:
            keto_index = 0

        # Get personal macros for comparison
        personal_macros = None
        goal_comparison = None

        try:
            # Get current profile
            profile = db.execute("SELECT * FROM user_profile ORDER BY updated_at DESC LIMIT 1").fetchone()

            if profile:
                profile_dict = dict(profile)

                # Calculate age
                from datetime import date, datetime

                birth_date = datetime.strptime(profile_dict["birth_date"], "%Y-%m-%d").date()
                today = date.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

                # Calculate BMR using advanced algorithm
                # Use Katch-McArdle if LBM is available (more accurate for high body fat)
                lbm = profile_dict.get("lean_body_mass_kg")
                if lbm is None and profile_dict.get("body_fat_percentage") is not None:
                    lbm = calculate_lean_body_mass(profile_dict["weight_kg"], profile_dict["body_fat_percentage"])

                if lbm is not None:
                    bmr = calculate_bmr_katch_mcardle(lbm)
                else:
                    bmr = calculate_bmr_mifflin_st_jeor(
                        profile_dict["weight_kg"], profile_dict["height_cm"], age, profile_dict["gender"]
                    )

                # Calculate TDEE using advanced algorithm
                tdee = calculate_tdee(bmr, profile_dict["activity_level"])

                # Calculate target calories using advanced algorithm
                target_calories = calculate_target_calories(tdee, profile_dict["goal"])

                # Calculate keto macros using advanced algorithm
                # LBM already calculated above for BMR
                keto_type = profile_dict.get("keto_type", "standard")
                macros = calculate_keto_macros_advanced(
                    target_calories, lbm, profile_dict["activity_level"], keto_type, profile_dict["goal"]
                )

                carbs_grams = macros["carbs"]
                protein_grams = macros["protein"]
                fats_grams = macros["fats"]
                carbs_calories = carbs_grams * 4
                protein_calories = protein_grams * 4
                fats_calories = fats_grams * 9

                personal_macros = {
                    "bmr": round(bmr, 0),
                    "tdee": round(tdee, 0),
                    "target_calories": round(target_calories, 0),
                    "carbs": round(carbs_grams, 1),
                    "protein": round(protein_grams, 1),
                    "fats": round(fats_grams, 1),
                    "carbs_percentage": round((carbs_calories / target_calories) * 100, 1),
                    "protein_percentage": round((protein_calories / target_calories) * 100, 1),
                    "fats_percentage": round((fats_calories / target_calories) * 100, 1),
                }

                # Calculate goal comparison percentages
                goal_comparison = {
                    "calories": {
                        "actual": round(calories, 1),
                        "target": round(target_calories, 0),
                        "percentage": round((calories / target_calories) * 100, 1) if target_calories > 0 else 0,
                        "status": (
                            "good"
                            if 90 <= (calories / target_calories) * 100 <= 110
                            else ("low" if calories < target_calories * 0.9 else "high")
                        ),
                    },
                    "protein": {
                        "actual": round(protein, 1),
                        "target": round(protein_grams, 1),
                        "percentage": round((protein / protein_grams) * 100, 1) if protein_grams > 0 else 0,
                        "status": (
                            "good"
                            if 90 <= (protein / protein_grams) * 100 <= 110
                            else ("low" if protein < protein_grams * 0.9 else "high")
                        ),
                    },
                    "fat": {
                        "actual": round(fat, 1),
                        "target": round(fats_grams, 1),
                        "percentage": round((fat / fats_grams) * 100, 1) if fats_grams > 0 else 0,
                        "status": (
                            "good"
                            if 90 <= (fat / fats_grams) * 100 <= 110
                            else ("low" if fat < fats_grams * 0.9 else "high")
                        ),
                    },
                    "carbs": {
                        "actual": round(carbs, 1),
                        "target": round(carbs_grams, 1),
                        "percentage": round((carbs / carbs_grams) * 100, 1) if carbs_grams > 0 else 0,
                        "status": (
                            "good" if carbs <= carbs_grams * 1.1 else "high"
                        ),  # For carbs, being under target is good
                    },
                }

        except Exception as e:
            app.logger.warning(f"Could not calculate personal macros: {e}")

        # Get meal breakdown (optimized query)
        meal_breakdown = {}
        for meal_type in MEAL_TYPES:
            meal_stats = db.execute(
                """
                SELECT COUNT(*) as count,
                       SUM(calculated_calories) as calories
                FROM log_entries_with_details
                WHERE date = ? AND meal_time = ?
                """,
                (date_str, meal_type),
            ).fetchone()

            meal_breakdown[meal_type] = {
                "entries": safe_int(meal_stats["count"]),
                "calories": safe_float(meal_stats["calories"]),
            }

        response_data = {
            "date": date_str,
            "calories": round(calories, 1),
            "protein": round(protein, 1),
            "fat": round(fat, 1),
            "carbs": round(carbs, 1),
            "keto_index": keto_index,
            "entries_count": entries_count,
            "meal_breakdown": meal_breakdown,
            "personal_macros": personal_macros,
            "goal_comparison": goal_comparison,
        }

        return jsonify(json_response(response_data))

    except Exception as e:
        app.logger.error(f"Stats API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


@app.route("/api/stats/weekly/<date_str>")
def weekly_stats_api(date_str):
    """Get weekly nutrition statistics"""
    db = get_db()

    try:
        from datetime import datetime, timedelta

        # Parse the date and calculate week start (Monday)
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        week_start = target_date - timedelta(days=target_date.weekday())
        week_end = week_start + timedelta(days=6)

        # Calculate nutrition totals for the week
        stats_query = """
            SELECT 
                SUM(calculated_calories) as calories,
                SUM(CASE 
                    WHEN item_type = 'product' THEN protein_per_100g * quantity_grams / 100.0
                    WHEN item_type = 'dish' THEN dish_protein_per_100g * quantity_grams / 100.0
                    ELSE 0 
                END) as protein,
                SUM(CASE 
                    WHEN item_type = 'product' THEN fat_per_100g * quantity_grams / 100.0
                    WHEN item_type = 'dish' THEN dish_fat_per_100g * quantity_grams / 100.0
                    ELSE 0 
                END) as fat,
                SUM(CASE 
                    WHEN item_type = 'product' THEN carbs_per_100g * quantity_grams / 100.0
                    WHEN item_type = 'dish' THEN dish_carbs_per_100g * quantity_grams / 100.0
                    ELSE 0 
                END) as carbs,
                COUNT(*) as entries_count
            FROM log_entries_with_details
            WHERE date >= ? AND date <= ?
        """

        stats = db.execute(stats_query, (week_start.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d"))).fetchone()

        # Calculate keto index using advanced algorithm
        calories = safe_float(stats["calories"])
        protein = safe_float(stats["protein"])
        fat = safe_float(stats["fat"])
        carbs = safe_float(stats["carbs"])
        entries_count = safe_int(stats["entries_count"])

        # Calculate keto index for daily totals (per 100g equivalent)
        if calories > 0:
            # Convert to per 100g values for keto index calculation
            total_weight = 1000  # Assume 1kg total food weight for calculation
            protein_per_100g = protein * 100 / total_weight
            fat_per_100g = fat * 100 / total_weight
            carbs_per_100g = carbs * 100 / total_weight

            keto_result = calculate_keto_index_advanced(
                protein_per_100g, fat_per_100g, carbs_per_100g, check_total=False
            )
            keto_index = keto_result["keto_index"]
        else:
            keto_index = 0

        # Get personal macros for comparison (multiply by 7 for weekly targets)
        personal_macros = None
        goal_comparison = None

        try:
            # Get current profile
            profile = db.execute("SELECT * FROM user_profile ORDER BY updated_at DESC LIMIT 1").fetchone()

            if profile:
                profile_dict = dict(profile)

                # Calculate age
                from datetime import date, datetime

                birth_date = datetime.strptime(profile_dict["birth_date"], "%Y-%m-%d").date()
                today = date.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

                # Calculate BMR using advanced algorithm
                # Use Katch-McArdle if LBM is available (more accurate for high body fat)
                lbm = profile_dict.get("lean_body_mass_kg")
                if lbm is None and profile_dict.get("body_fat_percentage") is not None:
                    lbm = calculate_lean_body_mass(profile_dict["weight_kg"], profile_dict["body_fat_percentage"])

                if lbm is not None:
                    bmr = calculate_bmr_katch_mcardle(lbm)
                else:
                    bmr = calculate_bmr_mifflin_st_jeor(
                        profile_dict["weight_kg"], profile_dict["height_cm"], age, profile_dict["gender"]
                    )

                # Calculate TDEE using advanced algorithm
                tdee = calculate_tdee(bmr, profile_dict["activity_level"])

                # Calculate target calories using advanced algorithm
                target_calories = calculate_target_calories(tdee, profile_dict["goal"])

                # Calculate keto macros using advanced algorithm
                # LBM already calculated above for BMR
                keto_type = profile_dict.get("keto_type", "standard")
                macros = calculate_keto_macros_advanced(
                    target_calories, lbm, profile_dict["activity_level"], keto_type, profile_dict["goal"]
                )

                carbs_grams = macros["carbs"]
                protein_grams = macros["protein"]
                fats_grams = macros["fats"]
                carbs_calories = carbs_grams * 4
                protein_calories = protein_grams * 4
                fats_calories = fats_grams * 9

                # Weekly targets (multiply by 7)
                personal_macros = {
                    "bmr": round(bmr * 7, 0),
                    "tdee": round(tdee * 7, 0),
                    "target_calories": round(target_calories * 7, 0),
                    "carbs": round(carbs_grams * 7, 1),
                    "protein": round(protein_grams * 7, 1),
                    "fats": round(fats_grams * 7, 1),
                    "carbs_percentage": round((carbs_calories / target_calories) * 100, 1),
                    "protein_percentage": round((protein_calories / target_calories) * 100, 1),
                    "fats_percentage": round((fats_calories / target_calories) * 100, 1),
                }

                # Calculate goal comparison percentages (weekly)
                weekly_target_calories = target_calories * 7
                weekly_protein_grams = protein_grams * 7
                weekly_fats_grams = fats_grams * 7
                weekly_carbs_grams = carbs_grams * 7

                goal_comparison = {
                    "calories": {
                        "actual": round(calories, 1),
                        "target": round(weekly_target_calories, 0),
                        "percentage": (
                            round((calories / weekly_target_calories) * 100, 1) if weekly_target_calories > 0 else 0
                        ),
                        "status": (
                            "good"
                            if 90 <= (calories / weekly_target_calories) * 100 <= 110
                            else ("low" if calories < weekly_target_calories * 0.9 else "high")
                        ),
                    },
                    "protein": {
                        "actual": round(protein, 1),
                        "target": round(weekly_protein_grams, 1),
                        "percentage": (
                            round((protein / weekly_protein_grams) * 100, 1) if weekly_protein_grams > 0 else 0
                        ),
                        "status": (
                            "good"
                            if 90 <= (protein / weekly_protein_grams) * 100 <= 110
                            else ("low" if protein < weekly_protein_grams * 0.9 else "high")
                        ),
                    },
                    "fat": {
                        "actual": round(fat, 1),
                        "target": round(weekly_fats_grams, 1),
                        "percentage": round((fat / weekly_fats_grams) * 100, 1) if weekly_fats_grams > 0 else 0,
                        "status": (
                            "good"
                            if 90 <= (fat / weekly_fats_grams) * 100 <= 110
                            else ("low" if fat < weekly_fats_grams * 0.9 else "high")
                        ),
                    },
                    "carbs": {
                        "actual": round(carbs, 1),
                        "target": round(weekly_carbs_grams, 1),
                        "percentage": round((carbs / weekly_carbs_grams) * 100, 1) if weekly_carbs_grams > 0 else 0,
                        "status": (
                            "good" if carbs <= weekly_carbs_grams * 1.1 else "high"
                        ),  # For carbs, being under target is good
                    },
                }

        except Exception as e:
            app.logger.warning(f"Could not calculate personal macros: {e}")

        # Get daily breakdown for the week
        daily_breakdown = {}
        for i in range(7):
            current_date = week_start + timedelta(days=i)
            date_str = current_date.strftime("%Y-%m-%d")

            day_stats = db.execute(
                """
                SELECT 
                    SUM(calculated_calories) as calories,
                    SUM(CASE 
                        WHEN item_type = 'product' THEN protein_per_100g * quantity_grams / 100.0
                        WHEN item_type = 'dish' THEN dish_protein_per_100g * quantity_grams / 100.0
                        ELSE 0 
                    END) as protein,
                    SUM(CASE 
                        WHEN item_type = 'product' THEN fat_per_100g * quantity_grams / 100.0
                        WHEN item_type = 'dish' THEN dish_fat_per_100g * quantity_grams / 100.0
                        ELSE 0 
                    END) as fat,
                    SUM(CASE 
                        WHEN item_type = 'product' THEN carbs_per_100g * quantity_grams / 100.0
                        WHEN item_type = 'dish' THEN dish_carbs_per_100g * quantity_grams / 100.0
                        ELSE 0 
                    END) as carbs,
                    COUNT(*) as entries_count
                FROM log_entries_with_details
                WHERE date = ?
            """,
                (date_str,),
            ).fetchone()

            daily_breakdown[date_str] = {
                "calories": round(safe_float(day_stats["calories"]), 1),
                "protein": round(safe_float(day_stats["protein"]), 1),
                "fat": round(safe_float(day_stats["fat"]), 1),
                "carbs": round(safe_float(day_stats["carbs"]), 1),
                "entries_count": safe_int(day_stats["entries_count"]),
            }

        response_data = {
            "week_start": week_start.strftime("%Y-%m-%d"),
            "week_end": week_end.strftime("%Y-%m-%d"),
            "calories": round(calories, 1),
            "protein": round(protein, 1),
            "fat": round(fat, 1),
            "carbs": round(carbs, 1),
            "keto_index": keto_index,
            "entries_count": entries_count,
            "daily_breakdown": daily_breakdown,
            "personal_macros": personal_macros,
            "goal_comparison": goal_comparison,
        }

        return jsonify(json_response(response_data))

    except Exception as e:
        app.logger.error(f"Weekly stats API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


# ============================================
# System API
# ============================================


@app.route("/api/gki", methods=["POST"])
def gki_api():
    """Calculate Glucose-Ketone Index (GKI)"""
    try:
        data = request.get_json() or {}

        # Validate input data
        glucose_mgdl = safe_float(data.get("glucose_mgdl"))
        ketones_mgdl = safe_float(data.get("ketones_mgdl"))

        if not glucose_mgdl or not ketones_mgdl:
            return (
                jsonify(
                    json_response(
                        None,
                        "Validation failed",
                        status=HTTP_BAD_REQUEST,
                        errors=["Both glucose_mgdl and ketones_mgdl are required"],
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        if glucose_mgdl <= 0 or ketones_mgdl <= 0:
            return (
                jsonify(
                    json_response(
                        None,
                        "Validation failed",
                        status=HTTP_BAD_REQUEST,
                        errors=["Glucose and ketones values must be positive"],
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        # Calculate GKI
        gki_result = calculate_gki(glucose_mgdl, ketones_mgdl)

        return jsonify(json_response(gki_result, "GKI calculated successfully"))

    except Exception as e:
        app.logger.error(f"GKI API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@app.route("/api/profile", methods=["GET", "POST", "PUT"])
def profile_api():
    """Get or update user profile"""
    try:
        db = get_db()

        if request.method == "GET":
            # Get current profile
            profile = db.execute("SELECT * FROM user_profile ORDER BY updated_at DESC LIMIT 1").fetchone()
            db.close()

            if profile:
                profile_dict = dict(profile)
                # Calculate age from birth_date
                from datetime import date, datetime

                birth_date = datetime.strptime(profile_dict["birth_date"], "%Y-%m-%d").date()
                today = date.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                profile_dict["age"] = age

                return jsonify(json_response(profile_dict, "Profile retrieved successfully"))
            else:
                return jsonify(json_response(None, "No profile found", status=HTTP_NOT_FOUND)), HTTP_NOT_FOUND

        else:  # POST or PUT
            data = request.get_json() or {}

            # Validate profile data
            errors = []

            # Required fields
            gender = data.get("gender")
            if not gender or gender not in ["male", "female"]:
                errors.append("Gender must be 'male' or 'female'")

            birth_date = data.get("birth_date")
            if not birth_date:
                errors.append("Birth date is required")
            else:
                try:
                    from datetime import datetime

                    datetime.strptime(birth_date, "%Y-%m-%d")
                except ValueError:
                    errors.append("Birth date must be in YYYY-MM-DD format")

            height_cm = data.get("height_cm")
            if not height_cm or not isinstance(height_cm, (int, float)) or height_cm < 100 or height_cm > 250:
                errors.append("Height must be between 100 and 250 cm")

            weight_kg = data.get("weight_kg")
            if not weight_kg or not isinstance(weight_kg, (int, float)) or weight_kg < 30 or weight_kg > 500:
                errors.append("Weight must be between 30 and 500 kg")

            activity_level = data.get("activity_level")
            if not activity_level or activity_level not in ["sedentary", "light", "moderate", "active", "very_active"]:
                errors.append("Activity level must be one of: sedentary, light, moderate, active, very_active")

            goal = data.get("goal")
            if not goal or goal not in ["weight_loss", "maintenance", "muscle_gain"]:
                errors.append("Goal must be one of: weight_loss, maintenance, muscle_gain")

            if errors:
                return (
                    jsonify(json_response(None, "Validation failed", status=HTTP_BAD_REQUEST, errors=errors)),
                    HTTP_BAD_REQUEST,
                )

            # Check if profile exists
            existing_profile = db.execute("SELECT id FROM user_profile ORDER BY updated_at DESC LIMIT 1").fetchone()

            if existing_profile and request.method == "PUT":
                # Update existing profile
                db.execute(
                    """
                    UPDATE user_profile 
                    SET gender = ?, birth_date = ?, height_cm = ?, weight_kg = ?, 
                        activity_level = ?, goal = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """,
                    (gender, birth_date, int(height_cm), float(weight_kg), activity_level, goal, existing_profile[0]),
                )
                profile_id = existing_profile[0]
            else:
                # Create new profile
                cursor = db.execute(
                    """
                    INSERT INTO user_profile (gender, birth_date, height_cm, weight_kg, activity_level, goal)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (gender, birth_date, int(height_cm), float(weight_kg), activity_level, goal),
                )
                profile_id = cursor.lastrowid

            db.commit()

            # Get updated profile
            updated_profile = db.execute("SELECT * FROM user_profile WHERE id = ?", (profile_id,)).fetchone()
            db.close()

            profile_dict = dict(updated_profile)
            # Calculate age
            from datetime import date, datetime

            birth_date = datetime.strptime(profile_dict["birth_date"], "%Y-%m-%d").date()
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            profile_dict["age"] = age

            return jsonify(
                json_response(
                    profile_dict,
                    "Profile updated successfully" if existing_profile else "Profile created successfully",
                    status=HTTP_CREATED if not existing_profile else HTTP_OK,
                )
            ), (HTTP_CREATED if not existing_profile else HTTP_OK)

    except Exception as e:
        app.logger.error(f"Profile API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@app.route("/api/profile/macros", methods=["GET"])
def profile_macros_api():
    """Calculate daily macros based on user profile"""
    try:
        db = get_db()

        # Get current profile
        profile = db.execute("SELECT * FROM user_profile ORDER BY updated_at DESC LIMIT 1").fetchone()
        db.close()

        if not profile:
            return (
                jsonify(json_response(None, "No profile found. Please create a profile first.", status=HTTP_NOT_FOUND)),
                HTTP_NOT_FOUND,
            )

        profile_dict = dict(profile)

        # Calculate age
        from datetime import date, datetime

        birth_date = datetime.strptime(profile_dict["birth_date"], "%Y-%m-%d").date()
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

        # Calculate BMR using advanced algorithm
        # Use Katch-McArdle if LBM is available (more accurate for high body fat)
        lbm = profile_dict.get("lean_body_mass_kg")
        if lbm is None and profile_dict.get("body_fat_percentage") is not None:
            lbm = calculate_lean_body_mass(profile_dict["weight_kg"], profile_dict["body_fat_percentage"])

        if lbm is not None:
            bmr = calculate_bmr_katch_mcardle(lbm)
        else:
            bmr = calculate_bmr_mifflin_st_jeor(
                profile_dict["weight_kg"], profile_dict["height_cm"], age, profile_dict["gender"]
            )

        # Calculate TDEE using advanced algorithm
        tdee = calculate_tdee(bmr, profile_dict["activity_level"])

        # Calculate target calories using advanced algorithm
        target_calories = calculate_target_calories(tdee, profile_dict["goal"])

        # Calculate keto macros using advanced algorithm
        # LBM already calculated above for BMR
        keto_type = profile_dict.get("keto_type", "standard")
        macros = calculate_keto_macros_advanced(
            target_calories, lbm, profile_dict["activity_level"], keto_type, profile_dict["goal"]
        )

        carbs_grams = macros["carbs"]
        protein_grams = macros["protein"]
        fats_grams = macros["fats"]
        carbs_calories = carbs_grams * 4
        protein_calories = protein_grams * 4
        fats_calories = fats_grams * 9

        macros = {
            "bmr": round(bmr, 0),
            "tdee": round(tdee, 0),
            "target_calories": round(target_calories, 0),
            "carbs": round(carbs_grams, 1),
            "protein": round(protein_grams, 1),
            "fats": round(fats_grams, 1),
            "carbs_percentage": round((carbs_calories / target_calories) * 100, 1),
            "protein_percentage": round((protein_calories / target_calories) * 100, 1),
            "fats_percentage": round((fats_calories / target_calories) * 100, 1),
        }

        return jsonify(json_response(macros, "Macros calculated successfully"))

    except Exception as e:
        app.logger.error(f"Profile macros API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@app.route("/api/system/status")
def system_status_api():
    """System status and statistics"""
    try:
        import psutil

        db_stats = get_database_stats()

        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        system_info = {
            "application": {
                "name": Config.APP_NAME,
                "version": Config.VERSION,
                "environment": Config.FLASK_ENV,
                "uptime": "N/A",  # Would need startup time tracking
            },
            "database": {
                "type": "SQLite",
                "size_mb": (
                    round(os.path.getsize(Config.DATABASE) / (1024 * 1024), 2) if os.path.exists(Config.DATABASE) else 0
                ),
                "products_count": db_stats.get("products", 0),
                "dishes_count": db_stats.get("dishes", 0),
                "log_entries_count": db_stats.get("log_entries", 0),
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": round(memory.used / (1024 * 1024), 2),
                "disk_percent": round((disk.used / disk.total) * 100, 2),
                "disk_free_gb": round(disk.free / (1024 * 1024 * 1024), 2),
            },
        }

        return jsonify(json_response(system_info))

    except Exception as e:
        app.logger.error(f"System status API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@app.route("/api/system/backup", methods=["POST"])
def system_backup_api():
    """Create a backup of the database"""
    try:
        import shutil
        from datetime import datetime

        # Create backups directory if it doesn't exist
        os.makedirs("backups", exist_ok=True)

        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"nutrition_backup_{timestamp}.db"
        backup_path = os.path.join("backups", backup_filename)

        # Copy database file
        shutil.copy2(Config.DATABASE, backup_path)

        # Get backup size
        backup_size_mb = round(os.path.getsize(backup_path) / (1024 * 1024), 2)

        return jsonify(
            json_response(
                {
                    "backup_id": backup_filename,
                    "backup_path": backup_path,
                    "backup_size_mb": backup_size_mb,
                    "created_at": datetime.now().isoformat(),
                    "download_url": f"/api/system/backup/{backup_filename}",
                },
                "Backup created successfully!",
            )
        )

    except Exception as e:
        app.logger.error(f"Backup API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@app.route("/api/system/restore", methods=["POST"])
def system_restore_api():
    """Restore database from backup"""
    try:
        if "backup_file" not in request.files:
            return (
                jsonify(
                    json_response(
                        None,
                        ERROR_MESSAGES["validation_error"],
                        status=HTTP_BAD_REQUEST,
                        errors=["No backup file provided"],
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        backup_file = request.files["backup_file"]
        if backup_file.filename == "":
            return (
                jsonify(
                    json_response(
                        None, ERROR_MESSAGES["validation_error"], status=HTTP_BAD_REQUEST, errors=["No file selected"]
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        if not backup_file.filename.endswith(".db"):
            return (
                jsonify(
                    json_response(
                        None,
                        ERROR_MESSAGES["validation_error"],
                        status=HTTP_BAD_REQUEST,
                        errors=["Invalid file type. Please upload a .db file"],
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        # Create backup of current database before restore
        import shutil
        from datetime import datetime

        os.makedirs("backups", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_backup = f"backups/pre_restore_backup_{timestamp}.db"
        shutil.copy2(Config.DATABASE, current_backup)

        # Save uploaded file
        backup_file.save(Config.DATABASE)

        return jsonify(
            json_response(
                {
                    "restored_file": backup_file.filename,
                    "current_backup": current_backup,
                    "restored_at": datetime.now().isoformat(),
                },
                "Database restored successfully! Current database backed up as safety measure.",
            )
        )

    except Exception as e:
        app.logger.error(f"Restore API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@app.route("/api/maintenance/vacuum", methods=["POST"])
def maintenance_vacuum_api():
    """Optimize database by running VACUUM and ANALYZE"""
    try:
        db = get_db()

        # Get database size before optimization
        size_before = os.path.getsize(Config.DATABASE) if os.path.exists(Config.DATABASE) else 0

        # Run ANALYZE first to update statistics
        db.execute("ANALYZE")
        db.commit()

        # Run VACUUM to optimize database
        db.execute("VACUUM")
        db.commit()

        # Get database size after optimization
        size_after = os.path.getsize(Config.DATABASE)

        # Calculate space saved
        space_saved = size_before - size_after
        space_saved_mb = round(space_saved / (1024 * 1024), 2)

        # Get database statistics
        stats = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_count = len(stats)

        db.close()

        message = f"Database optimized! Size: {round(size_after / (1024 * 1024), 2)} MB"
        if space_saved_mb > 0:
            message += f" (saved {space_saved_mb} MB)"
        else:
            message += " (no fragmentation found)"

        return jsonify(
            json_response(
                {
                    "space_saved_mb": space_saved_mb,
                    "size_before_mb": round(size_before / (1024 * 1024), 2),
                    "size_after_mb": round(size_after / (1024 * 1024), 2),
                    "table_count": table_count,
                    "optimization_type": "VACUUM + ANALYZE",
                },
                message,
            )
        )

    except Exception as e:
        app.logger.error(f"Vacuum API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@app.route("/api/maintenance/cleanup", methods=["POST"])
def maintenance_cleanup_api():
    """Clean up temporary files, logs, and cache"""
    try:
        import glob

        files_cleaned = 0
        space_freed = 0
        cleanup_details = []

        # Clean up log files older than 7 days
        log_patterns = ["logs/*.log", "logs/*.txt", "*.log"]
        for pattern in log_patterns:
            for file_path in glob.glob(pattern):
                try:
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        # Check if file is older than 7 days
                        file_age = time.time() - os.path.getmtime(file_path)
                        if file_age > (7 * 24 * 60 * 60):  # 7 days in seconds
                            os.remove(file_path)
                            files_cleaned += 1
                            space_freed += file_size
                            cleanup_details.append(f"Removed old log: {os.path.basename(file_path)}")
                except Exception:
                    continue

        # Clean up Python cache files (but not in venv)
        cache_patterns = ["**/__pycache__", "**/*.pyc", "**/*.pyo"]
        for pattern in cache_patterns:
            for file_path in glob.glob(pattern, recursive=True):
                try:
                    # Skip virtual environment directories
                    if "venv" in file_path or ".venv" in file_path:
                        continue

                    if os.path.exists(file_path):
                        if os.path.isfile(file_path):
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            files_cleaned += 1
                            space_freed += file_size
                        elif os.path.isdir(file_path):
                            # Count files in directory before removal
                            dir_files = sum(len(files) for _, _, files in os.walk(file_path))
                            shutil.rmtree(file_path)
                            files_cleaned += dir_files
                            cleanup_details.append(f"Removed cache directory: {os.path.basename(file_path)}")
                except Exception:
                    continue

        # Clean up temporary files
        temp_patterns = ["*.tmp", "*.temp", "*.swp", "*.swo"]
        for pattern in temp_patterns:
            for file_path in glob.glob(pattern):
                try:
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        files_cleaned += 1
                        space_freed += file_size
                        cleanup_details.append(f"Removed temp file: {os.path.basename(file_path)}")
                except Exception:
                    continue

        space_freed_mb = round(space_freed / (1024 * 1024), 2)

        message = f"Cleanup completed! Removed {files_cleaned} files"
        if space_freed_mb > 0:
            message += f" (freed {space_freed_mb} MB)"
        else:
            message += " (no files to clean)"

        return jsonify(
            json_response(
                {
                    "files_cleaned": files_cleaned,
                    "space_freed_mb": space_freed_mb,
                    "cleanup_time": datetime.now().isoformat(),
                    "cleanup_details": cleanup_details[:10],  # Limit to first 10 items
                },
                message,
            )
        )

    except Exception as e:
        app.logger.error(f"Cleanup API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@app.route("/api/maintenance/cleanup-test-data", methods=["POST"])
def maintenance_cleanup_test_data_api():
    """Clean up test data (items with TEST prefix)"""
    try:
        db = get_db()

        # Count test data before deletion
        test_products = db.execute("SELECT COUNT(*) FROM products WHERE name LIKE 'TEST%'").fetchone()[0]
        test_dishes = db.execute("SELECT COUNT(*) FROM dishes WHERE name LIKE 'TEST%'").fetchone()[0]
        test_logs = db.execute(
            """
            SELECT COUNT(*) FROM log_entries le 
            LEFT JOIN products p ON le.item_type = 'product' AND le.item_id = p.id
            LEFT JOIN dishes d ON le.item_type = 'dish' AND le.item_id = d.id
            WHERE p.name LIKE 'TEST%' OR d.name LIKE 'TEST%'
        """
        ).fetchone()[0]

        # Delete test log entries first (foreign key constraints)
        deleted_logs = db.execute(
            """
            DELETE FROM log_entries WHERE id IN (
                SELECT le.id FROM log_entries le 
                LEFT JOIN products p ON le.item_type = 'product' AND le.item_id = p.id
                LEFT JOIN dishes d ON le.item_type = 'dish' AND le.item_id = d.id
                WHERE p.name LIKE 'TEST%' OR d.name LIKE 'TEST%'
            )
        """
        ).rowcount

        # Delete test dishes (and their ingredients)
        deleted_dishes = db.execute("DELETE FROM dishes WHERE name LIKE 'TEST%'").rowcount

        # Delete test products
        deleted_products = db.execute("DELETE FROM products WHERE name LIKE 'TEST%'").rowcount

        db.commit()
        db.close()

        total_deleted = deleted_products + deleted_dishes + deleted_logs

        message = f"Test data cleanup completed! Removed {total_deleted} items"
        if total_deleted == 0:
            message += " (no test data found)"

        return jsonify(
            json_response(
                {
                    "deleted_products": deleted_products,
                    "deleted_dishes": deleted_dishes,
                    "deleted_logs": deleted_logs,
                    "total_deleted": total_deleted,
                    "cleanup_time": datetime.now().isoformat(),
                },
                message,
            )
        )

    except Exception as e:
        app.logger.error(f"Test data cleanup API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@app.route("/api/maintenance/wipe-database", methods=["POST"])
def maintenance_wipe_database_api():
    """Wipe entire database and reset to initial state"""
    try:
        db = get_db()

        # Get counts before deletion
        products_count = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        dishes_count = db.execute("SELECT COUNT(*) FROM dishes").fetchone()[0]
        logs_count = db.execute("SELECT COUNT(*) FROM log_entries").fetchone()[0]

        # Delete all data (respecting foreign key constraints)
        db.execute("DELETE FROM log_entries")
        db.execute("DELETE FROM dish_ingredients")
        db.execute("DELETE FROM dishes")
        db.execute("DELETE FROM products")

        # Reset auto-increment counters
        db.execute("DELETE FROM sqlite_sequence")

        db.commit()
        db.close()

        total_deleted = products_count + dishes_count + logs_count

        message = f"Database wiped! Removed {total_deleted} items"
        if total_deleted == 0:
            message += " (database was already empty)"

        return jsonify(
            json_response(
                {
                    "deleted_products": products_count,
                    "deleted_dishes": dishes_count,
                    "deleted_logs": logs_count,
                    "total_deleted": total_deleted,
                    "wipe_time": datetime.now().isoformat(),
                },
                message,
            )
        )

    except Exception as e:
        app.logger.error(f"Database wipe API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@app.route("/api/export/all")
def export_all_api():
    """Export all data from the application"""
    try:
        db = get_db()

        # Get all data
        products = db.execute("SELECT * FROM products ORDER BY name").fetchall()
        dishes = db.execute("SELECT * FROM dishes ORDER BY name").fetchall()
        log_entries = db.execute(
            "SELECT * FROM log_entries_with_details ORDER BY date DESC, created_at DESC"
        ).fetchall()

        # Get dish ingredients
        dish_ingredients = {}
        for dish in dishes:
            ingredients = db.execute(
                """
                SELECT di.*, p.name as product_name 
                FROM dish_ingredients di
                JOIN products p ON di.product_id = p.id
                WHERE di.dish_id = ?
                ORDER BY di.id
            """,
                (dish["id"],),
            ).fetchall()
            dish_ingredients[dish["id"]] = [dict(ingredient) for ingredient in ingredients]

        # Prepare export data
        export_data = {
            "export_info": {
                "exported_at": datetime.now().isoformat(),
                "app_version": Config.VERSION,
                "total_products": len(products),
                "total_dishes": len(dishes),
                "total_log_entries": len(log_entries),
            },
            "products": [dict(product) for product in products],
            "dishes": [dict(dish) for dish in dishes],
            "dish_ingredients": dish_ingredients,
            "log_entries": [dict(entry) for entry in log_entries],
        }

        db.close()

        return jsonify(export_data)

    except Exception as e:
        app.logger.error(f"Export API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


# ============================================
# Telegram Web App Integration
# ============================================


def verify_telegram_webapp_data(init_data: str, bot_token: str) -> bool:
    """Verify Telegram Web App initialization data"""
    try:
        # Parse the data
        parsed_data = {}
        for item in init_data.split("&"):
            key, value = item.split("=", 1)
            parsed_data[key] = value

        # Extract hash
        received_hash = parsed_data.pop("hash", "")

        # Create data string for verification
        data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(parsed_data.items())])

        # Create secret key
        secret_key = hmac.new(key="WebAppData".encode(), msg=bot_token.encode(), digestmod=hashlib.sha256).digest()

        # Calculate hash
        calculated_hash = hmac.new(key=secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256).hexdigest()

        return calculated_hash == received_hash

    except Exception:
        return False




# ============================================
# Error Handlers
# ============================================


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.path.startswith("/api/"):
        return jsonify(json_response(None, "Endpoint not found", 404)), 404
    return render_template("index.html")  # SPA fallback


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    app.logger.error(f"Internal error: {error}")
    if request.path.startswith("/api/"):
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    return render_template("index.html")


# ============================================
# Application Initialization
# ============================================


def initialize_app():
    """Initialize application on first request"""
    try:
        # Create directories
        os.makedirs("data", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        os.makedirs("backups", exist_ok=True)

        # Initialize database if it doesn't exist
        if not os.path.exists(Config.DATABASE):
            init_db()
            app.logger.info("Database initialized")

        app.logger.info(f"🥗 Nutrition Tracker v{Config.VERSION} started")

    except Exception as e:
        app.logger.error(f"Failed to initialize app: {e}")
        raise


# Initialize app when Flask starts
with app.app_context():
    initialize_app()

# ============================================
# Main Entry Point
# ============================================

if __name__ == "__main__":
    # Initialize database if running directly
    if not os.path.exists(Config.DATABASE):
        init_db()

    # Run development server
    port = int(os.environ.get("FLASK_RUN_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=Config.is_development())
