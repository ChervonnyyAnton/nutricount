"""
Authentication and Authorization Module
Handles JWT tokens, user authentication, and security
"""

import jwt
import bcrypt
import secrets
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any
from functools import wraps
from flask import request, jsonify
from .cache_manager import cache_manager

logger = logging.getLogger(__name__)


class SecurityManager:
    """Manages authentication and authorization"""

    def __init__(self, secret_key: str = None, algorithm: str = "HS256"):
        self.secret_key = secret_key or self._generate_secret_key()
        self.algorithm = algorithm
        self.token_expiry = timedelta(hours=24)  # 24 hours
        self.refresh_token_expiry = timedelta(days=30)  # 30 days

    def _generate_secret_key(self) -> str:
        """Generate a secure secret key"""
        return secrets.token_urlsafe(32)

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
            return hashed.decode("utf-8")
        except Exception as e:
            logger.error(f"Password hashing error: {e}")
            raise

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False

    def generate_token(self, user_id: int, username: str, is_refresh: bool = False) -> str:
        """Generate JWT token"""
        try:
            expiry = self.refresh_token_expiry if is_refresh else self.token_expiry
            payload = {
                "user_id": user_id,
                "username": username,
                "exp": datetime.now(timezone.utc) + expiry,
                "iat": datetime.now(timezone.utc),
                "type": "refresh" if is_refresh else "access",
            }

            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token
        except Exception as e:
            logger.error(f"Token generation error: {e}")
            raise

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Generate new access token from refresh token"""
        payload = self.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None

        try:
            new_access_token = self.generate_token(
                payload["user_id"], payload["username"], is_refresh=False
            )
            new_refresh_token = self.generate_token(
                payload["user_id"], payload["username"], is_refresh=True
            )

            return {"access_token": new_access_token, "refresh_token": new_refresh_token}
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return None

    def extract_token_from_header(self, auth_header: str) -> Optional[str]:
        """Extract token from Authorization header"""
        if not auth_header:
            return None

        try:
            scheme, token = auth_header.split(" ", 1)
            if scheme.lower() != "bearer":
                return None
            return token
        except ValueError:
            return None


# Global security manager instance
security_manager = SecurityManager()


def require_auth(f):
    """Decorator to require authentication"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        token = security_manager.extract_token_from_header(auth_header)

        if not token:
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": "Authentication required",
                        "message": "Please provide a valid token",
                    }
                ),
                401,
            )

        payload = security_manager.verify_token(token)
        if not payload:
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": "Invalid token",
                        "message": "Token is expired or invalid",
                    }
                ),
                401,
            )

        if payload.get("type") != "access":
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": "Invalid token type",
                        "message": "Access token required",
                    }
                ),
                401,
            )

        # Add user info to request context
        request.current_user = {
            "user_id": payload["user_id"],
            "username": payload["username"],
            "is_admin": payload.get("is_admin", False),
        }

        return f(*args, **kwargs)

    return decorated_function


