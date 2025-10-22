/**
 * Unit tests for nutrition-calculator.js
 * 
 * Tests core nutrition calculation functions
 */

// Import the module
const {
    CALORIES_PER_GRAM,
    calculateCaloriesFromMacros,
    calculateNetCarbs,
    calculateKetoIndex,
    getKetoRating,
    validateNutritionData,
    calculateBMR,
    calculateTDEE,
    calculateCalorieTarget,
    calculateMacroTargets
} = require('../../src/business-logic/nutrition-calculator');

describe('Nutrition Calculator', () => {
    
    describe('calculateCaloriesFromMacros', () => {
        test('should calculate calories correctly using Atwater system', () => {
            expect(calculateCaloriesFromMacros(10, 10, 10)).toBe(170); // 10*4 + 10*9 + 10*4 = 170
            expect(calculateCaloriesFromMacros(25, 15, 30)).toBe(355); // 25*4 + 15*9 + 30*4 = 355
        });
        
        test('should handle zero values', () => {
            expect(calculateCaloriesFromMacros(0, 0, 0)).toBe(0);
            expect(calculateCaloriesFromMacros(10, 0, 0)).toBe(40);
        });
        
        test('should use correct coefficients', () => {
            expect(calculateCaloriesFromMacros(1, 0, 0)).toBe(CALORIES_PER_GRAM.protein);
            expect(calculateCaloriesFromMacros(0, 1, 0)).toBe(CALORIES_PER_GRAM.fats);
            expect(calculateCaloriesFromMacros(0, 0, 1)).toBe(CALORIES_PER_GRAM.carbs);
        });
    });
    
    describe('calculateNetCarbs', () => {
        test('should subtract fiber from total carbs', () => {
            expect(calculateNetCarbs(20, 5)).toBe(15);
            expect(calculateNetCarbs(30, 10)).toBe(20);
        });
        
        test('should not go below zero', () => {
            expect(calculateNetCarbs(10, 15)).toBe(0);
            expect(calculateNetCarbs(5, 10)).toBe(0);
        });
        
        test('should estimate fiber based on category', () => {
            // Leafy vegetables: 50% fiber
            expect(calculateNetCarbs(20, null, 'leafy_vegetables')).toBe(10);
            // Nuts/seeds: 67.5% fiber
            expect(calculateNetCarbs(20, null, 'nuts_seeds')).toBeCloseTo(6.5, 1);
            // Unknown: 0% fiber (conservative)
            expect(calculateNetCarbs(20, null, 'unknown')).toBe(20);
        });
    });
    
    describe('calculateKetoIndex', () => {
        test('should return 0 for all zeros', () => {
            expect(calculateKetoIndex(0, 0, 0)).toBe(0);
        });
        
        test('should rate high-fat low-carb as excellent', () => {
            const index = calculateKetoIndex(25, 70, 5); // Typical keto ratios
            expect(index).toBeGreaterThanOrEqual(80); // Should be 80-100
        });
        
        test('should rate high-carb as moderate/limited', () => {
            const index = calculateKetoIndex(20, 20, 60); // High carb (60%)
            expect(index).toBeGreaterThanOrEqual(60); // Moderate range
            expect(index).toBeLessThan(70); // Not good for keto
        });
        
        test('should be in valid range 0-100', () => {
            const index1 = calculateKetoIndex(10, 80, 10);
            const index2 = calculateKetoIndex(50, 25, 25);
            const index3 = calculateKetoIndex(15, 15, 70);
            
            expect(index1).toBeGreaterThanOrEqual(0);
            expect(index1).toBeLessThanOrEqual(100);
            expect(index2).toBeGreaterThanOrEqual(0);
            expect(index2).toBeLessThanOrEqual(100);
            expect(index3).toBeGreaterThanOrEqual(0);
            expect(index3).toBeLessThanOrEqual(100);
        });
    });
    
    describe('getKetoRating', () => {
        test('should return correct rating for index', () => {
            expect(getKetoRating(95)).toBe('Идеально для кето');
            expect(getKetoRating(85)).toBe('Отлично для кето');
            expect(getKetoRating(75)).toBe('Хорошо для кето');
            expect(getKetoRating(65)).toBe('Умеренно подходит');
            expect(getKetoRating(50)).toBe('Ограниченно');
            expect(getKetoRating(30)).toBe('Избегать');
            expect(getKetoRating(10)).toBe('Исключить');
        });
        
        test('should handle edge cases', () => {
            expect(getKetoRating(100)).toBe('Идеально для кето');
            expect(getKetoRating(0)).toBe('Исключить');
        });
    });
    
    describe('validateNutritionData', () => {
        test('should validate correct data', () => {
            const result = validateNutritionData({
                protein: 25,
                fats: 15,
                carbs: 30,
                fiber: 5,
                calories: 355
            });
            
            expect(result.valid).toBe(true);
            expect(result.issues).toHaveLength(0);
        });
        
        test('should detect negative values', () => {
            const result = validateNutritionData({
                protein: -5,
                fats: 10,
                carbs: 20
            });
            
            expect(result.valid).toBe(false);
            expect(result.issues.length).toBeGreaterThan(0);
            expect(result.issues[0]).toContain('отрицательными');
        });
        
        test('should detect fiber > carbs', () => {
            const result = validateNutritionData({
                protein: 20,
                fats: 10,
                carbs: 10,
                fiber: 15
            });
            
            expect(result.valid).toBe(false);
            expect(result.issues[0]).toContain('Клетчатка');
        });
        
        test('should detect excessive total macros', () => {
            const result = validateNutritionData({
                protein: 50,
                fats: 40,
                carbs: 30 // Total: 120g
            });
            
            expect(result.valid).toBe(false);
            expect(result.issues[0]).toContain('превышает');
        });
        
        test('should detect calorie mismatch', () => {
            const result = validateNutritionData({
                protein: 20, // 80 cal
                fats: 10,    // 90 cal
                carbs: 20,   // 80 cal
                calories: 500 // Should be ~250
            });
            
            expect(result.valid).toBe(false);
            expect(result.issues[0]).toContain('расходятся');
        });
    });
    
    describe('calculateBMR', () => {
        test('should calculate BMR for male', () => {
            const bmr = calculateBMR({
                weight: 80,
                height: 180,
                age: 30,
                gender: 'male'
            });
            
            // Mifflin-St Jeor: 10*80 + 6.25*180 - 5*30 + 5
            const expected = 10 * 80 + 6.25 * 180 - 5 * 30 + 5;
            expect(bmr).toBe(Math.round(expected));
        });
        
        test('should calculate BMR for female', () => {
            const bmr = calculateBMR({
                weight: 65,
                height: 165,
                age: 28,
                gender: 'female'
            });
            
            // Mifflin-St Jeor: 10*65 + 6.25*165 - 5*28 - 161
            const expected = 10 * 65 + 6.25 * 165 - 5 * 28 - 161;
            expect(bmr).toBe(Math.round(expected));
        });
    });
    
    describe('calculateTDEE', () => {
        test('should multiply BMR by activity level', () => {
            const profile = {
                weight: 80,
                height: 180,
                age: 30,
                gender: 'male',
                activityLevel: 'moderate'
            };
            
            const bmr = calculateBMR(profile);
            const tdee = calculateTDEE(profile);
            
            expect(tdee).toBeGreaterThan(bmr);
            expect(tdee / bmr).toBeCloseTo(1.55, 1); // moderate = 1.55
        });
    });
    
    describe('calculateCalorieTarget', () => {
        test('should adjust TDEE based on goal', () => {
            const profile = {
                weight: 80,
                height: 180,
                age: 30,
                gender: 'male',
                activityLevel: 'moderate',
                goal: 'weight_loss'
            };
            
            const tdee = calculateTDEE(profile);
            const target = calculateCalorieTarget(profile);
            
            expect(target).toBeLessThan(tdee); // Weight loss should be less
            expect(target / tdee).toBeCloseTo(0.85, 1); // -15%
        });
    });
    
    describe('calculateMacroTargets', () => {
        test('should calculate balanced macros', () => {
            const profile = {
                weight: 80,
                goal: 'maintenance'
            };
            const targetCalories = 2000;
            
            const macros = calculateMacroTargets(profile, targetCalories);
            
            expect(macros.protein).toBeGreaterThan(0);
            expect(macros.fats).toBeGreaterThan(0);
            expect(macros.carbs).toBeGreaterThan(0);
            
            // Check that macros sum to approximately target calories
            const totalCalories = 
                macros.protein * 4 + 
                macros.fats * 9 + 
                macros.carbs * 4;
            
            expect(totalCalories).toBeCloseTo(targetCalories, -2); // Within 100 cal
        });
        
        test('should adjust protein for muscle gain', () => {
            const profileGain = { weight: 80, goal: 'muscle_gain' };
            const profileMaintain = { weight: 80, goal: 'maintenance' };
            
            const macrosGain = calculateMacroTargets(profileGain, 2500);
            const macrosMaintain = calculateMacroTargets(profileMaintain, 2000);
            
            expect(macrosGain.protein).toBeGreaterThan(macrosMaintain.protein);
        });
    });
});
