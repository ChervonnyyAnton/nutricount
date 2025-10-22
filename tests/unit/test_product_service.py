"""
Unit tests for ProductService.

Tests the Service Layer pattern implementation,
ensuring business logic is properly separated from data access.
"""

import pytest
from unittest.mock import MagicMock, patch

from services.product_service import ProductService
from repositories.product_repository import ProductRepository


@pytest.fixture
def mock_repository():
    """Create mock ProductRepository."""
    return MagicMock(spec=ProductRepository)


@pytest.fixture
def product_service(mock_repository):
    """Create ProductService with mock repository."""
    return ProductService(mock_repository)


class TestProductServiceGetProducts:
    """Test getting products."""
    
    @patch('services.product_service.cache_manager')
    def test_get_products_from_cache(self, mock_cache, product_service, mock_repository):
        """Test getting products from cache."""
        # Setup cache to return data
        cached_products = [
            {"id": 1, "name": "Chicken", "protein_per_100g": 31.0},
            {"id": 2, "name": "Beef", "protein_per_100g": 26.0},
        ]
        mock_cache.get.return_value = cached_products
        
        # Get products
        products = product_service.get_products(search="", limit=50, offset=0)
        
        # Verify cache was checked
        mock_cache.get.assert_called_once()
        
        # Verify repository was NOT called (cache hit)
        mock_repository.find_all.assert_not_called()
        
        # Verify correct products returned
        assert products == cached_products
    
    @patch('services.product_service.cache_manager')
    def test_get_products_from_repository(self, mock_cache, product_service, mock_repository):
        """Test getting products from repository when cache misses."""
        # Setup cache to miss
        mock_cache.get.return_value = None
        
        # Setup repository to return data
        repo_products = [
            {"id": 1, "name": "Eggs", "protein_per_100g": 13.0},
        ]
        mock_repository.find_all.return_value = repo_products
        
        # Get products
        products = product_service.get_products(search="", limit=50, offset=0)
        
        # Verify repository was called
        mock_repository.find_all.assert_called_once_with(
            search="",
            limit=50,
            offset=0,
            include_calculated_fields=True
        )
        
        # Verify cache was set
        mock_cache.set.assert_called_once()
        
        # Verify correct products returned
        assert products == repo_products
    
    @patch('services.product_service.cache_manager')
    def test_get_products_applies_limit_cap(self, mock_cache, product_service, mock_repository):
        """Test that limit is capped at API_MAX_PER_PAGE."""
        mock_cache.get.return_value = None  # Cache miss
        mock_repository.find_all.return_value = []
        
        # Try to get more than max
        product_service.get_products(search="", limit=1000, offset=0)
        
        # Verify limit was capped (Config.API_MAX_PER_PAGE = 200)
        call_args = mock_repository.find_all.call_args[1]
        assert call_args['limit'] <= 200
    
    @patch('services.product_service.cache_manager')
    def test_get_products_applies_offset_minimum(self, mock_cache, product_service, mock_repository):
        """Test that negative offset is set to 0."""
        mock_cache.get.return_value = None  # Cache miss
        mock_repository.find_all.return_value = []
        
        # Try negative offset
        product_service.get_products(search="", limit=50, offset=-10)
        
        # Verify offset was set to 0
        call_args = mock_repository.find_all.call_args[1]
        assert call_args['offset'] == 0


class TestProductServiceGetProductById:
    """Test getting single product."""
    
    def test_get_product_by_id_existing(self, product_service, mock_repository):
        """Test getting existing product by ID."""
        # Setup repository
        mock_product = {"id": 1, "name": "Salmon", "protein_per_100g": 20.0}
        mock_repository.find_by_id.return_value = mock_product
        
        # Get product
        product = product_service.get_product_by_id(1)
        
        # Verify
        mock_repository.find_by_id.assert_called_once_with(1)
        assert product == mock_product
    
    def test_get_product_by_id_nonexistent(self, product_service, mock_repository):
        """Test getting non-existent product by ID."""
        # Setup repository to return None
        mock_repository.find_by_id.return_value = None
        
        # Get product
        product = product_service.get_product_by_id(99999)
        
        # Verify
        assert product is None


class TestProductServiceCreateProduct:
    """Test creating products."""
    
    @patch('services.product_service.cache_invalidate')
    @patch('services.product_service.validate_product_data')
    def test_create_product_success(
        self,
        mock_validate,
        mock_invalidate,
        product_service,
        mock_repository
    ):
        """Test successful product creation."""
        # Setup validation
        cleaned_data = {
            "name": "Tuna",
            "protein_per_100g": 30.0,
            "fat_per_100g": 1.0,
            "carbs_per_100g": 0.0,
        }
        mock_validate.return_value = (True, [], cleaned_data)
        
        # Setup repository
        mock_repository.find_by_name.return_value = None  # No duplicate
        created_product = {**cleaned_data, "id": 1}
        mock_repository.create.return_value = created_product
        
        # Create product
        success, product, errors = product_service.create_product(cleaned_data)
        
        # Verify
        assert success is True
        assert product == created_product
        assert errors == []
        mock_repository.create.assert_called_once_with(cleaned_data)
        mock_invalidate.assert_called_once_with("products:*")
    
    @patch('services.product_service.validate_product_data')
    def test_create_product_validation_fails(
        self,
        mock_validate,
        product_service,
        mock_repository
    ):
        """Test product creation with validation errors."""
        # Setup validation to fail
        validation_errors = ["Name is required", "Invalid protein value"]
        mock_validate.return_value = (False, validation_errors, None)
        
        # Create product
        data = {"name": ""}
        success, product, errors = product_service.create_product(data)
        
        # Verify
        assert success is False
        assert product is None
        assert errors == validation_errors
        mock_repository.create.assert_not_called()
    
    @patch('services.product_service.validate_product_data')
    def test_create_product_duplicate_name(
        self,
        mock_validate,
        product_service,
        mock_repository
    ):
        """Test product creation with duplicate name."""
        # Setup validation
        cleaned_data = {"name": "Existing Product", "protein_per_100g": 10.0}
        mock_validate.return_value = (True, [], cleaned_data)
        
        # Setup repository to find existing product
        mock_repository.find_by_name.return_value = {"id": 1, "name": "Existing Product"}
        
        # Create product
        success, product, errors = product_service.create_product(cleaned_data)
        
        # Verify
        assert success is False
        assert product is None
        assert "already exists" in errors[0]
        mock_repository.create.assert_not_called()


