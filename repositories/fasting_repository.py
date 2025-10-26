"""
Fasting Repository - Data access layer for fasting sessions.

Implements Repository Pattern for intermittent fasting operations.
"""

import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from repositories.base_repository import BaseRepository


class FastingRepository(BaseRepository):
    """
    Repository for fasting session data access.

    Handles database operations for intermittent fasting tracking.
    """

    def __init__(self, db_path: str):
        """
        Initialize repository with database path.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def find_all(
        self, user_id: int = 1, status: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Find all fasting sessions with optional filters.

        Args:
            user_id: User ID to filter by
            status: Session status filter ('active', 'completed', 'paused', 'cancelled')
            limit: Maximum number of sessions
            offset: Number of sessions to skip

        Returns:
            List of fasting session dictionaries
        """
        with self._get_connection() as conn:
            if status:
                query = """
                    SELECT * FROM fasting_sessions
                    WHERE user_id = ? AND status = ?
                    ORDER BY start_time DESC
                    LIMIT ? OFFSET ?
                """
                params = (user_id, status, limit, offset)
            else:
                query = """
                    SELECT * FROM fasting_sessions
                    WHERE user_id = ?
                    ORDER BY start_time DESC
                    LIMIT ? OFFSET ?
                """
                params = (user_id, limit, offset)

            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def find_by_id(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Find fasting session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session dictionary or None if not found
        """
        with self._get_connection() as conn:
            query = "SELECT * FROM fasting_sessions WHERE id = ?"
            cursor = conn.execute(query, (session_id,))
            row = cursor.fetchone()

            return dict(row) if row else None

    def get_active_session(self, user_id: int = 1) -> Optional[Dict[str, Any]]:
        """
        Get active fasting session for user.

        Args:
            user_id: User ID

        Returns:
            Active session dictionary or None
        """
        with self._get_connection() as conn:
            query = """
                SELECT * FROM fasting_sessions
                WHERE user_id = ? AND status = 'active'
                ORDER BY start_time DESC
                LIMIT 1
            """
            cursor = conn.execute(query, (user_id,))
            row = cursor.fetchone()

            return dict(row) if row else None

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new fasting session.

        Args:
            data: Session data (start_time, fasting_type, notes, user_id, status)

        Returns:
            Created session dictionary with ID
        """
        with self._get_connection() as conn:
            query = """
                INSERT INTO fasting_sessions
                (user_id, start_time, fasting_type, status, notes)
                VALUES (?, ?, ?, ?, ?)
            """
            params = (
                data.get("user_id", 1),
                data.get("start_time", datetime.now().isoformat()),
                data.get("fasting_type", "16:8"),
                data.get("status", "active"),
                data.get("notes", ""),
            )

            cursor = conn.execute(query, params)
            conn.commit()

            return self.find_by_id(cursor.lastrowid)

    def update(self, session_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update existing fasting session.

        Args:
            session_id: Session ID
            data: Updated session data

        Returns:
            Updated session dictionary or None if not found
        """
        if not self.exists(session_id):
            return None

        with self._get_connection() as conn:
            # Build update query dynamically
            fields = []
            params = []

            if "status" in data:
                fields.append("status = ?")
                params.append(data["status"])
            if "end_time" in data:
                fields.append("end_time = ?")
                params.append(data["end_time"])
            if "duration_hours" in data:
                fields.append("duration_hours = ?")
                params.append(data["duration_hours"])
            if "notes" in data:
                fields.append("notes = ?")
                params.append(data["notes"])

            if not fields:
                return self.find_by_id(session_id)

            fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(session_id)

            query = f"UPDATE fasting_sessions SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, params)
            conn.commit()

            return self.find_by_id(session_id)

    def delete(self, session_id: int) -> bool:
        """
        Delete fasting session.

        Args:
            session_id: Session ID

        Returns:
            True if deleted, False if not found
        """
        if not self.exists(session_id):
            return False

        with self._get_connection() as conn:
            query = "DELETE FROM fasting_sessions WHERE id = ?"
            conn.execute(query, (session_id,))
            conn.commit()

        return True

    def get_statistics(self, user_id: int = 1) -> Dict[str, Any]:
        """
        Get fasting statistics for user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with statistics (total sessions, avg duration, etc.)
        """
        with self._get_connection() as conn:
            query = """
                SELECT
                    COUNT(*) as total_sessions,
                    COALESCE(AVG(CASE WHEN status = 'completed' THEN duration_hours END), 0) as avg_duration,
                    COALESCE(MAX(duration_hours), 0) as longest_session,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_sessions
                FROM fasting_sessions
                WHERE user_id = ?
            """
            cursor = conn.execute(query, (user_id,))
            row = cursor.fetchone()

            if not row:
                return {
                    "total_sessions": 0,
                    "avg_duration": 0,
                    "longest_session": 0,
                    "completed_sessions": 0,
                    "active_sessions": 0,
                }

            return dict(row)

    def count(self, user_id: int = 1, status: Optional[str] = None) -> int:
        """
        Count fasting sessions.

        Args:
            user_id: User ID
            status: Optional status filter

        Returns:
            Number of sessions
        """
        with self._get_connection() as conn:
            if status:
                query = "SELECT COUNT(*) FROM fasting_sessions WHERE user_id = ? AND status = ?"
                params = (user_id, status)
            else:
                query = "SELECT COUNT(*) FROM fasting_sessions WHERE user_id = ?"
                params = (user_id,)

            cursor = conn.execute(query, params)
            return cursor.fetchone()[0]

    # === Goal Operations ===

    def find_goals(
        self, user_id: int = 1, status: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Find fasting goals for user.

        Args:
            user_id: User ID
            status: Optional status filter ('active', 'completed', 'paused')
            limit: Maximum number of goals

        Returns:
            List of goal dictionaries
        """
        with self._get_connection() as conn:
            if status:
                query = """
                    SELECT * FROM fasting_goals
                    WHERE user_id = ? AND status = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """
                params = (user_id, status, limit)
            else:
                query = """
                    SELECT * FROM fasting_goals
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """
                params = (user_id, limit)

            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def create_goal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new fasting goal.

        Args:
            data: Goal data dictionary

        Returns:
            Created goal dictionary with ID
        """
        with self._get_connection() as conn:
            query = """
                INSERT INTO fasting_goals
                (user_id, goal_type, target_value, period_start, period_end, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (
                data.get("user_id", 1),
                data["goal_type"],
                data["target_value"],
                data["period_start"],
                data["period_end"],
                data.get("status", "active"),
            )

            cursor = conn.execute(query, params)
            conn.commit()

            # Fetch and return created goal
            query = "SELECT * FROM fasting_goals WHERE id = ?"
            cursor = conn.execute(query, (cursor.lastrowid,))
            row = cursor.fetchone()
            return dict(row) if row else {}

    def update_goal(self, goal_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update fasting goal.

        Args:
            goal_id: Goal ID
            data: Updated goal data

        Returns:
            Updated goal dictionary or None if not found
        """
        with self._get_connection() as conn:
            # Check if goal exists
            query = "SELECT id FROM fasting_goals WHERE id = ?"
            cursor = conn.execute(query, (goal_id,))
            if not cursor.fetchone():
                return None

            # Build update query
            fields = []
            params = []

            if "current_value" in data:
                fields.append("current_value = ?")
                params.append(data["current_value"])
            if "status" in data:
                fields.append("status = ?")
                params.append(data["status"])
            if "target_value" in data:
                fields.append("target_value = ?")
                params.append(data["target_value"])

            if not fields:
                # Return existing goal if no updates
                query = "SELECT * FROM fasting_goals WHERE id = ?"
                cursor = conn.execute(query, (goal_id,))
                row = cursor.fetchone()
                return dict(row) if row else None

            fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(goal_id)

            query = f"UPDATE fasting_goals SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, params)
            conn.commit()

            # Fetch and return updated goal
            query = "SELECT * FROM fasting_goals WHERE id = ?"
            cursor = conn.execute(query, (goal_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    # === Settings Operations ===

    def find_settings(self, user_id: int = 1) -> Optional[Dict[str, Any]]:
        """
        Find fasting settings for user.

        Args:
            user_id: User ID

        Returns:
            Settings dictionary or None if not found
        """
        with self._get_connection() as conn:
            query = "SELECT * FROM fasting_settings WHERE user_id = ? LIMIT 1"
            cursor = conn.execute(query, (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def create_settings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create fasting settings for user.

        Args:
            data: Settings data dictionary

        Returns:
            Created settings dictionary with ID
        """
        with self._get_connection() as conn:
            query = """
                INSERT INTO fasting_settings
                (user_id, fasting_goal, preferred_start_time, enable_reminders,
                 enable_notifications, default_notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (
                data.get("user_id", 1),
                data.get("fasting_goal", "16:8"),
                data.get("preferred_start_time"),
                data.get("enable_reminders", 0),
                data.get("enable_notifications", 0),
                data.get("default_notes", ""),
            )

            conn.execute(query, params)
            conn.commit()

            return self.find_settings(data.get("user_id", 1))

    def update_settings(self, user_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update fasting settings for user.

        Args:
            user_id: User ID
            data: Updated settings data

        Returns:
            Updated settings dictionary or None if not found
        """
        with self._get_connection() as conn:
            # Check if settings exist
            existing = self.find_settings(user_id)
            if not existing:
                return None

            # Build update query
            fields = []
            params = []

            if "fasting_goal" in data:
                fields.append("fasting_goal = ?")
                params.append(data["fasting_goal"])
            if "preferred_start_time" in data:
                fields.append("preferred_start_time = ?")
                params.append(data["preferred_start_time"])
            if "enable_reminders" in data:
                fields.append("enable_reminders = ?")
                params.append(data["enable_reminders"])
            if "enable_notifications" in data:
                fields.append("enable_notifications = ?")
                params.append(data["enable_notifications"])
            if "default_notes" in data:
                fields.append("default_notes = ?")
                params.append(data["default_notes"])

            if not fields:
                return existing

            fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(user_id)

            query = f"UPDATE fasting_settings SET {', '.join(fields)} WHERE user_id = ?"
            conn.execute(query, params)
            conn.commit()

            return self.find_settings(user_id)

    # === Advanced Statistics ===

    def get_stats_with_streak(self, user_id: int = 1, days: int = 30) -> Dict[str, Any]:
        """
        Get fasting statistics including current streak calculation.

        Args:
            user_id: User ID
            days: Number of days to include in statistics

        Returns:
            Dictionary with statistics including current streak
        """
        with self._get_connection() as conn:
            # Get basic stats
            basic_stats = self.get_statistics(user_id)

            # Calculate current streak (consecutive days with completed sessions)
            streak_query = """
                WITH RECURSIVE dates AS (
                    SELECT DATE('now') as date
                    UNION ALL
                    SELECT DATE(date, '-1 day')
                    FROM dates
                    WHERE date > DATE('now', '-30 day')
                ),
                daily_sessions AS (
                    SELECT
                        DATE(start_time) as session_date,
                        COUNT(*) as sessions
                    FROM fasting_sessions
                    WHERE user_id = ? AND status = 'completed'
                    GROUP BY DATE(start_time)
                )
                SELECT
                    d.date,
                    COALESCE(ds.sessions, 0) as sessions
                FROM dates d
                LEFT JOIN daily_sessions ds ON d.date = ds.session_date
                ORDER BY d.date DESC
            """
            cursor = conn.execute(streak_query, (user_id,))
            daily_data = cursor.fetchall()

            # Calculate streak from most recent day backwards
            current_streak = 0
            for row in daily_data:
                if row[1] > 0:  # Has sessions
                    current_streak += 1
                else:
                    break

            # Get longest streak
            longest_streak_query = """
                WITH daily_sessions AS (
                    SELECT
                        DATE(start_time) as session_date
                    FROM fasting_sessions
                    WHERE user_id = ? AND status = 'completed'
                    GROUP BY DATE(start_time)
                    ORDER BY DATE(start_time)
                )
                SELECT MAX(streak_length) as longest_streak
                FROM (
                    SELECT
                        session_date,
                        (julianday(session_date) -
                         ROW_NUMBER() OVER (ORDER BY session_date)) as streak_group
                    FROM daily_sessions
                )
                GROUP BY streak_group
            """
            cursor = conn.execute(longest_streak_query, (user_id,))
            result = cursor.fetchone()
            longest_streak = result[0] if result and result[0] else 0

            return {
                **basic_stats,
                "current_streak": current_streak,
                "longest_streak": longest_streak,
            }
