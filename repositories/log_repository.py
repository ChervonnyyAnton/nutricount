"""
Log Repository - Data access layer for log entries.

Implements Repository Pattern for daily food log operations.
"""

import sqlite3
from typing import Any, Dict, List, Optional

from repositories.base_repository import BaseRepository


class LogRepository(BaseRepository):
    """
    Repository for log entry data access.

    Handles database operations for daily food log entries.
    """

    def __init__(self, db_path: str):
        """
        Initialize repository with database path.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

    def find_all(
        self, date_filter: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Find all log entries with optional date filter and pagination.

        Args:
            date_filter: Filter by specific date (YYYY-MM-DD)
            limit: Maximum number of entries to return
            offset: Number of entries to skip

        Returns:
            List of log entry dictionaries with nutrition details
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            if date_filter:
                query = """
                    SELECT * FROM log_entries_with_details
                    WHERE date = ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """
                params = (date_filter, limit, offset)
            else:
                query = """
                    SELECT * FROM log_entries_with_details
                    ORDER BY date DESC, created_at DESC
                    LIMIT ? OFFSET ?
                """
                params = (limit, offset)

            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def find_by_id(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """
        Find log entry by ID.

        Args:
            entry_id: Log entry ID

        Returns:
            Log entry dictionary or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            query = """
                SELECT * FROM log_entries_with_details
                WHERE id = ?
            """
            cursor = conn.execute(query, (entry_id,))
            row = cursor.fetchone()

            return dict(row) if row else None

    def find_by_date(self, date: str) -> List[Dict[str, Any]]:
        """
        Find all log entries for a specific date.

        Args:
            date: Date string (YYYY-MM-DD)

        Returns:
            List of log entry dictionaries
        """
        return self.find_all(date_filter=date)

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new log entry.

        Args:
            data: Log entry data (date, item_type, item_id, quantity_grams, meal_time)

        Returns:
            Created log entry dictionary with ID
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            query = """
                INSERT INTO log_entries (date, item_type, item_id, quantity_grams, meal_time)
                VALUES (?, ?, ?, ?, ?)
            """
            params = (
                data["date"],
                data["item_type"],
                data["item_id"],
                data["quantity_grams"],
                data.get("meal_time", "other"),
            )

            cursor = conn.execute(query, params)
            conn.commit()

            # Fetch the created entry with all details
            return self.find_by_id(cursor.lastrowid)

    def update(self, entry_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update existing log entry.

        Args:
            entry_id: Log entry ID
            data: Updated log entry data

        Returns:
            Updated log entry dictionary or None if not found
        """
        if not self.exists(entry_id):
            return None

        with sqlite3.connect(self.db_path) as conn:
            # Build update query dynamically based on provided fields
            fields = []
            params = []

            if "date" in data:
                fields.append("date = ?")
                params.append(data["date"])
            if "item_type" in data:
                fields.append("item_type = ?")
                params.append(data["item_type"])
            if "item_id" in data:
                fields.append("item_id = ?")
                params.append(data["item_id"])
            if "quantity_grams" in data:
                fields.append("quantity_grams = ?")
                params.append(data["quantity_grams"])
            if "meal_time" in data:
                fields.append("meal_time = ?")
                params.append(data["meal_time"])

            if not fields:
                # No fields to update
                return self.find_by_id(entry_id)

            params.append(entry_id)
            query = f"UPDATE log_entries SET {', '.join(fields)} WHERE id = ?"

            conn.execute(query, params)
            conn.commit()

            return self.find_by_id(entry_id)

    def delete(self, entry_id: int) -> bool:
        """
        Delete log entry by ID.

        Args:
            entry_id: Log entry ID

        Returns:
            True if deleted, False if not found
        """
        if not self.exists(entry_id):
            return False

        with sqlite3.connect(self.db_path) as conn:
            query = "DELETE FROM log_entries WHERE id = ?"
            conn.execute(query, (entry_id,))
            conn.commit()

        return True

    def get_daily_totals(self, date: str) -> Dict[str, float]:
        """
        Calculate daily nutrition totals for a specific date.

        Args:
            date: Date string (YYYY-MM-DD)

        Returns:
            Dictionary with total calories, protein, fat, carbs, fiber
        """
        entries = self.find_by_date(date)

        totals = {
            "calories": 0.0,
            "protein": 0.0,
            "fat": 0.0,
            "carbs": 0.0,
            "fiber": 0.0,
        }

        for entry in entries:
            quantity_factor = entry["quantity_grams"] / 100.0

            if entry["item_type"] == "product":
                totals["calories"] += (entry["calories_per_100g"] or 0) * quantity_factor
                totals["protein"] += (entry["protein_per_100g"] or 0) * quantity_factor
                totals["fat"] += (entry["fat_per_100g"] or 0) * quantity_factor
                totals["carbs"] += (entry["carbs_per_100g"] or 0) * quantity_factor
                totals["fiber"] += (entry["fiber_per_100g"] or 0) * quantity_factor
            elif entry["item_type"] == "dish":
                totals["calories"] += entry["calculated_calories"] or 0
                totals["protein"] += (entry["dish_protein_per_100g"] or 0) * quantity_factor
                totals["fat"] += (entry["dish_fat_per_100g"] or 0) * quantity_factor
                totals["carbs"] += (entry["dish_carbs_per_100g"] or 0) * quantity_factor
                totals["fiber"] += (entry["dish_fiber_per_100g"] or 0) * quantity_factor

        return totals

    def count(self, date_filter: Optional[str] = None) -> int:
        """
        Count log entries with optional date filter.

        Args:
            date_filter: Filter by specific date

        Returns:
            Number of log entries
        """
        with sqlite3.connect(self.db_path) as conn:
            if date_filter:
                query = "SELECT COUNT(*) FROM log_entries WHERE date = ?"
                params = (date_filter,)
            else:
                query = "SELECT COUNT(*) FROM log_entries"
                params = ()

            cursor = conn.execute(query, params)
            return cursor.fetchone()[0]

    def verify_item_exists(self, item_type: str, item_id: int) -> bool:
        """
        Verify that a product or dish exists.

        Args:
            item_type: 'product' or 'dish'
            item_id: Product or dish ID

        Returns:
            True if item exists, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            if item_type == "product":
                table = "products"
            elif item_type == "dish":
                table = "dishes"
            else:
                return False

            query = f"SELECT COUNT(*) FROM {table} WHERE id = ?"
            cursor = conn.execute(query, (item_id,))
            count = cursor.fetchone()[0]

            return count > 0
