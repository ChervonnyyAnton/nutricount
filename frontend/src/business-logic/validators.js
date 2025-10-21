/**
 * Validators Module
 * 
 * Data validation functions for products, dishes, and log entries.
 * Ported from Python src/utils.py
 */

/**
 * Safely convert value to float
 * @param {any} value - Value to convert
 * @param {number} defaultValue - Default value if conversion fails
 * @returns {number} Float value
 */
function safeFloat(value, defaultValue = 0.0) {
    if (value === null || value === undefined) {
        return defaultValue;
    }
    
    const result = parseFloat(value);
    
    // Check for NaN and infinity
    if (isNaN(result) || !isFinite(result)) {
        return defaultValue;
    }
    
    return result;
}

/**
 * Safely convert value to integer
 * @param {any} value - Value to convert
 * @param {number} defaultValue - Default value if conversion fails
 * @returns {number} Integer value
 */
function safeInt(value, defaultValue = 0) {
    if (value === null || value === undefined) {
        return defaultValue;
    }
    
    const result = parseInt(value, 10);
    
    if (isNaN(result)) {
        return defaultValue;
    }
    
    return result;
}

/**
 * Clean and truncate string
 * @param {string} text - Text to clean
 * @param {number} maxLength - Maximum length
 * @returns {string} Cleaned text
 */
function cleanString(text, maxLength = 100) {
    if (!text) {
        return '';
    }
    
    // Remove extra whitespace and truncate
    const cleaned = String(text).trim().replace(/\s+/g, ' ');
    return cleaned.substring(0, maxLength);
}

/**
 * Validate product data
 * @param {Object} data - Product data
 * @param {string} data.name - Product name
 * @param {number} [data.calories_per_100g] - Calories per 100g
 * @param {number} data.protein_per_100g - Protein per 100g
 * @param {number} data.fat_per_100g - Fat per 100g
 * @param {number} data.carbs_per_100g - Carbs per 100g
 * @returns {Object} Validation result { valid: boolean, errors: string[], data: Object }
 */
function validateProductData(data) {
    const errors = [];
    const cleanedData = {};
    
    // Validate name
    const name = cleanString(data.name || '');
    if (!name) {
        errors.push('Product name is required');
    } else if (name.length < 2) {
        errors.push('Product name must be at least 2 characters long');
    } else if (name.length > 100) {
        errors.push('Product name cannot exceed 100 characters');
    } else {
        cleanedData.name = name;
    }
    
    // Validate nutrition values
    const calories = safeFloat(data.calories_per_100g);
    const protein = safeFloat(data.protein_per_100g);
    const fat = safeFloat(data.fat_per_100g);
    const carbs = safeFloat(data.carbs_per_100g);
    
    // Check for negative values
    if (protein < 0) {
        errors.push('Protein cannot be negative');
    } else if (protein > 100) {
        errors.push('Protein cannot exceed 100g per 100g');
    }
    
    if (fat < 0) {
        errors.push('Fat cannot be negative');
    } else if (fat > 100) {
        errors.push('Fat cannot exceed 100g per 100g');
    }
    
    if (carbs < 0) {
        errors.push('Carbs cannot be negative');
    } else if (carbs > 100) {
        errors.push('Carbs cannot exceed 100g per 100g');
    }
    
    // Check total macros
    const totalMacros = protein + fat + carbs;
    if (totalMacros > 100) {
        errors.push(`Total macros (${totalMacros.toFixed(1)}g) cannot exceed 100g per 100g`);
    }
    
    // Check calories if provided
    if (calories > 0 && calories > 9999) {
        errors.push('Calories cannot exceed 9999 per 100g');
    }
    
    if (errors.length === 0) {
        cleanedData.calories_per_100g = calories;
        cleanedData.protein_per_100g = protein;
        cleanedData.fat_per_100g = fat;
        cleanedData.carbs_per_100g = carbs;
    }
    
    return {
        valid: errors.length === 0,
        errors: errors,
        data: cleanedData
    };
}

/**
 * Validate dish data
 * @param {Object} data - Dish data
 * @param {string} data.name - Dish name
 * @param {Array} data.ingredients - Array of ingredients
 * @returns {Object} Validation result { valid: boolean, errors: string[], data: Object }
 */
