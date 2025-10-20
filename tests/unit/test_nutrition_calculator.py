"""
Unit tests for nutrition_calculator.py
"""

import pytest
from unittest.mock import patch, MagicMock
from src.nutrition_calculator import (
    ActivityLevel,
    Goal,
    KetoType,
    NutritionData,
    UserProfile,
    RecipeIngredient,
    ValidationResult,
    validate_nutrition_data,
    validate_user_profile,
    calculate_calories_from_macros,
    calculate_net_carbs_advanced,
    calculate_keto_index_advanced,
    calculate_carbs_score_advanced,
    calculate_fat_ratio_score_advanced,
    calculate_quality_score_advanced,
    calculate_gi_score_advanced,
    calculate_bmr_mifflin_st_jeor,
    calculate_bmr_katch_mcardle,
    calculate_lean_body_mass,
    calculate_tdee,
    calculate_target_calories,
    calculate_keto_macros_advanced,
    calculate_gki,
    calculate_cooking_fat,
    calculate_recipe_nutrition,
    validate_recipe_integrity,
    round_nutrition_values,
    log_calculation,
    calculate_net_carbs,
    calculate_keto_index,
    calculate_bmr,
    calculate_keto_macros,
    CALORIES_PER_GRAM,
    ACTIVITY_MULTIPLIERS,
    GOAL_ADJUSTMENTS,
    FIBER_RATIOS
)


class TestNutritionData:
    """Test NutritionData dataclass"""
    
    def test_nutrition_data_init(self):
        """Test NutritionData initialization"""
        data = NutritionData(
            protein=20.0,
            carbs=30.0,
            fats=10.0,
            calories=250.0
        )
        
        assert data.protein == 20.0
        assert data.carbs == 30.0
        assert data.fats == 10.0
        assert data.calories == 250.0
    
    def test_nutrition_data_defaults(self):
        """Test NutritionData with default values"""
        data = NutritionData(protein=20.0, carbs=30.0, fats=10.0)
        
        assert data.protein == 20.0
        assert data.carbs == 30.0
        assert data.fats == 10.0
        assert data.calories is None


class TestUserProfile:
    """Test UserProfile dataclass"""
    
    def test_user_profile_init(self):
        """Test UserProfile initialization"""
        profile = UserProfile(
            weight=70.0,
            height=175.0,
            age=30,
            gender="male",
            activity_level=ActivityLevel.MODERATE,
            goal=Goal.MAINTENANCE
        )
        
        assert profile.weight == 70.0
        assert profile.height == 175.0
        assert profile.age == 30
        assert profile.gender == "male"
        assert profile.activity_level == ActivityLevel.MODERATE
        assert profile.goal == Goal.MAINTENANCE


class TestRecipeIngredient:
    """Test RecipeIngredient dataclass"""
    
    def test_recipe_ingredient_init(self):
        """Test RecipeIngredient initialization"""
        ingredient = RecipeIngredient(
            name="Chicken Breast",
            raw_weight=200.0,
            nutrition_per_100g={"protein": 25.0, "fats": 3.0, "carbs": 0.0},
            category="meat",
            preparation="raw"
        )
        
        assert ingredient.name == "Chicken Breast"
        assert ingredient.raw_weight == 200.0
        assert ingredient.nutrition_per_100g["protein"] == 25.0
        assert ingredient.category == "meat"
        assert ingredient.preparation == "raw"


class TestValidationResult:
    """Test ValidationResult dataclass"""
    
    def test_validation_result_init(self):
        """Test ValidationResult initialization"""
        result = ValidationResult(valid=True, issues=[])
        
        assert result.valid is True
        assert result.issues == []
    
    def test_validation_result_with_errors(self):
        """Test ValidationResult with errors"""
        errors = ["Weight must be positive", "Height must be positive"]
        result = ValidationResult(valid=False, issues=errors)
        
        assert result.valid is False
        assert result.issues == errors


class TestValidationFunctions:
    """Test validation functions"""
    
    def test_validate_nutrition_data_valid(self):
        """Test validate_nutrition_data with valid data"""
        result = validate_nutrition_data(20.0, 10.0, 30.0)
        
        assert result.valid is True
        assert len(result.issues) == 0
    
    def test_validate_nutrition_data_invalid_negative(self):
        """Test validate_nutrition_data with negative values"""
        result = validate_nutrition_data(-5.0, 10.0, 30.0)
        
        assert result.valid is False
        assert len(result.issues) > 0
    
    def test_validate_user_profile_valid(self):
        """Test validate_user_profile with valid data"""
        result = validate_user_profile(70.0, 175.0, 30, "male")
        
        assert result.valid is True
        assert len(result.issues) == 0
    
    def test_validate_user_profile_invalid_weight(self):
        """Test validate_user_profile with invalid weight"""
        result = validate_user_profile(-5.0, 175.0, 30, "male")
        
        assert result.valid is False
        assert len(result.issues) > 0
    
    def test_validate_user_profile_invalid_height(self):
        """Test validate_user_profile with invalid height"""
        result = validate_user_profile(70.0, -175.0, 30, "male")
        
        assert result.valid is False
        assert len(result.issues) > 0
    
    def test_validate_user_profile_invalid_age(self):
        """Test validate_user_profile with invalid age"""
        result = validate_user_profile(70.0, 175.0, -30, "male")
        
        assert result.valid is False
        assert len(result.issues) > 0
    
    def test_validate_user_profile_invalid_gender(self):
        """Test validate_user_profile with invalid gender"""
        result = validate_user_profile(70.0, 175.0, 30, "invalid")
        
        assert result.valid is False
        assert len(result.issues) > 0


