"""
Fasting Manager Module
Handles intermittent fasting functionality
"""

import sqlite3
from datetime import datetime, date
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from dataclasses import dataclass
from enum import Enum
from enum import Enum



class FastingType(Enum):
        """Supported fasting types"""
    SIXTEEN_EIGHT = "16:8"  # 16 hours fasting, 8 hours eating
    EIGHTEEN_SIX = "18:6"   # 18 hours fasting, 6 hours eating
        TWENTY_FOUR = "20:4"    # 20 hours fasting, 4 hours eating
    OMAD = "OMAD"           # One Meal A Day
    CUSTOM = "Custom"       # Custom duration



    class FastingStatus(Enum):
    """Fasting session status"""
    ACTIVE = "active"
        COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

    @dataclass


class FastingSession:
        """Fasting session data"""
    id: Optional[int] = None
    user_id: int = 1
        start_time: datetime = None
    end_time: Optional[datetime] = None
    duration_hours: Optional[float] = None
        fasting_type: str = "16:8"
    status: str = "active"
    notes: Optional[str] = None
        created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass


    class FastingGoal:
    """Fasting goal data"""
    id: Optional[int] = None
        user_id: int = 1
    goal_type: str = "daily_hours"
    target_value: float = 16.0
        current_value: float = 0.0
    period_start: date = None
    period_end: date = None
        status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None



    class FastingManager:
    """Manages fasting sessions and goals"""

    def __init__(self, db_path: str):
            self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
            """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
            return conn

    def start_fasting_session(self, fasting_type: str = "16:8", notes: str = None) -> FastingSession:
            """Start a new fasting session"""
        session = FastingSession(
            start_time=datetime.now(),
                fasting_type=fasting_type,
            notes=notes,
            status=FastingStatus.ACTIVE.value
            )

        with self._get_connection() as conn:
                cursor = conn.execute("""
                INSERT INTO fasting_sessions
                (user_id, start_time, fasting_type, status, notes)
                    VALUES (?, ?, ?, ?, ?)
            """, (session.user_id, session.start_time.isoformat(), session.fasting_type,
                  session.status, session.notes))

                session.id = cursor.lastrowid
            conn.commit()

        return session

        def end_fasting_session(self, session_id: int) -> Optional[FastingSession]:
        """End a fasting session"""
        with self._get_connection() as conn:
                # Get current session
            cursor = conn.execute("""
                SELECT * FROM fasting_sessions WHERE id = ? AND status = 'active'
                """, (session_id,))

            row = cursor.fetchone()
                if not row:
                return None

            # Calculate duration
                end_time = datetime.now()
            start_time = datetime.fromisoformat(row['start_time'])
            duration_hours = (end_time - start_time).total_seconds() / 3600

                # Update session
            conn.execute("""
                UPDATE fasting_sessions
                    SET end_time = ?, duration_hours = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (end_time.isoformat(), duration_hours, FastingStatus.COMPLETED.value, session_id))

                conn.commit()

            # Return updated session
                cursor = conn.execute("SELECT * FROM fasting_sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            return self._row_to_session(row)

        def pause_fasting_session(self, session_id: int) -> bool:
        """Pause a fasting session"""
        with self._get_connection() as conn:
                cursor = conn.execute("""
                UPDATE fasting_sessions
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND status = 'active'
            """, (FastingStatus.PAUSED.value, session_id))

            conn.commit()
                return cursor.rowcount > 0

    def resume_fasting_session(self, session_id: int) -> bool:
            """Resume a paused fasting session"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                    UPDATE fasting_sessions
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND status = 'paused'
                """, (FastingStatus.ACTIVE.value, session_id))

            conn.commit()
                return cursor.rowcount > 0

    def cancel_fasting_session(self, session_id: int) -> bool:
            """Cancel a fasting session"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                    UPDATE fasting_sessions
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND status IN ('active', 'paused')
                """, (FastingStatus.CANCELLED.value, session_id))

            conn.commit()
                return cursor.rowcount > 0

    def get_active_session(self, user_id: int = 1) -> Optional[FastingSession]:
            """Get current active fasting session"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                    SELECT * FROM fasting_sessions
                WHERE user_id = ? AND status = 'active'
                ORDER BY start_time DESC LIMIT 1
                """, (user_id,))

            row = cursor.fetchone()
                return self._row_to_session(row) if row else None

    def get_fasting_sessions(self, user_id: int = 1, limit: int = 30) -> List[FastingSession]:
            """Get recent fasting sessions"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                    SELECT * FROM fasting_sessions
                WHERE user_id = ?
                ORDER BY start_time DESC
                    LIMIT ?
            """, (user_id, limit))

            rows = cursor.fetchall()
                return [self._row_to_session(row) for row in rows]

    def get_fasting_stats(self, user_id: int = 1, days: int = 30) -> Dict:
            """Get fasting statistics"""
        with self._get_connection() as conn:
            # Get completed sessions in the last N days
                cursor = conn.execute("""
                SELECT
                    COUNT(*) as total_sessions,
                        AVG(duration_hours) as avg_duration,
                    SUM(duration_hours) as total_hours,
                    MAX(duration_hours) as longest_session,
                        MIN(duration_hours) as shortest_session
                FROM fasting_sessions
                WHERE user_id = ?
                    AND status = 'completed'
                AND start_time >= datetime('now', '-{} days')
            """.format(days), (user_id,))

                stats = dict(cursor.fetchone())

            # Get current streak
                cursor = conn.execute("""
                WITH RECURSIVE fasting_days AS (
                    SELECT DATE(start_time) as fasting_date,
                               ROW_NUMBER() OVER (ORDER BY DATE(start_time) DESC) as rn
                    FROM fasting_sessions
                    WHERE user_id = ? AND status = 'completed'
                        GROUP BY DATE(start_time)
                )
                SELECT COUNT(*) as current_streak
                    FROM fasting_days
                WHERE rn <= (
                    SELECT MAX(rn) FROM fasting_days
                        WHERE fasting_date >= DATE('now', '-1 day')
                )
            """, (user_id,))

                streak_row = cursor.fetchone()
            stats['current_streak'] = streak_row['current_streak'] if streak_row else 0

            return stats

        def create_fasting_goal(self, goal_type: str, target_value: float,
                           period_start: date, period_end: date) -> FastingGoal:
        """Create a new fasting goal"""
            goal = FastingGoal(
            goal_type=goal_type,
            target_value=target_value,
                period_start=period_start,
            period_end=period_end
        )

            with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO fasting_goals
                    (user_id, goal_type, target_value, period_start, period_end)
                VALUES (?, ?, ?, ?, ?)
            """, (goal.user_id, goal.goal_type, goal.target_value,
                      goal.period_start.isoformat() if goal.period_start else None,
                  goal.period_end.isoformat() if goal.period_end else None))

            goal.id = cursor.lastrowid
                conn.commit()

        return goal

        def update_goal_progress(self, goal_id: int) -> bool:
        """Update goal progress based on completed sessions"""
        with self._get_connection() as conn:
                # Get goal
            cursor = conn.execute("SELECT * FROM fasting_goals WHERE id = ?", (goal_id,))
            goal_row = cursor.fetchone()
                if not goal_row:
                return False

            goal_type = goal_row['goal_type']
                period_start = goal_row['period_start']
            period_end = goal_row['period_end']

            # Calculate current progress
                if goal_type == 'daily_hours':
                cursor = conn.execute("""
                    SELECT SUM(duration_hours) as total_hours
                        FROM fasting_sessions
                    WHERE status = 'completed'
                    AND DATE(start_time) BETWEEN ? AND ?
                    """, (period_start, period_end))

                result = cursor.fetchone()
                    current_value = result['total_hours'] or 0.0

            elif goal_type == 'weekly_sessions':
                    cursor = conn.execute("""
                    SELECT COUNT(DISTINCT DATE(start_time)) as session_count
                    FROM fasting_sessions
                        WHERE status = 'completed'
                    AND DATE(start_time) BETWEEN ? AND ?
                """, (period_start, period_end))

                    result = cursor.fetchone()
                current_value = result['session_count'] or 0.0

            else:  # monthly_hours
                    cursor = conn.execute("""
                    SELECT SUM(duration_hours) as total_hours
                    FROM fasting_sessions
                        WHERE status = 'completed'
                    AND DATE(start_time) BETWEEN ? AND ?
                """, (period_start, period_end))

                    result = cursor.fetchone()
                current_value = result['total_hours'] or 0.0

            # Update goal
                conn.execute("""
                UPDATE fasting_goals
                SET current_value = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
            """, (current_value, goal_id))

            conn.commit()
                return True

    def get_fasting_goals(self, user_id: int = 1) -> List[FastingGoal]:
            """Get user's fasting goals"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                    SELECT * FROM fasting_goals
                WHERE user_id = ? AND status = 'active'
                ORDER BY created_at DESC
                """, (user_id,))

            rows = cursor.fetchall()
                return [self._row_to_goal(row) for row in rows]

    def get_fasting_progress(self, user_id: int = 1) -> Dict:
            """Get current fasting progress"""
        active_session = self.get_active_session(user_id)
        stats = self.get_fasting_stats(user_id, 7)  # Last 7 days
            goals = self.get_fasting_goals(user_id)

        progress = {
                'active_session': active_session,
            'stats': stats,
            'goals': goals,
                'is_fasting': active_session is not None
        }

        if active_session:
                # Calculate current fasting duration
            now = datetime.now()
            start_time = active_session.start_time
                current_duration = (now - start_time).total_seconds() / 3600
            progress['current_duration_hours'] = current_duration

            # Add fasting type to progress
                progress['fasting_type'] = active_session.fasting_type

            # Calculate progress percentage for common fasting types
                fasting_type = active_session.fasting_type
            if fasting_type == "16:8":
                progress['target_hours'] = 16
                    progress['progress_percentage'] = min(100, (current_duration / 16) * 100)
            elif fasting_type == "18:6":
                progress['target_hours'] = 18
                    progress['progress_percentage'] = min(100, (current_duration / 18) * 100)
            elif fasting_type == "20:4":
                progress['target_hours'] = 20
                    progress['progress_percentage'] = min(100, (current_duration / 20) * 100)
            else:
                progress['target_hours'] = None
                    progress['progress_percentage'] = None

        return progress

        def _row_to_session(self, row) -> FastingSession:
        """Convert database row to FastingSession"""
        if not row:
                return None

        return FastingSession(
                id=row['id'],
            user_id=row['user_id'],
            start_time=datetime.fromisoformat(row['start_time']) if row['start_time'] else None,
                end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
            duration_hours=row['duration_hours'],
            fasting_type=row['fasting_type'],
                status=row['status'],
            notes=row['notes'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )

    def _row_to_goal(self, row) -> FastingGoal:
            """Convert database row to FastingGoal"""
        if not row:
            return None

            return FastingGoal(
            id=row['id'],
            user_id=row['user_id'],
                goal_type=row['goal_type'],
            target_value=row['target_value'],
            current_value=row['current_value'],
                period_start=date.fromisoformat(row['period_start']) if row['period_start'] else None,
            period_end=date.fromisoformat(row['period_end']) if row['period_end'] else None,
            status=row['status'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )

        def get_fasting_settings(self, user_id: int = 1) -> Optional[Dict]:
        """Get user's fasting settings"""
        try:
                with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                    cursor.execute("""
                    SELECT * FROM fasting_settings
                    WHERE user_id = ?
                    """, (user_id,))

                row = cursor.fetchone()

                    if row:
                    return {
                        'id': row['id'],
                            'user_id': row['user_id'],
                        'fasting_goal': row['fasting_goal'],
                        'preferred_start_time': row['preferred_start_time'],
                            'enable_reminders': bool(row['enable_reminders']),
                        'enable_notifications': bool(row['enable_notifications']),
                        'default_notes': row['default_notes'],
                            'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    }
                    return None

        except Exception as e:
                print("Error getting fasting settings: {e}")
            return None

    def create_fasting_settings(self, settings_data: Dict) -> Dict:
            """Create new fasting settings"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()

                cursor.execute("""
                        INSERT INTO fasting_settings
                    (user_id, fasting_goal, preferred_start_time, enable_reminders,
                     enable_notifications, default_notes, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    settings_data['user_id'],
                        settings_data['fasting_goal'],
                    settings_data['preferred_start_time'],
                    settings_data['enable_reminders'],
                        settings_data['enable_notifications'],
                    settings_data['default_notes'],
                    datetime.now().isoformat(),
                        datetime.now().isoformat()
                ))

                conn.commit()

                    # Return the created settings
                return self.get_fasting_settings(settings_data['user_id'])

        except Exception as e:
                print("Error creating fasting settings: {e}")
            raise ValueError("Failed to create fasting settings: {e}")

    def update_fasting_settings(self, user_id: int, settings_data: Dict) -> Dict:
            """Update existing fasting settings"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()

                cursor.execute("""
                        UPDATE fasting_settings
                    SET fasting_goal = ?, preferred_start_time = ?, enable_reminders = ?,
                        enable_notifications = ?, default_notes = ?, updated_at = ?
                        WHERE user_id = ?
                """, (
                    settings_data['fasting_goal'],
                        settings_data['preferred_start_time'],
                    settings_data['enable_reminders'],
                    settings_data['enable_notifications'],
                        settings_data['default_notes'],
                    datetime.now().isoformat(),
                    user_id
                    ))

                if cursor.rowcount == 0:
                        raise ValueError("No fasting settings found for user")

                conn.commit()

                    # Return the updated settings
                return self.get_fasting_settings(user_id)

        except Exception as e:
                print("Error updating fasting settings: {e}")
            raise ValueError("Failed to update fasting settings: {e}")
