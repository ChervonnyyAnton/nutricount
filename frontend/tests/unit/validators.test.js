/**
 * Unit tests for validators.js
 * 
 * Tests validation functions for products, dishes, and log entries
 */

const {
    safeFloat,
    safeInt,
    cleanString,
    validateProductData,
    validateDishData,
    validateLogData,
    formatDate,
    parseDate
} = require('../../src/business-logic/validators');

describe('Validators', () => {
    
    describe('safeFloat', () => {
        test('should convert valid numbers', () => {
            expect(safeFloat('10.5')).toBe(10.5);
            expect(safeFloat(25.7)).toBe(25.7);
            expect(safeFloat('100')).toBe(100);
        });
        
        test('should return default for invalid values', () => {
            expect(safeFloat(null)).toBe(0);
            expect(safeFloat(undefined)).toBe(0);
            expect(safeFloat('abc')).toBe(0);
            expect(safeFloat(NaN)).toBe(0);
        });
        
        test('should use custom default', () => {
            expect(safeFloat(null, 10)).toBe(10);
            expect(safeFloat('invalid', 5.5)).toBe(5.5);
        });
    });
    
    describe('safeInt', () => {
        test('should convert valid integers', () => {
            expect(safeInt('10')).toBe(10);
            expect(safeInt(25)).toBe(25);
            expect(safeInt('100.7')).toBe(100);
        });
        
        test('should return default for invalid values', () => {
            expect(safeInt(null)).toBe(0);
            expect(safeInt(undefined)).toBe(0);
            expect(safeInt('abc')).toBe(0);
        });
    });
    
    describe('cleanString', () => {
        test('should trim and clean whitespace', () => {
            expect(cleanString('  hello  world  ')).toBe('hello world');
            expect(cleanString('test\n\nvalue')).toBe('test value');
        });
        
        test('should truncate to max length', () => {
            const long = 'a'.repeat(150);
            expect(cleanString(long, 100)).toHaveLength(100);
        });
        
        test('should handle empty strings', () => {
            expect(cleanString('')).toBe('');
            expect(cleanString(null)).toBe('');
        });
    });
    
    describe('validateProductData', () => {
        test('should validate correct product', () => {
            const result = validateProductData({
                name: 'Chicken Breast',
                protein_per_100g: 31,
                fat_per_100g: 3.6,
                carbs_per_100g: 0,
                calories_per_100g: 165
            });
            
            expect(result.valid).toBe(true);
            expect(result.errors).toHaveLength(0);
            expect(result.data.name).toBe('Chicken Breast');
        });
        
        test('should detect missing name', () => {
            const result = validateProductData({
                protein_per_100g: 20,
                fat_per_100g: 10,
                carbs_per_100g: 5
            });
            
            expect(result.valid).toBe(false);
            expect(result.errors[0]).toContain('name is required');
        });
        
        test('should detect short name', () => {
            const result = validateProductData({
                name: 'A',
                protein_per_100g: 20,
                fat_per_100g: 10,
                carbs_per_100g: 5
            });
            
            expect(result.valid).toBe(false);
            expect(result.errors[0]).toContain('at least 2 characters');
        });
        
        test('should detect negative nutrition values', () => {
            const result = validateProductData({
                name: 'Test Product',
                protein_per_100g: -5,
                fat_per_100g: 10,
                carbs_per_100g: 20
            });
            
            expect(result.valid).toBe(false);
            expect(result.errors[0]).toContain('cannot be negative');
        });
        
        test('should detect excessive macros', () => {
            const result = validateProductData({
                name: 'Test Product',
                protein_per_100g: 50,
                fat_per_100g: 40,
                carbs_per_100g: 30 // Total: 120g
            });
            
            expect(result.valid).toBe(false);
            expect(result.errors[0]).toContain('cannot exceed 100g');
        });
    });
    
    describe('validateDishData', () => {
        test('should validate correct dish', () => {
            const result = validateDishData({
                name: 'Chicken Salad',
                ingredients: [
                    { product_id: 1, quantity_grams: 150 },
                    { product_id: 2, quantity_grams: 100 }
                ]
            });
            
            expect(result.valid).toBe(true);
            expect(result.errors).toHaveLength(0);
            expect(result.data.ingredients).toHaveLength(2);
        });
        
        test('should detect missing name', () => {
            const result = validateDishData({
                ingredients: [
                    { product_id: 1, quantity_grams: 150 }
                ]
            });
            
            expect(result.valid).toBe(false);
            expect(result.errors[0]).toContain('name is required');
        });
        
        test('should detect missing ingredients', () => {
            const result = validateDishData({
                name: 'Test Dish',
                ingredients: []
            });
            
            expect(result.valid).toBe(false);
            expect(result.errors[0]).toContain('At least one ingredient');
        });
        
        test('should detect invalid ingredient', () => {
            const result = validateDishData({
                name: 'Test Dish',
                ingredients: [
                    { product_id: 0, quantity_grams: 100 }
                ]
            });
            
            expect(result.valid).toBe(false);
            expect(result.errors[0]).toContain('Valid product ID');
        });
        
        test('should validate preparation method', () => {
            const result = validateDishData({
                name: 'Test Dish',
                ingredients: [
                    { product_id: 1, quantity_grams: 100, preparation_method: 'invalid' }
                ]
            });
            
            expect(result.valid).toBe(false);
            expect(result.errors[0]).toContain('preparation method');
        });
    });
    
    describe('validateLogData', () => {
        test('should validate correct log entry', () => {
            const result = validateLogData({
                date: '2025-10-21',
                item_type: 'product',
                item_id: 1,
                quantity: 150,
                meal_time: 'lunch'
            });
            
            expect(result.valid).toBe(true);
            expect(result.errors).toHaveLength(0);
        });
        
        test('should detect missing date', () => {
            const result = validateLogData({
                item_type: 'product',
                item_id: 1,
                quantity: 150
            });
            
            expect(result.valid).toBe(false);
            expect(result.errors[0]).toContain('Date is required');
        });
        
        test('should detect invalid date format', () => {
            const result = validateLogData({
                date: '21-10-2025',
                item_type: 'product',
                item_id: 1,
                quantity: 150
            });
            
            expect(result.valid).toBe(false);
            expect(result.errors[0]).toContain('YYYY-MM-DD');
        });
        
        test('should detect invalid item type', () => {
            const result = validateLogData({
                date: '2025-10-21',
                item_type: 'invalid',
                item_id: 1,
                quantity: 150
            });
            
            expect(result.valid).toBe(false);
            expect(result.errors[0]).toContain('must be "product" or "dish"');
        });
        
        test('should detect excessive quantity', () => {
            const result = validateLogData({
                date: '2025-10-21',
                item_type: 'product',
                item_id: 1,
                quantity: 15000
            });
            
            expect(result.valid).toBe(false);
            expect(result.errors[0]).toContain('cannot exceed 10000g');
        });
    });
    
    describe('formatDate', () => {
        test('should format Date object', () => {
            const date = new Date('2025-10-21');
            expect(formatDate(date)).toMatch(/2025-10-2\d/);
        });
        
        test('should return string as-is', () => {
            expect(formatDate('2025-10-21')).toBe('2025-10-21');
        });
    });
    
    describe('parseDate', () => {
        test('should parse valid date', () => {
            const date = parseDate('2025-10-21');
            expect(date).toBeInstanceOf(Date);
            expect(date.getFullYear()).toBe(2025);
        });
        
        test('should return null for invalid date', () => {
            expect(parseDate('invalid')).toBeNull();
            expect(parseDate('2025-13-45')).toBeNull();
        });
    });
});
