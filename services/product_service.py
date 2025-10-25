"""
Product Service - Business logic for product operations.

This service encapsulates business logic for products,
coordinating between repositories and providing a clean API
for controllers/routes.
"""

import logging
import sqlite3
from typing import Any, Dict, List, Optional

from repositories.product_repository import ProductRepository
from src.cache_manager import cache_invalidate, cache_manager
from src.config import Config
from src.utils import validate_product_data

logger = logging.getLogger(__name__)


class ProductService:
    """
    Service class for product business logic.

    Handles product operations with business rules,
    validation, caching, and coordination with repository.
    """

    def __init__(self, repository: ProductRepository):
        """
        Initialize service with repository.

        Args:
            repository: ProductRepository instance for data access
        """
        self.repository = repository

    def get_products(
        self, search: str = "", limit: int = 50, offset: int = 0, use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get products with search, pagination, and caching.

        Args:
            search: Search term for product name
            limit: Maximum number of products (capped at API_MAX_PER_PAGE)
            offset: Number of products to skip
            use_cache: Whether to use cache

        Returns:
            List of product dictionaries with calculated fields
        """
        # Apply business rules
        limit = min(limit, Config.API_MAX_PER_PAGE)
        offset = max(0, offset)

        # Try cache first
        if use_cache:
            cache_key = f"products:{search}:{limit}:{offset}"
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

        # Get from repository
        products = self.repository.find_all(
            search=search, limit=limit, offset=offset, include_calculated_fields=True
        )

        # Cache result
        if use_cache:
            cache_manager.set(cache_key, products, 300)  # 5 minutes

        return products

    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """
        Get single product by ID.

        Args:
            product_id: Product ID

        Returns:
            Product dictionary or None if not found
        """
        return self.repository.find_by_id(product_id)

    def create_product(
        self, data: Dict[str, Any]
    ) -> tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """
        Create new product with validation and business rules.

        Args:
            data: Product data dictionary

        Returns:
            Tuple of (success, product_dict, errors)
            - success: True if created successfully
            - product_dict: Created product or None
            - errors: List of validation errors
        """
        # Validate product data
        is_valid, errors, cleaned_data = validate_product_data(data)
        if not is_valid:
            return False, None, errors

        # Check for duplicate name (business rule)
        existing = self.repository.find_by_name(cleaned_data["name"])
        if existing:
            return False, None, [f"Product '{cleaned_data['name']}' already exists"]

        # Create product
        try:
            product = self.repository.create(cleaned_data)

            # Invalidate cache
            cache_invalidate("products:*")

            return True, product, []
        except sqlite3.IntegrityError as e:
            logger.error("Database integrity error creating product: %s", e)
            return False, None, ["Database constraint violation"]
        except sqlite3.Error as e:
            logger.error("Database error creating product: %s", e)
            return False, None, ["Database error occurred"]
        except Exception:
            logger.exception("Unexpected error creating product")
            return False, None, ["Failed to create product"]

    def update_product(
        self, product_id: int, data: Dict[str, Any]
    ) -> tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """
        Update existing product with validation and business rules.

        Args:
            product_id: Product ID to update
            data: Updated product data

        Returns:
            Tuple of (success, product_dict, errors)
        """
        # Check if product exists
        if not self.repository.exists(product_id):
            return False, None, ["Product not found"]

        # Validate product data
        is_valid, errors, cleaned_data = validate_product_data(data)
        if not is_valid:
            return False, None, errors

        # Check for name conflicts (excluding current product)
        existing = self.repository.find_by_name(cleaned_data["name"])
        if existing and existing["id"] != product_id:
            return False, None, [f"Product '{cleaned_data['name']}' already exists"]

        # Update product
        try:
            product = self.repository.update(product_id, cleaned_data)

            # Invalidate cache
            cache_invalidate("products:*")

            return True, product, []
        except sqlite3.IntegrityError as e:
            logger.error("Database integrity error updating product %s: %s", product_id, e)
            return False, None, ["Database constraint violation"]
        except sqlite3.Error as e:
            logger.error("Database error updating product %s: %s", product_id, e)
            return False, None, ["Database error occurred"]
        except Exception:
            logger.exception("Unexpected error updating product %s", product_id)
            return False, None, ["Failed to update product"]

    def delete_product(self, product_id: int) -> tuple[bool, List[str]]:
        """
        Delete product with business rule checks.

        Business rule: Cannot delete product used in log entries.

        Args:
            product_id: Product ID to delete

        Returns:
            Tuple of (success, errors)
        """
        # Check if product exists
        if not self.repository.exists(product_id):
            return False, ["Product not found"]

        # Business rule: Check if product is used in logs
        is_used, usage_count = self.repository.is_used_in_logs(product_id)
        if is_used:
            return False, [f"Cannot delete product: used in {usage_count} log entries"]

        # Delete product
        try:
            success = self.repository.delete(product_id)

            if success:
                # Invalidate cache
                cache_invalidate("products:*")
                return True, []
            else:
                return False, ["Failed to delete product"]
        except sqlite3.IntegrityError as e:
            logger.error("Database integrity error deleting product %s: %s", product_id, e)
            return False, ["Cannot delete product due to foreign key constraint"]
        except sqlite3.Error as e:
            logger.error("Database error deleting product %s: %s", product_id, e)
            return False, ["Database error occurred"]
        except Exception:
            logger.exception("Unexpected error deleting product %s", product_id)
            return False, ["Failed to delete product"]

    def search_products(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search products by name (convenience method).

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching products
        """
        return self.get_products(search=query, limit=limit)

    def get_product_count(self) -> int:
        """
        Get total number of products.

        Returns:
            Count of products
        """
        return self.repository.count()
