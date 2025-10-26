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
