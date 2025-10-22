"""
Dish Service - Business logic layer for dishes (recipes).

Implements Service Layer Pattern for dish operations.
"""

from typing import Any, Dict, List, Optional, Tuple

from repositories.dish_repository import DishRepository
from src.cache_manager import cache_manager
from src.utils import validate_dish_data


class DishService:
    """
    Service layer for dish business logic.

    Handles validation, business rules, and caching for dishes.
    Delegates data access to DishRepository.
    """

    def __init__(self, repository: DishRepository):
        """
        Initialize service with repository.

        Args:
            repository: DishRepository instance
        """
        self.repository = repository

    def get_dishes(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Get all dishes with optional caching.

        Args:
            use_cache: Whether to use cache (default: True)

        Returns:
            List of dish dictionaries
        """
        # Check cache
        if use_cache:
            cache_key = "dishes:all"
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

        # Get from repository
        dishes = self.repository.find_all()

        # Cache result
        if use_cache:
            cache_manager.set(cache_key, dishes, 300)  # 5 minutes TTL

        return dishes

    def get_dish_by_id(self, dish_id: int) -> Optional[Dict[str, Any]]:
        """
        Get dish by ID.

        Args:
            dish_id: Dish ID

        Returns:
            Dish dictionary or None if not found
        """
        return self.repository.find_by_id(dish_id)

    def create_dish(self, data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """
        Create a new dish with validation and business rules.

        Business rules:
        - Name must not be duplicate
        - All products in ingredients must exist

        Args:
            data: Dish data with ingredients

        Returns:
            Tuple of (success, dish_data, errors)
        """
        # Validate data
        is_valid, errors, cleaned_data = validate_dish_data(data)
        if not is_valid:
            return (False, None, errors)

        # Business rule: Check for duplicate name
        existing = self.repository.find_by_name(cleaned_data["name"])
        if existing:
            return (False, None, [f"Dish '{cleaned_data['name']}' already exists"])

        # Business rule: Verify all products exist
        product_ids = [ing["product_id"] for ing in cleaned_data["ingredients"]]
        all_exist, missing_ids = self.repository.verify_products_exist(product_ids)
        if not all_exist:
            return (False, None, [f"Products with IDs {missing_ids} do not exist"])

        # Create dish
        try:
            dish = self.repository.create(cleaned_data)

            # Invalidate cache
            cache_manager.delete("dishes:all")

            return (True, dish, [])
        except Exception as e:
            return (False, None, [str(e)])

    def update_dish(
        self, dish_id: int, data: Dict[str, Any]
    ) -> Tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """
        Update existing dish with validation and business rules.

        Business rules:
        - Dish must exist
        - Name must not conflict with another dish
        - All products in ingredients must exist

        Args:
            dish_id: Dish ID
            data: Updated dish data

        Returns:
            Tuple of (success, dish_data, errors)
        """
        # Check if dish exists
        existing = self.repository.find_by_id(dish_id)
        if not existing:
            return (False, None, ["Dish not found"])

        # Validate data (if provided)
        if data:
            is_valid, errors, cleaned_data = validate_dish_data(data)
            if not is_valid:
                return (False, None, errors)
        else:
            cleaned_data = data

        # Business rule: Check for name conflict (if name is changing)
        if "name" in cleaned_data and cleaned_data["name"] != existing["name"]:
            name_conflict = self.repository.find_by_name(cleaned_data["name"])
            if name_conflict:
                return (False, None, [f"Dish name '{cleaned_data['name']}' is already taken"])

        # Business rule: Verify all products exist (if ingredients are provided)
        if "ingredients" in cleaned_data:
            product_ids = [ing["product_id"] for ing in cleaned_data["ingredients"]]
            all_exist, missing_ids = self.repository.verify_products_exist(product_ids)
            if not all_exist:
                return (False, None, [f"Products with IDs {missing_ids} do not exist"])

        # Update dish
        try:
            updated_dish = self.repository.update(dish_id, cleaned_data)

            # Invalidate cache
            cache_manager.delete("dishes:all")

            return (True, updated_dish, [])
        except Exception as e:
            return (False, None, [str(e)])

    def delete_dish(self, dish_id: int) -> Tuple[bool, List[str]]:
        """
        Delete dish with business rules.

        Business rules:
        - Cannot delete dish if used in log entries

        Args:
            dish_id: Dish ID

        Returns:
            Tuple of (success, errors)
        """
        # Check if dish exists
        if not self.repository.exists(dish_id):
            return (False, ["Dish not found"])

        # Business rule: Cannot delete if used in logs
        is_used, count = self.repository.is_used_in_logs(dish_id)
        if is_used:
            return (
                False,
                [f"Cannot delete dish: it is used in {count} log entry/entries"],
            )

        # Delete dish
        try:
            self.repository.delete(dish_id)

            # Invalidate cache
            cache_manager.delete("dishes:all")

            return (True, [])
        except Exception as e:
            return (False, [str(e)])

    def get_dish_count(self) -> int:
        """
        Get total number of dishes.

        Returns:
            Count of dishes
        """
        return self.repository.count()
