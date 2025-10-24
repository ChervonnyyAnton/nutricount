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
        use_cache: bool = True
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
        self,
        fasting_type: str = "16:8",
        notes: str = "",
        user_id: int = 1
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
                [f"Invalid fasting type. Must be one of: {', '.join(self.VALID_FASTING_TYPES)}"]
            )

        # Business rule: Check for active session
        active_session = self.repository.get_active_session(user_id)
        if active_session:
            return (
                False,
                None,
                ["You already have an active fasting session"]
            )

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
        self,
        session_id: int,
        user_id: int = 1
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
        self,
        session_id: int,
        user_id: int = 1
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
        self,
        session_id: int,
        user_id: int = 1
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
            return (
                False,
                None,
                ["You already have an active fasting session"]
            )

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

    def cancel_fasting_session(
        self,
        session_id: int,
        user_id: int = 1
    ) -> Tuple[bool, List[str]]:
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

    def get_fasting_statistics(
        self,
        user_id: int = 1,
        use_cache: bool = True
    ) -> Dict[str, Any]:
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
