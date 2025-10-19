"""
Nutrition Calculator Module v2.0
Полная реализация всех расчетов нутриентов согласно NUTRIENTS.md
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union

# Настройка логирования
logger = logging.getLogger("nutrition_calculator")

# ============================================
# Константы согласно NUTRIENTS.md
# ============================================

# Калорийность макронутриентов (ккал/г) - система Этуотера
CALORIES_PER_GRAM = {
    "protein": 4.0,
    "carbs": 4.0,
    "fats": 9.0,
    "alcohol": 7.0,
    "sugar_alcohols": 2.4,
    "organic_acids": 3.0,
}

# Коэффициенты активности (Harris-Benedict)
ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

# Корректировки по целям
GOAL_ADJUSTMENTS = {
    "weight_loss_aggressive": 0.75,  # -25%
    "weight_loss": 0.85,  # -15%
    "maintenance": 1.0,  # 0%
    "muscle_gain": 1.15,  # +15%
}

# Коэффициенты клетчатки по категориям продуктов (согласно NUTRIENTS.md)
# Используются средние значения из диапазонов
FIBER_RATIOS = {
    "leafy_vegetables": 0.5,  # 50% (среднее из 45-55%)
    "cruciferous": 0.4,  # 40% (среднее из 35-45%)
    "root_vegetables": 0.3,  # 30% (среднее из 25-35%)
    "nuts_seeds": 0.675,  # 67.5% (среднее из 60-75%)
    "berries": 0.4,  # 40% (среднее из 35-45%)
    "avocado_olives": 0.8,  # 80% (среднее из 75-85%)
    "processed": 0.05,  # 5% (среднее из 0-10%)
    "unknown": 0.0,  # 0% (консервативно)
}

# Коэффициенты вычета клетчатки по типам
FIBER_DEDUCTION_COEFFICIENTS = {
    "leafy_vegetables": 1.0,  # целлюлоза - полный вычет
    "cruciferous": 0.85,  # смесь - 85% вычет
    "root_vegetables": 0.75,  # пектин+целлюлоза - 75% вычет
    "nuts_seeds": 0.65,  # гемицеллюлоза - 65% вычет
    "berries": 0.70,  # пектин - 70% вычет
    "avocado_olives": 0.80,  # смеси - 80% вычет
    "processed": 0.50,  # добавки - 50% вычет
    "unknown": 0.0,  # консервативно
}

# Интерпретация кето-индекса (согласно NUTRIENTS.md)
KETO_INDEX_CATEGORIES = {
    (90, 100): "Идеально для кето",
    (80, 89): "Отлично для кето",
    (70, 79): "Хорошо для кето",
    (60, 69): "Умеренно подходит",
    (40, 59): "Ограниченно",
    (20, 39): "Избегать",
    (0, 19): "Исключить",
}

# Интерпретация GKI (глюкозо-кетоновый индекс)
GKI_CATEGORIES = {
    (0, 1): "Терапевтический высокий",
    (1, 3): "Терапевтический",
    (3, 6): "Оптимальный",
    (6, 9): "Умеренный",
    (9, 15): "Слабый кетоз",
    (15, float("inf")): "Нет кетоза",
}

# Коэффициенты выхода при готовке (Yield Factor)
COOKING_YIELD_FACTORS = {
    "meat_boiled": 0.68,
    "meat_grilled": 0.77,
    "meat_fried": 0.72,
    "fish_steamed": 0.87,
    "fish_boiled": 0.83,
    "vegetables_boiled": 0.90,
    "vegetables_steamed": 0.92,
    "pasta_grains": 2.3,  # среднее значение
    "raw": 1.0,
}

# Факторы сохранности нутриентов при готовке
NUTRIENT_RETENTION_FACTORS = {
    "protein": {"boiled": 0.95, "fried": 0.97, "grilled": 0.96, "steamed": 0.98, "raw": 1.00},
    "fats": {
        "boiled": 0.98,
        "fried": 0.85,
        "grilled": 0.90,
        "steamed": 1.00,
        "raw": 1.00,
    },  # +8% веса от масла
    "carbs": {"boiled": 0.95, "fried": 0.97, "grilled": 0.96, "steamed": 0.98, "raw": 1.00},
}

# ============================================
# Структуры данных
# ============================================


class ActivityLevel(Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"


class Goal(Enum):
    WEIGHT_LOSS_AGGRESSIVE = "weight_loss_aggressive"
    WEIGHT_LOSS = "weight_loss"
    MAINTENANCE = "maintenance"
    MUSCLE_GAIN = "muscle_gain"


class KetoType(Enum):
    STRICT = "strict"  # <20г углеводов
    STANDARD = "standard"  # 20-50г углеводов
    MODERATE = "moderate"  # 50-100г углеводов


@dataclass
class NutritionData:
    protein: float
    fats: float
    carbs: float
    fiber: Optional[float] = None
    sugars: Optional[float] = None
    calories: Optional[float] = None
    category: Optional[str] = None
    processing_level: Optional[str] = None
    glycemic_index: Optional[float] = None


@dataclass
class UserProfile:
    weight: float
    height: float
    age: int
    gender: str
    activity_level: ActivityLevel
    goal: Goal
    body_fat_percentage: Optional[float] = None
    lean_body_mass: Optional[float] = None


@dataclass
class RecipeIngredient:
    name: str
    raw_weight: float  # г сырого
    nutrition_per_100g: Dict[str, float]
    category: str
    preparation: str
    edible_portion: float = 1.0


@dataclass
class ValidationResult:
    valid: bool
    issues: List[str]
    severity: str = "warning"
    recommendation: str = ""


# ============================================
# Валидация данных
# ============================================


def validate_nutrition_data(
    protein: float,
    fats: float,
    carbs: float,
    fiber: Optional[float] = None,
    sugars: Optional[float] = None,
    calories: Optional[float] = None,
    check_total: bool = True,
) -> ValidationResult:
    """
    Валидация пищевых данных согласно NUTRIENTS.md

    Returns:
        ValidationResult с детальной информацией о проблемах
    """
    issues = []

    # Проверка отрицательных значений
    if any(x < 0 for x in [protein, fats, carbs]):
        issues.append("Макронутриенты не могут быть отрицательными")

    # Проверка клетчатки
    if fiber is not None:
        if fiber > carbs:
            issues.append(f"Клетчатка {fiber:.1f}г больше углеводов {carbs:.1f}г")
        elif fiber < 0:
            issues.append("Клетчатка не может быть отрицательной")

    # Проверка сахаров
    if sugars is not None:
        if sugars > carbs:
            issues.append(f"Сахара {sugars:.1f}г больше углеводов {carbs:.1f}г")
        elif sugars < 0:
            issues.append("Сахара не могут быть отрицательными")

    # Проверка суммы сахаров и клетчатки
    if sugars is not None and fiber is not None:
        if (sugars + fiber) > carbs * 1.2:
            excess_percent = ((sugars + fiber) / carbs - 1) * 100
            issues.append(f"Сахара + клетчатка больше углеводов на {excess_percent:.0f}%")

    # Проверка общей суммы БЖУ
    if check_total:
        total_macros = protein + fats + carbs
        if total_macros > 110:  # С учетом золы и воды
            issues.append(f"Сумма БЖУ {total_macros:.1f}г превышает разумный предел")

    # Проверка калорий
    if calories is not None and calories > 0:
        calculated_calories = calculate_calories_from_macros(protein, fats, carbs)
        calorie_diff = abs(calories - calculated_calories)
        if calorie_diff / max(calories, 1) > 0.25:  # 25% расхождение
            issues.append(
                f"Калории расходятся на {calorie_diff:.0f} ккал ({calorie_diff/calories*100:.0f}%)"
            )

    # Определение серьезности
    severity = (
        "critical" if any("превышает разумный предел" in issue for issue in issues) else "warning"
    )

    return ValidationResult(
        valid=len(issues) == 0,
        issues=issues,
        severity=severity,
        recommendation="Исправьте ошибки/предупреждения" if issues else "ОК",
    )


def validate_user_profile(weight: float, height: float, age: int, gender: str) -> ValidationResult:
    """Валидация профиля пользователя"""
    issues = []

    if not (30 <= weight <= 500):
        issues.append("Вес должен быть в диапазоне 30-500 кг")

    if not (100 <= height <= 250):
        issues.append("Рост должен быть в диапазоне 100-250 см")

    if not (10 <= age <= 120):
        issues.append("Возраст должен быть в диапазоне 10-120 лет")

    if gender not in ["male", "female"]:
        issues.append("Пол должен быть 'male' или 'female'")

    return ValidationResult(
        valid=len(issues) == 0,
        issues=issues,
        severity="critical" if issues else "ok",
        recommendation="Исправьте ошибки" if issues else "ОК",
    )


# ============================================
# Основные расчеты
# ============================================


def calculate_calories_from_macros(protein: float, fats: float, carbs: float) -> float:
    """
    Расчет калорийности из макронутриентов (система Этуотера)

    Args:
        protein: количество белка в граммах на 100г продукта
        fats: количество жиров в граммах на 100г продукта
        carbs: количество углеводов в граммах на 100г продукта

    Returns:
        calories: калорийность в ккал на 100г продукта
    """
    validation = validate_nutrition_data(protein, fats, carbs, check_total=False)
    if not validation.valid:
        logger.warning(f"Nutrition data validation issues: {validation.issues}")

    calories = (
        protein * CALORIES_PER_GRAM["protein"]
        + fats * CALORIES_PER_GRAM["fats"]
        + carbs * CALORIES_PER_GRAM["carbs"]
    )

    logger.info(
        f"Calories calculation: protein={protein}, fats={fats}, carbs={carbs} -> {calories} kcal"
    )
    return round(calories, 1)


def calculate_net_carbs_advanced(
    total_carbs: float,
    fiber: Optional[float] = None,
    category: Optional[str] = None,
    region: str = "US",
) -> Dict[str, Union[float, bool, str]]:
    """
    Расчет чистых углеводов с учетом клетчатки и категории продукта
    Согласно NUTRIENTS.md - продвинутый алгоритм

    Args:
        total_carbs: общее количество углеводов (г на 100г продукта)
        fiber: количество клетчатки (г на 100г продукта)
        category: категория продукта
        region: регион маркировки ('US', 'EU', 'AU')

    Returns:
        dict с net_carbs, fiber_estimated, estimation_method, fiber_deduction_coefficient
    """
    if total_carbs < 0:
        raise ValueError("Общие углеводы не могут быть отрицательными")

    if fiber is not None:
        # Есть данные о клетчатке
        if fiber > total_carbs:
            raise ValueError("Клетчатка не может превышать общие углеводы")

        # Применяем коэффициент вычета в зависимости от категории
        deduction_coeff = FIBER_DEDUCTION_COEFFICIENTS.get(category, 0.75)  # по умолчанию 75%
        net_carbs = total_carbs - (fiber * deduction_coeff)

        return {
            "net_carbs": round(max(0, net_carbs), 1),
            "fiber_estimated": False,
            "estimation_method": f"direct_fiber_data_coeff_{deduction_coeff}",
            "fiber_deduction_coefficient": deduction_coeff,
        }

    # Нет данных о клетчатке - используем коэффициенты по категории
    if category and category in FIBER_RATIOS:
        fiber_ratio = FIBER_RATIOS[category]
        deduction_coeff = FIBER_DEDUCTION_COEFFICIENTS.get(category, 0.75)
        estimated_fiber = total_carbs * fiber_ratio
        net_carbs = total_carbs - (estimated_fiber * deduction_coeff)
        estimation_method = f"category_{category}_ratio_{fiber_ratio}_coeff_{deduction_coeff}"
    else:
        # Неизвестная категория - консервативный подход
        net_carbs = total_carbs
        estimation_method = "unknown_category_conservative"
        deduction_coeff = 0.0

    logger.info(
        f"Net carbs calculation: total_carbs={total_carbs}, "
        f"category={category} -> net_carbs={net_carbs}"
    )

    return {
        "net_carbs": round(max(0, net_carbs), 1),
        "fiber_estimated": True,
        "estimation_method": estimation_method,
        "fiber_deduction_coefficient": deduction_coeff,
    }


def calculate_keto_index_advanced(
    protein: float,
    fats: float,
    carbs: float,
    fiber: Optional[float] = None,
    category: Optional[str] = None,
    glycemic_index: Optional[float] = None,
    processing_level: Optional[str] = None,
    check_total: bool = True,
) -> Dict[str, Union[float, str]]:
    """
    Расчет кето-индекса продукта согласно NUTRIENTS.md (улучшенная версия)

    Формула: keto_score = (carbs_score * 0.5) + (fat_ratio_score * 0.25) +
    (quality_score * 0.15) + (gi_score * 0.10)

    Args:
        protein: количество белка в граммах на 100г продукта
        fats: количество жиров в граммах на 100г продукта
        carbs: количество углеводов в граммах на 100г продукта
        fiber: количество клетчатки в граммах на 100г продукта
        category: категория продукта
        glycemic_index: гликемический индекс продукта
        processing_level: уровень обработки ('raw', 'minimal', 'processed', 'ultra_processed')
        check_total: проверять ли сумму БЖУ (False для статистики)

    Returns:
        dict с keto_index, keto_category, carbs_score, fat_score, quality_score, gi_score
    """
    validation = validate_nutrition_data(protein, fats, carbs, fiber, check_total=check_total)
    if not validation.valid:
        logger.warning(f"Nutrition data validation issues: {validation.issues}")

    # Расчет чистых углеводов
    net_carbs_result = calculate_net_carbs_advanced(carbs, fiber, category)
    net_carbs = net_carbs_result["net_carbs"]

    # 1. Оценка углеводов (50% веса)
    carbs_score = calculate_carbs_score_advanced(net_carbs)

    # 2. Оценка жиро-белкового профиля (25% веса)
    fat_ratio_score = calculate_fat_ratio_score_advanced(fats, protein, carbs)

    # 3. Оценка качества (15% веса)
    quality_score = calculate_quality_score_advanced(processing_level, category)

    # 4. Оценка гликемического индекса (10% веса)
    gi_score = calculate_gi_score_advanced(glycemic_index)

    # Итоговый кето-индекс
    keto_index = (
        (carbs_score * 0.5) + (fat_ratio_score * 0.25) + (quality_score * 0.15) + (gi_score * 0.10)
    )

    # Определение категории
    keto_category = "Исключить"
    for (min_val, max_val), category_name in KETO_INDEX_CATEGORIES.items():
        if min_val <= keto_index <= max_val:
            keto_category = category_name
            break

    result = {
        "keto_index": round(keto_index, 1),
        "keto_category": keto_category,
        "carbs_score": round(carbs_score, 1),
        "fat_score": round(fat_ratio_score, 1),
        "quality_score": round(quality_score, 1),
        "gi_score": round(gi_score, 1),
        "net_carbs": net_carbs,
        "fiber_estimated": net_carbs_result["fiber_estimated"],
        "fiber_deduction_coefficient": net_carbs_result["fiber_deduction_coefficient"],
    }

    logger.info(
        f"Advanced keto index calculation: protein={protein}, fats={fats}, "
        f"carbs={carbs} -> keto_index={keto_index}"
    )
    return result


def calculate_carbs_score_advanced(net_carbs: float) -> float:
    """Оценка углеводов для кето-индекса (50% веса) согласно NUTRIENTS.md"""
    if net_carbs <= 2:
        return 100  # Максимальный балл
    elif net_carbs <= 5:
        return 100 - ((net_carbs - 2) * 5)  # 85-100 баллов
    elif net_carbs <= 10:
        return 85 - ((net_carbs - 5) * 5)  # 60-85 баллов
    elif net_carbs <= 20:
        return 60 - ((net_carbs - 10) * 6)  # до 60 баллов
    else:
        return max(0, 60 - ((net_carbs - 20) * 3))  # резко ниже


def calculate_fat_ratio_score_advanced(fats: float, protein: float, carbs: float) -> float:
    """Оценка жиро-белкового профиля для кето-индекса (25% веса) согласно NUTRIENTS.md"""
    total_macros = fats + protein + carbs
    if total_macros == 0:
        return 0

    fat_percentage = (fats / total_macros) * 100

    if fat_percentage >= 75:  # Жиры 75-85%, белки ≤ 25%
        return 100
    elif fat_percentage >= 60:
        return 80
    elif fat_percentage >= 45:
        return 60
    elif fat_percentage >= 30:
        return 40
    else:
        return 20


def calculate_quality_score_advanced(
    processing_level: Optional[str], category: Optional[str]
) -> float:
    """Оценка качества для кето-индекса (15% веса) согласно NUTRIENTS.md"""
    base_score = 90  # RAW/минимально обработано

    if processing_level == "raw":
        return base_score
    elif processing_level == "minimal":
        return base_score - 10
    elif processing_level == "processed":
        return base_score - 30
    elif processing_level == "ultra_processed":
        return base_score - 50
    else:
        # Оценка по категории
        if category in ["leafy_vegetables", "cruciferous", "berries"]:
            return base_score - 5
        elif category in ["nuts_seeds", "avocado_olives"]:
            return base_score
        elif category == "processed":
            return base_score - 40
        else:
            return base_score - 20


def calculate_gi_score_advanced(glycemic_index: Optional[float]) -> float:
    """Оценка гликемического индекса для кето-индекса (10% веса) согласно NUTRIENTS.md"""
    if glycemic_index is None:
        return 50  # Нейтральная оценка при отсутствии данных
    elif glycemic_index <= 15:
        return 100
    elif glycemic_index <= 35:
        return 100 - ((glycemic_index - 15) * 2)  # линейный спад до 60
    elif glycemic_index <= 55:
        return 60 - ((glycemic_index - 35) * 1.5)  # до 30 баллов
    else:
        return max(0, 30 - ((glycemic_index - 55) * 0.6))  # до нуля


def calculate_bmr_mifflin_st_jeor(weight: float, height: float, age: int, gender: str) -> float:
    """
    Расчет базового метаболизма (BMR) по формуле Миффлина-Сан Жеора

    Args:
        weight: вес в кг
        height: рост в см
        age: возраст в годах
        gender: пол ('male' или 'female')

    Returns:
        BMR в ккал/день
    """
    validation = validate_user_profile(weight, height, age, gender)
    if not validation.valid:
        raise ValueError(f"Invalid user profile: {validation.issues}")

    if gender == "male":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (
            (10 * weight) + (6.25 * height) - (5 * age) - 161
        )

    logger.info(
        f"BMR calculation (Mifflin-St Jeor): weight={weight}, "
        f"height={height}, age={age}, gender={gender} -> {bmr} kcal"
    )
    return round(bmr, 0)


def calculate_bmr_katch_mcardle(lean_body_mass: float) -> float:
    """
    Расчет базового метаболизма (BMR) по формуле Кэтча-МакАрдла
    Точнее при высоком % жира

    Args:
        lean_body_mass: безжировая масса тела в кг

    Returns:
        BMR в ккал/день
    """
    if lean_body_mass <= 0:
        raise ValueError("Безжировая масса должна быть положительной")

    bmr = 370 + (21.6 * lean_body_mass)
    logger.info(f"BMR calculation (Katch-McArdle): LBM={lean_body_mass} -> {bmr} kcal")
    return round(bmr, 0)


def calculate_lean_body_mass(weight_kg: float, body_fat_percentage: float) -> float:
    """
    Расчет безжировой массы тела (LBM) из процента жира согласно NUTRIENTS.md

    Args:
        weight_kg: вес в кг
        body_fat_percentage: процент жира в теле (5-50%)

    Returns:
        LBM в кг
    """
    if weight_kg <= 0:
        raise ValueError("Вес должен быть положительным")

    if not (5 <= body_fat_percentage <= 50):
        raise ValueError("Процент жира должен быть в диапазоне 5-50%")

    lbm = weight_kg * (1 - body_fat_percentage / 100)

    logger.info(
        f"LBM calculation: weight={weight_kg}, body_fat={body_fat_percentage}% -> LBM={lbm} kg"
    )
    return round(lbm, 2)


def calculate_tdee(bmr: float, activity_level: Union[str, ActivityLevel]) -> float:
    """
    Расчет общего расхода энергии (TDEE)

    Args:
        bmr: базовый метаболизм в ккал/день
        activity_level: уровень активности

    Returns:
        TDEE в ккал/день
    """
    if isinstance(activity_level, ActivityLevel):
        activity_level = activity_level.value

    if activity_level not in ACTIVITY_MULTIPLIERS:
        raise ValueError(f"Неизвестный уровень активности: {activity_level}")

    tdee = bmr * ACTIVITY_MULTIPLIERS[activity_level]
    logger.info(f"TDEE calculation: BMR={bmr}, activity={activity_level} -> {tdee} kcal")
    return round(tdee, 0)


def calculate_target_calories(tdee: float, goal: Union[str, Goal]) -> float:
    """
    Расчет целевых калорий с учетом цели

    Args:
        tdee: общий расход энергии в ккал/день
        goal: цель

    Returns:
        целевые калории в ккал/день
    """
    if isinstance(goal, Goal):
        goal = goal.value

    if goal not in GOAL_ADJUSTMENTS:
        raise ValueError(f"Неизвестная цель: {goal}")

    target_calories = tdee * GOAL_ADJUSTMENTS[goal]
    logger.info(f"Target calories calculation: TDEE={tdee}, goal={goal} -> {target_calories} kcal")
    return round(target_calories, 0)


def calculate_keto_macros_advanced(
    target_calories: float,
    lbm: Optional[float] = None,
    activity_level: str = "moderate",
    keto_type: Union[str, KetoType] = "standard",
    goal: str = "maintenance",
) -> Dict[str, float]:
    """
    Расчет кетогенных макросов согласно NUTRIENTS.md

    Args:
        target_calories: целевые калории в ккал/день
        lbm: безжировая масса тела в кг (для расчета белка)
        activity_level: уровень активности
        keto_type: тип кето-диеты
        goal: цель

    Returns:
        dict с carbs, protein, fats в граммах и процентах
    """
    if isinstance(keto_type, KetoType):
        keto_type = keto_type.value

    # 1. Углеводы - фиксированное количество в зависимости от типа кето (согласно NUTRIENTS.md)
    if keto_type == "strict":
        carbs_grams = 20  # <20 г согласно NUTRIENTS.md
    elif keto_type == "standard":
        carbs_grams = 35  # среднее между 20-50 г согласно NUTRIENTS.md
    elif keto_type == "moderate":
        carbs_grams = 75  # среднее между 50-100 г согласно NUTRIENTS.md
    else:
        carbs_grams = 35  # по умолчанию стандартное кето

    carbs_calories = carbs_grams * 4

    # 2. Белки - от безжировой массы тела (LBM)
    if lbm is not None:
        # Коэффициенты белка от LBM (согласно NUTRIENTS.md)
        protein_coeff = 1.8  # базовый коэффициент для умеренной активности
        if activity_level in ["active", "very_active"]:
            protein_coeff = 2.1  # среднее из 2.0-2.2 г/кг LBM для активных тренировок
        else:
            # Для неактивных уровней применяем базовый коэффициент
            if goal == "weight_loss":
                protein_coeff += 0.2  # +0.2 к базовому коэффициенту для похудения

        protein_grams = lbm * protein_coeff
    else:
        # Если LBM неизвестна, используем процент от калорий
        protein_calories = target_calories * 0.20
        protein_grams = protein_calories / 4

    protein_calories = protein_grams * 4

    # 3. Жиры - остаток
    fats_calories = target_calories - carbs_calories - protein_calories
    fats_grams = fats_calories / 9

    result = {
        "carbs": round(carbs_grams, 1),
        "protein": round(protein_grams, 1),
        "fats": round(fats_grams, 1),
        "calories": round(target_calories, 0),
        "carbs_percentage": round((carbs_calories / target_calories) * 100, 1),
        "protein_percentage": round(
            (protein_calories / target_calories) * 100, 1
        ),
        "fats_percentage": round((fats_calories / target_calories) * 100, 1),
        "keto_type": keto_type,
        "lbm_used": lbm is not None,
    }

    logger.info(
        f"Advanced keto macros calculation: target_calories={target_calories}, "
        f"keto_type={keto_type} -> {result}"
    )
    return result


def calculate_gki(glucose_mgdl: float, ketones_mgdl: float) -> Dict[str, Union[float, str]]:
    """
    Расчет глюкозо-кетонового индекса (GKI) согласно NUTRIENTS.md

    Args:
        glucose_mgdl: уровень глюкозы в мг/дл
        ketones_mgdl: уровень кетонов в мг/дл

    Returns:
        dict с gki, gki_category, glucose_mmol, ketones_mmol
    """
    if glucose_mgdl <= 0 or ketones_mgdl <= 0:
        raise ValueError("Уровни глюкозы и кетонов должны быть положительными")

    # Конвертация в ммоль/л
    glucose_mmol = glucose_mgdl / 18.0
    ketones_mmol = ketones_mgdl / 10.4  # согласно NUTRIENTS.md

    # Расчет GKI
    gki = glucose_mmol / ketones_mmol

    # Определение категории
    gki_category = "Нет кетоза"
    for (min_val, max_val), category_name in GKI_CATEGORIES.items():
        if min_val <= gki < max_val:
            gki_category = category_name
            break

    result = {
        "gki": round(gki, 2),
        "gki_category": gki_category,
        "glucose_mmol": round(glucose_mmol, 2),
        "ketones_mmol": round(ketones_mmol, 2),
        "glucose_mgdl": glucose_mgdl,
        "ketones_mgdl": ketones_mgdl,
    }

    logger.info(f"GKI calculation: glucose={glucose_mgdl}, ketones={ketones_mgdl} -> GKI={gki}")
    return result


# ============================================
# Расчет рецептов и блюд
# ============================================


def calculate_cooking_fat(ingredient: RecipeIngredient, cooking_method: str) -> float:
    """
    Расчет дополнительного жира при готовке согласно NUTRIENTS.md

    Args:
        ingredient: ингредиент рецепта
        cooking_method: способ приготовления

    Returns:
        дополнительный жир в граммах
    """
    if cooking_method == "fried":
        if ingredient.category in ["meat", "fish"]:
            return ingredient.raw_weight * 0.03  # +3% от веса
        elif ingredient.category in ["vegetable", "bread"]:
            return ingredient.raw_weight * 0.08  # +8% от веса
    elif cooking_method == "grilled" and ingredient.category in ["meat"]:
        return -ingredient.raw_weight * 0.05  # -5% собственного жира

    return 0.0


def calculate_recipe_nutrition(
    ingredients: List[RecipeIngredient], recipe_name: str, servings: int = 1
) -> Dict:
    """
    Расчет нутриентов рецепта согласно NUTRIENTS.md

    Args:
        ingredients: список ингредиентов
        recipe_name: название рецепта
        servings: количество порций

    Returns:
        dict с полной информацией о рецепте
    """
    total_raw_weight = sum(ing.raw_weight for ing in ingredients)
    total_cooked_weight = 0
    total_nutrition = {"protein": 0, "fats": 0, "carbs": 0, "calories": 0}

    ingredients_breakdown = []

    for ingredient in ingredients:
        # Коэффициент выхода
        yield_factor = COOKING_YIELD_FACTORS.get(
            f"{ingredient.category}_{ingredient.preparation}", 1.0
        )
        cooked_weight = ingredient.raw_weight * yield_factor

        # Факторы сохранности нутриентов
        retention_protein = NUTRIENT_RETENTION_FACTORS["protein"].get(ingredient.preparation, 1.0)
        retention_fats = NUTRIENT_RETENTION_FACTORS["fats"].get(ingredient.preparation, 1.0)
        retention_carbs = NUTRIENT_RETENTION_FACTORS["carbs"].get(ingredient.preparation, 1.0)

        # Расчет нутриентов после готовки
        protein = (
            ingredient.nutrition_per_100g["protein"]
            * ingredient.raw_weight
            / 100
            * retention_protein
        )
        fats = ingredient.nutrition_per_100g["fats"] * ingredient.raw_weight / 100 * retention_fats
        carbs = (
            ingredient.nutrition_per_100g["carbs"] * ingredient.raw_weight / 100 * retention_carbs
        )

        # Дополнительный жир при готовке
        cooking_fat = calculate_cooking_fat(ingredient, ingredient.preparation)
        fats += cooking_fat

        calories = calculate_calories_from_macros(protein, fats, carbs)

        # Добавляем к общим нутриентам
        total_nutrition["protein"] += protein
        total_nutrition["fats"] += fats
        total_nutrition["carbs"] += carbs
        total_nutrition["calories"] += calories

        total_cooked_weight += cooked_weight

        ingredients_breakdown.append(
            {
                "name": ingredient.name,
                "raw_weight": ingredient.raw_weight,
                "cooked_weight": cooked_weight,
                "nutrition": {
                    "protein": round(protein, 1),
                    "fats": round(fats, 1),
                    "carbs": round(carbs, 1),
                    "calories": round(calories, 1),
                },
            }
        )

    # Расчет на 100г готового блюда
    nutrition_per_100g = {}
    for nutrient in total_nutrition:
        nutrition_per_100g[nutrient] = (
            round(total_nutrition[nutrient] * 100 / total_cooked_weight, 1)
            if total_cooked_weight > 0
            else 0
        )

    # Расчет на порцию
    nutrition_per_serving = {}
    for nutrient in total_nutrition:
        nutrition_per_serving[nutrient] = round(total_nutrition[nutrient] / servings, 1)

    # Расчет чистых углеводов для готового блюда
    total_fiber = sum(
        ing.nutrition_per_100g.get("fiber", 0) * ing.raw_weight / 100 for ing in ingredients
    )
    fiber_per_100g = total_fiber * 100 / total_cooked_weight if total_cooked_weight > 0 else 0
    net_carbs_per_100g = nutrition_per_100g["carbs"] - fiber_per_100g

    # Расчет кето-индекса для готового блюда
    keto_result = calculate_keto_index_advanced(
        nutrition_per_100g["protein"],
        nutrition_per_100g["fats"],
        nutrition_per_100g["carbs"],
        fiber=fiber_per_100g,
    )

    # Добавляем net_carbs в nutrition_per_100g
    nutrition_per_100g["net_carbs"] = round(net_carbs_per_100g, 1)
    nutrition_per_100g["fiber"] = round(fiber_per_100g, 1)

    result = {
        "recipe_name": recipe_name,
        "servings": servings,
        "weights": {
            "total_raw": round(total_raw_weight, 1),
            "total_cooked": round(total_cooked_weight, 1),
            "yield_factor": (
                round(total_cooked_weight / total_raw_weight, 2) if total_raw_weight > 0 else 0
            ),
        },
        "nutrition_total": {k: round(v, 1) for k, v in total_nutrition.items()},
        "nutrition_per_100g": nutrition_per_100g,
        "nutrition_per_serving": nutrition_per_serving,
        "ingredients_breakdown": ingredients_breakdown,
        "keto_index": keto_result["keto_index"],
        "keto_category": keto_result["keto_category"],
    }

    logger.info(f"Recipe calculation: {recipe_name} -> {result}")
    return result


def validate_recipe_integrity(recipe_data: Dict) -> ValidationResult:
    """
    Проверка целостности и корректности рецепта согласно NUTRIENTS.md

    Args:
        recipe_data: данные рецепта

    Returns:
        ValidationResult с результатами проверки
    """
    issues = []

    ingredients = recipe_data.get("ingredients_breakdown", [])
    calculated_raw_weight = sum(
        ing["raw_weight"] for ing in ingredients
    )
    stated_raw_weight = recipe_data["weights"]["total_raw"]

    # Проверка соответствия веса сырых ингредиентов
    if abs(calculated_raw_weight - stated_raw_weight) > 1:
        issues.append(
            f"Несоответствие веса сырых ингредиентов: "
            f"{calculated_raw_weight:.0f}г vs {stated_raw_weight:.0f}г"
        )

    # Проверка соответствия нутриентов
    calculated_nutrition = {"protein": 0, "fats": 0, "carbs": 0, "calories": 0}
    for ing in ingredients:
        for nutrient in calculated_nutrition:
            calculated_nutrition[nutrient] += ing["nutrition"][nutrient]

    stated_nutrition = recipe_data["nutrition_total"]
    for nutrient in calculated_nutrition:
        calc_val = calculated_nutrition[nutrient]
        stated_val = stated_nutrition[nutrient]
        if abs(calc_val - stated_val) > max(1, stated_val * 0.02):  # 2% погрешность
            issues.append(f"Несоответствие {nutrient}: {calc_val:.1f} vs {stated_val:.1f}")

    # Проверка коэффициента выхода
    total_raw = recipe_data["weights"]["total_raw"]
    total_cooked = recipe_data["weights"]["total_cooked"]
    overall_yield = total_cooked / total_raw if total_raw > 0 else 0

    if overall_yield < 0.5 or overall_yield > 3.0:
        issues.append(f"Необычный коэффициент выхода: {overall_yield:.2f}")

    return ValidationResult(
        valid=len(issues) == 0,
        issues=issues,
        severity="warning" if issues else "ok",
        recommendation="Проверьте расчеты рецепта" if issues else "ОК",
    )


# ============================================
# Утилиты и вспомогательные функции
# ============================================


def round_nutrition_values(
    calories: float, carbs: float, protein: float, fats: float
) -> Dict[str, float]:
    """Стандартное округление пищевых значений"""
    return {
        "calories": round(calories, 0),  # Целые числа
        "carbs": round(carbs, 1),  # 1 знак после запятой
        "protein": round(protein, 1),  # 1 знак после запятой
        "fats": round(fats, 1),  # 1 знак после запятой
    }


def log_calculation(func_name: str, inputs: Dict, result: Dict) -> None:
    """Логирование расчетов для отладки"""
    logger.info(f"{func_name}: inputs={inputs}, result={result}")


# ============================================
# Обратная совместимость
# ============================================


def calculate_net_carbs(
    total_carbs: float,
    fiber: Optional[float] = None,
    category: Optional[str] = None,
    region: str = "US",
) -> Dict[str, Union[float, bool, str]]:
    """Обратная совместимость - вызывает продвинутую версию"""
    return calculate_net_carbs_advanced(total_carbs, fiber, category, region)


def calculate_keto_index(
    protein: float,
    fats: float,
    carbs: float,
    fiber: Optional[float] = None,
    category: Optional[str] = None,
    glycemic_index: Optional[float] = None,
    check_total: bool = True,
) -> Dict[str, Union[float, str]]:
    """Обратная совместимость - вызывает продвинутую версию"""
    return calculate_keto_index_advanced(
        protein, fats, carbs, fiber, category, glycemic_index, None, check_total
    )


def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    """Обратная совместимость - вызывает Миффлин-Сан Жеор"""
    return calculate_bmr_mifflin_st_jeor(weight, height, age, gender)


def calculate_keto_macros(target_calories: float) -> Dict[str, float]:
    """Обратная совместимость - вызывает продвинутую версию"""
    return calculate_keto_macros_advanced(target_calories)


# ============================================
# Примеры использования
# ============================================


def example_avocado_analysis():
    """Пример анализа авокадо согласно NUTRIENTS.md"""
    protein = 2.0
    fats = 14.7
    total_carbs = 8.5
    fiber = 6.7

    # Расчеты
    calories = calculate_calories_from_macros(protein, fats, total_carbs)
    net_carbs_result = calculate_net_carbs_advanced(total_carbs, fiber, "avocado_olives")
    keto_result = calculate_keto_index_advanced(
        protein, fats, total_carbs, fiber, "avocado_olives", 15, "raw"
    )

    print("Авокадо (на 100г):")
    print(f"Калории: {calories} ккал")
    print(f"Чистые углеводы: {net_carbs_result['net_carbs']} г")
    print(f"Кето-индекс: {keto_result['keto_index']} - {keto_result['keto_category']}")
    print(
        f"Компоненты: углеводы={keto_result['carbs_score']}, "
        f"жиры={keto_result['fat_score']}, "
        f"качество={keto_result['quality_score']}, "
        f"ГИ={keto_result['gi_score']}"
    )

    return {
        "calories": calories,
        "net_carbs": net_carbs_result["net_carbs"],
        "keto_index": keto_result["keto_index"],
        "keto_category": keto_result["keto_category"],
    }


def example_daily_macros():
    """Пример расчета дневных макросов согласно NUTRIENTS.md"""
    # Профиль: мужчина 31 год, 121.8 кг, 185 см, умеренная активность, похудение, 35.2% жира
    weight = 121.8
    height = 185
    age = 31
    gender = "male"
    body_fat_percentage = 35.2
    lbm = weight * (1 - body_fat_percentage / 100)  # 78.93 кг

    bmr = calculate_bmr_mifflin_st_jeor(weight, height, age, gender)
    tdee = calculate_tdee(bmr, "moderate")
    target_calories = calculate_target_calories(tdee, "weight_loss")
    macros = calculate_keto_macros_advanced(
        target_calories, lbm, "moderate", "standard", "weight_loss"
    )

    print("Дневные макросы:")
    print(f"BMR: {bmr} ккал")
    print(f"TDEE: {tdee} ккал")
    print(f"Целевые калории: {target_calories} ккал")
    print(f"Углеводы: {macros['carbs']}г ({macros['carbs_percentage']}%)")
    print(f"Белки: {macros['protein']}г ({macros['protein_percentage']}%)")
    print(f"Жиры: {macros['fats']}г ({macros['fats_percentage']}%)")
    print(f"LBM использована: {macros['lbm_used']}")

    return macros


def example_recipe_calculation():
    """Пример расчета сложного рецепта согласно NUTRIENTS.md"""
    ingredients = [
        RecipeIngredient(
            "Куриное бедро",
            600,
            {"protein": 18.4, "fats": 8.1, "carbs": 0, "fiber": 0},
            "meat",
            "grilled",
        ),
        RecipeIngredient(
            "Брокколи",
            400,
            {"protein": 2.8, "fats": 0.4, "carbs": 6.6, "fiber": 2.6},
            "cruciferous",
            "steamed",
        ),
        RecipeIngredient(
            "Сыр чеддер", 150, {"protein": 25, "fats": 33, "carbs": 1.3, "fiber": 0}, "dairy", "raw"
        ),
        RecipeIngredient(
            "Оливковое масло", 30, {"protein": 0, "fats": 100, "carbs": 0, "fiber": 0}, "oil", "raw"
        ),
    ]

    recipe = calculate_recipe_nutrition(ingredients, "Кето-запеканка", servings=4)
    validation = validate_recipe_integrity(recipe)

    print(f"Рецепт: {recipe['recipe_name']}")
    print(f"Порций: {recipe['servings']}")
    print(f"Вес сырой: {recipe['weights']['total_raw']}г")
    print(f"Вес готовый: {recipe['weights']['total_cooked']}г")
    print(f"Коэффициент выхода: {recipe['weights']['yield_factor']}")
    print(
        f"На порцию: белки {recipe['nutrition_per_serving']['protein']}г, "
        f"жиры {recipe['nutrition_per_serving']['fats']}г, "
        f"углеводы {recipe['nutrition_per_serving']['carbs']}г"
    )
    print(f"Кето-индекс: {recipe['keto_index']} - {recipe['keto_category']}")
    print(f"Валидация: {'ОК' if validation.valid else validation.issues}")

    return recipe


if __name__ == "__main__":
    # Запуск примеров
    print("=== Пример анализа авокадо ===")
    example_avocado_analysis()

    print("\n=== Пример дневных макросов ===")
    example_daily_macros()

    print("\n=== Пример расчета рецепта ===")
    example_recipe_calculation()
