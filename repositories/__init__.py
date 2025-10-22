"""
Repository Pattern implementation for Nutricount.

Repositories abstract database access and provide a clean interface
for data operations following the Repository Pattern.
"""

from repositories.base_repository import BaseRepository
from repositories.dish_repository import DishRepository
from repositories.product_repository import ProductRepository

__all__ = ["BaseRepository", "DishRepository", "ProductRepository"]