def require_admin(f):
    """Decorator to require admin privileges"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For now, we'll implement a simple admin check
        # In a real application, this would check user roles/permissions
        auth_header = request.headers.get("Authorization")
        token = security_manager.extract_token_from_header(auth_header)

        if not token:
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": "Authentication required",
                        "message": "Please provide a valid token",
                    }
                ),
                401,
            )

        payload = security_manager.verify_token(token)
        if not payload:
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": "Invalid token",
                        "message": "Token is expired or invalid",
                    }
                ),
                401,
            )

        # Simple admin check - in production, this would be more sophisticated
        if payload.get("username") != "admin":
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": "Admin privileges required",
                        "message": "This operation requires admin access",
                    }
                ),
                403,
            )

        request.current_user = {
            "user_id": payload["user_id"],
            "username": payload["username"],
            "is_admin": True,
        }

        return f(*args, **kwargs)

    return decorated_function


class RateLimiter:
    """Simple rate limiter using Redis or in-memory storage"""

    def __init__(self, cache_manager):
        self.cache = cache_manager
        self.default_limits = {
            "api": {"requests": 100, "window": 3600},  # 100 requests per hour
            "auth": {"requests": 10, "window": 3600},  # 10 auth attempts per hour
            "fasting": {"requests": 50, "window": 3600},  # 50 fasting operations per hour
            "admin": {"requests": 200, "window": 3600},  # 200 admin operations per hour
        }

    def is_allowed(self, identifier: str, limit_type: str = "api") -> bool:
        """Check if request is allowed based on rate limits"""
        try:
            limits = self.default_limits.get(limit_type, self.default_limits["api"])
            key = f"rate_limit:{limit_type}:{identifier}"

            # Get current count
            current_count = self.cache.get(key) or 0

            if current_count >= limits["requests"]:
                return False

            # Increment counter
            if current_count == 0:
                # First request in window
                self.cache.set(key, 1, limits["window"])
            else:
                # Increment existing counter
                self.cache.set(key, current_count + 1, limits["window"])

            return True
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return True  # Allow request if rate limiting fails

    def get_remaining_requests(self, identifier: str, limit_type: str = "api") -> int:
        """Get remaining requests for identifier"""
        try:
            limits = self.default_limits.get(limit_type, self.default_limits["api"])
            key = f"rate_limit:{limit_type}:{identifier}"
            current_count = self.cache.get(key) or 0
            return max(0, limits["requests"] - current_count)
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return limits["requests"]


def rate_limit(limit_type: str = "api"):
    """Decorator for rate limiting"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip rate limiting in testing mode
            from flask import current_app

            if current_app.config.get("TESTING", False):
                return f(*args, **kwargs)

            # Get client identifier
            client_ip = request.remote_addr
            user_agent = request.headers.get("User-Agent", "")
            identifier = f"{client_ip}:{hash(user_agent) % 10000}"

            # Check rate limit
            rate_limiter = RateLimiter(cache_manager)
            if not rate_limiter.is_allowed(identifier, limit_type):
                remaining = rate_limiter.get_remaining_requests(identifier, limit_type)
                return (
                    jsonify(
                        {
                            "error": "Rate limit exceeded",
                            "message": "Too many requests. Try again later.",
                            "retry_after": 3600,  # 1 hour
                            "remaining_requests": remaining,
                        }
                    ),
                    429,
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


class SecurityHeaders:
    """Manages security headers"""

    @staticmethod
    def add_security_headers(response):
        """Add security headers to response"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        return response


class InputValidator:
    """Validates and sanitizes input data"""

    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            return ""

        # Remove potentially dangerous characters
        sanitized = value.strip()[:max_length]
        # Remove HTML tags
        import re

        sanitized = re.sub(r"<[^>]+>", "", sanitized)
        return sanitized

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """Validate password strength"""
        result = {"valid": True, "errors": []}

        if len(password) < 8:
            result["valid"] = False
            result["errors"].append("Password must be at least 8 characters long")

        if not re.search(r"[A-Z]", password):
            result["valid"] = False
            result["errors"].append("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", password):
            result["valid"] = False
            result["errors"].append("Password must contain at least one lowercase letter")

        if not re.search(r"\d", password):
            result["valid"] = False
            result["errors"].append("Password must contain at least one number")

        return result

    @staticmethod
    def validate_numeric(
        value: Any, min_val: float = None, max_val: float = None
    ) -> Optional[float]:
        """Validate and convert numeric input"""
        try:
            if isinstance(value, str):
                value = float(value)
            elif not isinstance(value, (int, float)):
                return None

            if min_val is not None and value < min_val:
                return None
            if max_val is not None and value > max_val:
                return None

            return value
        except (ValueError, TypeError):
            return None


class AuditLogger:
    """Logs security-related events"""

    def __init__(self):
        self.logger = logging.getLogger("security_audit")
        handler = logging.FileHandler("logs/security_audit.log")
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_auth_attempt(self, username: str, success: bool, ip: str, user_agent: str):
        """Log authentication attempt"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(
            f"AUTH_ATTEMPT - User: {username}, Status: {status}, "
            f"IP: {ip}, User-Agent: {user_agent}"
        )

    def log_token_usage(self, user_id: int, action: str, ip: str):
        """Log token usage"""
        self.logger.info(f"TOKEN_USAGE - User: {user_id}, Action: {action}, IP: {ip}")

    def log_rate_limit_hit(self, identifier: str, limit_type: str, ip: str):
        """Log rate limit hit"""
        self.logger.warning(
            f"RATE_LIMIT_HIT - Identifier: {identifier}, Type: {limit_type}, IP: {ip}"
        )

    def log_admin_action(self, user_id: int, action: str, ip: str):
        """Log admin action"""
        self.logger.info(f"ADMIN_ACTION - User: {user_id}, Action: {action}, IP: {ip}")


# Global instances
audit_logger = AuditLogger()
input_validator = InputValidator()
