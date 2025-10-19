# Utility functions - keep them simple and focused

import re
import sqlite3
from datetime import date, datetime, timezone
from typing import Any, Dict, Optional

from .nutrition_calculator import calculate_calories_from_macros


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float"""
    try:
        if value is None:
            return default
        result = float(value)
        # Check for NaN and infinity
        if result != result or result == float("inf") or result == float("-inf"):
            return default
        return result
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int"""
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def clean_string(text: str, max_length: int = 100) -> str:
    """Clean and truncate string"""
    if not text:
        return ""

    # Remove extra whitespace and truncate
    cleaned = re.sub(r"\s+", " ", str(text).strip())
    return cleaned[:max_length]


# Removed deprecated calculate_keto_index function -
# use nutrition_calculator.calculate_keto_index_advanced instead


def get_keto_rating(keto_index: float) -> str:
    """Get keto rating based on index"""
    if keto_index >= 2.0:
        return "excellent"
    elif keto_index >= 1.0:
        return "moderate"
    else:
        return "poor"


def format_date(date_obj) -> str:
    """Format date for display"""
    if isinstance(date_obj, str):
        return date_obj
    elif isinstance(date_obj, (date, datetime)):
        return date_obj.strftime("%Y-%m-%d")
    else:
        return str(date.today())