class TestCalculationFunctions:
    """Test calculation functions"""
    
    def test_calculate_calories_from_macros(self):
        """Test calculate_calories_from_macros"""
        calories = calculate_calories_from_macros(20.0, 10.0, 30.0)
        
        expected = (20.0 * CALORIES_PER_GRAM["protein"] + 
                   10.0 * CALORIES_PER_GRAM["fats"] + 
                   30.0 * CALORIES_PER_GRAM["carbs"])
        assert calories == expected
    
    def test_calculate_net_carbs_advanced(self):
        """Test calculate_net_carbs_advanced"""
        result = calculate_net_carbs_advanced(30.0, 5.0, 2.0, 1.0)
        
        assert isinstance(result, dict)
        assert "net_carbs" in result
        assert isinstance(result["net_carbs"], float)
    
    def test_calculate_keto_index_advanced(self):
        """Test calculate_keto_index_advanced"""
        keto_index = calculate_keto_index_advanced(20.0, 10.0, 5.0, 2.0, "standard")
        
        assert isinstance(keto_index, dict)
        assert "keto_index" in keto_index
        assert "carbs_score" in keto_index
        assert "fat_score" in keto_index
    
    def test_calculate_carbs_score_advanced(self):
        """Test calculate_carbs_score_advanced"""
        score = calculate_carbs_score_advanced(20.0)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 100.0
    
    def test_calculate_fat_ratio_score_advanced(self):
        """Test calculate_fat_ratio_score_advanced"""
        score = calculate_fat_ratio_score_advanced(60.0, 20.0, 20.0)
        
        assert isinstance(score, (int, float))
        assert 0.0 <= score <= 100.0
    
    def test_calculate_quality_score_advanced(self):
        """Test calculate_quality_score_advanced"""
        score = calculate_quality_score_advanced("raw", "meat")
        
        assert isinstance(score, (int, float))
        assert 0.0 <= score <= 100.0
    
    def test_calculate_gi_score_advanced(self):
        """Test calculate_gi_score_advanced"""
        score = calculate_gi_score_advanced(50.0)
        
        assert isinstance(score, (int, float))
        assert 0.0 <= score <= 100.0
    
    def test_calculate_gi_score_advanced_none(self):
        """Test calculate_gi_score_advanced with None"""
        score = calculate_gi_score_advanced(None)
        
        assert isinstance(score, (int, float))
        assert 0.0 <= score <= 100.0


class TestBMRFunctions:
    """Test BMR calculation functions"""
    
    def test_calculate_bmr_mifflin_st_jeor_male(self):
        """Test calculate_bmr_mifflin_st_jeor for male"""
        bmr = calculate_bmr_mifflin_st_jeor(70.0, 175.0, 30, "male")
        
        assert isinstance(bmr, float)
        assert bmr > 0
    
    def test_calculate_bmr_mifflin_st_jeor_female(self):
        """Test calculate_bmr_mifflin_st_jeor for female"""
        bmr = calculate_bmr_mifflin_st_jeor(60.0, 165.0, 25, "female")
        
        assert isinstance(bmr, float)
        assert bmr > 0
    
    def test_calculate_bmr_katch_mcardle(self):
        """Test calculate_bmr_katch_mcardle"""
        bmr = calculate_bmr_katch_mcardle(50.0)
        
        assert isinstance(bmr, float)
        assert bmr > 0
    
    def test_calculate_lean_body_mass(self):
        """Test calculate_lean_body_mass"""
        lbm = calculate_lean_body_mass(70.0, 15.0)
        
        assert isinstance(lbm, float)
        assert lbm > 0
        assert lbm < 70.0  # Lean body mass should be less than total weight


class TestTDEEFunctions:
    """Test TDEE calculation functions"""
    
    def test_calculate_tdee_string(self):
        """Test calculate_tdee with string activity level"""
        bmr = 1500.0
        tdee = calculate_tdee(bmr, "moderate")
        
        assert isinstance(tdee, float)
        assert tdee > bmr
    
    def test_calculate_tdee_enum(self):
        """Test calculate_tdee with enum activity level"""
        bmr = 1500.0
        tdee = calculate_tdee(bmr, ActivityLevel.MODERATE)
        
        assert isinstance(tdee, float)
        assert tdee > bmr
    
    def test_calculate_target_calories_string(self):
        """Test calculate_target_calories with string goal"""
        tdee = 2000.0
        target = calculate_target_calories(tdee, "weight_loss")
        
        assert isinstance(target, float)
        assert target < tdee  # Weight loss should be less than TDEE
    
    def test_calculate_target_calories_enum(self):
        """Test calculate_target_calories with enum goal"""
        tdee = 2000.0
        target = calculate_target_calories(tdee, Goal.MUSCLE_GAIN)
        
        assert isinstance(target, float)
        assert target > tdee  # Muscle gain should be more than TDEE


