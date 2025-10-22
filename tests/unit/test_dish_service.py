"""
Unit tests for DishService.

Tests the Service Layer pattern implementation for dishes,
ensuring business logic is properly separated from data access.
"""

import pytest
from unittest.mock import MagicMock, patch

from services.dish_service import DishService
from repositories.dish_repository import DishRepository


@pytest.fixture
def mock_repository():
    """Create mock DishRepository."""
    return MagicMock(spec=DishRepository)


@pytest.fixture
def dish_service(mock_repository):
    """Create DishService with mock repository."""
    return DishService(mock_repository)


class TestDishServiceGetDishes:
    """Test getting dishes."""

    @patch("services.dish_service.cache_manager")
    def test_get_dishes_from_cache(self, mock_cache, dish_service, mock_repository):
        """Test getting dishes from cache."""
        # Setup cache to return data
        cached_dishes = [
            {"id": 1, "name": "Chicken Salad", "calories_per_100g": 120.0},
            {"id": 2, "name": "Beef Stew", "calories_per_100g": 150.0},
        ]
        mock_cache.get.return_value = cached_dishes

        # Get dishes
        dishes = dish_service.get_dishes(use_cache=True)

        # Verify cache was checked
        mock_cache.get.assert_called_once_with("dishes:all")

        # Verify repository was NOT called (cache hit)
        mock_repository.find_all.assert_not_called()

        # Verify correct dishes returned
        assert dishes == cached_dishes

    @patch("services.dish_service.cache_manager")
    def test_get_dishes_from_repository(self, mock_cache, dish_service, mock_repository):
        """Test getting dishes from repository when cache misses."""
        # Setup cache to miss
        mock_cache.get.return_value = None

        # Setup repository to return data
        repo_dishes = [
            {"id": 1, "name": "Grilled Fish", "calories_per_100g": 110.0},
        ]
        mock_repository.find_all.return_value = repo_dishes

        # Get dishes
        dishes = dish_service.get_dishes(use_cache=True)

        # Verify repository was called
        mock_repository.find_all.assert_called_once()

        # Verify cache was set
        mock_cache.set.assert_called_once_with("dishes:all", repo_dishes, 300)

        # Verify correct dishes returned
        assert dishes == repo_dishes

    def test_get_dishes_without_cache(self, dish_service, mock_repository):
        """Test getting dishes without using cache."""
        # Setup repository to return data
        repo_dishes = [{"id": 1, "name": "Soup"}]
        mock_repository.find_all.return_value = repo_dishes

        # Get dishes without cache
        dishes = dish_service.get_dishes(use_cache=False)

        # Verify repository was called
        mock_repository.find_all.assert_called_once()

        # Verify correct dishes returned
        assert dishes == repo_dishes


class TestDishServiceGetDishById:
    """Test getting dish by ID."""

    def test_get_dish_by_id_existing(self, dish_service, mock_repository):
        """Test getting existing dish by ID."""
        expected_dish = {"id": 1, "name": "Test Dish"}
        mock_repository.find_by_id.return_value = expected_dish

        dish = dish_service.get_dish_by_id(1)

        assert dish == expected_dish
        mock_repository.find_by_id.assert_called_once_with(1)

    def test_get_dish_by_id_nonexistent(self, dish_service, mock_repository):
        """Test getting nonexistent dish by ID."""
        mock_repository.find_by_id.return_value = None

        dish = dish_service.get_dish_by_id(999)

        assert dish is None


class TestDishServiceCreateDish:
    """Test dish creation."""

    @patch("services.dish_service.validate_dish_data")
    @patch("services.dish_service.cache_manager")
    def test_create_dish_success(self, mock_cache, mock_validate, dish_service, mock_repository):
        """Test successful dish creation."""
        # Setup validation to pass
        cleaned_data = {
            "name": "New Dish",
            "ingredients": [{"product_id": 1, "quantity_grams": 100.0}],
        }
        mock_validate.return_value = (True, [], cleaned_data)

        # Setup repository checks
        mock_repository.find_by_name.return_value = None  # No duplicate
        mock_repository.verify_products_exist.return_value = (True, [])  # Products exist

        # Setup repository to return created dish
        created_dish = {"id": 1, **cleaned_data}
        mock_repository.create.return_value = created_dish

        # Create dish
        success, dish, errors = dish_service.create_dish(cleaned_data)

        # Verify success
        assert success is True
        assert dish == created_dish
        assert errors == []

        # Verify cache was invalidated
        mock_cache.delete.assert_called_once_with("dishes:all")

    @patch("services.dish_service.validate_dish_data")
    def test_create_dish_validation_fails(self, mock_validate, dish_service, mock_repository):
        """Test dish creation with validation failure."""
        # Setup validation to fail
        mock_validate.return_value = (False, ["Name is required"], {})

        # Create dish
        success, dish, errors = dish_service.create_dish({"name": ""})

        # Verify failure
        assert success is False
        assert dish is None
        assert "Name is required" in errors

        # Verify repository was not called
        mock_repository.create.assert_not_called()

    @patch("services.dish_service.validate_dish_data")
    def test_create_dish_duplicate_name(self, mock_validate, dish_service, mock_repository):
        """Test dish creation with duplicate name."""
        # Setup validation to pass
        cleaned_data = {"name": "Existing Dish", "ingredients": []}
        mock_validate.return_value = (True, [], cleaned_data)

        # Setup repository to find existing dish
        mock_repository.find_by_name.return_value = {"id": 1, "name": "Existing Dish"}

        # Create dish
        success, dish, errors = dish_service.create_dish(cleaned_data)

        # Verify failure
        assert success is False
        assert dish is None
        assert "already exists" in errors[0]

        # Verify repository create was not called
        mock_repository.create.assert_not_called()

    @patch("services.dish_service.validate_dish_data")
    def test_create_dish_missing_products(self, mock_validate, dish_service, mock_repository):
        """Test dish creation with missing products."""
        # Setup validation to pass
        cleaned_data = {
            "name": "New Dish",
            "ingredients": [{"product_id": 999, "quantity_grams": 100.0}],
        }
        mock_validate.return_value = (True, [], cleaned_data)

        # Setup repository checks
        mock_repository.find_by_name.return_value = None  # No duplicate
        mock_repository.verify_products_exist.return_value = (False, [999])  # Product missing

        # Create dish
        success, dish, errors = dish_service.create_dish(cleaned_data)

        # Verify failure
        assert success is False
        assert dish is None
        assert "999" in errors[0]

        # Verify repository create was not called
        mock_repository.create.assert_not_called()


