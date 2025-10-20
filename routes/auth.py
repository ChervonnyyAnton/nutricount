"""
Authentication routes for Nutricount application.
Handles login, logout, token refresh, and token verification.
"""

from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest

from src.constants import ERROR_MESSAGES, HTTP_BAD_REQUEST, HTTP_OK
from src.monitoring import monitor_http_request
from src.security import audit_logger, rate_limit, require_auth, security_manager
from src.utils import json_response


def safe_get_json():
    """Safely get JSON data from request, handling invalid JSON gracefully"""
    try:
        return request.get_json() or {}
    except BadRequest:
        return None


# Create authentication blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
@monitor_http_request
@rate_limit("auth")
def login_api():
    """User login endpoint"""
    try:
        data = safe_get_json()
        if data is None:
            return (
                jsonify(json_response(None, "Invalid JSON", status=HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )
        username = data.get("username", "").strip()
        password = data.get("password", "")

        if not username or not password:
            return (
                jsonify(
                    json_response(
                        None,
                        ERROR_MESSAGES["validation_error"],
                        HTTP_BAD_REQUEST,
                        errors=["Username and password are required"],
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        # For demo purposes, we'll use a simple hardcoded admin user
        # In production, this would check against a user database
        if username == "admin" and password == "admin123":
            # Generate tokens
            access_token = security_manager.generate_token(1, username, is_refresh=False)
            refresh_token = security_manager.generate_token(1, username, is_refresh=True)

            # Log successful authentication
            audit_logger.log_auth_attempt(
                username, True, request.remote_addr, request.headers.get("User-Agent", "")
            )

            return (
                jsonify(
                    json_response(
                        {
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                            "user": {"id": 1, "username": username, "is_admin": True},
                        },
                        "Login successful",
                        HTTP_OK,
                    )
                ),
                HTTP_OK,
            )
        else:
            # Log failed authentication
            audit_logger.log_auth_attempt(
                username, False, request.remote_addr, request.headers.get("User-Agent", "")
            )

            return jsonify(json_response(None, "Invalid username or password", 401)), 401

    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Login error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@auth_bp.route("/refresh", methods=["POST"])
@monitor_http_request
@rate_limit("auth")
def refresh_token_api():
    """Refresh access token"""
    try:
        # Try to get refresh token from JSON first, then from Authorization header
        data = safe_get_json()
        refresh_token = None

        if data is not None:
            refresh_token = data.get("refresh_token")

        # If not in JSON, try to get from Authorization header
        if not refresh_token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                refresh_token = auth_header[7:]  # Remove 'Bearer ' prefix

        if not refresh_token:
            return (
                jsonify(
                    json_response(
                        None,
                        ERROR_MESSAGES["validation_error"],
                        HTTP_BAD_REQUEST,
                        errors=["Refresh token is required"],
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        # Generate new tokens
        new_tokens = security_manager.refresh_token(refresh_token)

        if new_tokens:
            return (
                jsonify(json_response(new_tokens, "Token refreshed successfully", HTTP_OK)),
                HTTP_OK,
            )
        else:
            return jsonify(json_response(None, "Invalid refresh token", 401)), 401

    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Token refresh error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@auth_bp.route("/verify", methods=["GET"])
@monitor_http_request
@require_auth
def verify_token_api():
    """Verify token validity"""
    try:
        user_info = request.current_user

        return (
            jsonify(json_response({"valid": True, "user": user_info}, "Token is valid", HTTP_OK)),
            HTTP_OK,
        )

    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Token verification error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@auth_bp.route("/logout", methods=["POST"])
@monitor_http_request
@require_auth
def logout_api():
    """User logout endpoint"""
    try:
        user_info = request.current_user

        # Log logout
        audit_logger.log_token_usage(user_info["user_id"], "logout", request.remote_addr)

        return jsonify(json_response(None, "Logout successful", HTTP_OK)), HTTP_OK

    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Logout error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
