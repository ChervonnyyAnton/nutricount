"""
Unit tests for DishRepository.

Tests the Repository Pattern implementation for dishes (recipes),
ensuring proper abstraction of database operations and recipe calculations.
"""

import pytest
import sqlite3
from repositories.dish_repository import DishRepository


@pytest.fixture
def db_connection():
    """Create in-memory database for testing."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    # Create dishes table
    conn.execute(
        """
        CREATE TABLE dishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            total_weight_grams REAL,
            cooked_weight_grams REAL,
            calories_per_100g REAL,
            protein_per_100g REAL,
            fat_per_100g REAL,
            carbs_per_100g REAL,
            net_carbs_per_100g REAL,
            fiber_per_100g REAL,
            keto_index REAL,
            keto_category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Create products table (needed for ingredients)
    conn.execute(
        """
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            protein_per_100g REAL NOT NULL,
            fat_per_100g REAL NOT NULL,
            carbs_per_100g REAL NOT NULL,
            fiber_per_100g REAL DEFAULT 0,
            sugars_per_100g REAL DEFAULT 0,
            category TEXT DEFAULT 'unknown'
        )
    """
    )

    # Create dish_ingredients table
    conn.execute(
        """
        CREATE TABLE dish_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dish_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity_grams REAL NOT NULL,
            preparation_method TEXT DEFAULT 'raw',
            edible_portion REAL DEFAULT 1.0,
            FOREIGN KEY (dish_id) REFERENCES dishes (id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    """
    )

    # Create log_entries table for testing is_used_in_logs
    conn.execute(
        """
        CREATE TABLE log_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            date TEXT NOT NULL
        )
    """
    )

    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def dish_repo(db_connection):
    """Create DishRepository instance."""
    return DishRepository(db_connection)