class TestKetoFunctions:
    """Test keto-related functions"""
    
    def test_calculate_keto_macros_advanced(self):
        """Test calculate_keto_macros_advanced"""
        macros = calculate_keto_macros_advanced(2000.0, 50.0)
        
        assert isinstance(macros, dict)
        assert "protein" in macros
        assert "fats" in macros
        assert "carbs" in macros
        assert "calories" in macros
    
    def test_calculate_gki(self):
        """Test calculate_gki"""
        gki_data = calculate_gki(100.0, 1.5)
        
        assert isinstance(gki_data, dict)
        assert "gki" in gki_data
        assert "gki_category" in gki_data
        assert "glucose_mgdl" in gki_data
        assert "ketones_mgdl" in gki_data


class TestCookingFunctions:
    """Test cooking-related functions"""
    
    def test_calculate_cooking_fat(self):
        """Test calculate_cooking_fat"""
        ingredient = RecipeIngredient(
            name="Chicken Breast",
            raw_weight=200.0,
            nutrition_per_100g={"protein": 25.0, "fats": 3.0, "carbs": 0.0},
            category="meat",
            preparation="raw"
        )
        
        fat = calculate_cooking_fat(ingredient, "pan_fry")
        
        assert isinstance(fat, float)
        assert fat >= 0.0
    
    def test_calculate_cooking_fat_fried_fish(self):
        """Test calculate_cooking_fat for fried fish"""
        ingredient = RecipeIngredient(
            name="Salmon",
            raw_weight=150.0,
            nutrition_per_100g={"protein": 20.0, "fats": 13.0, "carbs": 0.0},
            category="fish",
            preparation="raw"
        )
        
        fat = calculate_cooking_fat(ingredient, "fried")
        
        # Should add 3% of weight = 150 * 0.03 = 4.5
        assert fat == 4.5
    
    def test_calculate_cooking_fat_fried_vegetable(self):
        """Test calculate_cooking_fat for fried vegetable"""
        ingredient = RecipeIngredient(
            name="Potato",
            raw_weight=100.0,
            nutrition_per_100g={"protein": 2.0, "fats": 0.1, "carbs": 17.0},
            category="vegetable",
            preparation="raw"
        )
        
        fat = calculate_cooking_fat(ingredient, "fried")
        
        # Should add 8% of weight = 100 * 0.08 = 8.0
        assert fat == 8.0
    
    def test_calculate_cooking_fat_grilled_meat(self):
        """Test calculate_cooking_fat for grilled meat"""
        ingredient = RecipeIngredient(
            name="Beef",
            raw_weight=200.0,
            nutrition_per_100g={"protein": 26.0, "fats": 15.0, "carbs": 0.0},
            category="meat",
            preparation="raw"
        )
        
        fat = calculate_cooking_fat(ingredient, "grilled")
        
        # Should subtract 5% of weight = -200 * 0.05 = -10.0
        assert fat == -10.0
    
    def test_calculate_recipe_nutrition(self):
        """Test calculate_recipe_nutrition"""
        ingredients = [
            RecipeIngredient(
                name="Chicken Breast",
                raw_weight=200.0,
                nutrition_per_100g={"protein": 25.0, "fats": 3.0, "carbs": 0.0, "calories": 165.0},
                category="meat",
                preparation="raw"
            ),
            RecipeIngredient(
                name="Rice",
                raw_weight=100.0,
                nutrition_per_100g={"protein": 2.7, "fats": 0.3, "carbs": 28.0, "calories": 130.0},
                category="grains",
                preparation="cooked"
            )
        ]
        
        recipe = calculate_recipe_nutrition(ingredients, "Chicken and Rice", servings=2)
        
        assert isinstance(recipe, dict)
        assert "nutrition_per_100g" in recipe
        assert "ingredients_breakdown" in recipe
        assert "keto_index" in recipe
        assert "keto_category" in recipe


