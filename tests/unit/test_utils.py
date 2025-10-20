"""
Unit tests for src/utils.py
"""

import pytest
from unittest.mock import patch, Mock, mock_open, MagicMock
import sqlite3
from datetime import date, datetime, timezone
from src.utils import (
    safe_float,
    safe_int,
    clean_string,
    get_keto_rating,
    format_date,
    parse_date,
    json_response,
    validate_nutrition_values,
    validate_product_data,
    validate_dish_data,
    validate_log_data,
    get_database_stats,
    database_connection
)


class TestSafeFloat:
    """Test safe_float function"""
    
    def test_safe_float_valid_values(self):
        """Test safe_float with valid values"""
        assert safe_float("123.45") == 123.45
        assert safe_float(123) == 123.0
        assert safe_float(123.45) == 123.45
        assert safe_float(0) == 0.0
        assert safe_float(-123.45) == -123.45
    
    def test_safe_float_none_value(self):
        """Test safe_float with None value"""
        assert safe_float(None) == 0.0
        assert safe_float(None, default=5.0) == 5.0
    
    def test_safe_float_invalid_values(self):
        """Test safe_float with invalid values"""
        assert safe_float("invalid") == 0.0
        assert safe_float("invalid", default=5.0) == 5.0
        assert safe_float([1, 2, 3]) == 0.0
        assert safe_float({"key": "value"}) == 0.0
    
    def test_safe_float_nan_infinity(self):
        """Test safe_float with NaN and infinity values"""
        import math
        assert safe_float(float('nan')) == 0.0
        assert safe_float(float('inf')) == 0.0
        assert safe_float(float('-inf')) == 0.0
        assert safe_float(math.nan) == 0.0


class TestSafeInt:
    """Test safe_int function"""
    
    def test_safe_int_valid_values(self):
        """Test safe_int with valid values"""
        assert safe_int("123") == 123
        assert safe_int(123) == 123
        assert safe_int(123.45) == 123
        assert safe_int(0) == 0
        assert safe_int(-123) == -123
    
    def test_safe_int_none_value(self):
        """Test safe_int with None value"""
        assert safe_int(None) == 0
        assert safe_int(None, default=5) == 5
    
    def test_safe_int_invalid_values(self):
        """Test safe_int with invalid values"""
        assert safe_int("invalid") == 0
        assert safe_int("invalid", default=5) == 5
        assert safe_int([1, 2, 3]) == 0
        assert safe_int({"key": "value"}) == 0


class TestCleanString:
    """Test clean_string function"""
    
    def test_clean_string_valid(self):
        """Test clean_string with valid input"""
        assert clean_string("  hello   world  ") == "hello world"
        assert clean_string("test") == "test"
        assert clean_string("") == ""
        assert clean_string(None) == ""
    
    def test_clean_string_max_length(self):
        """Test clean_string with max_length parameter"""
        long_string = "a" * 150
        result = clean_string(long_string, max_length=100)
        assert len(result) == 100
        assert result == "a" * 100
    
    def test_clean_string_whitespace(self):
        """Test clean_string with various whitespace"""
        assert clean_string("  \t\n  hello  \t\n  world  \t\n  ") == "hello world"
        assert clean_string("multiple    spaces") == "multiple spaces"


class TestGetKetoRating:
    """Test get_keto_rating function"""
    
    def test_get_keto_rating_excellent(self):
        """Test get_keto_rating for excellent values"""
        assert get_keto_rating(2.0) == "excellent"
        assert get_keto_rating(3.5) == "excellent"
        assert get_keto_rating(5.0) == "excellent"
    
    def test_get_keto_rating_moderate(self):
        """Test get_keto_rating for moderate values"""
        assert get_keto_rating(1.0) == "moderate"
        assert get_keto_rating(1.5) == "moderate"
        assert get_keto_rating(1.99) == "moderate"
    
    def test_get_keto_rating_poor(self):
        """Test get_keto_rating for poor values"""
        assert get_keto_rating(0.5) == "poor"
        assert get_keto_rating(0.0) == "poor"
        assert get_keto_rating(-1.0) == "poor"


class TestFormatDate:
    """Test format_date function"""
    
    def test_format_date_string(self):
        """Test format_date with string input"""
        assert format_date("2023-12-25") == "2023-12-25"
        assert format_date("invalid") == "invalid"
    
    def test_format_date_date_object(self):
        """Test format_date with date object"""
        test_date = date(2023, 12, 25)
        assert format_date(test_date) == "2023-12-25"
    
    def test_format_date_datetime_object(self):
        """Test format_date with datetime object"""
        test_datetime = datetime(2023, 12, 25, 10, 30, 0)
        assert format_date(test_datetime) == "2023-12-25"
    
    def test_format_date_invalid_object(self):
        """Test format_date with invalid object"""
        result = format_date(123)
        assert result == str(date.today())


