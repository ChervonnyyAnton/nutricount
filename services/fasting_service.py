"""
Fasting Service - Business logic layer for intermittent fasting.

Implements Service Layer Pattern for fasting operations.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from repositories.fasting_repository import FastingRepository
from src.cache_manager import cache_manager

logger = logging.getLogger(__name__)


class FastingService:
    """
    Service layer for fasting business logic.

    Handles validation, business rules, and caching for fasting sessions.
    Delegates data access to FastingRepository.
    """

    # Valid fasting types
    VALID_FASTING_TYPES = ["16:8", "18:6", "20:4", "OMAD", "Custom"]

    def __init__(self, repository: FastingRepository):
        """
        Initialize service with repository.

        Args:
            repository: FastingRepository instance
        """
        self.repository = repository

    def get_fasting_sessions(
        self,
        user_id: int = 1,
        status: Optional[str] = None,
        limit: int = 100,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Get fasting sessions with optional filters and caching.

        Args:
            user_id: User ID
            status: Session status filter
            limit: Maximum sessions to return
            use_cache: Whether to use cache

        Returns:
            List of fasting session dictionaries
        """
        # Try cache first
        if use_cache:
            cache_key = f"fasting:sessions:{user_id}:{status or 'all'}:{limit}"
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

        # Get from repository
        sessions = self.repository.find_all(user_id=user_id, status=status, limit=limit)

        # Cache result
        if use_cache:
            cache_manager.set(cache_key, sessions, 300)  # 5 minutes

        return sessions

    def get_active_session(self, user_id: int = 1) -> Optional[Dict[str, Any]]:
        """
        Get active fasting session for user.

        Args:
            user_id: User ID

        Returns:
            Active session dictionary or None
        """
        return self.repository.get_active_session(user_id)

    def get_session_by_id(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Get fasting session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session dictionary or None if not found
        """
        return self.repository.find_by_id(session_id)

    def start_fasting_session(
        self, fasting_type: str = "16:8", notes: str = "", user_id: int = 1
    ) -> Tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """
        Start new fasting session with validation and business rules.

        Business rules:
        - User can have only one active session at a time
        - Fasting type must be valid

        Args:
            fasting_type: Type of fasting (16:8, 18:6, 20:4, OMAD, Custom)
            notes: Optional notes
            user_id: User ID

        Returns:
            Tuple of (success, session_data, errors)
        """
        # Validate fasting type
        if fasting_type not in self.VALID_FASTING_TYPES:
            return (
                False,
                None,
                [f"Invalid fasting type. Must be one of: {', '.join(self.VALID_FASTING_TYPES)}"],
            )

        # Business rule: Check for active session
        active_session = self.repository.get_active_session(user_id)
        if active_session:
            return (False, None, ["You already have an active fasting session"])

        # Create session
        try:
            session_data = {
                "user_id": user_id,
                "start_time": datetime.now().isoformat(),
                "fasting_type": fasting_type,
                "status": "active",
                "notes": notes,
            }

            session = self.repository.create(session_data)

            # Invalidate cache
            self._invalidate_fasting_cache(user_id)

            return (True, session, [])
        except Exception as e:
            logger.exception("Error starting fasting session")
            return (False, None, [f"Failed to start fasting session: {str(e)}"])

    def end_fasting_session(
        self, session_id: int, user_id: int = 1
    ) -> Tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """
        End active fasting session.

        Args:
            session_id: Session ID
            user_id: User ID

        Returns:
            Tuple of (success, session_data, errors)
        """
        # Check if session exists and is active
        session = self.repository.find_by_id(session_id)
        if not session:
            return (False, None, ["Fasting session not found"])

        if session["status"] != "active":
            return (False, None, ["Session is not active"])

        # Calculate duration
        try:
            end_time = datetime.now()
            start_time = datetime.fromisoformat(session["start_time"])
            duration_hours = (end_time - start_time).total_seconds() / 3600

            # Update session
            update_data = {
                "end_time": end_time.isoformat(),
                "duration_hours": duration_hours,
                "status": "completed",
            }

            updated_session = self.repository.update(session_id, update_data)

            # Invalidate cache
            self._invalidate_fasting_cache(user_id)

            return (True, updated_session, [])
        except Exception as e:
            logger.exception(f"Error ending fasting session {session_id}")
            return (False, None, [f"Failed to end fasting session: {str(e)}"])

    def pause_fasting_session(
        self, session_id: int, user_id: int = 1
    ) -> Tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """
        Pause active fasting session.

        Args:
            session_id: Session ID
            user_id: User ID

        Returns:
            Tuple of (success, session_data, errors)
        """
        # Check if session exists and is active
        session = self.repository.find_by_id(session_id)
        if not session:
            return (False, None, ["Fasting session not found"])

        if session["status"] != "active":
            return (False, None, ["Session is not active"])

        # Pause session
        try:
            update_data = {"status": "paused"}
            updated_session = self.repository.update(session_id, update_data)

            # Invalidate cache
            self._invalidate_fasting_cache(user_id)

            return (True, updated_session, [])
        except Exception as e:
            logger.exception(f"Error pausing fasting session {session_id}")
            return (False, None, [f"Failed to pause fasting session: {str(e)}"])

    def resume_fasting_session(
        self, session_id: int, user_id: int = 1
    ) -> Tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """
        Resume paused fasting session.

        Args:
            session_id: Session ID
            user_id: User ID

        Returns:
            Tuple of (success, session_data, errors)
        """
        # Check if session exists and is paused
        session = self.repository.find_by_id(session_id)
        if not session:
            return (False, None, ["Fasting session not found"])

        if session["status"] != "paused":
            return (False, None, ["Session is not paused"])

        # Business rule: Check for other active sessions
        active_session = self.repository.get_active_session(user_id)
        if active_session:
            return (False, None, ["You already have an active fasting session"])

        # Resume session
        try:
            update_data = {"status": "active"}
            updated_session = self.repository.update(session_id, update_data)

            # Invalidate cache
            self._invalidate_fasting_cache(user_id)

            return (True, updated_session, [])
        except Exception as e:
            logger.exception(f"Error resuming fasting session {session_id}")
            return (False, None, [f"Failed to resume fasting session: {str(e)}"])

    def cancel_fasting_session(self, session_id: int, user_id: int = 1) -> Tuple[bool, List[str]]:
        """
        Cancel fasting session.

        Args:
            session_id: Session ID
            user_id: User ID

        Returns:
            Tuple of (success, errors)
        """
        # Check if session exists
        session = self.repository.find_by_id(session_id)
        if not session:
            return (False, ["Fasting session not found"])

        # Cancel session
        try:
            update_data = {"status": "cancelled"}
            self.repository.update(session_id, update_data)

            # Invalidate cache
            self._invalidate_fasting_cache(user_id)

            return (True, [])
        except Exception as e:
            logger.exception(f"Error cancelling fasting session {session_id}")
            return (False, [f"Failed to cancel fasting session: {str(e)}"])

    def get_fasting_statistics(self, user_id: int = 1, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get fasting statistics for user.

        Args:
            user_id: User ID
            use_cache: Whether to use cache

        Returns:
            Dictionary with statistics
        """
        # Try cache first
        if use_cache:
            cache_key = f"fasting:stats:{user_id}"
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

        # Get from repository
        stats = self.repository.get_statistics(user_id)

        # Cache result
        if use_cache:
            cache_manager.set(cache_key, stats, 600)  # 10 minutes

        return stats

    def _invalidate_fasting_cache(self, user_id: int):
        """
        Invalidate fasting cache for user.

        Args:
            user_id: User ID
        """
        # Invalidate all fasting cache for this user
        cache_manager.delete(f"fasting:sessions:{user_id}:*")
        cache_manager.delete(f"fasting:stats:{user_id}")

    # === Advanced Features (Previously delegated to FastingManager) ===

    def get_fasting_progress(self, user_id: int = 1) -> Dict[str, Any]:
        """
        Get current fasting progress with active session, stats, and goals.

        This includes complex calculations like progress percentage and streak.

        Args:
            user_id: User ID

        Returns:
            Dictionary with progress information
        """
        # Get active session
        active_session = self.repository.get_active_session(user_id)

        # Get basic stats
        stats = self.repository.get_statistics(user_id)

        # Get goals
        goals = self.repository.find_goals(user_id, status="active")

        # Calculate progress if there's an active session
        progress = {}
        if active_session:
            start_time = datetime.fromisoformat(active_session["start_time"])
            elapsed_hours = (datetime.now() - start_time).total_seconds() / 3600

            # Determine target hours based on fasting type
            fasting_type = active_session.get("fasting_type", "16:8")
            target_hours = float(fasting_type.split(":")[0]) if ":" in fasting_type else 16

            progress = {
                "elapsed_hours": round(elapsed_hours, 2),
                "target_hours": target_hours,
                "progress_percentage": min(100, round((elapsed_hours / target_hours) * 100, 1)),
                "is_complete": elapsed_hours >= target_hours,
            }

        return {
            "active_session": active_session,
            "progress": progress,
            "stats": stats,
            "goals": goals,
        }

    def get_fasting_stats_with_streak(self, user_id: int = 1, days: int = 30) -> Dict[str, Any]:
        """
        Get fasting statistics including current streak calculation.

        Streak calculation requires complex SQL queries.

        Args:
            user_id: User ID
            days: Number of days to include in statistics

        Returns:
            Dictionary with statistics including current streak
        """
        # Delegate to repository for streak calculation
        return self.repository.get_stats_with_streak(user_id, days)

    def get_fasting_goals(self, user_id: int = 1) -> List[Dict[str, Any]]:
        """
        Get user's fasting goals.

        Args:
            user_id: User ID

        Returns:
            List of goal dictionaries
        """
        return self.repository.find_goals(user_id)

    def create_fasting_goal(
        self,
        goal_type: str,
        target_value: float,
        period_start: Any,
        period_end: Any,
        user_id: int = 1,
    ) -> Tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """
        Create a new fasting goal.

        Args:
            goal_type: Type of goal (e.g., 'daily_hours', 'weekly_sessions')
            target_value: Target value for the goal
            period_start: Goal period start date
            period_end: Goal period end date
            user_id: User ID

        Returns:
            Tuple of (success, goal, errors)
        """
        errors = []

        # Validate goal type
        valid_types = ["daily_hours", "weekly_sessions", "monthly_hours"]
        if goal_type not in valid_types:
            errors.append(f"Invalid goal type. Must be one of: {', '.join(valid_types)}")

        # Validate target value
        if target_value <= 0:
            errors.append("Target value must be greater than 0")

        # Validate dates
        try:
            if isinstance(period_start, str):
                period_start = datetime.fromisoformat(period_start).date()
            if isinstance(period_end, str):
                period_end = datetime.fromisoformat(period_end).date()

            if period_end <= period_start:
                errors.append("Period end must be after period start")
        except (ValueError, AttributeError) as e:
            errors.append(f"Invalid date format: {e}")

        if errors:
            return (False, None, errors)

        try:
            goal_data = {
                "user_id": user_id,
                "goal_type": goal_type,
                "target_value": target_value,
                "period_start": str(period_start),
                "period_end": str(period_end),
            }
            goal = self.repository.create_goal(goal_data)
            return (True, goal, [])
        except Exception as e:
            logger.exception("Error creating fasting goal")
            return (False, None, [str(e)])

    def get_fasting_settings(self, user_id: int = 1) -> Optional[Dict[str, Any]]:
        """
        Get user's fasting settings.

        Args:
            user_id: User ID

        Returns:
            Settings dictionary or None
        """
        return self.repository.find_settings(user_id)

    def create_fasting_settings(
        self, settings_data: Dict[str, Any]
    ) -> Tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """
        Create user's fasting settings.

        Args:
            settings_data: Settings data dictionary

        Returns:
            Tuple of (success, settings, errors)
        """
        errors = []

        # Validate fasting_goal
        if "fasting_goal" in settings_data:
            valid_goals = ["16:8", "18:6", "20:4", "OMAD"]
            if settings_data["fasting_goal"] not in valid_goals:
                errors.append(f"Invalid fasting goal. Must be one of: {', '.join(valid_goals)}")

        if errors:
            return (False, None, errors)

        try:
            settings = self.repository.create_settings(settings_data)
            return (True, settings, [])
        except Exception as e:
            logger.exception("Error creating fasting settings")
            return (False, None, [str(e)])

    def update_fasting_settings(
        self, user_id: int, settings_data: Dict[str, Any]
    ) -> Tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """
        Update user's fasting settings.

        Args:
            user_id: User ID
            settings_data: Settings data dictionary

        Returns:
            Tuple of (success, settings, errors)
        """
        errors = []

        # Validate fasting_goal if provided
        if "fasting_goal" in settings_data:
            valid_goals = ["16:8", "18:6", "20:4", "OMAD"]
            if settings_data["fasting_goal"] not in valid_goals:
                errors.append(f"Invalid fasting goal. Must be one of: {', '.join(valid_goals)}")

        if errors:
            return (False, None, errors)

        try:
            settings = self.repository.update_settings(user_id, settings_data)
            if settings is None:
                return (False, None, ["Settings not found for user"])
            return (True, settings, [])
        except Exception as e:
            logger.exception("Error updating fasting settings")
            return (False, None, [str(e)])