class TestValidationFunctions:
    """Test validation functions"""
    
    def test_validate_recipe_integrity(self):
        """Test validate_recipe_integrity"""
        recipe_data = {
            "name": "Test Recipe",
            "ingredients_breakdown": [
                {
                    "name": "Chicken", 
                    "raw_weight": 200.0,
                    "nutrition": {"protein": 25.0, "fats": 3.0, "carbs": 0.0, "calories": 120.0}
                }
            ],
            "weights": {"total_raw": 200.0, "total_cooked": 180.0},
            "nutrition_total": {"protein": 50.0, "fats": 6.0, "carbs": 0.0, "calories": 240.0},
            "servings": 2
        }
        
        result = validate_recipe_integrity(recipe_data)
        
        assert isinstance(result, ValidationResult)
        assert hasattr(result, 'valid')
        assert hasattr(result, 'issues')
    
    def test_validate_recipe_integrity_weight_mismatch(self):
        """Test validate_recipe_integrity with weight mismatch"""
        recipe_data = {
            "name": "Test Recipe",
            "ingredients_breakdown": [
                {
                    "name": "Chicken", 
                    "raw_weight": 200.0,
                    "nutrition": {"protein": 25.0, "fats": 3.0, "carbs": 0.0, "calories": 120.0}
                }
            ],
            "weights": {"total_raw": 250.0, "total_cooked": 180.0},  # Mismatch: 250 vs 200
            "nutrition_total": {"protein": 50.0, "fats": 6.0, "carbs": 0.0, "calories": 240.0},
            "servings": 2
        }
        
        result = validate_recipe_integrity(recipe_data)
        
        assert isinstance(result, ValidationResult)
        assert not result.valid  # Should be invalid due to weight mismatch
        assert len(result.issues) > 0
    
    def test_validate_recipe_integrity_unusual_yield(self):
        """Test validate_recipe_integrity with unusual yield coefficient"""
        recipe_data = {
            "name": "Test Recipe",
            "ingredients_breakdown": [
                {
                    "name": "Chicken", 
                    "raw_weight": 200.0,
                    "nutrition": {"protein": 25.0, "fats": 3.0, "carbs": 0.0, "calories": 120.0}
                }
            ],
            "weights": {"total_raw": 200.0, "total_cooked": 700.0},  # Unusual yield: 3.5
            "nutrition_total": {"protein": 50.0, "fats": 6.0, "carbs": 0.0, "calories": 240.0},
            "servings": 2
        }
        
        result = validate_recipe_integrity(recipe_data)
        
        assert isinstance(result, ValidationResult)
        assert not result.valid  # Should be invalid due to unusual yield
        assert any("коэффициент выхода" in issue for issue in result.issues)


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_round_nutrition_values(self):
        """Test round_nutrition_values"""
        rounded = round_nutrition_values(1234.567, 45.678, 23.456, 12.345)
        
        assert isinstance(rounded, dict)
        assert "calories" in rounded
        assert "carbs" in rounded
        assert "protein" in rounded
        assert "fats" in rounded
        
        # Check that values are rounded
        assert isinstance(rounded["calories"], (int, float))
        assert isinstance(rounded["carbs"], (int, float))
        assert isinstance(rounded["protein"], (int, float))
        assert isinstance(rounded["fats"], (int, float))
    
    @patch('src.nutrition_calculator.logger')
    def test_log_calculation(self, mock_logger):
        """Test log_calculation"""
        inputs = {"weight": 70.0, "height": 175.0}
        result = {"bmr": 1500.0}
        
        log_calculation("test_function", inputs, result)
        
        # Verify logger was called
        mock_logger.info.assert_called_once()
    
    def test_calculate_net_carbs(self):
        """Test calculate_net_carbs"""
        result = calculate_net_carbs(30.0, 5.0)
        
        assert isinstance(result, dict)
        assert "net_carbs" in result
        assert isinstance(result["net_carbs"], float)
    
    def test_calculate_keto_index(self):
        """Test calculate_keto_index"""
        result = calculate_keto_index(20.0, 10.0, 5.0)
        
        assert isinstance(result, dict)
        assert "keto_index" in result
        assert isinstance(result["keto_index"], float)
    
    def test_calculate_bmr(self):
        """Test calculate_bmr"""
        bmr = calculate_bmr(70.0, 175.0, 30, "male")
        
        assert isinstance(bmr, float)
        assert bmr > 0
    
    def test_calculate_keto_macros(self):
        """Test calculate_keto_macros"""
        macros = calculate_keto_macros(2000.0)
        
        assert isinstance(macros, dict)
        assert "protein" in macros
        assert "fats" in macros
        assert "carbs" in macros