class TestParseDate:
    """Test parse_date function"""
    
    def test_parse_date_valid(self):
        """Test parse_date with valid date string"""
        result = parse_date("2023-12-25")
        assert result == date(2023, 12, 25)
    
    def test_parse_date_invalid_format(self):
        """Test parse_date with invalid format"""
        assert parse_date("25-12-2023") is None
        assert parse_date("2023/12/25") is None
        assert parse_date("invalid") is None
    
    def test_parse_date_invalid_type(self):
        """Test parse_date with invalid type"""
        assert parse_date(123) is None
        assert parse_date(None) is None


class TestJsonResponse:
    """Test json_response function"""
    
    def test_json_response_success(self):
        """Test json_response for success"""
        result = json_response({"test": "data"}, "Success message")
        assert result["status"] == "success"
        assert result["data"] == {"test": "data"}
        assert result["message"] == "Success message"
        assert "timestamp" in result
    
    def test_json_response_error(self):
        """Test json_response for error"""
        result = json_response(None, "Error message", status=400)
        assert result["status"] == "error"
        assert result["message"] == "Error message"
        assert "timestamp" in result
    
    def test_json_response_no_data(self):
        """Test json_response without data"""
        result = json_response()
        assert result["status"] == "success"
        assert "data" not in result
        assert "message" not in result
    
    def test_json_response_kwargs(self):
        """Test json_response with additional kwargs"""
        result = json_response({"test": "data"}, extra_field="extra_value")
        assert result["extra_field"] == "extra_value"


class TestValidateNutritionValues:
    """Test validate_nutrition_values function"""
    
    def test_validate_nutrition_values_valid(self):
        """Test validate_nutrition_values with valid values"""
        # Use values that match calculated calories
        errors = validate_nutrition_values(145.0, 10, 5, 15)  # 10*4 + 5*9 + 15*4 = 40 + 45 + 60 = 145
        assert len(errors) == 0
    
    def test_validate_nutrition_values_negative_calories(self):
        """Test validate_nutrition_values with negative calories"""
        errors = validate_nutrition_values(-10, 10, 5, 15)
        assert "Calories cannot be negative" in errors
    
    def test_validate_nutrition_values_high_calories(self):
        """Test validate_nutrition_values with high calories"""
        errors = validate_nutrition_values(10000, 10, 5, 15)
        assert "Calories cannot exceed 9999 per 100g" in errors
    
    def test_validate_nutrition_values_negative_protein(self):
        """Test validate_nutrition_values with negative protein"""
        errors = validate_nutrition_values(100, -10, 5, 15)
        assert "Protein cannot be negative" in errors
    
    def test_validate_nutrition_values_high_protein(self):
        """Test validate_nutrition_values with high protein"""
        errors = validate_nutrition_values(100, 101, 5, 15)
        assert "Protein cannot exceed 100g per 100g" in errors
    
    def test_validate_nutrition_values_negative_fat(self):
        """Test validate_nutrition_values with negative fat"""
        errors = validate_nutrition_values(100, 10, -5, 15)
        assert "Fat cannot be negative" in errors
    
    def test_validate_nutrition_values_high_fat(self):
        """Test validate_nutrition_values with high fat"""
        errors = validate_nutrition_values(100, 10, 101, 15)
        assert "Fat cannot exceed 100g per 100g" in errors
    
    def test_validate_nutrition_values_negative_carbs(self):
        """Test validate_nutrition_values with negative carbs"""
        errors = validate_nutrition_values(100, 10, 5, -15)
        assert "Carbs cannot be negative" in errors
    
    def test_validate_nutrition_values_high_carbs(self):
        """Test validate_nutrition_values with high carbs"""
        errors = validate_nutrition_values(100, 10, 5, 101)
        assert "Carbs cannot exceed 100g per 100g" in errors
    
    def test_validate_nutrition_values_high_total_macros(self):
        """Test validate_nutrition_values with high total macros"""
        errors = validate_nutrition_values(100, 50, 30, 25)
        assert "Total macros" in errors[0] and "cannot exceed 100g per 100g" in errors[0]
    
    def test_validate_nutrition_values_calories_optional(self):
        """Test validate_nutrition_values with calories optional"""
        errors = validate_nutrition_values(-10, 10, 5, 15, calories_optional=True)
        assert len(errors) == 0  # Should not error on negative calories when optional
    
    def test_validate_nutrition_values_no_total_check(self):
        """Test validate_nutrition_values without total macros check"""
        # Use values that match calculated calories
        errors = validate_nutrition_values(570.0, 50, 30, 25, check_total_macros=False)  # 50*4 + 30*9 + 25*4 = 200 + 270 + 100 = 570
        assert len(errors) == 0  # Should not error on high total macros when check disabled


