#!/usr/bin/env python3
"""
Nutrition Tracker v2.0 - WCAG 2.2 Compliant Web Application
Local nutrition tracking application optimized for Raspberry Pi Zero 2W
"""

import hashlib
import hmac
import os
import sqlite3
import time
from datetime import date, datetime, timedelta, timezone
from functools import wraps

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import BadRequest

# Import our modular components
from src.advanced_logging import structured_logger
from src.config import Config
from src.constants import (
    ERROR_MESSAGES,
    HTTP_BAD_REQUEST,
    HTTP_CREATED,
    HTTP_NOT_FOUND,
    HTTP_OK,
    MEAL_TYPES,
)
from src.monitoring import monitor_http_request
from src.nutrition_calculator import (
    calculate_bmr_katch_mcardle,
    calculate_bmr_mifflin_st_jeor,
    calculate_gki,
    calculate_keto_index_advanced,
    calculate_keto_macros_advanced,
    calculate_lean_body_mass,
    calculate_target_calories,
    calculate_tdee,
)
from src.security import SecurityHeaders, rate_limit
from src.ssl_config import setup_security_middleware
from src.utils import (
    json_response,
    safe_float,
    safe_int,
)

# Import route blueprints
from routes.auth import auth_bp
from routes.dishes import dishes_bp
from routes.fasting import fasting_bp
from routes.log import log_bp
from routes.metrics import metrics_bp
from routes.products import products_bp
from routes.system import system_bp


def safe_get_json():
    """Safely get JSON data from request, handling invalid JSON gracefully"""
    try:
        return request.get_json() or {}
    except BadRequest:
        return None


# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")
app.config.from_object(Config)

# Enable CORS for API endpoints
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Setup security middleware
setup_security_middleware(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dishes_bp)
app.register_blueprint(fasting_bp)
app.register_blueprint(log_bp)
app.register_blueprint(metrics_bp)
app.register_blueprint(products_bp)
app.register_blueprint(system_bp)


# Add security headers to all responses
@app.after_request
def add_security_headers(response):
    return SecurityHeaders.add_security_headers(response)


# Add request logging
@app.before_request
def log_request_start():
    request.start_time = time.time()


@app.after_request
def log_request_end(response):
    duration = time.time() - getattr(request, "start_time", time.time())

    # Log access event
    structured_logger.log_access_event(
        method=request.method,
        path=request.path,
        status_code=response.status_code,
        duration=duration,
        ip=request.remote_addr,
    )

    return response


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
    db = sqlite3.connect(app.config["DATABASE"])
    db.row_factory = sqlite3.Row

    # Enable WAL mode for better concurrency (only for file databases)
    if app.config["DATABASE"] != ":memory:":
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
        if not app.config.get("TESTING", False) and app.config["DATABASE"] != ":memory:":
            db = get_db()
            sample_products = [
                ("Chicken Breast", 165, 31.0, 3.6, 0.0, 0.0, "meat", 0, "raw"),
                ("Salmon", 208, 25.4, 12.4, 0.0, 0.0, "fish", 0, "raw"),
                ("Eggs", 155, 13.0, 11.0, 1.1, 0.0, "dairy", 0, "raw"),
                ("Avocado", 160, 2.0, 14.7, 8.5, 6.7, "fruits", 15, "raw"),
                ("Broccoli", 34, 2.8, 0.4, 6.6, 2.6, "vegetables", 15, "raw"),
                ("Almonds", 579, 21.2, 49.9, 21.6, 12.5, "nuts_seeds", 15, "minimal"),
                ("Spinach", 23, 2.9, 0.4, 3.6, 2.2, "leafy_vegetables", 15, "raw"),
                ("Blueberries", 57, 0.7, 0.3, 14.5, 2.4, "berries", 25, "raw"),
                ("Sweet Potato", 86, 1.6, 0.1, 20.1, 3.0, "root_vegetables", 70, "minimal"),
            ]

            for product in sample_products:
                db.execute(
                    "INSERT OR IGNORE INTO products (name, calories_per_100g, protein_per_100g, fat_per_100g, carbs_per_100g, fiber_per_100g, category, glycemic_index, processing_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    product,
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
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "database": "ok",
            }
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "version": Config.VERSION,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
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


