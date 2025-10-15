# Constants for Nutrition Tracker
# All the magic numbers in one place

# HTTP Status Codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_ERROR = 500

# Keto Index Thresholds
KETO_EXCELLENT = 2.0
KETO_MODERATE = 1.0

# Nutrition Limits (per 100g)
MIN_CALORIES = 0
MAX_CALORIES = 9999
MIN_MACRO = 0
MAX_MACRO = 100

# Meal Types
MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack"]

# Item Types
ITEM_TYPES = ["product", "dish"]

# Default Values
DEFAULT_QUANTITY = 100.0
DEFAULT_CALORIES = 0.0
DEFAULT_MACRO = 0.0

# UI Messages
SUCCESS_MESSAGES = {
    "product_created": "✅ Product created successfully!",
    "product_updated": "✅ Product updated successfully!",
    "product_deleted": "✅ Product deleted successfully!",
    "dish_created": "✅ Dish created successfully!",
    "dish_deleted": "✅ Dish deleted successfully!",
    "log_added": "✅ Food logged successfully!",
    "log_deleted": "✅ Log entry deleted successfully!",
    "backup_created": "✅ Backup created successfully!",
    "database_optimized": "✅ Database optimized successfully!",
}

ERROR_MESSAGES = {
    "invalid_data": "❌ Invalid data provided",
    "not_found": "❌ Item not found",
    "database_error": "❌ Database error occurred",
    "validation_error": "❌ Validation failed",
    "server_error": "❌ Internal server error",
}

# Emojis for UI
EMOJIS = {
    "food": "🥗",
    "stats": "📊",
    "product": "🥩",
    "dish": "🍽️",
    "log": "📝",
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "keto": "🥑",
    "calories": "🔥",
    "protein": "💪",
    "fat": "🧈",
    "carbs": "🍞",
}
