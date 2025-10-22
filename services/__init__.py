"""
Service Layer for Nutricount application.

Services contain business logic and coordinate between
repositories and routes, following the Service Layer pattern.
"""

from services.product_service import ProductService

__all__ = ["ProductService"]