class TestValidateProductData:
    """Test validate_product_data function"""
    
    def test_validate_product_data_valid(self):
        """Test validate_product_data with valid data"""
        data = {
            "name": "Test Product",
            "calories_per_100g": 100,
            "protein_per_100g": 10,
            "fat_per_100g": 5,
            "carbs_per_100g": 15
        }
        is_valid, errors, cleaned_data = validate_product_data(data)
        assert is_valid is True
        assert len(errors) == 0
        assert cleaned_data["name"] == "Test Product"
    
    def test_validate_product_data_missing_name(self):
        """Test validate_product_data with missing name"""
        data = {
            "calories_per_100g": 100,
            "protein_per_100g": 10,
            "fat_per_100g": 5,
            "carbs_per_100g": 15
        }
        is_valid, errors, cleaned_data = validate_product_data(data)
        assert is_valid is False
        assert "Product name is required" in errors
    
    def test_validate_product_data_short_name(self):
        """Test validate_product_data with short name"""
        data = {
            "name": "A",
            "calories_per_100g": 100,
            "protein_per_100g": 10,
            "fat_per_100g": 5,
            "carbs_per_100g": 15
        }
        is_valid, errors, cleaned_data = validate_product_data(data)
        assert is_valid is False
        assert "Product name must be at least 2 characters long" in errors
    
    def test_validate_product_data_long_name(self):
        """Test validate_product_data with long name"""
        data = {
            "name": "A" * 150,  # Much longer than 100 chars
            "calories_per_100g": 145.0,  # Match calculated calories
            "protein_per_100g": 10,
            "fat_per_100g": 5,
            "carbs_per_100g": 15
        }
        is_valid, errors, cleaned_data = validate_product_data(data)
        assert is_valid is True  # clean_string truncates to 100 chars, so it passes validation
        assert len(cleaned_data["name"]) == 100  # Should be truncated to 100 chars
    
    def test_validate_product_data_whitespace_name(self):
        """Test validate_product_data with whitespace name"""
        data = {
            "name": "   ",
            "calories_per_100g": 100,
            "protein_per_100g": 10,
            "fat_per_100g": 5,
            "carbs_per_100g": 15
        }
        is_valid, errors, cleaned_data = validate_product_data(data)
        assert is_valid is False
        assert "Product name is required" in errors


class TestValidateDishData:
    """Test validate_dish_data function"""
    
    def test_validate_dish_data_valid(self):
        """Test validate_dish_data with valid data"""
        data = {
            "name": "Test Dish",
            "ingredients": [
                {
                    "product_id": 1,
                    "quantity_grams": 100,
                    "preparation_method": "raw",
                    "edible_portion": 1.0
                }
            ]
        }
        is_valid, errors, cleaned_data = validate_dish_data(data)
        assert is_valid is True
        assert len(errors) == 0
        assert cleaned_data["name"] == "Test Dish"
        assert len(cleaned_data["ingredients"]) == 1
    
    def test_validate_dish_data_missing_name(self):
        """Test validate_dish_data with missing name"""
        data = {
            "ingredients": [
                {
                    "product_id": 1,
                    "quantity_grams": 100
                }
            ]
        }
        is_valid, errors, cleaned_data = validate_dish_data(data)
        assert is_valid is False
        assert "Dish name is required" in errors
    
    def test_validate_dish_data_no_ingredients(self):
        """Test validate_dish_data with no ingredients"""
        data = {
            "name": "Test Dish",
            "ingredients": []
        }
        is_valid, errors, cleaned_data = validate_dish_data(data)
        assert is_valid is False
        assert "At least one ingredient is required" in errors
    
    def test_validate_dish_data_invalid_ingredients_type(self):
        """Test validate_dish_data with invalid ingredients type"""
        data = {
            "name": "Test Dish",
            "ingredients": "not a list"
        }
        is_valid, errors, cleaned_data = validate_dish_data(data)
        assert is_valid is False
        assert "Ingredients must be a list" in errors
    
    def test_validate_dish_data_invalid_ingredient(self):
        """Test validate_dish_data with invalid ingredient"""
        data = {
            "name": "Test Dish",
            "ingredients": [
                {
                    "product_id": 0,
                    "quantity_grams": 0
                }
            ]
        }
        is_valid, errors, cleaned_data = validate_dish_data(data)
        assert is_valid is False
        assert any("Valid product ID is required" in error for error in errors)
        # Note: quantity check doesn't run due to elif logic when product_id is invalid
    
    def test_validate_dish_data_invalid_preparation_method(self):
        """Test validate_dish_data with invalid preparation method"""
        data = {
            "name": "Test Dish",
            "ingredients": [
                {
                    "product_id": 1,
                    "quantity_grams": 100,
                    "preparation_method": "invalid_method"
                }
            ]
        }
        is_valid, errors, cleaned_data = validate_dish_data(data)
        assert is_valid is False
        assert any("Invalid preparation method" in error for error in errors)
    
    def test_validate_dish_data_invalid_edible_portion(self):
        """Test validate_dish_data with invalid edible portion"""
        data = {
            "name": "Test Dish",
            "ingredients": [
                {
                    "product_id": 1,
                    "quantity_grams": 100,
                    "edible_portion": 1.5
                }
            ]
        }
        is_valid, errors, cleaned_data = validate_dish_data(data)
        assert is_valid is False
        assert any("Edible portion must be between 0 and 1.0" in error for error in errors)


