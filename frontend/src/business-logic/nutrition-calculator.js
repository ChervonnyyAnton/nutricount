/**
 * Nutrition Calculator Module
 * 
 * Core business logic for nutrition calculations.
 * Ported from Python src/nutrition_calculator.py
 * 
 * This module provides:
 * - Calorie calculations from macros
 * - Keto index calculations
 * - Net carbs calculations
 * - Nutrition validation
 * - BMR/TDEE calculations
 */

// ============================================
// Constants (Atwater system)
// ============================================

const CALORIES_PER_GRAM = {
    protein: 4.0,
    carbs: 4.0,
    fats: 9.0,
    alcohol: 7.0,
    sugar_alcohols: 2.4,
    organic_acids: 3.0
};

// Activity level multipliers (Harris-Benedict)
const ACTIVITY_MULTIPLIERS = {
    sedentary: 1.2,
    light: 1.375,
    moderate: 1.55,
    active: 1.725,
    very_active: 1.9
};

// Goal adjustments
const GOAL_ADJUSTMENTS = {
    weight_loss_aggressive: 0.75,  // -25%
    weight_loss: 0.85,              // -15%
    maintenance: 1.0,                // 0%
    muscle_gain: 1.15                // +15%
};

// Keto index categories
const KETO_INDEX_CATEGORIES = [
    { min: 90, max: 100, label: 'Идеально для кето' },
    { min: 80, max: 89, label: 'Отлично для кето' },
    { min: 70, max: 79, label: 'Хорошо для кето' },
    { min: 60, max: 69, label: 'Умеренно подходит' },
    { min: 40, max: 59, label: 'Ограниченно' },
    { min: 20, max: 39, label: 'Избегать' },
    { min: 0, max: 19, label: 'Исключить' }
];

// Fiber ratios by product category
const FIBER_RATIOS = {
    leafy_vegetables: 0.5,
    cruciferous: 0.4,
    root_vegetables: 0.3,
    nuts_seeds: 0.675,
    berries: 0.4,
    avocado_olives: 0.8,
    processed: 0.05,
    unknown: 0.0
};

// ============================================
// Core Calculation Functions
// ============================================

/**
 * Calculate calories from macronutrients using Atwater system
 * @param {number} protein - Protein in grams
 * @param {number} fats - Fats in grams
 * @param {number} carbs - Carbohydrates in grams
 * @returns {number} Total calories
 */
function calculateCaloriesFromMacros(protein, fats, carbs) {
    return (
        protein * CALORIES_PER_GRAM.protein +
        fats * CALORIES_PER_GRAM.fats +
        carbs * CALORIES_PER_GRAM.carbs
    );
}

/**
 * Calculate net carbs (total carbs - fiber)
 * @param {number} totalCarbs - Total carbohydrates in grams
 * @param {number} fiber - Fiber in grams (optional)
 * @param {string} category - Product category for fiber estimation
 * @returns {number} Net carbs
 */
function calculateNetCarbs(totalCarbs, fiber = null, category = 'unknown') {
    if (fiber !== null && fiber >= 0) {
        return Math.max(0, totalCarbs - fiber);
    }
    
    // Estimate fiber based on category
    const fiberRatio = FIBER_RATIOS[category] || FIBER_RATIOS.unknown;
    const estimatedFiber = totalCarbs * fiberRatio;
    return Math.max(0, totalCarbs - estimatedFiber);
}

/**
 * Calculate keto index (0-100 scale)
 * Higher values = better for keto diet
 * 
 * @param {number} protein - Protein in grams
 * @param {number} fats - Fats in grams
 * @param {number} carbs - Net carbs in grams
 * @returns {number} Keto index (0-100)
 */
function calculateKetoIndex(protein, fats, carbs) {
    // Avoid division by zero
    if (protein === 0 && fats === 0 && carbs === 0) {
        return 0;
    }
    
    // Calculate ratios
    const totalMacros = protein + fats + carbs;
    const fatRatio = fats / totalMacros;
    const carbRatio = carbs / totalMacros;
    const proteinRatio = protein / totalMacros;
    
    // Keto index formula
    // Fat bonus: 0-60 points (optimal at 70-80% of calories)
    const fatScore = Math.min(60, fatRatio * 100 * 0.75);
    
    // Carb penalty: 0-30 points deducted (optimal at <5% of calories)
    const carbPenalty = Math.min(30, carbRatio * 100 * 6);
    
    // Protein balance: 0-10 points (optimal at 15-25% of calories)
    let proteinScore = 0;
    if (proteinRatio >= 0.15 && proteinRatio <= 0.25) {
        proteinScore = 10;
    } else if (proteinRatio < 0.15) {
        proteinScore = proteinRatio / 0.15 * 10;
    } else {
        proteinScore = Math.max(0, 10 - (proteinRatio - 0.25) * 40);
    }
    
    const ketoIndex = Math.max(0, Math.min(100, 70 + fatScore - carbPenalty + proteinScore));
    return Math.round(ketoIndex);
}

/**
 * Get keto rating text based on keto index
 * @param {number} ketoIndex - Keto index (0-100)
 * @returns {string} Rating text
 */
function getKetoRating(ketoIndex) {
    for (const category of KETO_INDEX_CATEGORIES) {
        if (ketoIndex >= category.min && ketoIndex <= category.max) {
            return category.label;
        }
    }
    return 'Не определено';
}

/**
 * Validate nutrition data
 * @param {Object} nutrition - Nutrition data
 * @param {number} nutrition.protein - Protein in grams
 * @param {number} nutrition.fats - Fats in grams
 * @param {number} nutrition.carbs - Carbs in grams
 * @param {number} [nutrition.fiber] - Fiber in grams
 * @param {number} [nutrition.calories] - Calories
 * @returns {Object} Validation result { valid: boolean, issues: string[] }
 */
