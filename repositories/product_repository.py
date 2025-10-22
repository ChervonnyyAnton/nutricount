"""
Product Repository implementation.

Handles all database operations for products,
abstracting data access from business logic.
"""

from typing import Any, Dict, List, Optional

from repositories.base_repository import BaseRepository
from src.nutrition_calculator import (
    calculate_calories_from_macros,
    calculate_keto_index_advanced,
    calculate_net_carbs_advanced,
)
from src.utils import clean_string, safe_float


class ProductRepository(BaseRepository):
    """Repository for product data access."""
    
    def find_all(
        self,
        search: str = "",
        limit: int = 50,
        offset: int = 0,
        include_calculated_fields: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Find all products with optional search, pagination, and calculated fields.
        
        Args:
            search: Search term for product name
            limit: Maximum number of products to return
            offset: Number of products to skip
            include_calculated_fields: Whether to include net_carbs, keto_index, etc.
            
        Returns:
            List of product dictionaries
        """
        query = """
            SELECT * FROM products
            WHERE name LIKE ?
            ORDER BY name COLLATE NOCASE
            LIMIT ? OFFSET ?
        """
        
        products = []
        for row in self.db.execute(query, (f"%{search}%", limit, offset)).fetchall():
            product = dict(row)
            
            if include_calculated_fields:
                product = self._add_calculated_fields(product)
            
            products.append(product)
        
        return products
    
    def find_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """
        Find product by ID.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product dictionary or None if not found
        """
        row = self.db.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()
        
        if not row:
            return None
        
        return dict(row)
    
    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find product by exact name.
        
        Args:
            name: Product name
            
        Returns:
            Product dictionary or None if not found
        """
        row = self.db.execute(
            "SELECT * FROM products WHERE name = ?",
            (name,)
        ).fetchone()
        
        if not row:
            return None
        
        return dict(row)
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new product with enhanced nutrition calculations.
        
        Args:
            data: Product data dictionary with required fields:
                - name: Product name
                - protein_per_100g: Protein in grams
                - fat_per_100g: Fat in grams
                - carbs_per_100g: Carbs in grams
                And optional fields:
                - fiber_per_100g, sugars_per_100g, category, etc.
            
        Returns:
            Created product dictionary with ID and calculated fields
        """
        # Extract required fields
        name = data["name"]
        protein = data["protein_per_100g"]
        fat = data["fat_per_100g"]
        carbs = data["carbs_per_100g"]
        
        # Extract optional fields
        fiber_per_100g = safe_float(data.get("fiber_per_100g"))
        sugars_per_100g = safe_float(data.get("sugars_per_100g"))
        category = data.get("category")
        processing_level = data.get("processing_level")
        glycemic_index = safe_float(data.get("glycemic_index"))
        region = clean_string(data.get("region", "US"))
        
        # Calculate enhanced nutrition values
        calculated_calories = calculate_calories_from_macros(protein, fat, carbs)
        
        net_carbs_result = calculate_net_carbs_advanced(
            carbs, fiber_per_100g, category, region
        )
        
        keto_result = calculate_keto_index_advanced(
            protein, fat, carbs, fiber_per_100g,
            category, glycemic_index, processing_level
        )
        
        # Insert product
        cursor = self.db.execute(
            """
            INSERT INTO products (
                name, calories_per_100g, protein_per_100g, fat_per_100g, carbs_per_100g,
                fiber_per_100g, sugars_per_100g, category, processing_level, glycemic_index,
                region, net_carbs_per_100g, keto_index, keto_category, carbs_score,
                fat_score, quality_score, gi_score, fiber_estimated, fiber_deduction_coefficient
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                calculated_calories,
                protein,
                fat,
                carbs,
                fiber_per_100g,
                sugars_per_100g,
                category,
                processing_level,
                glycemic_index,
                region,
                net_carbs_result["net_carbs"],
                keto_result["keto_index"],
                keto_result["keto_category"],
                keto_result["carbs_score"],
                keto_result["fat_score"],
                keto_result["quality_score"],
                keto_result["gi_score"],
                net_carbs_result["fiber_estimated"],
                net_carbs_result["fiber_deduction_coefficient"],
            ),
        )
        
        self.db.commit()
        
        # Return created product
        product_id = cursor.lastrowid
        return self.find_by_id(product_id)
    
    def update(self, product_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update existing product.
        
        Args:
            product_id: Product ID
            data: Updated product data
            
        Returns:
            Updated product dictionary or None if not found
        """
        # Check if product exists
        if not self.exists(product_id):
            return None
        
        # Extract fields
        name = data["name"]
        calories = safe_float(data.get("calories_per_100g", 0))
        protein = data["protein_per_100g"]
        fat = data["fat_per_100g"]
        carbs = data["carbs_per_100g"]
        
        # Calculate calories if not provided
        if calories == 0:
            calories = calculate_calories_from_macros(protein, fat, carbs)
        
        # Update product
        self.db.execute(
            """
            UPDATE products
            SET name = ?, calories_per_100g = ?, protein_per_100g = ?,
                fat_per_100g = ?, carbs_per_100g = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (name, calories, protein, fat, carbs, product_id),
        )
        
        self.db.commit()
        
        # Return updated product
        return self.find_by_id(product_id)
    
    def delete(self, product_id: int) -> bool:
        """
        Delete product by ID.
        
        Args:
            product_id: Product ID
            
        Returns:
            True if deleted, False if not found
        """
        cursor = self.db.execute(
            "DELETE FROM products WHERE id = ?",
            (product_id,)
        )
        
        self.db.commit()
        
        return cursor.rowcount > 0
    
    def is_used_in_logs(self, product_id: int) -> tuple[bool, int]:
        """
        Check if product is used in any log entries.
        
        Args:
            product_id: Product ID
            
        Returns:
            Tuple of (is_used, usage_count)
        """
        usage_count = self.db.execute(
            """
            SELECT COUNT(*) as count FROM log_entries
            WHERE item_type = 'product' AND item_id = ?
            """,
            (product_id,)
        ).fetchone()["count"]
        
        return usage_count > 0, usage_count
    
    def _add_calculated_fields(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add calculated fields (net_carbs, keto_index, etc.) to product.
        
        Args:
            product: Product dictionary
            
        Returns:
            Product dictionary with calculated fields added
        """
        try:
            # Calculate net carbs
            net_carbs_result = calculate_net_carbs_advanced(
                product["carbs_per_100g"],
                product.get("fiber_per_100g"),
                product.get("category"),
                product.get("region", "US"),
            )
            
            # Calculate keto index
            keto_result = calculate_keto_index_advanced(
                product["protein_per_100g"],
                product["fat_per_100g"],
                product["carbs_per_100g"],
                product.get("fiber_per_100g"),
                product.get("category"),
                product.get("glycemic_index"),
                product.get("processing_level"),
            )
            
            # Add calculated fields
            product["net_carbs"] = net_carbs_result["net_carbs"]
            product["fiber_estimated"] = net_carbs_result["fiber_estimated"]
            product["fiber_deduction_coefficient"] = net_carbs_result[
                "fiber_deduction_coefficient"
            ]
            product["keto_index"] = keto_result["keto_index"]
            product["keto_category"] = keto_result["keto_category"]
            product["carbs_score"] = keto_result["carbs_score"]
            product["fat_score"] = keto_result["fat_score"]
            product["quality_score"] = keto_result["quality_score"]
            product["gi_score"] = keto_result["gi_score"]
            
        except Exception:
            # Add default values if calculation fails
            product["net_carbs"] = product["carbs_per_100g"]
            product["fiber_estimated"] = True
            product["keto_index"] = 0
            product["keto_category"] = "Не для кето"
            product["carbs_score"] = 0
            product["fat_score"] = 0
            product["gi_score"] = 50
        
        return product