class TestValidateLogData:
    """Test validate_log_data function"""
    
    def test_validate_log_data_valid(self):
        """Test validate_log_data with valid data"""
        data = {
            "date": "2023-12-25",
            "item_type": "product",
            "item_id": 1,
            "quantity_grams": 100,
            "meal_time": "breakfast",
            "notes": "Test notes"
        }
        is_valid, errors, cleaned_data = validate_log_data(data)
        assert is_valid is True
        assert len(errors) == 0
        assert cleaned_data["date"] == "2023-12-25"
        assert cleaned_data["item_type"] == "product"
    
    def test_validate_log_data_missing_date(self):
        """Test validate_log_data with missing date"""
        data = {
            "item_type": "product",
            "item_id": 1,
            "quantity_grams": 100
        }
        is_valid, errors, cleaned_data = validate_log_data(data)
        assert is_valid is False
        assert "Date is required" in errors
    
    def test_validate_log_data_invalid_date_format(self):
        """Test validate_log_data with invalid date format"""
        data = {
            "date": "25-12-2023",
            "item_type": "product",
            "item_id": 1,
            "quantity_grams": 100
        }
        is_valid, errors, cleaned_data = validate_log_data(data)
        assert is_valid is False
        assert "Date must be in YYYY-MM-DD format" in errors
    
    def test_validate_log_data_future_date(self):
        """Test validate_log_data with future date"""
        future_date = (date.today().replace(year=date.today().year + 1)).strftime("%Y-%m-%d")
        data = {
            "date": future_date,
            "item_type": "product",
            "item_id": 1,
            "quantity_grams": 100
        }
        is_valid, errors, cleaned_data = validate_log_data(data)
        assert is_valid is False
        assert "Date cannot be in the future" in errors
    
    def test_validate_log_data_old_date(self):
        """Test validate_log_data with old date"""
        data = {
            "date": "2019-12-25",
            "item_type": "product",
            "item_id": 1,
            "quantity_grams": 100
        }
        is_valid, errors, cleaned_data = validate_log_data(data)
        assert is_valid is False
        assert "Date cannot be before 2020" in errors
    
    def test_validate_log_data_invalid_item_type(self):
        """Test validate_log_data with invalid item type"""
        data = {
            "date": "2023-12-25",
            "item_type": "invalid",
            "item_id": 1,
            "quantity_grams": 100
        }
        is_valid, errors, cleaned_data = validate_log_data(data)
        assert is_valid is False
        assert "Item type must be 'product' or 'dish'" in errors
    
    def test_validate_log_data_invalid_item_id(self):
        """Test validate_log_data with invalid item ID"""
        data = {
            "date": "2023-12-25",
            "item_type": "product",
            "item_id": 0,
            "quantity_grams": 100
        }
        is_valid, errors, cleaned_data = validate_log_data(data)
        assert is_valid is False
        assert "Valid item ID is required" in errors
    
    def test_validate_log_data_invalid_quantity(self):
        """Test validate_log_data with invalid quantity"""
        data = {
            "date": "2023-12-25",
            "item_type": "product",
            "item_id": 1,
            "quantity_grams": 0
        }
        is_valid, errors, cleaned_data = validate_log_data(data)
        assert is_valid is False
        assert "Quantity must be greater than 0" in errors
    
    def test_validate_log_data_high_quantity(self):
        """Test validate_log_data with high quantity"""
        data = {
            "date": "2023-12-25",
            "item_type": "product",
            "item_id": 1,
            "quantity_grams": 10001
        }
        is_valid, errors, cleaned_data = validate_log_data(data)
        assert is_valid is False
        assert "Quantity cannot exceed 10000g" in errors
    
    def test_validate_log_data_invalid_meal_time(self):
        """Test validate_log_data with invalid meal time"""
        data = {
            "date": "2023-12-25",
            "item_type": "product",
            "item_id": 1,
            "quantity_grams": 100,
            "meal_time": "invalid"
        }
        is_valid, errors, cleaned_data = validate_log_data(data)
        assert is_valid is False
        assert any("Meal time must be one of:" in error for error in errors)
    
    def test_validate_log_data_default_meal_time(self):
        """Test validate_log_data with default meal time"""
        data = {
            "date": "2023-12-25",
            "item_type": "product",
            "item_id": 1,
            "quantity_grams": 100
        }
        is_valid, errors, cleaned_data = validate_log_data(data)
        assert is_valid is True
        assert cleaned_data["meal_time"] == "snack"