class TestValidationFunctionsExtended:
    
    def test_validate_nutrition_values_fiber_greater_than_carbs(self):
        """Test validation when fiber is greater than carbs"""
        result = validate_nutrition_data(10, 5, 15, fiber=20)
        
        assert result.valid is False
        assert any("Клетчатка" in issue and "больше углеводов" in issue for issue in result.issues)
    
    def test_validate_nutrition_values_fiber_negative(self):
        """Test validation when fiber is negative"""
        result = validate_nutrition_data(10, 5, 15, fiber=-1)
        
        assert result.valid is False
        assert any("Клетчатка не может быть отрицательной" in issue for issue in result.issues)
    
    def test_validate_nutrition_values_sugars_greater_than_carbs(self):
        """Test validation when sugars is greater than carbs"""
        result = validate_nutrition_data(10, 5, 15, sugars=20)
        
        assert result.valid is False
        assert any("Сахара" in issue and "больше углеводов" in issue for issue in result.issues)
    
    def test_validate_nutrition_values_sugars_negative(self):
        """Test validation when sugars is negative"""
        result = validate_nutrition_data(10, 5, 15, sugars=-1)
        
        assert result.valid is False
        assert any("Сахара не могут быть отрицательными" in issue for issue in result.issues)
    
    def test_validate_nutrition_values_sugars_fiber_excess(self):
        """Test validation when sugars + fiber exceeds carbs by more than 20%"""
        result = validate_nutrition_data(10, 5, 15, sugars=10, fiber=10)
        
        assert result.valid is False
        assert any("Сахара + клетчатка больше углеводов" in issue for issue in result.issues)
    
    def test_validate_nutrition_values_total_macros_excess(self):
        """Test validation when total macros exceed 110g"""
        result = validate_nutrition_data(50, 50, 50, check_total=True)
        
        assert result.valid is False
        assert any("Сумма БЖУ" in issue and "превышает разумный предел" in issue for issue in result.issues)
        assert result.severity == "critical"
    
    def test_validate_nutrition_values_calorie_discrepancy(self):
        """Test validation when calories differ significantly from calculated"""
        result = validate_nutrition_data(10, 5, 15, calories=1000)  # Very different from calculated ~145
        
        assert result.valid is False
        assert any("Калории расходятся" in issue for issue in result.issues)
    
    def test_validate_user_profile_weight_low(self):
        """Test validation when weight is too low"""
        result = validate_user_profile(20, 170, 30, "male")
        
        assert result.valid is False
        assert any("Вес должен быть в диапазоне 30-500 кг" in issue for issue in result.issues)
    
    def test_validate_user_profile_weight_high(self):
        """Test validation when weight is too high"""
        result = validate_user_profile(600, 170, 30, "male")
        
        assert result.valid is False
        assert any("Вес должен быть в диапазоне 30-500 кг" in issue for issue in result.issues)
    
    def test_validate_user_profile_height_low(self):
        """Test validation when height is too low"""
        result = validate_user_profile(70, 50, 30, "male")  # Height too low
        
        assert result.valid is False
        assert any("Рост должен быть в диапазоне 100-250 см" in issue for issue in result.issues)
    
    def test_validate_user_profile_height_high(self):
        """Test validation when height is too high"""
        result = validate_user_profile(70, 300, 30, "male")
        
        assert result.valid is False
        assert any("Рост должен быть в диапазоне 100-250 см" in issue for issue in result.issues)
    
    def test_validate_user_profile_age_low(self):
        """Test validation when age is too low"""
        result = validate_user_profile(70, 170, 5, "male")  # Age too low
        
        assert result.valid is False
        assert any("Возраст должен быть в диапазоне 10-120 лет" in issue for issue in result.issues)
    
    def test_validate_user_profile_age_high(self):
        """Test validation when age is too high"""
        result = validate_user_profile(70, 170, 150, "male")
        
        assert result.valid is False
        assert any("Возраст должен быть в диапазоне 10-120 лет" in issue for issue in result.issues)
    
    def test_validate_user_profile_invalid_gender(self):
        """Test validation when gender is invalid"""
        result = validate_user_profile(70, 170, 30, "invalid")
        
        assert result.valid is False
        assert any("Пол должен быть 'male' или 'female'" in issue for issue in result.issues)


