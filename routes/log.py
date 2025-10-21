"""
Log routes for Nutricount application.
Handles CRUD operations for food log entries.
"""

import sqlite3

from flask import Blueprint, current_app, jsonify, request
from werkzeug.exceptions import BadRequest

from src.config import Config
from src.constants import (
    ERROR_MESSAGES,
    HTTP_BAD_REQUEST,
    HTTP_CREATED,
    HTTP_NOT_FOUND,
    SUCCESS_MESSAGES,
)
from src.monitoring import monitor_http_request
from src.security import rate_limit
from src.utils import json_response, safe_float, validate_log_data


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


# Create blueprint
log_bp = Blueprint("log", __name__, url_prefix="/api/log")


@log_bp.route("", methods=["GET", "POST"])
@monitor_http_request
@rate_limit("api")
def log_api():
    """Food log CRUD endpoint"""
    db = get_db()

    try:
        if request.method == "GET":
            date_filter = request.args.get("date")
            limit = min(int(request.args.get("limit", 100)), Config.API_MAX_PER_PAGE)

            if date_filter:
                query = """
                    SELECT * FROM log_entries_with_details
                    WHERE date = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """
                params = (date_filter, limit)
            else:
                query = """
                    SELECT * FROM log_entries_with_details
                    ORDER BY date DESC, created_at DESC
                    LIMIT ?
                """
                params = (limit,)

            log_entries = [dict(row) for row in db.execute(query, params).fetchall()]

            # Process log entries to calculate nutrition values
            processed_entries = []
            for entry in log_entries:
                processed_entry = dict(entry)

                # Calculate nutrition values based on item type
                if entry["item_type"] == "product":
                    # For products, use per_100g values and calculate actual amounts
                    quantity_factor = entry["quantity_grams"] / 100.0
                    processed_entry["calories"] = (
                        entry["calories_per_100g"] * quantity_factor
                        if entry["calories_per_100g"]
                        else None
                    )
                    processed_entry["protein"] = (
                        entry["protein_per_100g"] * quantity_factor
                        if entry["protein_per_100g"]
                        else None
                    )
                    processed_entry["fat"] = (
                        entry["fat_per_100g"] * quantity_factor if entry["fat_per_100g"] else None
                    )
                    processed_entry["carbs"] = (
                        entry["carbs_per_100g"] * quantity_factor
                        if entry["carbs_per_100g"]
                        else None
                    )
                elif entry["item_type"] == "dish":
                    # For dishes, use dish_per_100g values and calculate actual amounts
                    quantity_factor = entry["quantity_grams"] / 100.0
                    processed_entry["calories"] = (
                        entry["calculated_calories"] if entry["calculated_calories"] else None
                    )
                    processed_entry["protein"] = (
                        entry["dish_protein_per_100g"] * quantity_factor
                        if entry["dish_protein_per_100g"]
                        else None
                    )
                    processed_entry["fat"] = (
                        entry["dish_fat_per_100g"] * quantity_factor
                        if entry["dish_fat_per_100g"]
                        else None
                    )
                    processed_entry["carbs"] = (
                        entry["dish_carbs_per_100g"] * quantity_factor
                        if entry["dish_carbs_per_100g"]
                        else None
                    )

                processed_entries.append(processed_entry)

            return jsonify(json_response(processed_entries))

        else:  # POST
            data = safe_get_json()
            if data is None:
                return (
                    jsonify(json_response(None, "Invalid JSON", status=HTTP_BAD_REQUEST)),
                    HTTP_BAD_REQUEST,
                )

            # Validate log data
            is_valid, errors, cleaned_data = validate_log_data(data)
            if not is_valid:
                return (
                    jsonify(
                        json_response(
                            None, "Validation failed", status=HTTP_BAD_REQUEST, errors=errors
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Verify item exists
            if cleaned_data["item_type"] == "product":
                item_exists = db.execute(
                    "SELECT name FROM products WHERE id = ?", (cleaned_data["item_id"],)
                ).fetchone()
            else:
                item_exists = db.execute(
                    "SELECT name FROM dishes WHERE id = ?", (cleaned_data["item_id"],)
                ).fetchone()

            if not item_exists:
                return (
                    jsonify(
                        json_response(
                            None,
                            "Validation failed",
                            status=HTTP_BAD_REQUEST,
                            errors=[
                                f"{cleaned_data['item_type'].title()} with ID {cleaned_data['item_id']} not found"
                            ],
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Create log entry
            try:
                cursor = db.execute(
                    """
                    INSERT INTO log_entries (date, item_type, item_id, quantity_grams, meal_time, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        cleaned_data["date"],
                        cleaned_data["item_type"],
                        cleaned_data["item_id"],
                        cleaned_data["quantity_grams"],
                        cleaned_data["meal_time"],
                        cleaned_data.get("notes", ""),
                    ),
                )

                db.commit()

                # Return created log entry with details
                log_id = cursor.lastrowid
                log_entry = dict(
                    db.execute(
                        "SELECT * FROM log_entries_with_details WHERE id = ?", (log_id,)
                    ).fetchone()
                )

                return (
                    jsonify(json_response(log_entry, SUCCESS_MESSAGES["log_added"], HTTP_CREATED)),
                    HTTP_CREATED,
                )

            except sqlite3.IntegrityError as e:
                current_app.logger.error(f"Log creation integrity error: {e}")
                return (
                    jsonify(
                        json_response(
                            None,
                            "Database error",
                            status=HTTP_BAD_REQUEST,
                            errors=["Failed to create log entry due to database constraint"],
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

    except Exception as e:
        current_app.logger.error(f"Log API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()


@log_bp.route("/<int:log_id>", methods=["GET", "PUT", "DELETE"])
def log_detail_api(log_id):
    """Log entry detail operations (GET, PUT, DELETE)"""
    db = get_db()

    try:
        if request.method == "GET":
            # Get log entry details
            log_entry = db.execute(
                """
                SELECT * FROM log_entries_with_details WHERE id = ?
            """,
                (log_id,),
            ).fetchone()

            if not log_entry:
                return (
                    jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)),
                    HTTP_NOT_FOUND,
                )

            return jsonify(json_response(dict(log_entry)))

        elif request.method == "PUT":
            # Update log entry
            data = safe_get_json()
            if data is None:
                return (
                    jsonify(json_response(None, "Invalid JSON", status=HTTP_BAD_REQUEST)),
                    HTTP_BAD_REQUEST,
                )

            # Validate required fields
            date = (data.get("date") or "").strip()
            item_type = (data.get("item_type") or "").strip()
            item_id = data.get("item_id")
            quantity_grams = safe_float(data.get("quantity_grams", 0))
            meal_time = (data.get("meal_time") or "").strip()

            if not date or not item_type or not item_id or quantity_grams <= 0 or not meal_time:
                return (
                    jsonify(
                        json_response(
                            None,
                            ERROR_MESSAGES["validation_error"],
                            status=HTTP_BAD_REQUEST,
                            errors=["All fields are required"],
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Check if log entry exists
            existing = db.execute("SELECT id FROM log_entries WHERE id = ?", (log_id,)).fetchone()
            if not existing:
                return (
                    jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)),
                    HTTP_NOT_FOUND,
                )

            # Validate item exists
            if item_type == "product":
                item_exists = db.execute(
                    "SELECT id FROM products WHERE id = ?", (item_id,)
                ).fetchone()
            elif item_type == "dish":
                item_exists = db.execute(
                    "SELECT id FROM dishes WHERE id = ?", (item_id,)
                ).fetchone()
            else:
                return (
                    jsonify(
                        json_response(
                            None,
                            ERROR_MESSAGES["validation_error"],
                            status=HTTP_BAD_REQUEST,
                            errors=["Invalid item type"],
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            if not item_exists:
                return (
                    jsonify(
                        json_response(
                            None,
                            ERROR_MESSAGES["validation_error"],
                            status=HTTP_BAD_REQUEST,
                            errors=[f"{item_type.title()} not found"],
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Update log entry
            cursor = db.execute(
                """
                UPDATE log_entries
                SET date = ?, item_type = ?, item_id = ?, quantity_grams = ?,
                    meal_time = ?, notes = ?
                WHERE id = ?
            """,
                (
                    date,
                    item_type,
                    item_id,
                    quantity_grams,
                    meal_time,
                    (data.get("notes") or "").strip(),
                    log_id,
                ),
            )

            db.commit()

            # Return updated log entry
            updated_entry = db.execute(
                """
                SELECT * FROM log_entries_with_details WHERE id = ?
            """,
                (log_id,),
            ).fetchone()

            return jsonify(json_response(dict(updated_entry), "Log entry updated successfully!"))

        elif request.method == "DELETE":
            cursor = db.execute("DELETE FROM log_entries WHERE id = ?", (log_id,))
            if cursor.rowcount == 0:
                return (
                    jsonify(json_response(None, ERROR_MESSAGES["not_found"], HTTP_NOT_FOUND)),
                    HTTP_NOT_FOUND,
                )

            db.commit()
            return jsonify(json_response({}, SUCCESS_MESSAGES["log_deleted"]))

    except Exception as e:
        current_app.logger.error(f"Log detail API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        db.close()
