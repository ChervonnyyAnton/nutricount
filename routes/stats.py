"""
Stats routes for Nutricount application.
Handles daily and weekly nutrition statistics.
"""

import sqlite3
import time
from datetime import date, datetime, timedelta
from functools import wraps

from flask import Blueprint, current_app, jsonify, request
from werkzeug.exceptions import BadRequest

from src.constants import (
    ERROR_MESSAGES,
    HTTP_BAD_REQUEST,
    MEAL_TYPES,
)
from src.monitoring import monitor_http_request
from src.nutrition_calculator import (
    calculate_bmr_katch_mcardle,
    calculate_bmr_mifflin_st_jeor,
    calculate_keto_index_advanced,
    calculate_keto_macros_advanced,
    calculate_lean_body_mass,
    calculate_target_calories,
    calculate_tdee,
)
from src.security import rate_limit
from src.utils import json_response, safe_float, safe_int


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


# Simple in-memory cache for stats responses
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


# Create blueprint
stats_bp = Blueprint("stats", __name__, url_prefix="/api/stats")


@stats_bp.route("/<date_str>")
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
            current_app.logger.warning(f"Could not calculate personal macros: {e}")

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
        current_app.logger.error(f"Stats API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


@stats_bp.route("/weekly/<date_str>")
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
            current_app.logger.warning(f"Could not calculate personal macros: {e}")

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
        current_app.logger.error(f"Weekly stats API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()
