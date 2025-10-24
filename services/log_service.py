"""
Log Service - Business logic layer for daily food log.

Implements Service Layer Pattern for log operations.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from repositories.log_repository import LogRepository
from src.cache_manager import cache_manager
from src.config import Config
from src.utils import validate_log_data

logger = logging.getLogger(__name__)


class LogService:
    """
    Service layer for log entry business logic.

    Handles validation, business rules, calculations, and caching for log entries.
    Delegates data access to LogRepository.
    """

    def __init__(self, repository: LogRepository):
        """
        Initialize service with repository.

        Args:
            repository: LogRepository instance
        """
        self.repository = repository

    def get_log_entries(
        self,
        date_filter: Optional[str] = None,
        limit: int = 100,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get log entries with optional date filter and caching.

        Args:
            date_filter: Filter by specific date (YYYY-MM-DD)
            limit: Maximum number of entries (capped at API_MAX_PER_PAGE)
            use_cache: Whether to use cache

        Returns:
            List of processed log entry dictionaries with calculated nutrition
        """
        # Apply business rules
        limit = min(limit, Config.API_MAX_PER_PAGE)

        # Try cache first
        if use_cache:
            cache_key = f"log:{date_filter or 'all'}:{limit}"
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

        # Get from repository
        entries = self.repository.find_all(date_filter=date_filter, limit=limit)

        # Process entries to calculate actual nutrition values
        processed_entries = self._process_log_entries(entries)

        # Cache result
        if use_cache:
            cache_manager.set(cache_key, processed_entries, 300)  # 5 minutes

        return processed_entries

    def get_log_entry_by_id(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """
        Get single log entry by ID.

        Args:
            entry_id: Log entry ID

        Returns:
            Processed log entry dictionary or None if not found
        """
        entry = self.repository.find_by_id(entry_id)
        if not entry:
            return None

        # Process single entry
        processed = self._process_log_entries([entry])
        return processed[0] if processed else None

    def create_log_entry(
        self, data: Dict[str, Any]
    ) -> Tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """
        Create new log entry with validation and business rules.

        Business rules:
        - Date must not be in the future
        - Item (product or dish) must exist
        - Quantity must be positive

        Args:
            data: Log entry data (date, item_type, item_id, quantity_grams, meal_time)

        Returns:
            Tuple of (success, entry_data, errors)
        """
        # Validate data
        is_valid, errors, cleaned_data = validate_log_data(data)
        if not is_valid:
            return (False, None, errors)

        # Business rule: Verify item exists
        item_exists = self.repository.verify_item_exists(
            cleaned_data["item_type"],
            cleaned_data["item_id"]
        )
        if not item_exists:
            return (
                False,
                None,
                [f"{cleaned_data['item_type'].capitalize()} with ID {cleaned_data['item_id']} does not exist"]
            )

        # Create log entry
        try:
            entry = self.repository.create(cleaned_data)

            # Invalidate cache
            self._invalidate_log_cache(entry["date"])

            # Process entry for response
            processed = self._process_log_entries([entry])

            return (True, processed[0] if processed else entry, [])
        except Exception as e:
            logger.exception("Error creating log entry")
            return (False, None, [f"Failed to create log entry: {str(e)}"])

    def update_log_entry(
        self,
        entry_id: int,
        data: Dict[str, Any]
    ) -> Tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """
        Update existing log entry with validation and business rules.

        Args:
            entry_id: Log entry ID
            data: Updated log entry data

        Returns:
            Tuple of (success, entry_data, errors)
        """
        # Check if entry exists
        existing = self.repository.find_by_id(entry_id)
        if not existing:
            return (False, None, ["Log entry not found"])

        # Validate data (if provided)
        if data:
            is_valid, errors, cleaned_data = validate_log_data(data)
            if not is_valid:
                return (False, None, errors)
        else:
            cleaned_data = data

        # Business rule: Verify item exists (if changing item)
        if "item_type" in cleaned_data or "item_id" in cleaned_data:
            item_type = cleaned_data.get("item_type", existing["item_type"])
            item_id = cleaned_data.get("item_id", existing["item_id"])

            item_exists = self.repository.verify_item_exists(item_type, item_id)
            if not item_exists:
                return (
                    False,
                    None,
                    [f"{item_type.capitalize()} with ID {item_id} does not exist"]
                )

        # Update entry
        try:
            updated = self.repository.update(entry_id, cleaned_data)

            # Invalidate cache for both old and new dates
            self._invalidate_log_cache(existing["date"])
            if "date" in cleaned_data and cleaned_data["date"] != existing["date"]:
                self._invalidate_log_cache(cleaned_data["date"])

            # Process entry for response
            processed = self._process_log_entries([updated])

            return (True, processed[0] if processed else updated, [])
        except Exception as e:
            logger.exception(f"Error updating log entry {entry_id}")
            return (False, None, [f"Failed to update log entry: {str(e)}"])

    def delete_log_entry(self, entry_id: int) -> Tuple[bool, List[str]]:
        """
        Delete log entry.

        Args:
            entry_id: Log entry ID

        Returns:
            Tuple of (success, errors)
        """
        # Check if entry exists and get date for cache invalidation
        entry = self.repository.find_by_id(entry_id)
        if not entry:
            return (False, ["Log entry not found"])

        # Delete entry
        try:
            success = self.repository.delete(entry_id)

            if success:
                # Invalidate cache
                self._invalidate_log_cache(entry["date"])
                return (True, [])
            else:
                return (False, ["Failed to delete log entry"])
        except Exception as e:
            logger.exception(f"Error deleting log entry {entry_id}")
            return (False, [f"Failed to delete log entry: {str(e)}"])

    def get_daily_summary(self, date: str) -> Dict[str, Any]:
        """
        Get daily nutrition summary for a specific date.

        Args:
            date: Date string (YYYY-MM-DD)

        Returns:
            Dictionary with entries, totals, and calculated fields
        """
        # Get entries for the date
        entries = self.get_log_entries(date_filter=date)

        # Calculate totals
        totals = self.repository.get_daily_totals(date)

        # Calculate additional metrics
        total_carbs = totals["carbs"]
        total_fiber = totals["fiber"]
        net_carbs = max(0, total_carbs - total_fiber)

        # Calculate keto index (if applicable)
        # Keto index: higher = more keto-friendly
        # Formula: (fat * 2 + protein) / (net_carbs + 1)
        keto_index = 0
        if totals["fat"] > 0 or totals["protein"] > 0:
            keto_index = (totals["fat"] * 2 + totals["protein"]) / (net_carbs + 1)

        return {
            "date": date,
            "entries": entries,
            "entry_count": len(entries),
            "totals": {
                "calories": round(totals["calories"], 1),
                "protein": round(totals["protein"], 1),
                "fat": round(totals["fat"], 1),
                "carbs": round(total_carbs, 1),
                "fiber": round(total_fiber, 1),
                "net_carbs": round(net_carbs, 1),
            },
            "metrics": {
                "keto_index": round(keto_index, 2),
                "protein_percentage": round((totals["protein"] * 4 / totals["calories"] * 100) if totals["calories"] > 0 else 0, 1),
                "fat_percentage": round((totals["fat"] * 9 / totals["calories"] * 100) if totals["calories"] > 0 else 0, 1),
                "carb_percentage": round((total_carbs * 4 / totals["calories"] * 100) if totals["calories"] > 0 else 0, 1),
            }
        }

    def _process_log_entries(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process log entries to calculate actual nutrition values.

        Args:
            entries: Raw log entries from database

        Returns:
            Processed entries with calculated nutrition
        """
        processed_entries = []

        for entry in entries:
            processed_entry = dict(entry)
            quantity_factor = entry["quantity_grams"] / 100.0

            # Calculate nutrition values based on item type
            if entry["item_type"] == "product":
                # For products, use per_100g values
                processed_entry["calories"] = (
                    entry["calories_per_100g"] * quantity_factor
                    if entry.get("calories_per_100g")
                    else None
                )
                processed_entry["protein"] = (
                    entry["protein_per_100g"] * quantity_factor
                    if entry.get("protein_per_100g")
                    else None
                )
                processed_entry["fat"] = (
                    entry["fat_per_100g"] * quantity_factor
                    if entry.get("fat_per_100g")
                    else None
                )
                processed_entry["carbs"] = (
                    entry["carbs_per_100g"] * quantity_factor
                    if entry.get("carbs_per_100g")
                    else None
                )
                fiber_per_100g = entry.get("fiber_per_100g") or 0
                processed_entry["fiber"] = fiber_per_100g * quantity_factor
            elif entry["item_type"] == "dish":
                # For dishes, use dish_per_100g values
                processed_entry["calories"] = entry.get("calculated_calories")
                processed_entry["protein"] = (
                    entry["dish_protein_per_100g"] * quantity_factor
                    if entry.get("dish_protein_per_100g")
                    else None
                )
                processed_entry["fat"] = (
                    entry["dish_fat_per_100g"] * quantity_factor
                    if entry.get("dish_fat_per_100g")
                    else None
                )
                processed_entry["carbs"] = (
                    entry["dish_carbs_per_100g"] * quantity_factor
                    if entry.get("dish_carbs_per_100g")
                    else None
                )
                dish_fiber_per_100g = entry.get("dish_fiber_per_100g") or 0
                processed_entry["fiber"] = dish_fiber_per_100g * quantity_factor

            # Calculate net carbs
            carbs = processed_entry.get("carbs") or 0
            fiber = processed_entry.get("fiber") or 0
            processed_entry["net_carbs"] = max(0, carbs - fiber)

            processed_entries.append(processed_entry)

        return processed_entries

    def _invalidate_log_cache(self, date: Optional[str] = None):
        """
        Invalidate log cache for specific date or all.

        Args:
            date: Specific date to invalidate, or None for all
        """
        if date:
            # Invalidate specific date and "all" cache
            cache_manager.delete(f"log:{date}:*")
            cache_manager.delete("log:all:*")
        else:
            # Invalidate all log cache
            cache_manager.delete("log:*")