# Products API routes moved to routes/products.py blueprint


# ============================================
# Statistics API
# ============================================


@app.route("/api/stats/<date_str>")
@monitor_http_request
@rate_limit("api")
@cached_response(timeout=300)  # Cache stats for 5 minutes
def daily_stats_api(date_str):
    """Get daily nutrition statistics"""
    db = get_db()

    try:
        # Validate date format
        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            today = datetime.now().date()
            if parsed_date > today:
                return (
                    jsonify(
                        json_response(None, "Future date not allowed", status=HTTP_BAD_REQUEST)
                    ),
                    HTTP_BAD_REQUEST,
                )
        except ValueError:
            return (
                jsonify(
                    json_response(
                        None, "Invalid date format. Use YYYY-MM-DD", status=HTTP_BAD_REQUEST
                    )
                ),
                HTTP_BAD_REQUEST,
            )
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
            profile = db.execute(
                "SELECT * FROM user_profile ORDER BY updated_at DESC LIMIT 1"
            ).fetchone()

            if profile:
                profile_dict = dict(profile)

                # Calculate age

                birth_date = datetime.strptime(profile_dict["birth_date"], "%Y-%m-%d").date()
                today = date.today()
                age = (
                    today.year
                    - birth_date.year
                    - ((today.month, today.day) < (birth_date.month, birth_date.day))
                )

                # Calculate BMR using advanced algorithm
                # Use Katch-McArdle if LBM is available (more accurate for high body fat)
                lbm = profile_dict.get("lean_body_mass_kg")
                if lbm is None and profile_dict.get("body_fat_percentage") is not None:
                    lbm = calculate_lean_body_mass(
                        profile_dict["weight_kg"], profile_dict["body_fat_percentage"]
                    )

                if lbm is not None:
                    bmr = calculate_bmr_katch_mcardle(lbm)
                else:
                    bmr = calculate_bmr_mifflin_st_jeor(
                        profile_dict["weight_kg"],
                        profile_dict["height_cm"],
                        age,
                        profile_dict["gender"],
                    )

                # Calculate TDEE using advanced algorithm
                tdee = calculate_tdee(bmr, profile_dict["activity_level"])

                # Calculate target calories using advanced algorithm
                target_calories = calculate_target_calories(tdee, profile_dict["goal"])

                # Calculate keto macros using advanced algorithm
                # LBM already calculated above for BMR
                keto_type = profile_dict.get("keto_type", "standard")
                macros = calculate_keto_macros_advanced(
                    target_calories,
                    lbm,
                    profile_dict["activity_level"],
                    keto_type,
                    profile_dict["goal"],
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
                        "percentage": (
                            round((calories / target_calories) * 100, 1)
                            if target_calories > 0
                            else 0
                        ),
                        "status": (
                            "good"
                            if 90 <= (calories / target_calories) * 100 <= 110
                            else ("low" if calories < target_calories * 0.9 else "high")
                        ),
                    },
                    "protein": {
                        "actual": round(protein, 1),
                        "target": round(protein_grams, 1),
                        "percentage": (
                            round((protein / protein_grams) * 100, 1) if protein_grams > 0 else 0
                        ),
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
                        "percentage": (
                            round((carbs / carbs_grams) * 100, 1) if carbs_grams > 0 else 0
                        ),
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
@monitor_http_request
@rate_limit("api")
def weekly_stats_api(date_str):
    """Get weekly nutrition statistics"""
    db = get_db()

    try:

        # Validate date format
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            today = datetime.now().date()
            if target_date > today:
                return (
                    jsonify(
                        json_response(None, "Future date not allowed", status=HTTP_BAD_REQUEST)
                    ),
                    HTTP_BAD_REQUEST,
                )
        except ValueError:
            return (
                jsonify(
                    json_response(
                        None, "Invalid date format. Use YYYY-MM-DD", status=HTTP_BAD_REQUEST
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        # Parse the date and calculate week start (Monday)
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

        stats = db.execute(
            stats_query, (week_start.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d"))
        ).fetchone()

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
            profile = db.execute(
                "SELECT * FROM user_profile ORDER BY updated_at DESC LIMIT 1"
            ).fetchone()

            if profile:
                profile_dict = dict(profile)

                # Calculate age

                birth_date = datetime.strptime(profile_dict["birth_date"], "%Y-%m-%d").date()
                today = date.today()
                age = (
                    today.year
                    - birth_date.year
                    - ((today.month, today.day) < (birth_date.month, birth_date.day))
                )

                # Calculate BMR using advanced algorithm
                # Use Katch-McArdle if LBM is available (more accurate for high body fat)
                lbm = profile_dict.get("lean_body_mass_kg")
                if lbm is None and profile_dict.get("body_fat_percentage") is not None:
                    lbm = calculate_lean_body_mass(
                        profile_dict["weight_kg"], profile_dict["body_fat_percentage"]
                    )

                if lbm is not None:
                    bmr = calculate_bmr_katch_mcardle(lbm)
                else:
                    bmr = calculate_bmr_mifflin_st_jeor(
                        profile_dict["weight_kg"],
                        profile_dict["height_cm"],
                        age,
                        profile_dict["gender"],
                    )

                # Calculate TDEE using advanced algorithm
                tdee = calculate_tdee(bmr, profile_dict["activity_level"])

                # Calculate target calories using advanced algorithm
                target_calories = calculate_target_calories(tdee, profile_dict["goal"])

                # Calculate keto macros using advanced algorithm
                # LBM already calculated above for BMR
                keto_type = profile_dict.get("keto_type", "standard")
                macros = calculate_keto_macros_advanced(
                    target_calories,
                    lbm,
                    profile_dict["activity_level"],
                    keto_type,
                    profile_dict["goal"],
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
                            round((calories / weekly_target_calories) * 100, 1)
                            if weekly_target_calories > 0
                            else 0
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
                            round((protein / weekly_protein_grams) * 100, 1)
                            if weekly_protein_grams > 0
                            else 0
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
                        "percentage": (
                            round((fat / weekly_fats_grams) * 100, 1)
                            if weekly_fats_grams > 0
                            else 0
                        ),
                        "status": (
                            "good"
                            if 90 <= (fat / weekly_fats_grams) * 100 <= 110
                            else ("low" if fat < weekly_fats_grams * 0.9 else "high")
                        ),
                    },
                    "carbs": {
                        "actual": round(carbs, 1),
                        "target": round(weekly_carbs_grams, 1),
                        "percentage": (
                            round((carbs / weekly_carbs_grams) * 100, 1)
                            if weekly_carbs_grams > 0
                            else 0
                        ),
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
        data = safe_get_json()
        if data is None:
            return (
                jsonify(json_response(None, "Invalid JSON", status=HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )

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
            profile = db.execute(
                "SELECT * FROM user_profile ORDER BY updated_at DESC LIMIT 1"
            ).fetchone()
            db.close()

            if profile:
                profile_dict = dict(profile)
                # Calculate age from birth_date

                birth_date = datetime.strptime(profile_dict["birth_date"], "%Y-%m-%d").date()
                today = date.today()
                age = (
                    today.year
                    - birth_date.year
                    - ((today.month, today.day) < (birth_date.month, birth_date.day))
                )
                profile_dict["age"] = age

                return jsonify(json_response(profile_dict, "Profile retrieved successfully"))
            else:
                return (
                    jsonify(json_response(None, "No profile found", status=HTTP_NOT_FOUND)),
                    HTTP_NOT_FOUND,
                )

        else:  # POST or PUT
            data = safe_get_json()
            if data is None:
                return (
                    jsonify(json_response(None, "Invalid JSON", status=HTTP_BAD_REQUEST)),
                    HTTP_BAD_REQUEST,
                )

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

                    datetime.strptime(birth_date, "%Y-%m-%d")
                except ValueError:
                    errors.append("Birth date must be in YYYY-MM-DD format")

            height_cm = data.get("height_cm")
            if (
                not height_cm
                or not isinstance(height_cm, (int, float))
                or height_cm < 100
                or height_cm > 250
            ):
                errors.append("Height must be between 100 and 250 cm")

            weight_kg = data.get("weight_kg")
            if (
                not weight_kg
                or not isinstance(weight_kg, (int, float))
                or weight_kg < 30
                or weight_kg > 500
            ):
                errors.append("Weight must be between 30 and 500 kg")

            activity_level = data.get("activity_level")
            if not activity_level or activity_level not in [
                "sedentary",
                "light",
                "moderate",
                "active",
                "very_active",
            ]:
                errors.append(
                    "Activity level must be one of: sedentary, light, moderate, active, very_active"
                )

            goal = data.get("goal")
            if not goal or goal not in ["weight_loss", "maintenance", "muscle_gain"]:
                errors.append("Goal must be one of: weight_loss, maintenance, muscle_gain")

            if errors:
                return (
                    jsonify(
                        json_response(
                            None, "Validation failed", status=HTTP_BAD_REQUEST, errors=errors
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Check if profile exists
            existing_profile = db.execute(
                "SELECT id FROM user_profile ORDER BY updated_at DESC LIMIT 1"
            ).fetchone()

            if existing_profile and request.method == "PUT":
                # Update existing profile
                db.execute(
                    """
                    UPDATE user_profile
                    SET gender = ?, birth_date = ?, height_cm = ?, weight_kg = ?,
                        activity_level = ?, goal = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """,
                    (
                        gender,
                        birth_date,
                        int(height_cm),
                        float(weight_kg),
                        activity_level,
                        goal,
                        existing_profile[0],
                    ),
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
            updated_profile = db.execute(
                "SELECT * FROM user_profile WHERE id = ?", (profile_id,)
            ).fetchone()
            db.close()

            profile_dict = dict(updated_profile)
            # Calculate age

            birth_date = datetime.strptime(profile_dict["birth_date"], "%Y-%m-%d").date()
            today = date.today()
            age = (
                today.year
                - birth_date.year
                - ((today.month, today.day) < (birth_date.month, birth_date.day))
            )
            profile_dict["age"] = age

            return jsonify(
                json_response(
                    profile_dict,
                    (
                        "Profile updated successfully"
                        if existing_profile
                        else "Profile created successfully"
                    ),
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
        profile = db.execute(
            "SELECT * FROM user_profile ORDER BY updated_at DESC LIMIT 1"
        ).fetchone()
        db.close()

        if not profile:
            return (
                jsonify(
                    json_response(
                        None,
                        "No profile found. Please create a profile first.",
                        status=HTTP_NOT_FOUND,
                    )
                ),
                HTTP_NOT_FOUND,
            )

        profile_dict = dict(profile)

        # Calculate age

        birth_date = datetime.strptime(profile_dict["birth_date"], "%Y-%m-%d").date()
        today = date.today()
        age = (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )

        # Calculate BMR using advanced algorithm
        # Use Katch-McArdle if LBM is available (more accurate for high body fat)
        lbm = profile_dict.get("lean_body_mass_kg")
        if lbm is None and profile_dict.get("body_fat_percentage") is not None:
            lbm = calculate_lean_body_mass(
                profile_dict["weight_kg"], profile_dict["body_fat_percentage"]
            )

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
        secret_key = hmac.new(
            key="WebAppData".encode(), msg=bot_token.encode(), digestmod=hashlib.sha256
        ).digest()

        # Calculate hash
        calculated_hash = hmac.new(
            key=secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256
        ).hexdigest()

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
