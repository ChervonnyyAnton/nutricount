"""
Log routes for Nutricount application.
Handles CRUD operations for food log entries.
"""

from flask import Blueprint, current_app, jsonify, request

from repositories.log_repository import LogRepository
from routes.helpers import safe_get_json
from services.log_service import LogService
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
log_bp = Blueprint("log", __name__, url_prefix="/api/log")


# Initialize service (repository will be created with Config.DATABASE)
def _get_log_service() -> LogService:
    """Get LogService instance."""
    from flask import current_app
    repository = LogRepository(current_app.config["DATABASE"])
    return LogService(repository)


@log_bp.route("", methods=["GET", "POST"])
@monitor_http_request
@rate_limit("api")
def log_api():
    """Food log CRUD endpoint"""
    service = _get_log_service()

    try:
        if request.method == "GET":
            date_filter = request.args.get("date")
            limit = int(request.args.get("limit", 100))

            # Get log entries using service
            entries = service.get_log_entries(date_filter=date_filter, limit=limit)

            return jsonify(json_response(entries))

        else:  # POST
            data = safe_get_json()
            if data is None:
                return (
                    jsonify(json_response(None, "Invalid JSON", status=HTTP_BAD_REQUEST)),
                    HTTP_BAD_REQUEST,
                )

            # Create log entry using service
            success, entry, errors = service.create_log_entry(data)

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
                jsonify(json_response(entry, SUCCESS_MESSAGES["log_added"], HTTP_CREATED)),
                HTTP_CREATED,
            )

    except Exception as e:
        current_app.logger.error(f"Log API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@log_bp.route("/<int:log_id>", methods=["GET", "PUT", "DELETE"])
@monitor_http_request
@rate_limit("api")
def log_detail_api(log_id):
    """Log entry detail operations (GET, PUT, DELETE)"""
    service = _get_log_service()

    try:
        if request.method == "GET":
            # Get log entry using service
            entry = service.get_log_entry_by_id(log_id)

            if not entry:
                return (
                    jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)),
                    HTTP_NOT_FOUND,
                )

            return jsonify(json_response(entry))

        elif request.method == "PUT":
            # Update log entry
            data = safe_get_json()
            if data is None:
                return (
                    jsonify(json_response(None, "Invalid JSON", status=HTTP_BAD_REQUEST)),
                    HTTP_BAD_REQUEST,
                )

            # Update using service
            success, entry, errors = service.update_log_entry(log_id, data)

            if not success:
                # Check if it's a not found error or validation error
                if "not found" in (errors[0] if errors else "").lower():
                    return (
                        jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)),
                        HTTP_NOT_FOUND,
                    )
                return (
                    jsonify(
                        json_response(
                            None,
                            ERROR_MESSAGES["validation_error"],
                            status=HTTP_BAD_REQUEST,
                            errors=errors,
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            return jsonify(json_response(entry, "Log entry updated successfully!"))

        elif request.method == "DELETE":
            # Delete using service
            success, errors = service.delete_log_entry(log_id)

            if not success:
                if "not found" in (errors[0] if errors else "").lower():
                    return (
                        jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)),
                        HTTP_NOT_FOUND,
                    )
                return (
                    jsonify(
                        json_response(
                            None,
                            ERROR_MESSAGES["server_error"],
                            status=500,
                            errors=errors,
                        )
                    ),
                    500,
                )

            return jsonify(json_response({}, SUCCESS_MESSAGES["log_deleted"]))

    except Exception as e:
        current_app.logger.error(f"Log detail API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