class TestGetDatabaseStats:
    """Test get_database_stats function"""
    
    def test_get_database_stats_success(self):
        """Test get_database_stats with successful database connection"""
        mock_row = Mock()
        mock_row.__getitem__ = Mock(side_effect=lambda key: {"count": 5, "first_date": "2023-01-01", "last_date": "2023-12-31"}[key])
        
        mock_conn = Mock()
        mock_conn.row_factory = sqlite3.Row
        mock_conn.execute.return_value.fetchone.return_value = mock_row
        
        with patch('src.utils.sqlite3.connect', return_value=mock_conn), \
             patch('src.config.Config') as mock_config:
            
            mock_config.DATABASE = "test.db"
            
            result = get_database_stats()
            
            assert result["products"] == 5
            assert result["dishes"] == 5
            assert result["log_entries"] == 5
            assert result["first_entry"] == "2023-01-01"
            assert result["last_entry"] == "2023-12-31"
            mock_conn.close.assert_called_once()
    
    def test_get_database_stats_exception(self):
        """Test get_database_stats with database exception"""
        with patch('src.utils.sqlite3.connect', side_effect=Exception("Database error")):
            result = get_database_stats()
            assert "error" in result
            assert result["error"] == "Database error"


class TestValidationFunctionsExtended:
    """Extended tests for validation functions to increase coverage"""
    
    def test_validate_product_data_long_name(self):
        """Test validate_product_data with name that exceeds 100 characters"""
        data = {
            "name": "A" * 101,  # 101 characters
            "calories_per_100g": 100,
            "protein_per_100g": 10,
            "fat_per_100g": 5,
            "carbs_per_100g": 15
        }
        
        is_valid, errors, cleaned_data = validate_product_data(data)
        
        assert is_valid is True  # clean_string truncates to 100 chars
        assert len(cleaned_data["name"]) == 100
        assert len(errors) == 0
    
    def test_validate_dish_data_long_name(self):
        """Test validate_dish_data with name that exceeds 100 characters"""
        data = {
            "name": "A" * 101,  # 101 characters
            "ingredients": [
                {"product_id": 1, "quantity_grams": 100}
            ]
        }
        
        is_valid, errors, cleaned_data = validate_dish_data(data)
        
        assert is_valid is True  # clean_string truncates to 100 chars
        assert len(cleaned_data["name"]) == 100
        assert len(errors) == 0
    
    def test_validate_dish_data_ingredient_not_dict(self):
        """Test validate_dish_data with ingredient that is not a dict"""
        data = {
            "name": "Test Dish",
            "ingredients": [
                "not_a_dict",  # Invalid ingredient
                {"product_id": 1, "quantity_grams": 100}
            ]
        }
        
        is_valid, errors, cleaned_data = validate_dish_data(data)
        
        assert is_valid is False  # Has errors due to invalid ingredient
        assert any("Ingredient 1: Must be an object" in error for error in errors)
    
    def test_validate_dish_data_quantity_too_large(self):
        """Test validate_dish_data with quantity exceeding 10000g"""
        data = {
            "name": "Test Dish",
            "ingredients": [
                {"product_id": 1, "quantity_grams": 15000}  # Too large
            ]
        }
        
        is_valid, errors, cleaned_data = validate_dish_data(data)
        
        assert is_valid is False
        assert any("Quantity cannot exceed 10000g" in error for error in errors)
    
    def test_validate_dish_data_no_valid_ingredients(self):
        """Test validate_dish_data with no valid ingredients"""
        data = {
            "name": "Test Dish",
            "ingredients": [
                {"product_id": 0, "quantity_grams": 100}  # Invalid product_id
            ]
        }
        
        is_valid, errors, cleaned_data = validate_dish_data(data)
        
        assert is_valid is False
        assert any("Valid product ID is required" in error for error in errors)