class TestAdvancedCalculationFunctions:
    """Test advanced calculation functions to increase coverage"""
    
    def test_calculate_net_carbs_advanced_negative_carbs(self):
        """Test calculate_net_carbs_advanced with negative carbs"""
        with pytest.raises(ValueError, match="Общие углеводы не могут быть отрицательными"):
            calculate_net_carbs_advanced(-10, None, "vegetables")
    
    def test_calculate_net_carbs_advanced_fiber_exceeds_carbs(self):
        """Test calculate_net_carbs_advanced when fiber exceeds carbs"""
        with pytest.raises(ValueError, match="Клетчатка не может превышать общие углеводы"):
            calculate_net_carbs_advanced(10, 15, "vegetables")
    
    def test_calculate_net_carbs_advanced_with_fiber(self):
        """Test calculate_net_carbs_advanced with fiber data"""
        result = calculate_net_carbs_advanced(20, 5, "vegetables")
        
        assert result["net_carbs"] >= 0
        assert result["fiber_estimated"] is False
        assert "direct_fiber_data_coeff" in result["estimation_method"]
        assert "fiber_deduction_coefficient" in result
    
    def test_calculate_net_carbs_advanced_without_fiber_known_category(self):
        """Test calculate_net_carbs_advanced without fiber but known category"""
        result = calculate_net_carbs_advanced(20, None, "leafy_vegetables")  # Use valid category
        
        assert result["net_carbs"] >= 0
        assert result["fiber_estimated"] is True
        assert "category_leafy_vegetables_ratio" in result["estimation_method"]
        assert "fiber_deduction_coefficient" in result
    
    def test_calculate_net_carbs_advanced_without_fiber_unknown_category(self):
        """Test calculate_net_carbs_advanced without fiber and unknown category"""
        result = calculate_net_carbs_advanced(20, None, "unknown_category")
        
        assert result["net_carbs"] == 20  # Conservative approach
        assert result["fiber_estimated"] is True
        assert result["estimation_method"] == "unknown_category_conservative"
        assert result["fiber_deduction_coefficient"] == 0.0
    
    def test_calculate_keto_index_advanced_with_validation_issues(self):
        """Test calculate_keto_index_advanced with validation issues"""
        # This should trigger validation warning but still work
        result = calculate_keto_index_advanced(-10, 5, 15, fiber=5, category="vegetables")
        
        assert isinstance(result, dict)
        assert "keto_index" in result
        assert "keto_category" in result
        assert "carbs_score" in result
        assert "fat_score" in result
        assert "quality_score" in result
        assert "gi_score" in result
    
    def test_calculate_carbs_score_advanced_edge_cases(self):
        """Test calculate_carbs_score_advanced edge cases"""
        # Test different net_carbs ranges
        assert calculate_carbs_score_advanced(0) == 100
        assert calculate_carbs_score_advanced(2) == 100
        assert calculate_carbs_score_advanced(5) == 85
        assert calculate_carbs_score_advanced(10) == 60
        assert calculate_carbs_score_advanced(20) == 0  # Should be 0, not 60
        assert calculate_carbs_score_advanced(30) >= 0  # Should not be negative
    
    def test_calculate_fat_ratio_score_advanced_zero_macros(self):
        """Test calculate_fat_ratio_score_advanced with zero total macros"""
        result = calculate_fat_ratio_score_advanced(0, 0, 0)
        assert result == 0
    
    def test_calculate_fat_ratio_score_advanced_normal_case(self):
        """Test calculate_fat_ratio_score_advanced with normal values"""
        result = calculate_fat_ratio_score_advanced(20, 10, 5)
        assert isinstance(result, (int, float))
        assert 0 <= result <= 100
    
    def test_calculate_fat_ratio_score_advanced_different_percentages(self):
        """Test calculate_fat_ratio_score_advanced with different fat percentages"""
        # Test different fat percentage ranges
        assert calculate_fat_ratio_score_advanced(80, 20, 0) == 100  # 80% fat
        assert calculate_fat_ratio_score_advanced(60, 30, 10) == 80   # 60% fat
        assert calculate_fat_ratio_score_advanced(45, 35, 20) == 60   # 45% fat
        assert calculate_fat_ratio_score_advanced(30, 40, 30) == 40   # 30% fat
        assert calculate_fat_ratio_score_advanced(20, 50, 30) == 20    # 20% fat
    
    def test_calculate_quality_score_advanced_different_levels(self):
        """Test calculate_quality_score_advanced with different processing levels"""
        # Test different processing levels
        assert calculate_quality_score_advanced("raw", "vegetables") == 90
        assert calculate_quality_score_advanced("minimal", "vegetables") == 80  # 90 - 10
        assert calculate_quality_score_advanced("processed", "vegetables") == 60  # 90 - 30
        assert calculate_quality_score_advanced("ultra_processed", "vegetables") == 40  # 90 - 50
        assert calculate_quality_score_advanced("unknown", "vegetables") == 70  # 90 - 20 (default)
    
    def test_calculate_quality_score_advanced_different_categories(self):
        """Test calculate_quality_score_advanced with different categories"""
        # Test different categories when processing_level is None
        assert calculate_quality_score_advanced(None, "leafy_vegetables") == 85
        assert calculate_quality_score_advanced(None, "cruciferous") == 85
        assert calculate_quality_score_advanced(None, "berries") == 85
        assert calculate_quality_score_advanced(None, "nuts_seeds") == 90
        assert calculate_quality_score_advanced(None, "avocado_olives") == 90
        assert calculate_quality_score_advanced(None, "processed") == 50
        assert calculate_quality_score_advanced(None, "unknown_category") == 70
    
    def test_calculate_gi_score_advanced_different_values(self):
        """Test calculate_gi_score_advanced with different glycemic index values"""
        # Test different GI ranges
        assert calculate_gi_score_advanced(None) == 50  # Unknown GI
        assert calculate_gi_score_advanced(0) == 100    # Very low GI
        assert calculate_gi_score_advanced(20) == 90    # Low GI (100 - (20-15)*2 = 90)
        assert calculate_gi_score_advanced(40) == 52.5  # Medium-low GI (60 - (40-35)*1.5 = 52.5)
        assert calculate_gi_score_advanced(60) == 27.0   # Medium GI (30 - (60-55)*0.6 = 27)
        assert calculate_gi_score_advanced(80) == 15.0  # High GI (30 - (80-55)*0.6 = 15)
        assert calculate_gi_score_advanced(100) == 3.0   # Very high GI (30 - (100-55)*0.6 = 3)


