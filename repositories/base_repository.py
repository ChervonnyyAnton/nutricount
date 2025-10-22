"""
Base Repository class for implementing the Repository Pattern.

This abstract base class provides common database operations
and enforces a consistent interface across all repositories.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseRepository(ABC):
    """
    Abstract base repository class.
    
    All repositories should inherit from this class and implement
    the required abstract methods.
    """
    
    def __init__(self, db):
        """
        Initialize repository with database connection.
        
        Args:
            db: SQLite database connection
        """
        self.db = db
    
    @abstractmethod
    def find_all(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Find all entities matching optional criteria.
        
        Returns:
            List of entity dictionaries
        """
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[Dict[str, Any]]:
        """
        Find entity by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Entity dictionary or None if not found
        """
        pass
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new entity.
        
        Args:
            data: Entity data dictionary
            
        Returns:
            Created entity dictionary with ID
        """
        pass
    
    @abstractmethod
    def update(self, entity_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update existing entity.
        
        Args:
            entity_id: Entity ID
            data: Updated entity data
            
        Returns:
            Updated entity dictionary or None if not found
        """
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """
        Delete entity by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    def exists(self, entity_id: int) -> bool:
        """
        Check if entity exists.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            True if exists, False otherwise
        """
        return self.find_by_id(entity_id) is not None
    
    def count(self, **kwargs) -> int:
        """
        Count entities matching optional criteria.
        
        Returns:
            Number of entities
        """
        return len(self.find_all(**kwargs))
