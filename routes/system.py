"""
System and maintenance routes for Nutricount application.
Handles system status, backups, restore, maintenance, and data export.
"""

import glob
import os
import shutil
import time
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request

from src.config import Config
from src.constants import ERROR_MESSAGES, HTTP_BAD_REQUEST
from src.security import rate_limit, require_admin
from src.utils import get_database_stats, json_response

# Create system blueprint
system_bp = Blueprint("system", __name__, url_prefix="/api")


@system_bp.route("/system/status")
def system_status_api():
    """System status and statistics"""
    try:
        import psutil

        db_stats = get_database_stats()

        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        system_info = {
            "application": {
                "name": Config.APP_NAME,
                "version": Config.VERSION,
                "environment": Config.FLASK_ENV,
                "uptime": "N/A",  # Would need startup time tracking
            },
            "database": {
                "type": "SQLite",
                "size_mb": (
                    round(os.path.getsize(Config.DATABASE) / (1024 * 1024), 2)
                    if os.path.exists(Config.DATABASE)
                    else 0
                ),
                "products_count": db_stats.get("products", 0),
                "dishes_count": db_stats.get("dishes", 0),
                "log_entries_count": db_stats.get("log_entries", 0),
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": round(memory.used / (1024 * 1024), 2),
                "disk_percent": round((disk.used / disk.total) * 100, 2),
                "disk_free_gb": round(disk.free / (1024 * 1024 * 1024), 2),
            },
        }

        return jsonify(json_response(system_info))

    except Exception as e:
        current_app.logger.error(f"System status API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@system_bp.route("/system/backup", methods=["POST"])
@require_admin
@rate_limit("admin")
def system_backup_api():
    """Create a backup of the database"""
    try:
        # Create backups directory if it doesn't exist
        os.makedirs("backups", exist_ok=True)

        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"nutrition_backup_{timestamp}.db"
        backup_path = os.path.join("backups", backup_filename)

        # Copy database file
        shutil.copy2(Config.DATABASE, backup_path)

        # Get backup size
        backup_size_mb = round(os.path.getsize(backup_path) / (1024 * 1024), 2)

        return jsonify(
            json_response(
                {
                    "backup_id": backup_filename,
                    "backup_path": backup_path,
                    "backup_size_mb": backup_size_mb,
                    "created_at": datetime.now().isoformat(),
                    "download_url": f"/api/system/backup/{backup_filename}",
                },
                "Backup created successfully!",
            )
        )

    except Exception as e:
        current_app.logger.error(f"Backup API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@system_bp.route("/system/restore", methods=["POST"])
def system_restore_api():
    """Restore database from backup"""
    try:
        if "backup_file" not in request.files:
            return (
                jsonify(
                    json_response(
                        None,
                        ERROR_MESSAGES["validation_error"],
                        status=HTTP_BAD_REQUEST,
                        errors=["No backup file provided"],
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        backup_file = request.files["backup_file"]
        if backup_file.filename == "":
            return (
                jsonify(
                    json_response(
                        None,
                        ERROR_MESSAGES["validation_error"],
                        status=HTTP_BAD_REQUEST,
                        errors=["No file selected"],
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        if not backup_file.filename.endswith(".db"):
            return (
                jsonify(
                    json_response(
                        None,
                        ERROR_MESSAGES["validation_error"],
                        status=HTTP_BAD_REQUEST,
                        errors=["Invalid file type. Please upload a .db file"],
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        # Create backup of current database before restore
        os.makedirs("backups", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_backup = f"backups/pre_restore_backup_{timestamp}.db"
        shutil.copy2(Config.DATABASE, current_backup)

        # Save uploaded file
        backup_file.save(Config.DATABASE)

        return jsonify(
            json_response(
                {
                    "restored_file": backup_file.filename,
                    "current_backup": current_backup,
                    "restored_at": datetime.now().isoformat(),
                },
                "Database restored successfully! Current database backed up as safety measure.",
            )
        )

    except Exception as e:
        current_app.logger.error(f"Restore API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@system_bp.route("/maintenance/vacuum", methods=["POST"])
def maintenance_vacuum_api():
    """Optimize database by running VACUUM and ANALYZE"""
    try:
        # Import get_db from app module
        from app import get_db

        db = get_db()

        # Get database size before optimization
        size_before = os.path.getsize(Config.DATABASE) if os.path.exists(Config.DATABASE) else 0

        # Run ANALYZE first to update statistics
        db.execute("ANALYZE")
        db.commit()

        # Run VACUUM to optimize database
        db.execute("VACUUM")
        db.commit()

        # Get database size after optimization
        size_after = os.path.getsize(Config.DATABASE)

        # Calculate space saved
        space_saved = size_before - size_after
        space_saved_mb = round(space_saved / (1024 * 1024), 2)

        # Get database statistics
        stats = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_count = len(stats)

        db.close()

        message = f"Database optimized! Size: {round(size_after / (1024 * 1024), 2)} MB"
        if space_saved_mb > 0:
            message += f" (saved {space_saved_mb} MB)"
        else:
            message += " (no fragmentation found)"

        return jsonify(
            json_response(
                {
                    "space_saved_mb": space_saved_mb,
                    "size_before_mb": round(size_before / (1024 * 1024), 2),
                    "size_after_mb": round(size_after / (1024 * 1024), 2),
                    "table_count": table_count,
                    "optimization_type": "VACUUM + ANALYZE",
                },
                message,
            )
        )

    except Exception as e:
        current_app.logger.error(f"Vacuum API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@system_bp.route("/maintenance/cleanup", methods=["POST"])
def maintenance_cleanup_api():
    """Clean up temporary files, logs, and cache"""
    try:
        files_cleaned = 0
        space_freed = 0
        cleanup_details = []

        # Clean up log files older than 7 days
        log_patterns = ["logs/*.log", "logs/*.txt", "*.log"]
        for pattern in log_patterns:
            for file_path in glob.glob(pattern):
                try:
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        # Check if file is older than 7 days
                        file_age = time.time() - os.path.getmtime(file_path)
                        if file_age > (7 * 24 * 60 * 60):  # 7 days in seconds
                            os.remove(file_path)
                            files_cleaned += 1
                            space_freed += file_size
                            cleanup_details.append(
                                f"Removed old log: {os.path.basename(file_path)}"
                            )
                except Exception:
                    continue

        # Clean up Python cache files (but not in venv)
        cache_patterns = ["**/__pycache__", "**/*.pyc", "**/*.pyo"]
        for pattern in cache_patterns:
            for file_path in glob.glob(pattern, recursive=True):
                try:
                    # Skip virtual environment directories
                    if "venv" in file_path or ".venv" in file_path:
                        continue

                    if os.path.exists(file_path):
                        if os.path.isfile(file_path):
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            files_cleaned += 1
                            space_freed += file_size
                        elif os.path.isdir(file_path):
                            # Count files in directory before removal
                            dir_files = sum(len(files) for _, _, files in os.walk(file_path))
                            shutil.rmtree(file_path)
                            files_cleaned += dir_files
                            cleanup_details.append(
                                f"Removed cache directory: {os.path.basename(file_path)}"
                            )
                except Exception:
                    continue

        # Clean up temporary files
        temp_patterns = ["*.tmp", "*.temp", "*.swp", "*.swo"]
        for pattern in temp_patterns:
            for file_path in glob.glob(pattern):
                try:
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        files_cleaned += 1
                        space_freed += file_size
                        cleanup_details.append(f"Removed temp file: {os.path.basename(file_path)}")
                except Exception:
                    continue

        space_freed_mb = round(space_freed / (1024 * 1024), 2)

        message = f"Cleanup completed! Removed {files_cleaned} files"
        if space_freed_mb > 0:
            message += f" (freed {space_freed_mb} MB)"
        else:
            message += " (no files to clean)"

        return jsonify(
            json_response(
                {
                    "files_cleaned": files_cleaned,
                    "space_freed_mb": space_freed_mb,
                    "cleanup_time": datetime.now().isoformat(),
                    "cleanup_details": cleanup_details[:10],  # Limit to first 10 items
                },
                message,
            )
        )

    except Exception as e:
        current_app.logger.error(f"Cleanup API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@system_bp.route("/maintenance/cleanup-test-data", methods=["POST"])
def maintenance_cleanup_test_data_api():
    """Clean up test data (items with TEST prefix)"""
    try:
        # Import get_db from app module
        from app import get_db

        db = get_db()

        # Count test data before deletion (for logging)
        count_products = db.execute(
            "SELECT COUNT(*) FROM products WHERE name LIKE 'TEST%'"
        ).fetchone()[0]
        count_dishes = db.execute("SELECT COUNT(*) FROM dishes WHERE name LIKE 'TEST%'").fetchone()[
            0
        ]
        count_logs = db.execute(
            """
            SELECT COUNT(*) FROM log_entries le
            LEFT JOIN products p ON le.item_type = 'product' AND le.item_id = p.id
            LEFT JOIN dishes d ON le.item_type = 'dish' AND le.item_id = d.id
            WHERE p.name LIKE 'TEST%' OR d.name LIKE 'TEST%'
        """
        ).fetchone()[0]

        # Delete test log entries first (foreign key constraints)
        deleted_logs = db.execute(
            """
            DELETE FROM log_entries WHERE id IN (
                SELECT le.id FROM log_entries le
                LEFT JOIN products p ON le.item_type = 'product' AND le.item_id = p.id
                LEFT JOIN dishes d ON le.item_type = 'dish' AND le.item_id = d.id
                WHERE p.name LIKE 'TEST%' OR d.name LIKE 'TEST%'
            )
        """
        ).rowcount

        # Delete test dishes (and their ingredients)
        deleted_dishes = db.execute("DELETE FROM dishes WHERE name LIKE 'TEST%'").rowcount

        # Delete test products
        deleted_products = db.execute("DELETE FROM products WHERE name LIKE 'TEST%'").rowcount

        db.commit()
        db.close()

        total_deleted = deleted_products + deleted_dishes + deleted_logs

        message = f"Test data cleanup completed! Removed {total_deleted} items"
        if total_deleted == 0:
            message += " (no test data found)"

        current_app.logger.info(
            f"Test data cleanup: {count_products} products, "
            f"{count_dishes} dishes, {count_logs} logs checked"
        )

        return jsonify(
            json_response(
                {
                    "deleted_products": deleted_products,
                    "deleted_dishes": deleted_dishes,
                    "deleted_logs": deleted_logs,
                    "total_deleted": total_deleted,
                    "cleanup_time": datetime.now().isoformat(),
                },
                message,
            )
        )

    except Exception as e:
        current_app.logger.error(f"Test data cleanup API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@system_bp.route("/maintenance/wipe-database", methods=["POST"])
def maintenance_wipe_database_api():
    """Wipe entire database and reset to initial state"""
    try:
        # Import get_db and init_db from app module
        from app import get_db, init_db

        db = get_db()

        # Get counts before deletion
        products_count = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        dishes_count = db.execute("SELECT COUNT(*) FROM dishes").fetchone()[0]
        logs_count = db.execute("SELECT COUNT(*) FROM log_entries").fetchone()[0]

        # Delete all data (respecting foreign key constraints)
        db.execute("DELETE FROM log_entries")
        db.execute("DELETE FROM dish_ingredients")
        db.execute("DELETE FROM dishes")
        db.execute("DELETE FROM products")

        # Reset auto-increment counters
        db.execute("DELETE FROM sqlite_sequence")

        db.commit()
        db.close()

        # Reinitialize database with initial data
        init_db()

        # Get count of initial products after reinitialization
        db = get_db()
        initial_products_count = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        db.close()

        total_deleted = products_count + dishes_count + logs_count

        message = f"Database wiped and reset! Removed {total_deleted} items, loaded {initial_products_count} initial products"
        if total_deleted == 0:
            message += " (database was already empty)"

        return jsonify(
            json_response(
                {
                    "deleted_products": products_count,
                    "deleted_dishes": dishes_count,
                    "deleted_logs": logs_count,
                    "total_deleted": total_deleted,
                    "initial_products_loaded": initial_products_count,
                    "wipe_time": datetime.now().isoformat(),
                },
                message,
            )
        )

    except Exception as e:
        current_app.logger.error(f"Database wipe API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@system_bp.route("/export/all")
def export_all_api():
    """Export all data from the application"""
    try:
        # Import get_db from app module
        from app import get_db

        db = get_db()

        # Get all data
        products = db.execute("SELECT * FROM products ORDER BY name").fetchall()
        dishes = db.execute("SELECT * FROM dishes ORDER BY name").fetchall()
        log_entries = db.execute(
            "SELECT * FROM log_entries_with_details ORDER BY date DESC, created_at DESC"
        ).fetchall()

        # Get dish ingredients
        dish_ingredients = {}
        for dish in dishes:
            ingredients = db.execute(
                """
                SELECT di.*, p.name as product_name
                FROM dish_ingredients di
                JOIN products p ON di.product_id = p.id
                WHERE di.dish_id = ?
                ORDER BY di.id
            """,
                (dish["id"],),
            ).fetchall()
            dish_ingredients[dish["id"]] = [dict(ingredient) for ingredient in ingredients]

        # Prepare export data
        export_data = {
            "export_info": {
                "exported_at": datetime.now().isoformat(),
                "app_version": Config.VERSION,
                "total_products": len(products),
                "total_dishes": len(dishes),
                "total_log_entries": len(log_entries),
            },
            "products": [dict(product) for product in products],
            "dishes": [dict(dish) for dish in dishes],
            "dish_ingredients": dish_ingredients,
            "log_entries": [dict(entry) for entry in log_entries],
        }

        db.close()

        return jsonify(export_data)

    except Exception as e:
        current_app.logger.error(f"Export API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