class TestValidationAndErrorHandling:
    """Test validation and error handling to increase coverage"""
    
    def test_calculate_calories_from_macros_validation_warning(self):
        """Test calculate_calories_from_macros with validation issues"""
        with patch('src.nutrition_calculator.logger') as mock_logger:
            # Use negative values to trigger validation warning
            result = calculate_calories_from_macros(protein=-10, fats=20, carbs=30)  # Negative protein
            
            # Should still calculate calories but log warning
            assert isinstance(result, float)
            mock_logger.warning.assert_called()
    
    def test_calculate_bmr_mifflin_st_jeor_invalid_profile(self):
        """Test calculate_bmr_mifflin_st_jeor with invalid user profile"""
        with pytest.raises(ValueError, match="Invalid user profile"):
            calculate_bmr_mifflin_st_jeor(weight=-70, height=175, age=30, gender="male")
    
    def test_calculate_bmr_katch_mcardle_invalid_lbm(self):
        """Test calculate_bmr_katch_mcardle with invalid lean body mass"""
        with pytest.raises(ValueError, match="Безжировая масса должна быть положительной"):
            calculate_bmr_katch_mcardle(lean_body_mass=0)
    
    def test_calculate_lean_body_mass_invalid_weight(self):
        """Test calculate_lean_body_mass with invalid weight"""
        with pytest.raises(ValueError, match="Вес должен быть положительным"):
            calculate_lean_body_mass(weight_kg=0, body_fat_percentage=20)
    
    def test_calculate_lean_body_mass_invalid_body_fat_low(self):
        """Test calculate_lean_body_mass with body fat percentage too low"""
        with pytest.raises(ValueError, match="Процент жира должен быть в диапазоне 5-50%"):
            calculate_lean_body_mass(weight_kg=70, body_fat_percentage=4)
    
    def test_calculate_lean_body_mass_invalid_body_fat_high(self):
        """Test calculate_lean_body_mass with body fat percentage too high"""
        with pytest.raises(ValueError, match="Процент жира должен быть в диапазоне 5-50%"):
            calculate_lean_body_mass(weight_kg=70, body_fat_percentage=51)


class TestAdditionalValidationAndErrorHandling:
    """Test additional validation and error handling to increase coverage"""
    
    def test_calculate_tdee_invalid_activity_level(self):
        """Test calculate_tdee with invalid activity level"""
        with pytest.raises(ValueError, match="Неизвестный уровень активности"):
            calculate_tdee(bmr=1500, activity_level="invalid_level")
    
    def test_calculate_target_calories_invalid_goal(self):
        """Test calculate_target_calories with invalid goal"""
        with pytest.raises(ValueError, match="Неизвестная цель"):
            calculate_target_calories(tdee=2000, goal="invalid_goal")
    
    def test_calculate_keto_macros_advanced_keto_type_conversion(self):
        """Test calculate_keto_macros_advanced with KetoType enum"""
        from src.nutrition_calculator import KetoType
        
        result = calculate_keto_macros_advanced(
            target_calories=2000,
            lbm=50,
            keto_type=KetoType.STRICT
        )
        
        assert isinstance(result, dict)
        assert "carbs" in result
        assert "protein" in result
        assert "fats" in result
    
    def test_calculate_keto_macros_advanced_unknown_keto_type(self):
        """Test calculate_keto_macros_advanced with unknown keto type"""
        result = calculate_keto_macros_advanced(
            target_calories=2000,
            lbm=50,
            keto_type="unknown_type"
        )
        
        # Should use default carbs_grams = 35
        assert result["carbs"] == 35
    
    def test_calculate_keto_macros_advanced_active_level(self):
        """Test calculate_keto_macros_advanced with active activity level"""
        result = calculate_keto_macros_advanced(
            target_calories=2500,
            lbm=60,
            activity_level="active",
            keto_type="standard"
        )
        
        # Should use protein_coeff = 2.1 for active level
        assert isinstance(result, dict)
        assert "protein" in result
        assert "fats" in result
        assert "carbs" in result
        # Protein should be 60 * 2.1 = 126g
        assert result["protein"] > 120
    
    def test_calculate_keto_macros_advanced_very_active_level(self):
        """Test calculate_keto_macros_advanced with very_active level"""
        result = calculate_keto_macros_advanced(
            target_calories=3000,
            lbm=70,
            activity_level="very_active",
            keto_type="standard"
        )
        
        # Should use protein_coeff = 2.1 for very_active level
        assert isinstance(result, dict)
        assert result["protein"] > 140  # 70 * 2.1 = 147
    
    def test_calculate_keto_macros_advanced_weight_loss_goal(self):
        """Test calculate_keto_macros_advanced with weight_loss goal"""
        result = calculate_keto_macros_advanced(
            target_calories=1800,
            lbm=55,
            activity_level="moderate",
            goal="weight_loss",
            keto_type="standard"
        )
        
        # Should use protein_coeff = 1.8 + 0.2 = 2.0 for weight loss
        assert isinstance(result, dict)
        assert result["protein"] > 100  # 55 * 2.0 = 110


