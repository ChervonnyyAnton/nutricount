/**
 * Test data fixtures for E2E tests
 */

module.exports = {
  /**
   * Sample product data
   */
  products: {
    apple: {
      name: 'Apple',
      calories_per_100g: 52,
      protein_per_100g: 0.3,
      fat_per_100g: 0.2,
      carbs_per_100g: 14.0,
      fiber_per_100g: 2.4,
      sugars_per_100g: 10.4,
      category: 'berries',
      processing_level: 'raw',
      glycemic_index: 36,
    },
    chicken: {
      name: 'Chicken Breast',
      calories_per_100g: 165,
      protein_per_100g: 31,
      fat_per_100g: 3.6,
      carbs_per_100g: 0,
      fiber_per_100g: 0,
      sugars_per_100g: 0,
      category: 'meat',
      processing_level: 'raw',
      glycemic_index: 0,
    },
    avocado: {
      name: 'Avocado',
      calories_per_100g: 160,
      protein_per_100g: 2,
      fat_per_100g: 14.7,
      carbs_per_100g: 8.5,
      fiber_per_100g: 6.7,
      sugars_per_100g: 0.7,
      category: 'vegetables',
      processing_level: 'raw',
      glycemic_index: 15,
    },
  },

  /**
   * Sample dish data
   */
  dishes: {
    chickenSalad: {
      name: 'Chicken Salad',
      description: 'Healthy chicken salad',
      ingredients: [
        { product_id: null, quantity_grams: 150 }, // Will be filled with actual product_id
        { product_id: null, quantity_grams: 100 },
      ],
    },
  },

  /**
   * Sample log entry data
   */
  logEntries: {
    breakfast: {
      date: new Date().toISOString().split('T')[0],
      item_type: 'product',
      item_id: null, // Will be filled with actual item_id
      quantity_grams: 100,
      meal_time: 'breakfast',
    },
    lunch: {
      date: new Date().toISOString().split('T')[0],
      item_type: 'product',
      item_id: null,
      quantity_grams: 200,
      meal_time: 'lunch',
    },
  },

  /**
   * Sample user credentials (for authentication tests)
   */
  users: {
    admin: {
      username: 'admin',
      password: 'admin123',
    },
    testUser: {
      username: 'testuser',
      email: 'test@example.com',
      password: 'Test123!@#',
    },
  },
};