class TestDishServiceUpdateDish:
    """Test dish updates."""

    @patch("services.dish_service.validate_dish_data")
    @patch("services.dish_service.cache_manager")
    def test_update_dish_success(self, mock_cache, mock_validate, dish_service, mock_repository):
        """Test successful dish update."""
        # Setup existing dish
        existing_dish = {"id": 1, "name": "Old Name"}
        mock_repository.find_by_id.return_value = existing_dish

        # Setup validation to pass
        cleaned_data = {"name": "New Name", "ingredients": []}
        mock_validate.return_value = (True, [], cleaned_data)

        # Setup repository checks
        mock_repository.find_by_name.return_value = None  # No name conflict
        mock_repository.verify_products_exist.return_value = (True, [])  # No products to verify

        # Setup repository to return updated dish
        updated_dish = {"id": 1, "name": "New Name"}
        mock_repository.update.return_value = updated_dish

        # Update dish
        success, dish, errors = dish_service.update_dish(1, cleaned_data)

        # Verify success
        assert success is True
        assert dish == updated_dish
        assert errors == []

        # Verify cache was invalidated
        mock_cache.delete.assert_called_once_with("dishes:all")

    def test_update_dish_not_found(self, dish_service, mock_repository):
        """Test updating nonexistent dish."""
        # Setup repository to return None
        mock_repository.find_by_id.return_value = None

        # Update dish
        success, dish, errors = dish_service.update_dish(999, {"name": "New Name"})

        # Verify failure
        assert success is False
        assert dish is None
        assert "not found" in errors[0]

    @patch("services.dish_service.validate_dish_data")
    def test_update_dish_name_conflict(self, mock_validate, dish_service, mock_repository):
        """Test updating dish with conflicting name."""
        # Setup existing dish
        existing_dish = {"id": 1, "name": "Old Name"}
        mock_repository.find_by_id.return_value = existing_dish

        # Setup validation to pass
        cleaned_data = {"name": "Taken Name", "ingredients": []}
        mock_validate.return_value = (True, [], cleaned_data)

        # Setup repository to find name conflict
        mock_repository.find_by_name.return_value = {"id": 2, "name": "Taken Name"}

        # Update dish
        success, dish, errors = dish_service.update_dish(1, cleaned_data)

        # Verify failure
        assert success is False
        assert dish is None
        assert "already taken" in errors[0]


class TestDishServiceDeleteDish:
    """Test dish deletion."""

    @patch("services.dish_service.cache_manager")
    def test_delete_dish_success(self, mock_cache, dish_service, mock_repository):
        """Test successful dish deletion."""
        # Setup dish exists
        mock_repository.exists.return_value = True

        # Setup not used in logs
        mock_repository.is_used_in_logs.return_value = (False, 0)

        # Delete dish
        success, errors = dish_service.delete_dish(1)

        # Verify success
        assert success is True
        assert errors == []

        # Verify repository delete was called
        mock_repository.delete.assert_called_once_with(1)

        # Verify cache was invalidated
        mock_cache.delete.assert_called_once_with("dishes:all")

    def test_delete_dish_not_found(self, dish_service, mock_repository):
        """Test deleting nonexistent dish."""
        # Setup dish doesn't exist
        mock_repository.exists.return_value = False

        # Delete dish
        success, errors = dish_service.delete_dish(999)

        # Verify failure
        assert success is False
        assert "not found" in errors[0]

        # Verify repository delete was not called
        mock_repository.delete.assert_not_called()

    def test_delete_dish_used_in_logs(self, dish_service, mock_repository):
        """Test deleting dish that's used in logs."""
        # Setup dish exists
        mock_repository.exists.return_value = True

        # Setup used in logs
        mock_repository.is_used_in_logs.return_value = (True, 5)

        # Delete dish
        success, errors = dish_service.delete_dish(1)

        # Verify failure
        assert success is False
        assert "5" in errors[0]
        assert "log" in errors[0].lower()

        # Verify repository delete was not called
        mock_repository.delete.assert_not_called()


class TestDishServiceHelperMethods:
    """Test helper methods."""

    def test_get_dish_count(self, dish_service, mock_repository):
        """Test getting dish count."""
        mock_repository.count.return_value = 42

        count = dish_service.get_dish_count()

        assert count == 42
        mock_repository.count.assert_called_once()