function validateDishData(data) {
    const errors = [];
    const cleanedData = {};
    
    // Validate name
    const name = cleanString(data.name || '');
    if (!name) {
        errors.push('Dish name is required');
    } else if (name.length < 2) {
        errors.push('Dish name must be at least 2 characters long');
    } else if (name.length > 100) {
        errors.push('Dish name cannot exceed 100 characters');
    } else {
        cleanedData.name = name;
    }
    
    // Validate ingredients
    const ingredients = data.ingredients || [];
    if (!Array.isArray(ingredients)) {
        errors.push('Ingredients must be a list');
    } else if (ingredients.length === 0) {
        errors.push('At least one ingredient is required');
    } else {
        const validIngredients = [];
        
        for (let i = 0; i < ingredients.length; i++) {
            const ingredient = ingredients[i];
            
            if (typeof ingredient !== 'object' || ingredient === null) {
                errors.push(`Ingredient ${i + 1}: Must be an object`);
                continue;
            }
            
            const productId = safeInt(ingredient.product_id);
            const quantity = safeFloat(ingredient.quantity_grams);
            
            if (!productId || productId <= 0) {
                errors.push(`Ingredient ${i + 1}: Valid product ID is required`);
            } else if (quantity <= 0) {
                errors.push(`Ingredient ${i + 1}: Quantity must be greater than 0`);
            } else if (quantity > 10000) {
                errors.push(`Ingredient ${i + 1}: Quantity cannot exceed 10000g`);
            } else {
                // Validate optional preparation method
                const preparationMethod = ingredient.preparation_method || 'raw';
                const validMethods = ['raw', 'boiled', 'steamed', 'grilled', 'fried', 'baked'];
                
                if (!validMethods.includes(preparationMethod)) {
                    errors.push(`Ingredient ${i + 1}: Invalid preparation method '${preparationMethod}'`);
                    continue;
                }
                
                // Validate optional edible portion
                const ediblePortion = safeFloat(ingredient.edible_portion, 1.0);
                if (ediblePortion <= 0 || ediblePortion > 1.0) {
                    errors.push(`Ingredient ${i + 1}: Edible portion must be between 0 and 1.0`);
                    continue;
                }
                
                validIngredients.push({
                    product_id: productId,
                    quantity_grams: quantity,
                    preparation_method: preparationMethod,
                    edible_portion: ediblePortion
                });
            }
        }
        
        if (validIngredients.length === 0 && errors.length === 0) {
            errors.push('At least one valid ingredient is required');
        }
        
        cleanedData.ingredients = validIngredients;
    }
    
    return {
        valid: errors.length === 0,
        errors: errors,
        data: cleanedData
    };
}

/**
 * Validate log entry data
 * @param {Object} data - Log entry data
 * @param {string} data.date - Date in YYYY-MM-DD format
 * @param {string} data.item_type - Type ('product' or 'dish')
 * @param {number} data.item_id - Product or dish ID
 * @param {number} data.quantity - Quantity in grams
 * @param {string} [data.meal_time] - Meal time
 * @returns {Object} Validation result { valid: boolean, errors: string[], data: Object }
 */
function validateLogData(data) {
    const errors = [];
    const cleanedData = {};
    
    // Validate date
    const dateStr = data.date;
    if (!dateStr) {
        errors.push('Date is required');
    } else {
        // Check date format YYYY-MM-DD
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (!dateRegex.test(dateStr)) {
            errors.push('Date must be in YYYY-MM-DD format');
        } else {
            const date = new Date(dateStr);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            // Check if date is not in the future
            if (date > today) {
                errors.push('Date cannot be in the future');
            }
            
            // Check if date is not too old (more than 1 year)
            const oneYearAgo = new Date();
            oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
            if (date < oneYearAgo) {
                errors.push('Date cannot be more than 1 year in the past');
            }
            
            cleanedData.date = dateStr;
        }
    }
    
    // Validate item type
    const itemType = data.item_type;
    if (!itemType) {
        errors.push('Item type is required');
    } else if (!['product', 'dish'].includes(itemType)) {
        errors.push('Item type must be "product" or "dish"');
    } else {
        cleanedData.item_type = itemType;
    }
    
    // Validate item ID
    const itemId = safeInt(data.item_id);
    if (!itemId || itemId <= 0) {
        errors.push('Valid item ID is required');
    } else {
        cleanedData.item_id = itemId;
    }
    
    // Validate quantity
    const quantity = safeFloat(data.quantity);
    if (quantity <= 0) {
        errors.push('Quantity must be greater than 0');
    } else if (quantity > 10000) {
        errors.push('Quantity cannot exceed 10000g');
    } else {
        cleanedData.quantity = quantity;
    }
    
    // Validate meal time (optional)
    const mealTime = data.meal_time || 'other';
    const validMealTimes = ['breakfast', 'lunch', 'dinner', 'snack', 'other'];
    if (!validMealTimes.includes(mealTime)) {
        errors.push(`Invalid meal time '${mealTime}'`);
    } else {
        cleanedData.meal_time = mealTime;
    }
    
    return {
        valid: errors.length === 0,
        errors: errors,
        data: cleanedData
    };
}

/**
 * Format date for display (YYYY-MM-DD)
 * @param {Date|string} dateObj - Date object or string
 * @returns {string} Formatted date string
 */
function formatDate(dateObj) {
    if (typeof dateObj === 'string') {
        return dateObj;
    }
    
    if (dateObj instanceof Date) {
        const year = dateObj.getFullYear();
        const month = String(dateObj.getMonth() + 1).padStart(2, '0');
        const day = String(dateObj.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
    
    return formatDate(new Date());
}

/**
 * Parse date string to Date object
 * @param {string} dateStr - Date string in YYYY-MM-DD format
 * @returns {Date|null} Date object or null if invalid
 */
function parseDate(dateStr) {
    try {
        const date = new Date(dateStr);
        if (isNaN(date.getTime())) {
            return null;
        }
        return date;
    } catch (e) {
        return null;
    }
}

// ============================================
// Export for use in Node.js (tests) and browsers
// ============================================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        safeFloat,
        safeInt,
        cleanString,
        validateProductData,
        validateDishData,
        validateLogData,
        formatDate,
        parseDate
    };
}
