"""
Metrics and task routes for Nutricount application.
Handles Prometheus metrics, metrics summary, and background task management.
"""

from flask import Blueprint, current_app, jsonify

from routes.helpers import safe_get_json
from src.cache_manager import cache_manager
from src.constants import ERROR_MESSAGES, HTTP_BAD_REQUEST, HTTP_CREATED, HTTP_NOT_FOUND, HTTP_OK
from src.monitoring import metrics_collector, monitor_http_request, system_monitor
from src.security import rate_limit
from src.task_manager import task_manager
from src.utils import json_response


# Create metrics blueprint
metrics_bp = Blueprint("metrics", __name__)


@metrics_bp.route("/metrics", methods=["GET"])
@monitor_http_request
def prometheus_metrics():
    """Prometheus metrics endpoint"""
    try:
        # Update system metrics
        system_monitor.update_metrics()

        # Get metrics in Prometheus format
        metrics_data = metrics_collector.get_metrics()

        return metrics_data, 200, {"Content-Type": "text/plain; charset=utf-8"}
    except Exception as e:
        current_app.logger.error(f"Metrics error: {e}")
        return f"# Error getting metrics: {e}\n", 500, {"Content-Type": "text/plain; charset=utf-8"}


@metrics_bp.route("/api/metrics/summary", methods=["GET"])
@monitor_http_request
@rate_limit("api")
def metrics_summary():
    """Get metrics summary for API"""
    try:
        summary = metrics_collector.get_metrics_summary()

        # Add cache stats
        cache_stats = cache_manager.get_stats()
        summary["cache_stats"] = cache_stats

        return (
            jsonify(json_response(summary, "Metrics summary retrieved successfully", HTTP_OK)),
            HTTP_OK,
        )
    except Exception as e:
        current_app.logger.error(f"Metrics summary error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@metrics_bp.route("/api/tasks", methods=["POST"])
@monitor_http_request
@rate_limit("api")
def create_background_task():
    """Create a background task"""
    try:
        data = safe_get_json()
        if data is None:
            return (
                jsonify(json_response(None, "Invalid JSON", status=HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )
        task_type = data.get("task_type")

        if not task_type:
            return (
                jsonify(
                    json_response(
                        None,
                        ERROR_MESSAGES["validation_error"],
                        HTTP_BAD_REQUEST,
                        errors=["task_type is required"],
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        task_id = None

        if task_type == "backup":
            backup_path = data.get("backup_path")
            task_id = task_manager.backup_database(backup_path)
        elif task_type == "optimize":
            task_id = task_manager.optimize_database()
        elif task_type == "export":
            export_format = data.get("export_format", "json")
            task_id = task_manager.export_data(export_format)
        elif task_type == "cleanup":
            days = data.get("days", 30)
            task_id = task_manager.cleanup_old_logs(days)
        else:
            return (
                jsonify(
                    json_response(
                        None,
                        ERROR_MESSAGES["validation_error"],
                        HTTP_BAD_REQUEST,
                        errors=[f"Unknown task type: {task_type}"],
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        return (
            jsonify(
                json_response(
                    {"task_id": task_id, "task_type": task_type},
                    "Background task created successfully",
                    HTTP_CREATED,
                )
            ),
            HTTP_CREATED,
        )

    except Exception as e:
        current_app.logger.error(f"Create task error: {e}")
        # Check if it's a Redis/Celery connection error
        if (
            "redis" in str(e).lower()
            or "celery" in str(e).lower()
            or "connection refused" in str(e).lower()
        ):
            error_message = f"❌ Task service unavailable: {str(e)}"
        else:
            error_message = ERROR_MESSAGES["server_error"]
        return jsonify(json_response(None, error_message, 500)), 500


@metrics_bp.route("/api/tasks/<task_id>", methods=["GET"])
@monitor_http_request
@rate_limit("api")
def get_task_status(task_id):
    """Get background task status"""
    try:
        status = task_manager.get_task_status(task_id)

        # Debug logging
        current_app.logger.info(f"Task status for {task_id}: {status}")

        # Check if task exists (if status is FAILURE and has specific error)
        if (
            status.get("status") == "FAILURE"
            and "not found" in str(status.get("error", "")).lower()
        ):
            return (
                jsonify(json_response(None, "Task not found", status=HTTP_NOT_FOUND)),
                HTTP_NOT_FOUND,
            )

        # Check if task status is NOT_FOUND
        if status.get("status") == "NOT_FOUND":
            return (
                jsonify(json_response(None, "Task not found", status=HTTP_NOT_FOUND)),
                HTTP_NOT_FOUND,
            )

        # Check if task status is FAILURE with any error (task doesn't exist)
        if status.get("status") == "FAILURE":
            return (
                jsonify(json_response(None, "Task not found", status=HTTP_NOT_FOUND)),
                HTTP_NOT_FOUND,
            )

        return (
            jsonify(json_response(status, "Task status retrieved successfully", HTTP_OK)),
            HTTP_OK,
        )

    except Exception as e:
        current_app.logger.error(f"Get task status error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
