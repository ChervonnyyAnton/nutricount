"""
Integration tests for dishes routes.
Tests comprehensive dish CRUD operations including error cases.
"""

from unittest.mock import patch


def test_create_dish_duplicate_name(client, app):
    """Test creating a dish with duplicate name"""
    # First, create a product to use in ingredients
    product_data = {
        "name": "Test Product",
        "calories_per_100g": 100,
        "protein_per_100g": 10,
        "fat_per_100g": 5,
        "carbs_per_100g": 15,
    }
    product_response = client.post("/api/products", json=product_data)
    assert product_response.status_code == 201
    product_id = product_response.json["data"]["id"]

    # Create first dish
    dish_data = {
        "name": "Test Dish",
        "ingredients": [{"product_id": product_id, "quantity_grams": 100}],
    }
    response1 = client.post("/api/dishes", json=dish_data)
    assert response1.status_code == 201

    # Try to create duplicate
    response2 = client.post("/api/dishes", json=dish_data)
    assert response2.status_code == 400
    assert "already exists" in str(response2.json.get("errors", []))


def test_create_dish_missing_product(client, app):
    """Test creating a dish with non-existent product"""
    dish_data = {
        "name": "Test Dish",
        "ingredients": [{"product_id": 99999, "quantity_grams": 100}],
    }
    response = client.post("/api/dishes", json=dish_data)
    assert response.status_code == 400
    assert "do not exist" in str(response.json.get("errors", []))


def test_create_dish_exception_handling(client, app):
    """Test exception handling when creating dish"""
    with patch("routes.dishes.get_db") as mock_get_db:
        mock_db = mock_get_db.return_value
        mock_db.execute.side_effect = Exception("Database error")
        mock_db.close = lambda: None

        dish_data = {
            "name": "Test Dish",
            "ingredients": [{"product_id": 1, "quantity_grams": 100}],
        }
        response = client.post("/api/dishes", json=dish_data)
        assert response.status_code == 500
        assert "error" in response.json["message"].lower()


def test_update_dish_invalid_json(client, app):
    """Test updating dish with invalid JSON"""
    # Create a dish first
    product_data = {
        "name": "Test Product",
        "calories_per_100g": 100,
        "protein_per_100g": 10,
        "fat_per_100g": 5,
        "carbs_per_100g": 15,
    }
    product_response = client.post("/api/products", json=product_data)
    product_id = product_response.json["data"]["id"]

    dish_data = {
        "name": "Test Dish",
        "ingredients": [{"product_id": product_id, "quantity_grams": 100}],
    }
    dish_response = client.post("/api/dishes", json=dish_data)
    dish_id = dish_response.json["data"]["id"]

    # Send invalid JSON (empty content type or malformed)
    with patch("routes.dishes.safe_get_json", return_value=None):
        response = client.put(f"/api/dishes/{dish_id}", data="invalid")
        assert response.status_code == 400
        assert "Invalid JSON" in response.json["message"]


def test_update_dish_missing_name(client, app):
    """Test updating dish without name"""
    # Create a dish first
    product_data = {
        "name": "Test Product",
        "calories_per_100g": 100,
        "protein_per_100g": 10,
        "fat_per_100g": 5,
        "carbs_per_100g": 15,
    }
    product_response = client.post("/api/products", json=product_data)
    product_id = product_response.json["data"]["id"]

    dish_data = {
        "name": "Test Dish",
        "ingredients": [{"product_id": product_id, "quantity_grams": 100}],
    }
    dish_response = client.post("/api/dishes", json=dish_data)
    dish_id = dish_response.json["data"]["id"]

    # Update without name
    response = client.put(f"/api/dishes/{dish_id}", json={"name": ""})
    assert response.status_code == 400
    assert "required" in str(response.json.get("errors", [])).lower()


def test_update_dish_not_found(client, app):
    """Test updating non-existent dish"""
    response = client.put("/api/dishes/99999", json={"name": "Updated Dish"})
    assert response.status_code == 404
    assert "not found" in response.json["message"].lower()


