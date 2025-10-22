"""
Unit tests for ProductRepository.

Tests the Repository Pattern implementation for products,
ensuring proper abstraction of database operations.
"""

import pytest
import sqlite3
from repositories.product_repository import ProductRepository


@pytest.fixture
def db_connection():
    """Create in-memory database for testing."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    
    # Create products table
    conn.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            calories_per_100g REAL,
            protein_per_100g REAL NOT NULL,
            fat_per_100g REAL NOT NULL,
            carbs_per_100g REAL NOT NULL,
            fiber_per_100g REAL,
            sugars_per_100g REAL,
            category TEXT,
            processing_level TEXT,
            glycemic_index REAL,
            region TEXT DEFAULT 'US',
            net_carbs_per_100g REAL,
            keto_index REAL,
            keto_category TEXT,
            carbs_score REAL,
            fat_score REAL,
            quality_score REAL,
            gi_score REAL,
            fiber_estimated INTEGER,
            fiber_deduction_coefficient REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create log_entries table for testing is_used_in_logs
    conn.execute("""
        CREATE TABLE log_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            date TEXT NOT NULL
        )
    """)
    
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def product_repo(db_connection):
    """Create ProductRepository instance."""
    return ProductRepository(db_connection)


class TestProductRepositoryCreate:
    """Test product creation."""
    
    def test_create_product_minimal(self, product_repo):
        """Test creating product with minimal required fields."""
        data = {
            "name": "Chicken Breast",
            "protein_per_100g": 31.0,
            "fat_per_100g": 3.6,
            "carbs_per_100g": 0.0,
        }
        
        product = product_repo.create(data)
        
        assert product is not None
        assert product["id"] > 0
        assert product["name"] == "Chicken Breast"
        assert product["protein_per_100g"] == 31.0
        assert product["fat_per_100g"] == 3.6
        assert product["carbs_per_100g"] == 0.0
        # Calculated calories: 31*4 + 3.6*9 + 0*4 = 156.4
        assert 150 < product["calories_per_100g"] < 160
    
    def test_create_product_with_optional_fields(self, product_repo):
        """Test creating product with optional nutrition fields."""
        data = {
            "name": "Avocado",
            "protein_per_100g": 2.0,
            "fat_per_100g": 15.0,
            "carbs_per_100g": 9.0,
            "fiber_per_100g": 7.0,
            "sugars_per_100g": 0.7,
            "category": "Vegetables",
            "region": "US",
        }
        
        product = product_repo.create(data)
        
        assert product is not None
        assert product["name"] == "Avocado"
        assert product["fiber_per_100g"] == 7.0
        assert product["category"] == "Vegetables"
        # Net carbs should be lower than total carbs due to fiber
        assert product["net_carbs_per_100g"] < product["carbs_per_100g"]
    
    def test_create_product_calculates_keto_fields(self, product_repo):
        """Test that keto index and related fields are calculated."""
        data = {
            "name": "Butter",
            "protein_per_100g": 0.9,
            "fat_per_100g": 81.0,
            "carbs_per_100g": 0.1,
        }
        
        product = product_repo.create(data)
        
        assert "keto_index" in product
        assert "keto_category" in product
        assert "carbs_score" in product
        assert "fat_score" in product
        # High-fat, low-carb should have good keto index
        assert product["keto_index"] > 70


class TestProductRepositoryFind:
    """Test product retrieval."""
    
    def test_find_by_id_existing(self, product_repo):
        """Test finding product by existing ID."""
        # Create product
        data = {
            "name": "Eggs",
            "protein_per_100g": 13.0,
            "fat_per_100g": 11.0,
            "carbs_per_100g": 1.1,
        }
        created = product_repo.create(data)
        
        # Find by ID
        found = product_repo.find_by_id(created["id"])
        
        assert found is not None
        assert found["id"] == created["id"]
        assert found["name"] == "Eggs"
    
    def test_find_by_id_nonexistent(self, product_repo):
        """Test finding product by non-existent ID."""
        found = product_repo.find_by_id(99999)
        assert found is None
    
    def test_find_by_name_existing(self, product_repo):
        """Test finding product by name."""
        # Create product
        data = {
            "name": "Salmon",
            "protein_per_100g": 20.0,
            "fat_per_100g": 13.0,
            "carbs_per_100g": 0.0,
        }
        product_repo.create(data)
        
        # Find by name
        found = product_repo.find_by_name("Salmon")
        
        assert found is not None
        assert found["name"] == "Salmon"
    
    def test_find_by_name_nonexistent(self, product_repo):
        """Test finding product by non-existent name."""
        found = product_repo.find_by_name("Nonexistent Product")
        assert found is None
    
    def test_find_all_empty(self, product_repo):
        """Test finding all products when none exist."""
        products = product_repo.find_all()
        assert products == []
    
    def test_find_all_multiple_products(self, product_repo):
        """Test finding all products."""
        # Create multiple products
        products_data = [
            {"name": "Beef", "protein_per_100g": 26.0, "fat_per_100g": 15.0, "carbs_per_100g": 0.0},
            {"name": "Pork", "protein_per_100g": 21.0, "fat_per_100g": 14.0, "carbs_per_100g": 0.0},
            {"name": "Lamb", "protein_per_100g": 25.0, "fat_per_100g": 21.0, "carbs_per_100g": 0.0},
        ]
        
        for data in products_data:
            product_repo.create(data)
        
        # Find all
        products = product_repo.find_all()
        
        assert len(products) == 3
        names = [p["name"] for p in products]
        assert "Beef" in names
        assert "Pork" in names
        assert "Lamb" in names
    
    def test_find_all_with_search(self, product_repo):
        """Test finding products with search term."""
        # Create products
        products_data = [
            {"name": "Chicken Breast", "protein_per_100g": 31.0, "fat_per_100g": 3.6, "carbs_per_100g": 0.0},
            {"name": "Chicken Thigh", "protein_per_100g": 26.0, "fat_per_100g": 7.0, "carbs_per_100g": 0.0},
            {"name": "Beef Steak", "protein_per_100g": 26.0, "fat_per_100g": 15.0, "carbs_per_100g": 0.0},
        ]
        
        for data in products_data:
            product_repo.create(data)
        
        # Search for "chicken"
        products = product_repo.find_all(search="Chicken")
        
        assert len(products) == 2
        assert all("Chicken" in p["name"] for p in products)
    
    def test_find_all_with_pagination(self, product_repo):
        """Test finding products with pagination."""
        # Create 10 products
        for i in range(10):
            data = {
                "name": f"Product {i}",
                "protein_per_100g": 10.0,
                "fat_per_100g": 5.0,
                "carbs_per_100g": 2.0,
            }
            product_repo.create(data)
        
        # Get first page (5 items)
        page1 = product_repo.find_all(limit=5, offset=0)
        assert len(page1) == 5
        
        # Get second page (5 items)
        page2 = product_repo.find_all(limit=5, offset=5)
        assert len(page2) == 5
        
        # Ensure no overlap
        page1_ids = {p["id"] for p in page1}
        page2_ids = {p["id"] for p in page2}
        assert len(page1_ids.intersection(page2_ids)) == 0


class TestProductRepositoryUpdate:
    """Test product updates."""
    
    def test_update_product_existing(self, product_repo):
        """Test updating existing product."""
        # Create product
        data = {
            "name": "Tuna",
            "protein_per_100g": 30.0,
            "fat_per_100g": 1.0,
            "carbs_per_100g": 0.0,
        }
        created = product_repo.create(data)
        
        # Update product
        update_data = {
            "name": "Tuna (updated)",
            "protein_per_100g": 32.0,
            "fat_per_100g": 1.5,
            "carbs_per_100g": 0.0,
        }
        updated = product_repo.update(created["id"], update_data)
        
        assert updated is not None
        assert updated["name"] == "Tuna (updated)"
        assert updated["protein_per_100g"] == 32.0
    
    def test_update_product_nonexistent(self, product_repo):
        """Test updating non-existent product."""
        update_data = {
            "name": "Ghost Product",
            "protein_per_100g": 10.0,
            "fat_per_100g": 5.0,
            "carbs_per_100g": 2.0,
        }
        updated = product_repo.update(99999, update_data)
        
        assert updated is None


class TestProductRepositoryDelete:
    """Test product deletion."""
    
    def test_delete_product_existing(self, product_repo):
        """Test deleting existing product."""
        # Create product
        data = {
            "name": "Turkey",
            "protein_per_100g": 29.0,
            "fat_per_100g": 7.0,
            "carbs_per_100g": 0.0,
        }
        created = product_repo.create(data)
        
        # Delete product
        result = product_repo.delete(created["id"])
        
        assert result is True
        
        # Verify deleted
        found = product_repo.find_by_id(created["id"])
        assert found is None
    
    def test_delete_product_nonexistent(self, product_repo):
        """Test deleting non-existent product."""
        result = product_repo.delete(99999)
        assert result is False


class TestProductRepositoryHelpers:
    """Test helper methods."""
    
    def test_exists_true(self, product_repo):
        """Test exists() for existing product."""
        # Create product
        data = {
            "name": "Duck",
            "protein_per_100g": 19.0,
            "fat_per_100g": 12.0,
            "carbs_per_100g": 0.0,
        }
        created = product_repo.create(data)
        
        assert product_repo.exists(created["id"]) is True
    
    def test_exists_false(self, product_repo):
        """Test exists() for non-existent product."""
        assert product_repo.exists(99999) is False
    
    def test_count_empty(self, product_repo):
        """Test count() when no products exist."""
        assert product_repo.count() == 0
    
    def test_count_multiple(self, product_repo):
        """Test count() with multiple products."""
        # Create 5 products
        for i in range(5):
            data = {
                "name": f"Product {i}",
                "protein_per_100g": 10.0,
                "fat_per_100g": 5.0,
                "carbs_per_100g": 2.0,
            }
            product_repo.create(data)
        
        assert product_repo.count() == 5
    
    def test_is_used_in_logs_false(self, product_repo, db_connection):
        """Test is_used_in_logs() when product is not used."""
        # Create product
        data = {
            "name": "Unused Product",
            "protein_per_100g": 10.0,
            "fat_per_100g": 5.0,
            "carbs_per_100g": 2.0,
        }
        created = product_repo.create(data)
        
        is_used, count = product_repo.is_used_in_logs(created["id"])
        
        assert is_used is False
        assert count == 0
    
    def test_is_used_in_logs_true(self, product_repo, db_connection):
        """Test is_used_in_logs() when product is used."""
        # Create product
        data = {
            "name": "Used Product",
            "protein_per_100g": 10.0,
            "fat_per_100g": 5.0,
            "carbs_per_100g": 2.0,
        }
        created = product_repo.create(data)
        
        # Add log entries
        db_connection.execute(
            "INSERT INTO log_entries (item_type, item_id, date) VALUES (?, ?, ?)",
            ("product", created["id"], "2025-10-22")
        )
        db_connection.execute(
            "INSERT INTO log_entries (item_type, item_id, date) VALUES (?, ?, ?)",
            ("product", created["id"], "2025-10-23")
        )
        db_connection.commit()
        
        is_used, count = product_repo.is_used_in_logs(created["id"])
        
        assert is_used is True
        assert count == 2
