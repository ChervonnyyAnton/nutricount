"""
Fasting routes for Nutricount application.
Handles intermittent fasting tracking: sessions, goals, statistics, and settings.
"""

from flask import Blueprint, current_app, jsonify, request

from routes.helpers import safe_get_json
from src.config import Config
from src.constants import ERROR_MESSAGES, HTTP_BAD_REQUEST, HTTP_CREATED, HTTP_OK
from src.fasting_manager import FastingManager
from src.monitoring import monitor_http_request
from src.security import rate_limit
from src.utils import json_response


# Create fasting blueprint
fasting_bp = Blueprint("fasting", __name__, url_prefix="/api/fasting")


@fasting_bp.route("/start", methods=["POST"])
@monitor_http_request
@rate_limit("api")
def start_fasting():
    """Start a new fasting session"""
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

        # Validate fasting type
        valid_types = ["16:8", "18:6", "20:4", "OMAD", "Custom"]
        if fasting_type not in valid_types:
            return (
                jsonify(
                    json_response(
                        None,
                        ERROR_MESSAGES["validation_error"],
                        HTTP_BAD_REQUEST,
                        errors=[f"Invalid fasting type. Must be one of: {', '.join(valid_types)}"],
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        # Validate target_hours if provided
        if target_hours is not None and target_hours < 0:
            return (
                jsonify(
                    json_response(
                        None,
                        ERROR_MESSAGES["validation_error"],
                        HTTP_BAD_REQUEST,
                        errors=["Target hours must be non-negative"],
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        fasting_manager = FastingManager(Config.DATABASE)

        # Check if there's already an active session
        active_session = fasting_manager.get_active_session()
        if active_session:
            return (
                jsonify(
                    json_response(
                        None, "You already have an active fasting session", HTTP_BAD_REQUEST
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        # Start new session
        session = fasting_manager.start_fasting_session(fasting_type, notes)

        return (
            jsonify(
                json_response(
                    {
                        "session_id": session.id,
                        "start_time": session.start_time.isoformat(),
                        "fasting_type": session.fasting_type,
                        "status": session.status,
                    },
                    "Fasting session started successfully",
                    HTTP_CREATED,
                )
            ),
            HTTP_CREATED,
        )

    except Exception as e:
        current_app.logger.error(f"Start fasting error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@fasting_bp.route("/end", methods=["POST"])
@monitor_http_request
@rate_limit("api")
def end_fasting():
    """End current fasting session"""
    try:
        fasting_manager = FastingManager(Config.DATABASE)

        # Get active session
        active_session = fasting_manager.get_active_session()
        if not active_session:
            return (
                jsonify(json_response(None, "No active fasting session found", HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )

        # End session
        ended_session = fasting_manager.end_fasting_session(active_session.id)

        if ended_session:
            return (
                jsonify(
                    json_response(
                        {
                            "session_id": ended_session.id,
                            "duration_hours": ended_session.duration_hours,
                            "end_time": ended_session.end_time.isoformat(),
                        },
                        "Fasting session completed successfully",
                        HTTP_OK,
                    )
                ),
                HTTP_OK,
            )
        else:
            return (
                jsonify(json_response(None, "Failed to end fasting session", HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )

    except Exception as e:
        current_app.logger.error(f"End fasting error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@fasting_bp.route("/pause", methods=["POST"])
@monitor_http_request
@rate_limit("api")
def pause_fasting():
    """Pause current fasting session"""
    try:
        fasting_manager = FastingManager(Config.DATABASE)

        active_session = fasting_manager.get_active_session()
        if not active_session:
            return (
                jsonify(json_response(None, "No active fasting session found", HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )

        success = fasting_manager.pause_fasting_session(active_session.id)

        if success:
            return (
                jsonify(
                    json_response(
                        {"session_id": active_session.id},
                        "Fasting session paused successfully",
                        HTTP_OK,
                    )
                ),
                HTTP_OK,
            )
        else:
            return (
                jsonify(json_response(None, "Failed to pause fasting session", HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )

    except Exception as e:
        current_app.logger.error(f"Pause fasting error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@fasting_bp.route("/resume", methods=["POST"])
@monitor_http_request
@rate_limit("api")
def resume_fasting():
    """Resume paused fasting session"""
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

        fasting_manager = FastingManager(Config.DATABASE)
        success = fasting_manager.resume_fasting_session(session_id)

        if success:
            return (
                jsonify(
                    json_response(
                        {"session_id": session_id}, "Fasting session resumed successfully", HTTP_OK
                    )
                ),
                HTTP_OK,
            )
        else:
            return (
                jsonify(json_response(None, "Failed to resume fasting session", HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )

    except Exception as e:
        current_app.logger.error(f"Resume fasting error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@fasting_bp.route("/cancel", methods=["POST"])
@monitor_http_request
@rate_limit("api")
def cancel_fasting():
    """Cancel current fasting session"""
    try:
        fasting_manager = FastingManager(Config.DATABASE)

        active_session = fasting_manager.get_active_session()
        if not active_session:
            return (
                jsonify(json_response(None, "No active fasting session found", HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )

        success = fasting_manager.cancel_fasting_session(active_session.id)

        if success:
            return (
                jsonify(
                    json_response(
                        {"session_id": active_session.id},
                        "Fasting session cancelled successfully",
                        HTTP_OK,
                    )
                ),
                HTTP_OK,
            )
        else:
            return (
                jsonify(json_response(None, "Failed to cancel fasting session", HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )

    except Exception as e:
        current_app.logger.error(f"Cancel fasting error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@fasting_bp.route("/status", methods=["GET"])
@monitor_http_request
@rate_limit("api")
def get_fasting_status():
    """Get current fasting status and progress"""
    try:
        fasting_manager = FastingManager(Config.DATABASE)
        progress = fasting_manager.get_fasting_progress()

        return (
            jsonify(json_response(progress, "Fasting status retrieved successfully", HTTP_OK)),
            HTTP_OK,
        )

    except Exception as e:
        current_app.logger.error(f"Get fasting status error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@fasting_bp.route("/sessions", methods=["GET"])
@monitor_http_request
@rate_limit("api")
def get_fasting_sessions():
    """Get recent fasting sessions"""
    try:
        limit = request.args.get("limit", 30, type=int)
        fasting_manager = FastingManager(Config.DATABASE)
        sessions = fasting_manager.get_fasting_sessions(limit=limit)

        # Convert sessions to dict format
        sessions_data = []
        for session in sessions:
            session_dict = {
                "id": session.id,
                "start_time": session.start_time.isoformat() if session.start_time else None,
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "duration_hours": session.duration_hours,
                "fasting_type": session.fasting_type,
                "status": session.status,
                "notes": session.notes,
            }
            sessions_data.append(session_dict)

        return (
            jsonify(
                json_response(
                    {"sessions": sessions_data}, "Fasting sessions retrieved successfully", HTTP_OK
                )
            ),
            HTTP_OK,
        )

    except Exception as e:
        current_app.logger.error(f"Get fasting sessions error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@fasting_bp.route("/stats", methods=["GET"])
@monitor_http_request
@rate_limit("api")
def get_fasting_stats():
    """Get fasting statistics"""
    try:
        days = request.args.get("days", 30, type=int)
        fasting_manager = FastingManager(Config.DATABASE)
        stats = fasting_manager.get_fasting_stats(days=days)

        return (
            jsonify(json_response(stats, "Fasting statistics retrieved successfully", HTTP_OK)),
            HTTP_OK,
        )

    except Exception as e:
        current_app.logger.error(f"Get fasting stats error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@fasting_bp.route("/goals", methods=["GET"])
@monitor_http_request
@rate_limit("api")
def get_fasting_goals():
    """Get fasting goals"""
    try:
        fasting_manager = FastingManager(Config.DATABASE)
        goals = fasting_manager.get_fasting_goals()

        # Convert goals to dict format
        goals_data = []
        for goal in goals:
            goal_dict = {
                "id": goal.id,
                "goal_type": goal.goal_type,
                "target_value": goal.target_value,
                "current_value": goal.current_value,
                "period_start": goal.period_start.isoformat() if goal.period_start else None,
                "period_end": goal.period_end.isoformat() if goal.period_end else None,
                "status": goal.status,
                "progress_percentage": (
                    (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0
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


@fasting_bp.route("/goals", methods=["POST"])
@monitor_http_request
@rate_limit("api")
def create_fasting_goal():
    """Create a new fasting goal"""
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

        fasting_manager = FastingManager(Config.DATABASE)
        goal = fasting_manager.create_fasting_goal(
            goal_type, target_value, period_start, period_end
        )

        return (
            jsonify(
                json_response(
                    {
                        "goal_id": goal.id,
                        "goal_type": goal.goal_type,
                        "target_value": goal.target_value,
                        "period_start": goal.period_start.isoformat(),
                        "period_end": goal.period_end.isoformat(),
                    },
                    "Fasting goal created successfully",
                    HTTP_CREATED,
                )
            ),
            HTTP_CREATED,
        )

    except Exception as e:
        current_app.logger.error(f"Create fasting goal error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@fasting_bp.route("/settings", methods=["GET", "POST", "PUT"])
@monitor_http_request
@rate_limit("api")
def fasting_settings_api():
    """Get, create, or update fasting settings"""
    try:
        user_id = 1  # Default user for now

        if request.method == "GET":
            # Get fasting settings
            fasting_manager = FastingManager(Config.DATABASE)
            settings = fasting_manager.get_fasting_settings(user_id)

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

            fasting_manager = FastingManager(Config.DATABASE)

            if request.method == "POST":
                # Create new settings
                settings = fasting_manager.create_fasting_settings(settings_data)
                message = "Fasting settings created successfully"
            else:
                # Update existing settings
                settings = fasting_manager.update_fasting_settings(user_id, settings_data)
                message = "Fasting settings updated successfully"

            return jsonify(json_response(settings, message, HTTP_OK)), HTTP_OK

    except Exception as e:
        current_app.logger.error(f"Fasting settings error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