def test_update_dish_name_conflict(client, app):
    """Test updating dish with name that already exists"""
    # Create a product
    product_data = {
        "name": "Test Product",
        "calories_per_100g": 100,
        "protein_per_100g": 10,
        "fat_per_100g": 5,
        "carbs_per_100g": 15,
    }
    product_response = client.post("/api/products", json=product_data)
    product_id = product_response.json["data"]["id"]

    # Create two dishes
    dish1_data = {
        "name": "Dish One",
        "ingredients": [{"product_id": product_id, "quantity_grams": 100}],
    }
    client.post("/api/dishes", json=dish1_data)  # Just ensure it exists

    dish2_data = {
        "name": "Dish Two",
        "ingredients": [{"product_id": product_id, "quantity_grams": 100}],
    }
    dish2_response = client.post("/api/dishes", json=dish2_data)
    dish2_id = dish2_response.json["data"]["id"]

    # Try to update dish2 with dish1's name (must include ingredients for validation)
    response = client.put(
        f"/api/dishes/{dish2_id}",
        json={
            "name": "Dish One",
            "ingredients": [{"product_id": product_id, "quantity_grams": 100}]
        }
    )
    assert response.status_code == 400
    assert "already" in str(response.json.get("errors", []))


def test_delete_dish_with_log_entries(client, app):
    """Test deleting dish that is used in log entries"""
    # Create a product
    product_data = {
        "name": "Test Product",
        "calories_per_100g": 100,
        "protein_per_100g": 10,
        "fat_per_100g": 5,
        "carbs_per_100g": 15,
    }
    product_response = client.post("/api/products", json=product_data)
    product_id = product_response.json["data"]["id"]

    # Create a dish
    dish_data = {
        "name": "Test Dish",
        "ingredients": [{"product_id": product_id, "quantity_grams": 100}],
    }
    dish_response = client.post("/api/dishes", json=dish_data)
    dish_id = dish_response.json["data"]["id"]

    # Manually insert log entry into database to bypass validation
    with app.app_context():
        from routes.helpers import get_db
        db = get_db()
        db.execute(
            "INSERT INTO log_entries (date, item_type, item_id, quantity_grams, meal_time) VALUES (?, ?, ?, ?, ?)",
            ("2024-01-01", "dish", dish_id, 100.0, "breakfast")
        )
        db.commit()
        db.close()

    # Try to delete dish
    response = client.delete(f"/api/dishes/{dish_id}")
    assert response.status_code == 400
    assert "Cannot delete" in response.json["message"]
    assert "used in" in response.json["message"]


def test_delete_dish_not_found(client, app):
    """Test deleting non-existent dish"""
    response = client.delete("/api/dishes/99999")
    assert response.status_code == 404
    assert "not found" in response.json["message"].lower()


def test_dish_detail_exception_handling(client, app):
    """Test exception handling in dish detail endpoint"""
    with patch("routes.dishes.get_db") as mock_get_db:
        mock_db = mock_get_db.return_value
        mock_db.execute.side_effect = Exception("Database error")
        mock_db.close = lambda: None

        response = client.get("/api/dishes/1")
        assert response.status_code == 500
        assert "error" in response.json["message"].lower()


def test_dish_create_integrity_error(client, app):
    """Test IntegrityError handling in dish creation"""
    import sqlite3
    from unittest.mock import MagicMock

    # First create a valid product
    product_data = {
        "name": "Test Product for Dish Integrity",
        "category": "leafy_vegetables",
        "proteins": 5.0,
        "fats": 2.0,
        "carbs": 10.0,
        "calories": 80.0
    }
    product_response = client.post("/api/products", json=product_data)
    assert product_response.status_code == 201
    product_id = product_response.json["data"]["id"]

    dish_data = {
        "name": "Test Dish with Integrity Error",
        "preparation_method": "Raw",
        "edible_portion": 95.0,
        "ingredients": [
            {"product_id": product_id, "quantity": 100.0}
        ]
    }

    # Mock database to raise IntegrityError after validation passes
    with patch("routes.dishes.get_db") as mock_get_db:
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Mock fetchone to return valid product data for ingredient validation
        mock_db.execute.return_value.fetchone.return_value = {
            "id": product_id,
            "name": "Test Product",
            "proteins_per_100g": 5.0,
            "fats_per_100g": 2.0,
            "carbs_per_100g": 10.0,
            "calories_per_100g": 80.0
        }
        # But when execute is called for insertion, raise IntegrityError
        mock_db.execute.side_effect = [
            MagicMock(fetchone=lambda: {"id": product_id}),  # First call for product check
            sqlite3.IntegrityError("UNIQUE constraint failed")  # Second call for insertion
        ]

        response = client.post("/api/dishes", json=dish_data)
        assert response.status_code == 400
        data = response.json
        assert data["status"] == "error"
        # Check for database or constraint error
        assert "database" in data["message"].lower() or "failed" in data["message"].lower()
