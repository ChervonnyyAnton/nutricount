#!/usr/bin/env python3
"""
Nutrition Tracker v2.0 - WCAG 2.2 Compliant Web Application
Local nutrition tracking application optimized for Raspberry Pi Zero 2W
"""

import hashlib
import hmac
import os
import sqlite3
import time
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import BadRequest

# Import our modular components
from src.advanced_logging import structured_logger
from src.config import Config
from src.constants import ERROR_MESSAGES
from src.security import SecurityHeaders
from src.ssl_config import setup_security_middleware
from src.utils import json_response

# Import route blueprints
from routes.auth import auth_bp
from routes.dishes import dishes_bp
from routes.fasting import fasting_bp
from routes.log import log_bp
from routes.metrics import metrics_bp
from routes.products import products_bp
from routes.profile import profile_bp
from routes.stats import stats_bp
from routes.system import system_bp


# Cache for compatibility with tests (actual caching now in stats blueprint)
_cache = {}


def safe_get_json():
    """Safely get JSON data from request, handling invalid JSON gracefully"""
    try:
        return request.get_json() or {}
    except BadRequest:
        return None


# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")
app.config.from_object(Config)

# Enable CORS for API endpoints
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Setup security middleware
setup_security_middleware(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dishes_bp)
app.register_blueprint(fasting_bp)
app.register_blueprint(log_bp)
app.register_blueprint(metrics_bp)
app.register_blueprint(products_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(stats_bp)
app.register_blueprint(system_bp)


# Add security headers to all responses
@app.after_request
def add_security_headers(response):
    return SecurityHeaders.add_security_headers(response)


# Add request logging
@app.before_request
def log_request_start():
    request.start_time = time.time()


@app.after_request
def log_request_end(response):
    duration = time.time() - getattr(request, "start_time", time.time())

    # Log access event
    structured_logger.log_access_event(
        method=request.method,
        path=request.path,
        status_code=response.status_code,
        duration=duration,
        ip=request.remote_addr,
    )

    return response


# ============================================
# Database Connection Management
# ============================================


def get_db():
    """Get database connection with proper configuration"""
    db = sqlite3.connect(app.config["DATABASE"])
    db.row_factory = sqlite3.Row

    # Enable WAL mode for better concurrency (only for file databases)
    if app.config["DATABASE"] != ":memory:":
        db.execute("PRAGMA journal_mode = WAL")
        db.execute("PRAGMA synchronous = NORMAL")

    db.execute("PRAGMA foreign_keys = ON")

    return db


def init_db():
    """Initialize database with schema v2"""
    try:
        with open("schema_v2.sql", "r") as f:
            schema = f.read()

        db = get_db()
        db.executescript(schema)
        db.commit()
        db.close()

        print("✅ Database initialized successfully")

        # Load sample data only for non-testing environments
        if not app.config.get("TESTING", False) and app.config["DATABASE"] != ":memory:":
            db = get_db()
            sample_products = [
                ("Chicken Breast", 165, 31.0, 3.6, 0.0, 0.0, "meat", 0, "raw"),
                ("Salmon", 208, 25.4, 12.4, 0.0, 0.0, "fish", 0, "raw"),
                ("Eggs", 155, 13.0, 11.0, 1.1, 0.0, "dairy", 0, "raw"),
                ("Avocado", 160, 2.0, 14.7, 8.5, 6.7, "fruits", 15, "raw"),
                ("Broccoli", 34, 2.8, 0.4, 6.6, 2.6, "vegetables", 15, "raw"),
                ("Almonds", 579, 21.2, 49.9, 21.6, 12.5, "nuts_seeds", 15, "minimal"),
                ("Spinach", 23, 2.9, 0.4, 3.6, 2.2, "leafy_vegetables", 15, "raw"),
                ("Blueberries", 57, 0.7, 0.3, 14.5, 2.4, "berries", 25, "raw"),
                ("Sweet Potato", 86, 1.6, 0.1, 20.1, 3.0, "root_vegetables", 70, "minimal"),
            ]

            for product in sample_products:
                db.execute(
                    "INSERT OR IGNORE INTO products (name, calories_per_100g, protein_per_100g, fat_per_100g, carbs_per_100g, fiber_per_100g, category, glycemic_index, processing_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    product,
                )

            db.commit()
            db.close()

            print(f"📊 Sample products loaded: {len(sample_products)}")

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise


# ============================================
# Main Routes
# ============================================


@app.route("/")
def index():
    """Main application page"""
    return render_template("index.html")


@app.route("/health")
def health():
    """Health check endpoint"""
    try:
        db = get_db()
        db.execute("SELECT 1").fetchone()
        db.close()

        return jsonify(
            {
                "status": "healthy",
                "version": Config.VERSION,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "database": "ok",
            }
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "version": Config.VERSION,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error": str(e),
                }
            ),
            500,
        )


# ============================================
# PWA Support
# ============================================


@app.route("/manifest.json")
def manifest():
    """PWA manifest file"""
    return send_from_directory(app.root_path, "manifest.json")


@app.route("/sw.js")
def service_worker():
    """Service worker for offline support"""
    return send_from_directory("static", "sw.js")


# Products API routes moved to routes/products.py blueprint


# ============================================
# Statistics API


# ============================================
# Telegram Web App Integration
# ============================================


def verify_telegram_webapp_data(init_data: str, bot_token: str) -> bool:
    """Verify Telegram Web App initialization data"""
    try:
        # Parse the data
        parsed_data = {}
        for item in init_data.split("&"):
            key, value = item.split("=", 1)
            parsed_data[key] = value

        # Extract hash
        received_hash = parsed_data.pop("hash", "")

        # Create data string for verification
        data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(parsed_data.items())])

        # Create secret key
        secret_key = hmac.new(
            key="WebAppData".encode(), msg=bot_token.encode(), digestmod=hashlib.sha256
        ).digest()

        # Calculate hash
        calculated_hash = hmac.new(
            key=secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256
        ).hexdigest()

        return calculated_hash == received_hash

    except Exception:
        return False


# ============================================
# Error Handlers
# ============================================


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.path.startswith("/api/"):
        return jsonify(json_response(None, "Endpoint not found", 404)), 404
    return render_template("index.html")  # SPA fallback


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    app.logger.error(f"Internal error: {error}")
    if request.path.startswith("/api/"):
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    return render_template("index.html")


# ============================================
# Application Initialization
# ============================================


def initialize_app():
    """Initialize application on first request"""
    try:
        # Create directories
        os.makedirs("data", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        os.makedirs("backups", exist_ok=True)

        # Initialize database if it doesn't exist
        if not os.path.exists(Config.DATABASE):
            init_db()
            app.logger.info("Database initialized")

        app.logger.info(f"🥗 Nutrition Tracker v{Config.VERSION} started")

    except Exception as e:
        app.logger.error(f"Failed to initialize app: {e}")
        raise


# Initialize app when Flask starts
with app.app_context():
    initialize_app()


# ============================================
# Main Entry Point
# ============================================

if __name__ == "__main__":
    # Initialize database if running directly
    if not os.path.exists(Config.DATABASE):
        init_db()

    # Run development server
    port = int(os.environ.get("FLASK_RUN_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=Config.is_development())