class TestProductServiceUpdateProduct:
    """Test updating products."""
    
    @patch('services.product_service.cache_invalidate')
    @patch('services.product_service.validate_product_data')
    def test_update_product_success(
        self,
        mock_validate,
        mock_invalidate,
        product_service,
        mock_repository
    ):
        """Test successful product update."""
        # Setup validation
        cleaned_data = {
            "name": "Updated Product",
            "protein_per_100g": 32.0,
            "fat_per_100g": 1.5,
            "carbs_per_100g": 0.0,
        }
        mock_validate.return_value = (True, [], cleaned_data)
        
        # Setup repository
        mock_repository.exists.return_value = True
        mock_repository.find_by_name.return_value = None  # No name conflict
        updated_product = {**cleaned_data, "id": 1}
        mock_repository.update.return_value = updated_product
        
        # Update product
        success, product, errors = product_service.update_product(1, cleaned_data)
        
        # Verify
        assert success is True
        assert product == updated_product
        assert errors == []
        mock_repository.update.assert_called_once_with(1, cleaned_data)
        mock_invalidate.assert_called_once_with("products:*")
    
    @patch('services.product_service.validate_product_data')
    def test_update_product_not_found(
        self,
        mock_validate,
        product_service,
        mock_repository
    ):
        """Test updating non-existent product."""
        # Setup repository
        mock_repository.exists.return_value = False
        
        # Update product
        data = {"name": "Product"}
        success, product, errors = product_service.update_product(99999, data)
        
        # Verify
        assert success is False
        assert product is None
        assert "not found" in errors[0]
        mock_repository.update.assert_not_called()
    
    @patch('services.product_service.validate_product_data')
    def test_update_product_name_conflict(
        self,
        mock_validate,
        product_service,
        mock_repository
    ):
        """Test updating product with conflicting name."""
        # Setup validation
        cleaned_data = {"name": "Existing Name"}
        mock_validate.return_value = (True, [], cleaned_data)
        
        # Setup repository
        mock_repository.exists.return_value = True
        # Another product has this name
        mock_repository.find_by_name.return_value = {"id": 2, "name": "Existing Name"}
        
        # Update product ID 1
        success, product, errors = product_service.update_product(1, cleaned_data)
        
        # Verify
        assert success is False
        assert product is None
        assert "already exists" in errors[0]
        mock_repository.update.assert_not_called()


class TestProductServiceDeleteProduct:
    """Test deleting products."""
    
    @patch('services.product_service.cache_invalidate')
    def test_delete_product_success(
        self,
        mock_invalidate,
        product_service,
        mock_repository
    ):
        """Test successful product deletion."""
        # Setup repository
        mock_repository.exists.return_value = True
        mock_repository.is_used_in_logs.return_value = (False, 0)
        mock_repository.delete.return_value = True
        
        # Delete product
        success, errors = product_service.delete_product(1)
        
        # Verify
        assert success is True
        assert errors == []
        mock_repository.delete.assert_called_once_with(1)
        mock_invalidate.assert_called_once_with("products:*")
    
    def test_delete_product_not_found(self, product_service, mock_repository):
        """Test deleting non-existent product."""
        # Setup repository
        mock_repository.exists.return_value = False
        
        # Delete product
        success, errors = product_service.delete_product(99999)
        
        # Verify
        assert success is False
        assert "not found" in errors[0]
        mock_repository.delete.assert_not_called()
    
    def test_delete_product_used_in_logs(self, product_service, mock_repository):
        """Test deleting product used in logs (business rule violation)."""
        # Setup repository
        mock_repository.exists.return_value = True
        mock_repository.is_used_in_logs.return_value = (True, 5)
        
        # Delete product
        success, errors = product_service.delete_product(1)
        
        # Verify
        assert success is False
        assert "used in 5 log entries" in errors[0]
        mock_repository.delete.assert_not_called()


class TestProductServiceHelperMethods:
    """Test helper methods."""
    
    @patch('services.product_service.cache_manager')
    def test_search_products(self, mock_cache, product_service, mock_repository):
        """Test search convenience method."""
        mock_cache.get.return_value = None  # Cache miss
        mock_repository.find_all.return_value = []
        
        product_service.search_products("chicken", limit=20)
        
        # Verify correct parameters passed
        call_args = mock_repository.find_all.call_args[1]
        assert call_args['search'] == "chicken"
        assert call_args['limit'] == 20
    
    def test_get_product_count(self, product_service, mock_repository):
        """Test getting product count."""
        mock_repository.count.return_value = 42
        
        count = product_service.get_product_count()
        
        assert count == 42
        mock_repository.count.assert_called_once()