@pytest.fixture
def sample_products(db_connection):
    """Create sample products for testing."""
    products = [
        (1, "Chicken Breast", 31.0, 3.6, 0.0, 0.0, 0.0, "meat"),
        (2, "Olive Oil", 0.0, 100.0, 0.0, 0.0, 0.0, "fats"),
        (3, "Broccoli", 2.8, 0.4, 7.0, 2.6, 1.7, "vegetables"),
    ]

    for product in products:
        db_connection.execute(
            """INSERT INTO products (id, name, protein_per_100g, fat_per_100g,
               carbs_per_100g, fiber_per_100g, sugars_per_100g, category)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            product,
        )
    db_connection.commit()

    return products


class TestDishRepositoryCreate:
    """Test dish creation."""

    def test_create_dish_with_single_ingredient(self, dish_repo, sample_products):
        """Test creating dish with single ingredient."""
        data = {
            "name": "Grilled Chicken",
            "description": "Simple grilled chicken breast",
            "ingredients": [
                {
                    "product_id": 1,
                    "quantity_grams": 200.0,
                    "preparation_method": "grilled",
                    "edible_portion": 1.0,
                }
            ],
        }

        dish = dish_repo.create(data)

        assert dish is not None
        assert dish["id"] > 0
        assert dish["name"] == "Grilled Chicken"
        assert dish["description"] == "Simple grilled chicken breast"
        # Check that nutrition was calculated
        assert dish["protein_per_100g"] > 0
        assert dish["calories_per_100g"] > 0
        # Check that ingredients were stored
        assert len(dish["ingredients"]) == 1

    def test_create_dish_with_multiple_ingredients(self, dish_repo, sample_products):
        """Test creating dish with multiple ingredients."""
        data = {
            "name": "Chicken with Veggies",
            "description": "Healthy meal",
            "ingredients": [
                {"product_id": 1, "quantity_grams": 150.0},
                {"product_id": 2, "quantity_grams": 10.0},
                {"product_id": 3, "quantity_grams": 100.0},
            ],
        }

        dish = dish_repo.create(data)

        assert dish is not None
        assert len(dish["ingredients"]) == 3
        # Check calculated fields
        assert dish["total_weight_grams"] > 0
        assert dish["cooked_weight_grams"] > 0
        assert dish["keto_index"] is not None
        assert dish["keto_category"] is not None

    def test_create_dish_calculates_keto_fields(self, dish_repo, sample_products):
        """Test that dish creation calculates keto-specific fields."""
        data = {
            "name": "Keto Meal",
            "ingredients": [
                {"product_id": 1, "quantity_grams": 100.0},  # High protein
                {"product_id": 2, "quantity_grams": 20.0},  # High fat
            ],
        }

        dish = dish_repo.create(data)

        # Should have keto fields calculated
        assert "keto_index" in dish
        assert "keto_category" in dish
        assert "net_carbs_per_100g" in dish
        # High fat/protein should result in good keto index
        assert dish["keto_index"] > 50  # Good for keto


class TestDishRepositoryFind:
    """Test finding dishes."""

    def test_find_all_empty(self, dish_repo):
        """Test finding all dishes when none exist."""
        dishes = dish_repo.find_all()

        assert dishes == []

    def test_find_all_multiple_dishes(self, dish_repo, sample_products):
        """Test finding all dishes with multiple dishes."""
        # Create two dishes
        dish_repo.create(
            {"name": "Dish One", "ingredients": [{"product_id": 1, "quantity_grams": 100.0}]}
        )
        dish_repo.create(
            {"name": "Dish Two", "ingredients": [{"product_id": 2, "quantity_grams": 50.0}]}
        )

        dishes = dish_repo.find_all()

        assert len(dishes) == 2
        # Should be ordered by name
        assert dishes[0]["name"] == "Dish One"
        assert dishes[1]["name"] == "Dish Two"

    def test_find_by_id_existing(self, dish_repo, sample_products):
        """Test finding dish by ID when it exists."""
        created = dish_repo.create(
            {"name": "Test Dish", "ingredients": [{"product_id": 1, "quantity_grams": 100.0}]}
        )

        dish = dish_repo.find_by_id(created["id"])

        assert dish is not None
        assert dish["id"] == created["id"]
        assert dish["name"] == "Test Dish"
        assert "ingredients" in dish
        assert len(dish["ingredients"]) > 0

    def test_find_by_id_nonexistent(self, dish_repo):
        """Test finding dish by ID when it doesn't exist."""
        dish = dish_repo.find_by_id(999)

        assert dish is None

    def test_find_by_name_existing(self, dish_repo, sample_products):
        """Test finding dish by name when it exists."""
        dish_repo.create(
            {"name": "Unique Name", "ingredients": [{"product_id": 1, "quantity_grams": 100.0}]}
        )

        found = dish_repo.find_by_name("Unique Name")

        assert found is not None
        assert "id" in found

    def test_find_by_name_nonexistent(self, dish_repo):
        """Test finding dish by name when it doesn't exist."""
        found = dish_repo.find_by_name("Nonexistent Dish")

        assert found is None


class TestDishRepositoryUpdate:
    """Test dish updates."""

    def test_update_dish_basic_info(self, dish_repo, sample_products):
        """Test updating dish basic information."""
        created = dish_repo.create(
            {
                "name": "Original Name",
                "description": "Original description",
                "ingredients": [{"product_id": 1, "quantity_grams": 100.0}],
            }
        )

        updated = dish_repo.update(
            created["id"], {"name": "Updated Name", "description": "Updated description"}
        )

        assert updated is not None
        assert updated["name"] == "Updated Name"
        assert updated["description"] == "Updated description"

    def test_update_dish_ingredients(self, dish_repo, sample_products):
        """Test updating dish ingredients."""
        created = dish_repo.create(
            {"name": "Test Dish", "ingredients": [{"product_id": 1, "quantity_grams": 100.0}]}
        )

        updated = dish_repo.update(
            created["id"],
            {
                "name": "Test Dish",
                "ingredients": [
                    {"product_id": 1, "quantity_grams": 150.0},
                    {"product_id": 2, "quantity_grams": 10.0},
                ],
            },
        )

        assert updated is not None
        assert len(updated["ingredients"]) == 2
        # Nutrition should be recalculated
        assert updated["calories_per_100g"] != created["calories_per_100g"]

    def test_update_dish_nonexistent(self, dish_repo):
        """Test updating dish that doesn't exist."""
        updated = dish_repo.update(999, {"name": "New Name"})

        assert updated is None


class TestDishRepositoryDelete:
    """Test dish deletion."""

    def test_delete_dish_existing(self, dish_repo, sample_products):
        """Test deleting existing dish."""
        created = dish_repo.create(
            {"name": "To Delete", "ingredients": [{"product_id": 1, "quantity_grams": 100.0}]}
        )

        result = dish_repo.delete(created["id"])

        assert result is True
        # Verify dish is gone
        assert dish_repo.find_by_id(created["id"]) is None

    def test_delete_dish_nonexistent(self, dish_repo):
        """Test deleting dish that doesn't exist."""
        result = dish_repo.delete(999)

        assert result is False

    def test_delete_dish_removes_ingredients(self, dish_repo, sample_products):
        """Test that deleting dish also removes ingredients."""
        created = dish_repo.create(
            {
                "name": "With Ingredients",
                "ingredients": [
                    {"product_id": 1, "quantity_grams": 100.0},
                    {"product_id": 2, "quantity_grams": 50.0},
                ],
            }
        )

        # Delete dish
        dish_repo.delete(created["id"])

        # Check that ingredients were also deleted
        ingredients = dish_repo.db.execute(
            "SELECT * FROM dish_ingredients WHERE dish_id = ?", (created["id"],)
        ).fetchall()

        assert len(ingredients) == 0


class TestDishRepositoryHelpers:
    """Test helper methods."""

    def test_exists_true(self, dish_repo, sample_products):
        """Test exists returns True for existing dish."""
        created = dish_repo.create(
            {"name": "Existing Dish", "ingredients": [{"product_id": 1, "quantity_grams": 100.0}]}
        )

        assert dish_repo.exists(created["id"]) is True

    def test_exists_false(self, dish_repo):
        """Test exists returns False for nonexistent dish."""
        assert dish_repo.exists(999) is False

    def test_count_empty(self, dish_repo):
        """Test count with no dishes."""
        assert dish_repo.count() == 0

    def test_count_multiple(self, dish_repo, sample_products):
        """Test count with multiple dishes."""
        dish_repo.create(
            {"name": "Dish 1", "ingredients": [{"product_id": 1, "quantity_grams": 100.0}]}
        )
        dish_repo.create(
            {"name": "Dish 2", "ingredients": [{"product_id": 2, "quantity_grams": 50.0}]}
        )

        assert dish_repo.count() == 2

    def test_is_used_in_logs_false(self, dish_repo, sample_products):
        """Test is_used_in_logs returns False when not used."""
        created = dish_repo.create(
            {"name": "Unused Dish", "ingredients": [{"product_id": 1, "quantity_grams": 100.0}]}
        )

        is_used, count = dish_repo.is_used_in_logs(created["id"])

        assert is_used is False
        assert count == 0

    def test_is_used_in_logs_true(self, dish_repo, sample_products):
        """Test is_used_in_logs returns True when used in logs."""
        created = dish_repo.create(
            {"name": "Used Dish", "ingredients": [{"product_id": 1, "quantity_grams": 100.0}]}
        )

        # Add to log
        dish_repo.db.execute(
            "INSERT INTO log_entries (item_type, item_id, date) VALUES ('dish', ?, '2025-01-01')",
            (created["id"],),
        )
        dish_repo.db.commit()

        is_used, count = dish_repo.is_used_in_logs(created["id"])

        assert is_used is True
        assert count == 1

    def test_verify_products_exist_all_exist(self, dish_repo, sample_products):
        """Test verify_products_exist when all products exist."""
        all_exist, missing = dish_repo.verify_products_exist([1, 2, 3])

        assert all_exist is True
        assert missing == []

    def test_verify_products_exist_some_missing(self, dish_repo, sample_products):
        """Test verify_products_exist when some products don't exist."""
        all_exist, missing = dish_repo.verify_products_exist([1, 2, 999, 998])

        assert all_exist is False
        assert 999 in missing
        assert 998 in missing

    def test_verify_products_exist_empty_list(self, dish_repo):
        """Test verify_products_exist with empty list."""
        all_exist, missing = dish_repo.verify_products_exist([])

        assert all_exist is True
        assert missing == []
