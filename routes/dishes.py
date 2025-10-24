"""
Dishes routes for Nutricount application.
Handles CRUD operations for dishes (recipes).
Refactored to use Service Layer Pattern.
"""

from flask import Blueprint, current_app, jsonify, request

from repositories.dish_repository import DishRepository
from routes.helpers import get_db, safe_get_json
from services.dish_service import DishService
from src.constants import (
    ERROR_MESSAGES,
    HTTP_BAD_REQUEST,
    HTTP_CREATED,
    HTTP_NOT_FOUND,
    SUCCESS_MESSAGES,
)
from src.monitoring import monitor_http_request
from src.security import rate_limit
from src.utils import json_response


# Create blueprint
dishes_bp = Blueprint("dishes", __name__, url_prefix="/api/dishes")


def _get_dish_service() -> DishService:
    """Get DishService instance."""
    db = get_db()
    repository = DishRepository(db)
    return DishService(repository)


@dishes_bp.route("", methods=["GET", "POST"])
@monitor_http_request
@rate_limit("api")
def dishes_api():
    """
    Dishes CRUD endpoint.
    
    Delegates business logic to DishService.
    """
    db = None
    try:
        if request.method == "GET":
            # Get service instance
            service = _get_dish_service()
            
            # Get dishes from service
            dishes = service.get_dishes()
            
            return jsonify(json_response(dishes))

        else:  # POST
            data = safe_get_json()
            if data is None:
                return (
                    jsonify(json_response(None, "Invalid JSON", status=HTTP_BAD_REQUEST)),
                    HTTP_BAD_REQUEST,
                )

            # Get service instance
            service = _get_dish_service()
            
            # Create dish via service
            success, dish, errors = service.create_dish(data)
            
            if not success:
                return (
                    jsonify(
                        json_response(
                            None, "Validation failed", status=HTTP_BAD_REQUEST, errors=errors
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )
            
            return (
                jsonify(json_response(dish, SUCCESS_MESSAGES["dish_created"], HTTP_CREATED)),
                HTTP_CREATED,
            )

    except Exception as e:
        current_app.logger.error(f"Dishes API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        if db:
            db.close()


@dishes_bp.route("/<int:dish_id>", methods=["GET", "PUT", "DELETE"])
@monitor_http_request
@rate_limit("api")
def dish_detail_api(dish_id):
    """
    Dish detail operations (GET, PUT, DELETE).
    
    Delegates business logic to DishService.
    """
    try:
        # Get service instance
        service = _get_dish_service()
        
        if request.method == "GET":
            # Get dish by ID
            dish = service.get_dish_by_id(dish_id)
            if not dish:
                return (
                    jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)),
                    HTTP_NOT_FOUND,
                )
            
            return jsonify(json_response(dish))

        elif request.method == "PUT":
            # Update dish
            data = safe_get_json()
            if data is None:
                return (
                    jsonify(json_response(None, "Invalid JSON", status=HTTP_BAD_REQUEST)),
                    HTTP_BAD_REQUEST,
                )
            
            # Update via service
            success, updated_dish, errors = service.update_dish(dish_id, data)
            
            if not success:
                # Check if it's "not found" error
                if errors and "not found" in errors[0].lower():
                    return (
                        jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)),
                        HTTP_NOT_FOUND,
                    )
                
                return (
                    jsonify(
                        json_response(
                            None, "Validation failed", status=HTTP_BAD_REQUEST, errors=errors
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )
            
            return jsonify(json_response(updated_dish, "Dish updated successfully!"))

        elif request.method == "DELETE":
            # Delete via service
            success, errors = service.delete_dish(dish_id)
            
            if not success:
                # Check if it's "not found" error
                if errors and "not found" in errors[0].lower():
                    return (
                        jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)),
                        HTTP_NOT_FOUND,
                    )
                
                return (
                    jsonify(
                        json_response(None, errors[0] if errors else "Delete failed", HTTP_BAD_REQUEST)
                    ),
                    HTTP_BAD_REQUEST,
                )
            
            return jsonify(json_response(None, "Dish deleted successfully!"))

    except Exception as e:
        current_app.logger.error(f"Dish detail API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