function validateNutritionData(nutrition) {
    const issues = [];
    const { protein, fats, carbs, fiber, calories } = nutrition;
    
    // Check for negative values
    if (protein < 0 || fats < 0 || carbs < 0) {
        issues.push('Макронутриенты не могут быть отрицательными');
    }
    
    // Check fiber
    if (fiber !== null && fiber !== undefined) {
        if (fiber > carbs) {
            issues.push(`Клетчатка (${fiber.toFixed(1)}г) больше углеводов (${carbs.toFixed(1)}г)`);
        } else if (fiber < 0) {
            issues.push('Клетчатка не может быть отрицательной');
        }
    }
    
    // Check total macros
    const totalMacros = protein + fats + carbs;
    if (totalMacros > 110) {
        issues.push(`Сумма БЖУ (${totalMacros.toFixed(1)}г) превышает разумный предел`);
    }
    
    // Check calories if provided
    if (calories !== null && calories !== undefined && calories > 0) {
        const calculatedCalories = calculateCaloriesFromMacros(protein, fats, carbs);
        const calorieDiff = Math.abs(calories - calculatedCalories);
        const diffPercent = (calorieDiff / calories) * 100;
        
        if (diffPercent > 25) {
            issues.push(`Калории расходятся на ${calorieDiff.toFixed(0)} ккал (${diffPercent.toFixed(0)}%)`);
        }
    }
    
    return {
        valid: issues.length === 0,
        issues: issues
    };
}

/**
 * Calculate BMR (Basal Metabolic Rate) using Mifflin-St Jeor equation
 * @param {Object} profile - User profile
 * @param {number} profile.weight - Weight in kg
 * @param {number} profile.height - Height in cm
 * @param {number} profile.age - Age in years
 * @param {string} profile.gender - Gender ('male' or 'female')
 * @returns {number} BMR in calories
 */
function calculateBMR(profile) {
    const { weight, height, age, gender } = profile;
    
    // Mifflin-St Jeor equation
    let bmr = 10 * weight + 6.25 * height - 5 * age;
    
    if (gender === 'male') {
        bmr += 5;
    } else {
        bmr -= 161;
    }
    
    return Math.round(bmr);
}

/**
 * Calculate TDEE (Total Daily Energy Expenditure)
 * @param {Object} profile - User profile
 * @param {number} profile.weight - Weight in kg
 * @param {number} profile.height - Height in cm
 * @param {number} profile.age - Age in years
 * @param {string} profile.gender - Gender ('male' or 'female')
 * @param {string} profile.activityLevel - Activity level
 * @returns {number} TDEE in calories
 */
function calculateTDEE(profile) {
    const bmr = calculateBMR(profile);
    const multiplier = ACTIVITY_MULTIPLIERS[profile.activityLevel] || ACTIVITY_MULTIPLIERS.sedentary;
    return Math.round(bmr * multiplier);
}

/**
 * Calculate daily calorie target based on goal
 * @param {Object} profile - User profile with goal
 * @param {string} profile.goal - Goal (weight_loss, maintenance, muscle_gain)
 * @returns {number} Target calories
 */
function calculateCalorieTarget(profile) {
    const tdee = calculateTDEE(profile);
    const adjustment = GOAL_ADJUSTMENTS[profile.goal] || GOAL_ADJUSTMENTS.maintenance;
    return Math.round(tdee * adjustment);
}

/**
 * Calculate macro targets based on goal
 * @param {Object} profile - User profile
 * @param {string} profile.goal - Goal
 * @param {number} targetCalories - Target daily calories
 * @returns {Object} Macro targets { protein, fats, carbs } in grams
 */
function calculateMacroTargets(profile, targetCalories) {
    const { weight, goal } = profile;
    
    // Protein: 1.6-2.2g per kg for muscle gain, 1.2-1.6g for maintenance/loss
    let proteinGrams;
    if (goal === 'muscle_gain') {
        proteinGrams = weight * 2.0;
    } else if (goal === 'weight_loss' || goal === 'weight_loss_aggressive') {
        proteinGrams = weight * 1.8;
    } else {
        proteinGrams = weight * 1.6;
    }
    
    const proteinCalories = proteinGrams * CALORIES_PER_GRAM.protein;
    
    // Fat: 20-30% of calories for muscle gain, 25-35% for maintenance, 30-40% for weight loss
    let fatPercent;
    if (goal === 'muscle_gain') {
        fatPercent = 0.25;
    } else if (goal === 'weight_loss' || goal === 'weight_loss_aggressive') {
        fatPercent = 0.35;
    } else {
        fatPercent = 0.30;
    }
    
    const fatCalories = targetCalories * fatPercent;
    const fatGrams = fatCalories / CALORIES_PER_GRAM.fats;
    
    // Carbs: remaining calories
    const carbCalories = targetCalories - proteinCalories - fatCalories;
    const carbGrams = Math.max(0, carbCalories / CALORIES_PER_GRAM.carbs);
    
    return {
        protein: Math.round(proteinGrams),
        fats: Math.round(fatGrams),
        carbs: Math.round(carbGrams)
    };
}

// ============================================
// Export for use in Node.js (tests) and browsers
// ============================================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        CALORIES_PER_GRAM,
        ACTIVITY_MULTIPLIERS,
        GOAL_ADJUSTMENTS,
        KETO_INDEX_CATEGORIES,
        FIBER_RATIOS,
        calculateCaloriesFromMacros,
        calculateNetCarbs,
        calculateKetoIndex,
        getKetoRating,
        validateNutritionData,
        calculateBMR,
        calculateTDEE,
        calculateCalorieTarget,
        calculateMacroTargets
    };
}