def parse_date(date_str: str) -> Optional[date]:
    """Parse date string"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def json_response(data: Any = None, message: str = "", status: int = 200, **kwargs) -> Dict:
    """Create consistent JSON response"""
    response = {
        "status": "success" if status < 400 else "error",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if data is not None:
        response["data"] = data
    if message:
        response["message"] = message

    response.update(kwargs)
    return response


def validate_nutrition_values(
    calories: float,
    protein: float,
    fat: float,
    carbs: float,
    calories_optional: bool = False,
    check_total_macros: bool = True,
) -> list:
    """Validate nutrition values and return detailed errors"""
    errors = []

    # Check for negative values
    if not calories_optional and calories < 0:
        errors.append("Calories cannot be negative")
    elif calories > 9999:
        errors.append("Calories cannot exceed 9999 per 100g")

    if protein < 0:
        errors.append("Protein cannot be negative")
    elif protein > 100:
        errors.append("Protein cannot exceed 100g per 100g")

    if fat < 0:
        errors.append("Fat cannot be negative")
    elif fat > 100:
        errors.append("Fat cannot exceed 100g per 100g")

    if carbs < 0:
        errors.append("Carbs cannot be negative")
    elif carbs > 100:
        errors.append("Carbs cannot exceed 100g per 100g")

    # Check for reasonable total (only for individual products, not aggregated stats)
    if check_total_macros:
        total_macros = protein + fat + carbs
        if total_macros > 100:
            errors.append(f"Total macros ({total_macros:.1f}g) cannot exceed 100g per 100g")

    # If calories are provided manually, check if they match calculated calories
    if not calories_optional and calories > 0:
        calculated_calories = calculate_calories_from_macros(protein, fat, carbs)
        if abs(calories - calculated_calories) > 0.1:
            errors.append(
                f"Provided calories ({calories}) don't match "
                f"calculated calories ({calculated_calories:.1f})"
            )

    return errors


def validate_product_data(data: dict) -> tuple[bool, list, dict]:
    """Validate product data and return (is_valid, errors, cleaned_data)"""
    errors = []
    cleaned_data = {}

    # Validate name
    name = clean_string(data.get("name", ""))
    if not name:
        errors.append("Product name is required")
    elif len(name) < 2:
        errors.append("Product name must be at least 2 characters long")
    elif len(name) > 100:
        errors.append("Product name cannot exceed 100 characters")
    else:
        cleaned_data["name"] = name

    # Validate nutrition values
    calories = safe_float(data.get("calories_per_100g"))
    protein = safe_float(data.get("protein_per_100g"))
    fat = safe_float(data.get("fat_per_100g"))
    carbs = safe_float(data.get("carbs_per_100g"))

    # Calories are now optional - will be calculated from macros if not provided
    nutrition_errors = validate_nutrition_values(
        calories, protein, fat, carbs, calories_optional=True
    )
    errors.extend(nutrition_errors)

    if not errors:
        cleaned_data.update(
            {
                "calories_per_100g": calories,
                "protein_per_100g": protein,
                "fat_per_100g": fat,
                "carbs_per_100g": carbs,
            }
        )

    return len(errors) == 0, errors, cleaned_data


def validate_dish_data(data: dict) -> tuple[bool, list, dict]:
    """Validate dish data and return (is_valid, errors, cleaned_data)"""
    errors = []
    cleaned_data = {}

    # Validate name
    name = clean_string(data.get("name", ""))
    if not name:
        errors.append("Dish name is required")
    elif len(name) < 2:
        errors.append("Dish name must be at least 2 characters long")
    elif len(name) > 100:
        errors.append("Dish name cannot exceed 100 characters")
    else:
        cleaned_data["name"] = name

    # Validate ingredients
    ingredients = data.get("ingredients", [])
    if not ingredients:
        errors.append("At least one ingredient is required")
    elif not isinstance(ingredients, list):
        errors.append("Ingredients must be a list")
    else:
        valid_ingredients = []
        for i, ingredient in enumerate(ingredients):
            if not isinstance(ingredient, dict):
                errors.append(f"Ingredient {i+1}: Must be an object")
                continue

            product_id = safe_int(ingredient.get("product_id"))
            quantity = safe_float(ingredient.get("quantity_grams"))

            if not product_id or product_id <= 0:
                errors.append(f"Ingredient {i+1}: Valid product ID is required")
            elif quantity <= 0:
                errors.append(f"Ingredient {i+1}: Quantity must be greater than 0")
            elif quantity > 10000:
                errors.append(f"Ingredient {i+1}: Quantity cannot exceed 10000g")
            else:
                # Validate optional preparation method
                preparation_method = ingredient.get("preparation_method", "raw")
                if preparation_method not in [
                    "raw",
                    "boiled",
                    "steamed",
                    "grilled",
                    "fried",
                    "baked",
                ]:
                    errors.append(
                        f"Ingredient {i+1}: Invalid preparation method '{preparation_method}'"
                    )
                    continue

                # Validate optional edible portion
                edible_portion = safe_float(ingredient.get("edible_portion", 1.0))
                if edible_portion <= 0 or edible_portion > 1.0:
                    errors.append(f"Ingredient {i+1}: Edible portion must be between 0 and 1.0")
                    continue

                valid_ingredients.append(
                    {
                        "product_id": product_id,
                        "quantity_grams": quantity,
                        "preparation_method": preparation_method,
                        "edible_portion": edible_portion,
                    }
                )

        if valid_ingredients:
            cleaned_data["ingredients"] = valid_ingredients
        elif not errors:  # Only add this error if no other ingredient errors
            errors.append("No valid ingredients provided")

    return len(errors) == 0, errors, cleaned_data


def validate_log_data(data: dict) -> tuple[bool, list, dict]:
    """Validate log entry data and return (is_valid, errors, cleaned_data)"""
    errors = []
    cleaned_data = {}

    # Validate date
    date_str = data.get("date", "").strip()
    if not date_str:
        errors.append("Date is required")
    else:
        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if parsed_date > date.today():
                errors.append("Date cannot be in the future")
            elif parsed_date < date(2020, 1, 1):
                errors.append("Date cannot be before 2020")
            else:
                cleaned_data["date"] = date_str
        except ValueError:
            errors.append("Date must be in YYYY-MM-DD format")

    # Validate item type
    item_type = data.get("item_type", "").strip().lower()
    if item_type not in ["product", "dish"]:
        errors.append("Item type must be 'product' or 'dish'")
    else:
        cleaned_data["item_type"] = item_type

    # Validate item ID
    item_id = safe_int(data.get("item_id"))
    if not item_id or item_id <= 0:
        errors.append("Valid item ID is required")
    else:
        cleaned_data["item_id"] = item_id

    # Validate quantity
    quantity = safe_float(data.get("quantity_grams"))
    if quantity <= 0:
        errors.append("Quantity must be greater than 0")
    elif quantity > 10000:
        errors.append("Quantity cannot exceed 10000g")
    else:
        cleaned_data["quantity_grams"] = quantity

    # Validate meal time
    meal_time = data.get("meal_time", "").strip().lower()
    valid_meal_times = ["breakfast", "lunch", "dinner", "snack"]
    if meal_time and meal_time not in valid_meal_times:
        errors.append(f"Meal time must be one of: {', '.join(valid_meal_times)}")
    else:
        cleaned_data["meal_time"] = meal_time or "snack"

    # Validate notes (optional)
    notes = clean_string(data.get("notes", ""), max_length=500)
    if notes:
        cleaned_data["notes"] = notes

    return len(errors) == 0, errors, cleaned_data


def get_database_stats() -> Dict:
    """Get basic database statistics"""
    try:
        from .config import Config

        conn = sqlite3.connect(Config.DATABASE)
        conn.row_factory = sqlite3.Row

        # Get counts
        products_count = conn.execute("SELECT COUNT(*) as count FROM products").fetchone()["count"]
        dishes_count = conn.execute("SELECT COUNT(*) as count FROM dishes").fetchone()["count"]
        log_count = conn.execute("SELECT COUNT(*) as count FROM log_entries").fetchone()["count"]

        # Get date range
        date_range = conn.execute(
            """
            SELECT MIN(date) as first_date, MAX(date) as last_date
            FROM log_entries
        """
        ).fetchone()

        conn.close()

        return {
            "products": products_count,
            "dishes": dishes_count,
            "log_entries": log_count,
            "first_entry": date_range["first_date"],
            "last_entry": date_range["last_date"],
        }

    except Exception as e:
        return {"error": str(e)}