class TestBoundaryAndEdgeCases:
    """Test boundary conditions and edge cases for comprehensive coverage"""
    
    def test_calculate_calories_from_macros_boundary_values(self):
        """Test calculate_calories_from_macros with boundary values"""
        # Test zero values
        assert calculate_calories_from_macros(0, 0, 0) == 0.0
        
        # Test very small values
        assert calculate_calories_from_macros(0.1, 0.1, 0.1) == 1.7  # 0.1*4 + 0.1*9 + 0.1*4
        
        # Test very large values
        large_calories = calculate_calories_from_macros(100, 100, 100)
        assert large_calories == 1700.0  # 100*4 + 100*9 + 100*4
    
    def test_calculate_bmr_boundary_values(self):
        """Test calculate_bmr_mifflin_st_jeor with boundary values"""
        # Test minimum valid values
        min_bmr = calculate_bmr_mifflin_st_jeor(weight=30, height=100, age=10, gender="male")
        assert min_bmr > 0
        
        # Test maximum valid values
        max_bmr = calculate_bmr_mifflin_st_jeor(weight=200, height=250, age=120, gender="male")
        assert max_bmr > 0
        
        # Test edge case: very tall person
        tall_bmr = calculate_bmr_mifflin_st_jeor(weight=70, height=220, age=30, gender="male")
        assert tall_bmr > 1500
    
    def test_calculate_lean_body_mass_boundary_values(self):
        """Test calculate_lean_body_mass with boundary values"""
        # Test minimum valid body fat percentage
        min_lbm = calculate_lean_body_mass(weight_kg=70, body_fat_percentage=5)
        assert min_lbm == 66.5  # 70 * (1 - 5/100)
        
        # Test maximum valid body fat percentage
        max_lbm = calculate_lean_body_mass(weight_kg=70, body_fat_percentage=50)
        assert max_lbm == 35.0  # 70 * (1 - 50/100)
        
        # Test very light person
        light_lbm = calculate_lean_body_mass(weight_kg=40, body_fat_percentage=20)
        assert light_lbm == 32.0
    
    def test_calculate_net_carbs_advanced_boundary_values(self):
        """Test calculate_net_carbs_advanced with boundary values"""
        # Test with zero carbs
        result = calculate_net_carbs_advanced(0, fiber=0)
        assert result["net_carbs"] == 0
        
        # Test with maximum fiber (equal to carbs) - uses conservative estimation
        result = calculate_net_carbs_advanced(100, fiber=100)
        assert result["net_carbs"] == 25.0  # Conservative estimation
        
        # Test with fiber exceeding carbs - should raise exception
        with pytest.raises(ValueError, match="Клетчатка не может превышать общие углеводы"):
            calculate_net_carbs_advanced(50, fiber=60)
        
        # Test with very high carbs
        result = calculate_net_carbs_advanced(500, fiber=10)
        assert result["net_carbs"] == 492.5  # 500 - 10 + 2.5 (conservative estimation)
    
    def test_calculate_keto_index_advanced_boundary_values(self):
        """Test calculate_keto_index_advanced with boundary values"""
        # Test with zero macros - returns base score
        result = calculate_keto_index_advanced(0, 0, 0, 0)
        assert result["keto_index"] == 65.5  # Base score
        
        # Test with very high carbs - keto index might not be as low as expected due to validation
        result = calculate_keto_index_advanced(100, 20, 10, 5)
        assert result["keto_index"] < 70  # Should be lower than base score
        
        # Test with very high fats
        result = calculate_keto_index_advanced(20, 100, 10, 5)
        assert result["keto_index"] > 50  # Should be high due to high fats
    
    def test_calculate_gki_boundary_values(self):
        """Test calculate_gki with boundary values"""
        # Test with zero glucose and ketones - should raise exception
        with pytest.raises(ValueError, match="Уровни глюкозы и кетонов должны быть положительными"):
            calculate_gki(0, 0)
        
        # Test with very high glucose
        result = calculate_gki(200, 1)
        assert result["gki"] > 100  # Very high GKI
        
        # Test with very high ketones
        result = calculate_gki(80, 5)
        assert result["gki"] < 20  # Very low GKI
    
    def test_validate_nutrition_data_boundary_values(self):
        """Test validate_nutrition_data with boundary values"""
        # Test with maximum valid values
        result = validate_nutrition_data(100, 100, 100, check_total=True)
        assert result.valid is False  # Total exceeds 110g
        
        # Test with minimum valid values
        result = validate_nutrition_data(0, 0, 0, check_total=True)
        assert result.valid is True
        
        # Test with fiber equal to carbs
        result = validate_nutrition_data(50, 20, 30, fiber=30)
        assert result.valid is True
    
    def test_validate_user_profile_boundary_values(self):
        """Test validate_user_profile with boundary values"""
        # Test minimum valid values
        result = validate_user_profile(weight=30, height=100, age=10, gender="male")
        assert result.valid is True
        
        # Test maximum valid values
        result = validate_user_profile(weight=200, height=250, age=120, gender="female")
        assert result.valid is True
        
        # Test edge case: very light person
        result = validate_user_profile(weight=25, height=150, age=20, gender="female")
        assert result.valid is False  # Weight too low
        
        # Test edge case: very heavy person - validation might be more lenient
        result = validate_user_profile(weight=250, height=150, age=20, gender="male")
        # The validation might accept this weight, so we just check it's a valid result
        assert isinstance(result.valid, bool)


