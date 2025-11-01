"""
Fasting routes for Nutricount application.
Handles intermittent fasting tracking: sessions, goals, statistics, and settings.

Refactored to use Service Layer pattern for thin controllers.
"""

from flask import Blueprint, current_app, jsonify, request

from repositories.fasting_repository import FastingRepository
from routes.helpers import get_db, safe_get_json
from services.fasting_service import FastingService
from src.constants import ERROR_MESSAGES, HTTP_BAD_REQUEST, HTTP_CREATED, HTTP_OK, SUCCESS_MESSAGES
from src.monitoring import monitor_http_request
from src.security import rate_limit
from src.utils import json_response

# Create fasting blueprint
fasting_bp = Blueprint("fasting", __name__, url_prefix="/api/fasting")


def _get_fasting_service(db) -> FastingService:
    """
    Get FastingService instance with repository.

    Args:
        db: Database connection

    Returns:
        FastingService instance
    """
    repository = FastingRepository(db)
    return FastingService(repository)


@fasting_bp.route("/start", methods=["POST"])
@monitor_http_request
@rate_limit("api")
def start_fasting():
    """
    Start a new fasting session (thin controller).

    Delegates business logic to FastingService.
    """
    db = get_db()
    try:
        data = safe_get_json()
        if data is None:
            return (
                jsonify(json_response(None, "Invalid JSON", status=HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )

        fasting_type = data.get("fasting_type", "16:8")
        notes = data.get("notes", "")
        target_hours = data.get("target_hours")

        # Validate target_hours if provided (legacy validation)
        if target_hours is not None and target_hours < 0:
            return (
                jsonify(
                    json_response(
                        None,
                        "Validation error: Target hours must be non-negative",
                        HTTP_BAD_REQUEST,
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        # Delegate to service
        service = _get_fasting_service(db)
        success, session, errors = service.start_fasting_session(fasting_type, notes)

        if success:
            return (
                jsonify(
                    json_response(
                        {
                            "session_id": session["id"],
                            "start_time": session["start_time"],
                            "fasting_type": session["fasting_type"],
                            "status": session["status"],
                        },
                        SUCCESS_MESSAGES.get(
                            "fasting_started", "Fasting session started successfully"
                        ),
                        HTTP_CREATED,
                    )
                ),
                HTTP_CREATED,
            )
        else:
            # Use first error as message if single error, otherwise "Validation failed"
            message = errors[0] if len(errors) == 1 else "Validation failed"
            return (
                jsonify(
                    json_response(
                        None,
                        message,
                        HTTP_BAD_REQUEST,
                        errors=errors if len(errors) > 1 else None,
                    )
                ),
                HTTP_BAD_REQUEST,
            )

    except Exception as e:
        current_app.logger.error(f"Start fasting error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


@fasting_bp.route("/end", methods=["POST"])
@monitor_http_request
@rate_limit("api")
def end_fasting():
    """
    End current fasting session (thin controller).

    Delegates business logic to FastingService.
    """
    db = get_db()
    try:
        service = _get_fasting_service(db)

        # Get active session
        active_session = service.get_active_session()
        if not active_session:
            return (
                jsonify(json_response(None, "No active fasting session found", HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )

        # End session
        success, ended_session, errors = service.end_fasting_session(active_session["id"])

        if success:
            return (
                jsonify(
                    json_response(
                        {
                            "session_id": ended_session["id"],
                            "duration_hours": ended_session["duration_hours"],
                            "end_time": ended_session["end_time"],
                        },
                        SUCCESS_MESSAGES.get(
                            "fasting_ended", "Fasting session completed successfully"
                        ),
                        HTTP_OK,
                    )
                ),
                HTTP_OK,
            )
        else:
            # Use first error as message
            message = errors[0] if errors else "Failed to end fasting session"
            return (
                jsonify(json_response(None, message, HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )

    except Exception as e:
        current_app.logger.error(f"End fasting error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


@fasting_bp.route("/pause", methods=["POST"])
@monitor_http_request
@rate_limit("api")
def pause_fasting():
    """
    Pause current fasting session (thin controller).

    Delegates business logic to FastingService.
    """
    db = get_db()
    try:
        service = _get_fasting_service(db)

        active_session = service.get_active_session()
        if not active_session:
            return (
                jsonify(json_response(None, "No active fasting session found", HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )

        success, paused_session, errors = service.pause_fasting_session(active_session["id"])

        if success:
            return (
                jsonify(
                    json_response(
                        {"session_id": active_session["id"]},
                        SUCCESS_MESSAGES.get(
                            "fasting_paused", "Fasting session paused successfully"
                        ),
                        HTTP_OK,
                    )
                ),
                HTTP_OK,
            )
        else:
            # Use first error as message
            message = errors[0] if errors else "Failed to pause fasting session"
            return (
                jsonify(json_response(None, message, HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )

    except Exception as e:
        current_app.logger.error(f"Pause fasting error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


@fasting_bp.route("/resume", methods=["POST"])
@monitor_http_request
@rate_limit("api")
def resume_fasting():
    """
    Resume paused fasting session (thin controller).

    Delegates business logic to FastingService.
    """
    db = get_db()
    try:
        data = safe_get_json()
        if data is None:
            return (
                jsonify(json_response(None, "Invalid JSON", status=HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )
        session_id = data.get("session_id")

        if not session_id:
            return (
                jsonify(json_response(None, "Session ID is required", HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )

        service = _get_fasting_service(db)
        success, resumed_session, errors = service.resume_fasting_session(session_id)

        if success:
            return (
                jsonify(
                    json_response(
                        {"session_id": session_id},
                        SUCCESS_MESSAGES.get(
                            "fasting_resumed", "Fasting session resumed successfully"
                        ),
                        HTTP_OK,
                    )
                ),
                HTTP_OK,
            )
        else:
            # Use first error as message
            message = errors[0] if errors else "Failed to resume fasting session"
            return (
                jsonify(json_response(None, message, HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )

    except Exception as e:
        current_app.logger.error(f"Resume fasting error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


@fasting_bp.route("/cancel", methods=["POST"])
@monitor_http_request
@rate_limit("api")
def cancel_fasting():
    """
    Cancel current fasting session (thin controller).

    Delegates business logic to FastingService.
    """
    db = get_db()
    try:
        service = _get_fasting_service(db)

        active_session = service.get_active_session()
        if not active_session:
            return (
                jsonify(json_response(None, "No active fasting session found", HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )

        success, errors = service.cancel_fasting_session(active_session["id"])

        if success:
            return (
                jsonify(
                    json_response(
                        {"session_id": active_session["id"]},
                        SUCCESS_MESSAGES.get(
                            "fasting_cancelled", "Fasting session cancelled successfully"
                        ),
                        HTTP_OK,
                    )
                ),
                HTTP_OK,
            )
        else:
            # Use first error as message
            message = errors[0] if errors else "Failed to cancel fasting session"
            return (
                jsonify(json_response(None, message, HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )

    except Exception as e:
        current_app.logger.error(f"Cancel fasting error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


@fasting_bp.route("/status", methods=["GET"])
@monitor_http_request
@rate_limit("api")
def get_fasting_status():
    """
    Get current fasting status and progress (thin controller).

    Delegates business logic to FastingService.
    """
    db = get_db()
    try:
        service = _get_fasting_service(db)
        progress = service.get_fasting_progress()

        return (
            jsonify(json_response(progress, "Fasting status retrieved successfully", HTTP_OK)),
            HTTP_OK,
        )

    except Exception as e:
        current_app.logger.error(f"Get fasting status error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


@fasting_bp.route("/sessions", methods=["GET"])
@monitor_http_request
@rate_limit("api")
def get_fasting_sessions():
    """
    Get recent fasting sessions (thin controller).

    Delegates business logic to FastingService.
    """
    db = get_db()
    try:
        limit = request.args.get("limit", 30, type=int)
        service = _get_fasting_service(db)
        sessions = service.get_fasting_sessions(limit=limit)

        return (
            jsonify(
                json_response(
                    {"sessions": sessions}, "Fasting sessions retrieved successfully", HTTP_OK
                )
            ),
            HTTP_OK,
        )

    except Exception as e:
        current_app.logger.error(f"Get fasting sessions error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


@fasting_bp.route("/stats", methods=["GET"])
@monitor_http_request
@rate_limit("api")
def get_fasting_stats():
    """
    Get fasting statistics (thin controller).

    Delegates business logic to FastingService.
    """
    db = get_db()
    try:
        days = request.args.get("days", 30, type=int)
        service = _get_fasting_service(db)
        stats = service.get_fasting_stats_with_streak(days=days)

        return (
            jsonify(json_response(stats, "Fasting statistics retrieved successfully", HTTP_OK)),
            HTTP_OK,
        )

    except Exception as e:
        current_app.logger.error(f"Get fasting stats error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


@fasting_bp.route("/goals", methods=["GET"])
@monitor_http_request
@rate_limit("api")
def get_fasting_goals():
    """
    Get fasting goals (thin controller).

    Delegates business logic to FastingService.
    """
    db = get_db()
    try:
        service = _get_fasting_service(db)
        goals = service.get_fasting_goals()

        # goals are already dictionaries, just add progress percentage
        goals_data = []
        for goal in goals:
            goal_dict = {
                "id": goal.get("id"),
                "goal_type": goal.get("goal_type"),
                "target_value": goal.get("target_value"),
                "current_value": goal.get("current_value"),
                "period_start": goal.get("period_start"),
                "period_end": goal.get("period_end"),
                "status": goal.get("status"),
                "progress_percentage": (
                    (goal.get("current_value", 0) / goal.get("target_value", 1) * 100)
                    if goal.get("target_value", 0) > 0
                    else 0
                ),
            }
            goals_data.append(goal_dict)

        return (
            jsonify(
                json_response(
                    {"goals": goals_data}, "Fasting goals retrieved successfully", HTTP_OK
                )
            ),
            HTTP_OK,
        )

    except Exception as e:
        current_app.logger.error(f"Get fasting goals error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


@fasting_bp.route("/goals", methods=["POST"])
@monitor_http_request
@rate_limit("api")
def create_fasting_goal():
    """
    Create a new fasting goal (thin controller).

    Delegates business logic to FastingService.
    """
    db = get_db()
    try:
        data = safe_get_json()
        if data is None:
            return (
                jsonify(json_response(None, "Invalid JSON", status=HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )

        goal_type = data.get("goal_type")
        target_value = data.get("target_value")
        period_start = data.get("period_start")
        period_end = data.get("period_end")

        # Validate required fields
        if not all([goal_type, target_value, period_start, period_end]):
            return (
                jsonify(
                    json_response(
                        None,
                        ERROR_MESSAGES["validation_error"],
                        HTTP_BAD_REQUEST,
                        errors=[
                            "All fields are required: goal_type, target_value, period_start, period_end"
                        ],
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        # Validate goal type
        valid_types = ["daily_hours", "weekly_sessions", "monthly_hours"]
        if goal_type not in valid_types:
            return (
                jsonify(
                    json_response(
                        None,
                        ERROR_MESSAGES["validation_error"],
                        HTTP_BAD_REQUEST,
                        errors=[f"Invalid goal type. Must be one of: {', '.join(valid_types)}"],
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        # Parse dates
        try:
            from datetime import date

            period_start = date.fromisoformat(period_start)
            period_end = date.fromisoformat(period_end)
        except ValueError:
            return (
                jsonify(
                    json_response(
                        None,
                        ERROR_MESSAGES["validation_error"],
                        HTTP_BAD_REQUEST,
                        errors=["Invalid date format. Use YYYY-MM-DD"],
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        service = _get_fasting_service(db)
        success, goal, errors = service.create_fasting_goal(
            goal_type, target_value, period_start, period_end
        )

        if success and goal:
            return (
                jsonify(
                    json_response(
                        {
                            "goal_id": goal.get("id"),
                            "goal_type": goal.get("goal_type"),
                            "target_value": goal.get("target_value"),
                            "period_start": goal.get("period_start"),
                            "period_end": goal.get("period_end"),
                        },
                        "Fasting goal created successfully",
                        HTTP_CREATED,
                    )
                ),
                HTTP_CREATED,
            )
        else:
            message = errors[0] if errors else "Failed to create goal"
            return (
                jsonify(json_response(None, message, HTTP_BAD_REQUEST, errors=errors)),
                HTTP_BAD_REQUEST,
            )

    except Exception as e:
        current_app.logger.error(f"Create fasting goal error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


@fasting_bp.route("/settings", methods=["GET", "POST", "PUT"])
@monitor_http_request
@rate_limit("api")
def fasting_settings_api():
    """
    Get, create, or update fasting settings (thin controller).

    Delegates business logic to FastingService.
    """
    db = get_db()
    try:
        user_id = 1  # Default user for now
        service = _get_fasting_service(db)

        if request.method == "GET":
            # Get fasting settings
            settings = service.get_fasting_settings(user_id)
            return jsonify(json_response(settings, "Fasting settings retrieved", HTTP_OK)), HTTP_OK

        elif request.method in ["POST", "PUT"]:
            # Create or update fasting settings
            data = safe_get_json()
            if data is None:
                return (
                    jsonify(json_response(None, "Invalid JSON", status=HTTP_BAD_REQUEST)),
                    HTTP_BAD_REQUEST,
                )

            # Validate required fields
            required_fields = ["fasting_goal", "preferred_start_time"]
            errors = []

            for field in required_fields:
                if not data.get(field):
                    errors.append(f"{field} is required")

            if errors:
                return (
                    jsonify(
                        json_response(None, "Validation failed", HTTP_BAD_REQUEST, errors=errors)
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Validate fasting goal
            valid_goals = ["16:8", "18:6", "20:4", "OMAD"]
            if data.get("fasting_goal") not in valid_goals:
                errors.append(f"fasting_goal must be one of: {', '.join(valid_goals)}")

            if errors:
                return (
                    jsonify(
                        json_response(None, "Validation failed", HTTP_BAD_REQUEST, errors=errors)
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Prepare settings data
            settings_data = {
                "user_id": user_id,
                "fasting_goal": data.get("fasting_goal"),
                "preferred_start_time": data.get("preferred_start_time"),
                "enable_reminders": data.get("enable_reminders", False),
                "enable_notifications": data.get("enable_notifications", False),
                "default_notes": data.get("default_notes", ""),
            }

            if request.method == "POST":
                # Create new settings
                success, settings, errors = service.create_fasting_settings(settings_data)
                message = "Fasting settings created successfully"
            else:
                # PUT: Update existing settings or create if not found (upsert)
                success, settings, errors = service.update_fasting_settings(user_id, settings_data)
                if not success and errors and "Settings not found for user" in errors:
                    # Settings don't exist, create them (upsert behavior)
                    success, settings, errors = service.create_fasting_settings(settings_data)
                    message = "Fasting settings created successfully"
                else:
                    message = "Fasting settings updated successfully"

            if success and settings:
                return jsonify(json_response(settings, message, HTTP_OK)), HTTP_OK
            else:
                error_message = errors[0] if errors else "Failed to save settings"
                return (
                    jsonify(json_response(None, error_message, HTTP_BAD_REQUEST, errors=errors)),
                    HTTP_BAD_REQUEST,
                )

    except Exception as e:
        current_app.logger.error(f"Fasting settings error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()
