"""
Products routes for Nutricount application.
Handles CRUD operations for products (food items).

Refactored to use Service Layer pattern for thin controllers.
"""

from flask import Blueprint, jsonify, request

from repositories.product_repository import ProductRepository
from routes.helpers import get_db, safe_get_json
from services.product_service import ProductService
from src.constants import (
    HTTP_BAD_REQUEST,
    HTTP_CREATED,
    HTTP_NOT_FOUND,
    SUCCESS_MESSAGES,
)
from src.monitoring import monitor_http_request
from src.security import rate_limit
from src.utils import json_response


# Create products blueprint
products_bp = Blueprint("products", __name__, url_prefix="/api/products")


@products_bp.route("", methods=["GET", "POST"])
@monitor_http_request
@rate_limit("api")
def products_api():
    """
    Products CRUD endpoint (thin controller).

    Delegates business logic to ProductService.
    """
    # Initialize service with repository
    db = get_db()
    repository = ProductRepository(db)
    service = ProductService(repository)

    try:
        if request.method == "GET":
            # Get query parameters
            search = request.args.get("search", "").strip()
            limit = int(request.args.get("limit", 50))
            offset = int(request.args.get("offset", 0))

            # Delegate to service
            products = service.get_products(search, limit, offset)

            return jsonify(json_response(products))

        else:  # POST
            data = safe_get_json()
            if data is None:
                return (
                    jsonify(json_response(None, "Invalid JSON", status=HTTP_BAD_REQUEST)),
                    HTTP_BAD_REQUEST,
                )

            # Delegate to service
            success, product, errors = service.create_product(data)

            if success:
                return (
                    jsonify(json_response(product, SUCCESS_MESSAGES["product_created"], HTTP_CREATED)),
                    HTTP_CREATED,
                )
            else:
                return (
                    jsonify(json_response(None, "Validation failed", status=HTTP_BAD_REQUEST, errors=errors)),
                    HTTP_BAD_REQUEST,
                )

    except Exception as e:
        # Handle unexpected errors
        from flask import current_app
        current_app.logger.error(f"Unexpected error in products API: {e}")
        return jsonify(json_response(None, "Internal server error", status=500)), 500
    finally:
        db.close()


@products_bp.route("/<int:product_id>", methods=["GET", "DELETE", "PUT"])
@monitor_http_request
@rate_limit("api")
def product_detail_api(product_id):
    """
    Individual product operations (thin controller).

    Delegates business logic to ProductService.
    """
    # Initialize service with repository
    db = get_db()
    repository = ProductRepository(db)
    service = ProductService(repository)

    try:
        if request.method == "GET":
            # Delegate to service
            product = service.get_product_by_id(product_id)

            if not product:
                return (
                    jsonify(json_response(None, "Product not found", HTTP_NOT_FOUND)),
                    HTTP_NOT_FOUND,
                )

            return jsonify(json_response(product))

        elif request.method == "DELETE":
            # Delegate to service
            success, errors = service.delete_product(product_id)

            if success:
                return jsonify(json_response({}, SUCCESS_MESSAGES["product_deleted"]))
            else:
                # Determine status code based on error message
                status = HTTP_NOT_FOUND if "not found" in errors[0].lower() else HTTP_BAD_REQUEST
                return (
                    jsonify(json_response(None, errors[0], status)),
                    status,
                )

        elif request.method == "PUT":
            data = safe_get_json()
            if data is None:
                return (
                    jsonify(json_response(None, "Invalid JSON", status=HTTP_BAD_REQUEST)),
                    HTTP_BAD_REQUEST,
                )

            # Delegate to service
            success, product, errors = service.update_product(product_id, data)

            if success:
                return jsonify(json_response(product, SUCCESS_MESSAGES["product_updated"]))
            else:
                # Determine status code based on error message
                status = HTTP_NOT_FOUND if "not found" in errors[0].lower() else HTTP_BAD_REQUEST
                return (
                    jsonify(json_response(None, "Validation failed", status=status, errors=errors)),
                    status,
                )

    except Exception as e:
        # Handle unexpected errors
        from flask import current_app
        current_app.logger.error(f"Unexpected error in products API: {e}")
        return jsonify(json_response(None, "Internal server error", status=500)), 500
    finally:
        db.close()