class TestDatabaseConnection:
    """Test database_connection context manager"""

    def test_database_connection_basic_usage(self):
        """Test database_connection creates connection with proper settings"""
        import tempfile
        import os
        from src.utils import database_connection

        # Create a temporary database file
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        try:
            with database_connection(db_path) as conn:
                # Check connection was created
                assert conn is not None
                assert isinstance(conn, sqlite3.Connection)
                
                # Check row_factory is set
                assert conn.row_factory == sqlite3.Row
                
                # Test we can execute a query
                cursor = conn.execute("SELECT 1")
                result = cursor.fetchone()
                assert result[0] == 1
        finally:
            # Clean up
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_database_connection_memory_database(self):
        """Test database_connection with in-memory database"""
        from src.utils import database_connection

        with database_connection(":memory:") as conn:
            # Check connection was created
            assert conn is not None
            
            # Create a table and insert data
            conn.execute("CREATE TABLE test (id INTEGER, value TEXT)")
            conn.execute("INSERT INTO test VALUES (1, 'test')")
            
            # Query the data
            cursor = conn.execute("SELECT * FROM test")
            result = cursor.fetchone()
            assert result["id"] == 1
            assert result["value"] == "test"

    def test_database_connection_auto_commit_on_success(self):
        """Test database_connection automatically commits on success"""
        import tempfile
        import os
        from src.utils import database_connection

        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        try:
            # First connection - create table and insert data
            with database_connection(db_path) as conn:
                conn.execute("CREATE TABLE test (id INTEGER, value TEXT)")
                conn.execute("INSERT INTO test VALUES (1, 'test')")
            
            # Second connection - verify data was committed
            with database_connection(db_path) as conn:
                cursor = conn.execute("SELECT * FROM test")
                result = cursor.fetchone()
                assert result["id"] == 1
                assert result["value"] == "test"
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_database_connection_auto_rollback_on_error(self):
        """Test database_connection automatically rolls back on error"""
        import tempfile
        import os
        from src.utils import database_connection

        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        try:
            # First connection - create table
            with database_connection(db_path) as conn:
                conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
            
            # Second connection - try to insert data but raise error
            try:
                with database_connection(db_path) as conn:
                    conn.execute("INSERT INTO test VALUES (1, 'test')")
                    raise ValueError("Test error")
            except ValueError:
                pass
            
            # Third connection - verify data was rolled back
            with database_connection(db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM test")
                count = cursor.fetchone()[0]
                assert count == 0  # No data should be committed
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_database_connection_wal_mode_for_file_db(self):
        """Test database_connection enables WAL mode for file databases"""
        import tempfile
        import os
        from src.utils import database_connection

        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        try:
            with database_connection(db_path) as conn:
                # Check WAL mode is enabled for file database
                cursor = conn.execute("PRAGMA journal_mode")
                mode = cursor.fetchone()[0]
                assert mode.upper() == "WAL"
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_database_connection_foreign_keys_enabled(self):
        """Test database_connection enables foreign keys"""
        from src.utils import database_connection

        with database_connection(":memory:") as conn:
            # Check foreign keys are enabled
            cursor = conn.execute("PRAGMA foreign_keys")
            result = cursor.fetchone()[0]
            assert result == 1  # Foreign keys enabled

    def test_database_connection_no_wal_for_memory_db(self):
        """Test database_connection does not enable WAL mode for in-memory database"""
        from src.utils import database_connection

        with database_connection(":memory:") as conn:
            # Check that WAL mode is NOT enabled for in-memory database
            cursor = conn.execute("PRAGMA journal_mode")
            mode = cursor.fetchone()[0]
            # In-memory databases should use default mode (memory), not WAL
            assert mode.upper() != "WAL"
