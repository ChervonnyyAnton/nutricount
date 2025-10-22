/**
 * Integration tests for StorageAdapter
 * 
 * Tests the localStorage-based data persistence for the Public version.
 */

// Mock localStorage for Node.js environment
class LocalStorageMock {
    constructor() {
        this.store = {};
    }

    clear() {
        this.store = {};
    }

    getItem(key) {
        return this.store[key] || null;
    }

    setItem(key, value) {
        this.store[key] = String(value);
    }

    removeItem(key) {
        delete this.store[key];
    }

    get length() {
        return Object.keys(this.store).length;
    }

    key(index) {
        const keys = Object.keys(this.store);
        return keys[index] || null;
    }
}

// Set up global localStorage mock
global.localStorage = new LocalStorageMock();
global.window = { localStorage: global.localStorage };

// Import the adapter after setting up mocks
// We need to make BackendAdapter available globally for StorageAdapter to extend it
const BackendAdapter = require('../../src/adapters/backend-adapter');
global.BackendAdapter = BackendAdapter;

const StorageAdapter = require('../../src/adapters/storage-adapter');

describe('StorageAdapter - Products', () => {
    let adapter;

    beforeEach(() => {
        // Clear localStorage before each test
        global.localStorage.clear();
        adapter = new StorageAdapter();
    });

    describe('getProducts', () => {
        test('should return empty array initially', async () => {
            const products = await adapter.getProducts();
            expect(products).toEqual([]);
        });

        test('should return stored products', async () => {
            const testProduct = { name: 'Test Product', calories: 100 };
            await adapter.createProduct(testProduct);
            
            const products = await adapter.getProducts();
            expect(products).toHaveLength(1);
            expect(products[0].name).toBe('Test Product');
            expect(products[0].calories).toBe(100);
        });
    });

    describe('createProduct', () => {
        test('should create a new product with generated id', async () => {
            const productData = {
                name: 'Chicken Breast',
                calories: 165,
                protein: 31,
                fats: 3.6,
                carbs: 0
            };

            const created = await adapter.createProduct(productData);

            expect(created).toHaveProperty('id');
            expect(created).toHaveProperty('created_at');
            expect(created.name).toBe('Chicken Breast');
            expect(created.calories).toBe(165);
            expect(created.protein).toBe(31);
        });

        test('should persist product to storage', async () => {
            const productData = { name: 'Avocado', calories: 160 };
            await adapter.createProduct(productData);

            // Create a new adapter instance to verify persistence
            const newAdapter = new StorageAdapter();
            const products = await newAdapter.getProducts();
            
            expect(products).toHaveLength(1);
            expect(products[0].name).toBe('Avocado');
        });

        test('should handle multiple products', async () => {
            await adapter.createProduct({ name: 'Product 1', calories: 100 });
            await adapter.createProduct({ name: 'Product 2', calories: 200 });
            await adapter.createProduct({ name: 'Product 3', calories: 300 });

            const products = await adapter.getProducts();
            expect(products).toHaveLength(3);
            expect(products[0].name).toBe('Product 1');
            expect(products[2].name).toBe('Product 3');
        });
    });

    describe('updateProduct', () => {
        test('should update existing product', async () => {
            const created = await adapter.createProduct({ 
                name: 'Original Name', 
                calories: 100 
            });

            const updated = await adapter.updateProduct(created.id, {
                name: 'Updated Name',
                calories: 150
            });

            expect(updated.id).toBe(created.id);
            expect(updated.name).toBe('Updated Name');
            expect(updated.calories).toBe(150);
            expect(updated).toHaveProperty('updated_at');
        });

        test('should throw error for non-existent product', async () => {
            await expect(
                adapter.updateProduct('non-existent-id', { name: 'Test' })
            ).rejects.toThrow('Product with id non-existent-id not found');
        });

        test('should preserve other fields when updating', async () => {
            const created = await adapter.createProduct({ 
                name: 'Test', 
                calories: 100,
                protein: 10,
                fats: 5,
                carbs: 3
            });

            await adapter.updateProduct(created.id, { calories: 120 });

            const products = await adapter.getProducts();
            const updated = products.find(p => p.id === created.id);
            
            expect(updated.calories).toBe(120);
            expect(updated.protein).toBe(10);
            expect(updated.fats).toBe(5);
            expect(updated.carbs).toBe(3);
        });
    });

    describe('deleteProduct', () => {
        test('should delete existing product', async () => {
            const created = await adapter.createProduct({ name: 'To Delete', calories: 100 });
            
            const result = await adapter.deleteProduct(created.id);
            
            expect(result.success).toBe(true);
            const products = await adapter.getProducts();
            expect(products).toHaveLength(0);
        });

        test('should return success even for non-existent product', async () => {
            const result = await adapter.deleteProduct('non-existent-id');
            expect(result.success).toBe(true);
        });

        test('should only delete specified product', async () => {
            const product1 = await adapter.createProduct({ name: 'Keep', calories: 100 });
            const product2 = await adapter.createProduct({ name: 'Delete', calories: 200 });
            const product3 = await adapter.createProduct({ name: 'Keep', calories: 300 });

            await adapter.deleteProduct(product2.id);

            const products = await adapter.getProducts();
            expect(products).toHaveLength(2);
            expect(products.find(p => p.id === product1.id)).toBeDefined();
            expect(products.find(p => p.id === product3.id)).toBeDefined();
            expect(products.find(p => p.id === product2.id)).toBeUndefined();
        });
    });
});

describe('StorageAdapter - Log Entries', () => {
    let adapter;

    beforeEach(() => {
        global.localStorage.clear();
        adapter = new StorageAdapter();
    });

    describe('getLogEntries', () => {
        test('should return empty array initially', async () => {
            const entries = await adapter.getLogEntries();
            expect(entries).toEqual([]);
        });

        test('should return logged entries for a date', async () => {
            const today = new Date().toISOString().split('T')[0];
            
            await adapter.createLogEntry({
                product_id: 'prod1',
                weight: 100,
                date: today
            });

            const entries = await adapter.getLogEntries(today);
            expect(entries).toHaveLength(1);
            expect(entries[0].weight).toBe(100);
        });
    });

    describe('createLogEntry', () => {
        test('should create a new log entry', async () => {
            const entryData = {
                product_id: 'test-product',
                weight: 150,
                date: '2025-10-22'
            };

            const created = await adapter.createLogEntry(entryData);

            expect(created).toHaveProperty('id');
            expect(created).toHaveProperty('created_at');
            expect(created.product_id).toBe('test-product');
            expect(created.weight).toBe(150);
        });

        test('should persist log entry to storage', async () => {
            await adapter.createLogEntry({
                product_id: 'prod1',
                weight: 100,
                date: '2025-10-22'
            });

            const newAdapter = new StorageAdapter();
            const entries = await newAdapter.getLogEntries();
            
            expect(entries).toHaveLength(1);
        });
    });

    describe('deleteLogEntry', () => {
        test('should delete existing log entry', async () => {
            const created = await adapter.createLogEntry({
                product_id: 'prod1',
                weight: 100,
                date: '2025-10-22'
            });

            const result = await adapter.deleteLogEntry(created.id);

            expect(result.success).toBe(true);
            const entries = await adapter.getLogEntries();
            expect(entries).toHaveLength(0);
        });

        test('should return success even for non-existent entry', async () => {
            const result = await adapter.deleteLogEntry('non-existent-id');
            expect(result.success).toBe(true);
        });
    });
});

describe('StorageAdapter - Dishes', () => {
    let adapter;

    beforeEach(() => {
        global.localStorage.clear();
        adapter = new StorageAdapter();
    });

    describe('getDishes', () => {
        test('should return empty array initially', async () => {
            const dishes = await adapter.getDishes();
            expect(dishes).toEqual([]);
        });

        test('should return stored dishes', async () => {
            await adapter.createDish({ name: 'Test Dish', ingredients: [] });
            
            const dishes = await adapter.getDishes();
            expect(dishes).toHaveLength(1);
            expect(dishes[0].name).toBe('Test Dish');
        });
    });

    describe('createDish', () => {
        test('should create a new dish', async () => {
            const dishData = {
                name: 'Keto Salad',
                ingredients: [
                    { product_id: 'prod1', weight: 50 },
                    { product_id: 'prod2', weight: 100 }
                ]
            };

            const created = await adapter.createDish(dishData);

            expect(created).toHaveProperty('id');
            expect(created).toHaveProperty('created_at');
            expect(created.name).toBe('Keto Salad');
            expect(created.ingredients).toHaveLength(2);
        });

        test('should persist dish to storage', async () => {
            await adapter.createDish({ 
                name: 'Test Dish', 
                ingredients: [] 
            });

            const newAdapter = new StorageAdapter();
            const dishes = await newAdapter.getDishes();
            
            expect(dishes).toHaveLength(1);
        });
    });

    describe('updateDish', () => {
        test('should update existing dish', async () => {
            const created = await adapter.createDish({ 
                name: 'Original', 
                ingredients: [] 
            });

            const updated = await adapter.updateDish(created.id, {
                name: 'Updated',
                ingredients: [{ product_id: 'prod1', weight: 100 }]
            });

            expect(updated.id).toBe(created.id);
            expect(updated.name).toBe('Updated');
            expect(updated.ingredients).toHaveLength(1);
        });

        test('should throw error for non-existent dish', async () => {
            await expect(
                adapter.updateDish('non-existent-id', { name: 'Test' })
            ).rejects.toThrow('Dish with id non-existent-id not found');
        });
    });

    describe('deleteDish', () => {
        test('should delete existing dish', async () => {
            const created = await adapter.createDish({ 
                name: 'To Delete', 
                ingredients: [] 
            });

            const result = await adapter.deleteDish(created.id);

            expect(result.success).toBe(true);
            const dishes = await adapter.getDishes();
            expect(dishes).toHaveLength(0);
        });

        test('should return success even for non-existent dish', async () => {
            const result = await adapter.deleteDish('non-existent-id');
            expect(result.success).toBe(true);
        });
    });
});

describe('StorageAdapter - Statistics', () => {
    let adapter;

    beforeEach(() => {
        global.localStorage.clear();
        adapter = new StorageAdapter();
    });

    describe('getDailyStats', () => {
        test('should calculate statistics from log entries', async () => {
            const today = new Date().toISOString().split('T')[0];
            
            // Create some products
            const product1 = await adapter.createProduct({
                name: 'Product 1',
                calories: 100,
                protein: 10,
                fat: 5,
                carbs: 8
            });

            const product2 = await adapter.createProduct({
                name: 'Product 2',
                calories: 200,
                protein: 20,
                fat: 10,
                carbs: 15
            });

            // Create log entries with quantity (per 100g)
            await adapter.createLogEntry({
                product_id: product1.id,
                quantity: 100,
                date: today
            });

            await adapter.createLogEntry({
                product_id: product2.id,
                quantity: 100,
                date: today
            });

            const stats = await adapter.getDailyStats(today);

            expect(stats).toHaveProperty('date');
            expect(stats).toHaveProperty('calories');
            expect(stats).toHaveProperty('protein');
            expect(stats).toHaveProperty('fat');
            expect(stats).toHaveProperty('carbs');
            expect(stats).toHaveProperty('entries_count');
            expect(stats.entries_count).toBe(2);
            expect(stats.calories).toBe(300); // 100 + 200
        });

        test('should return zero stats for empty day', async () => {
            const stats = await adapter.getDailyStats('2025-10-22');

            expect(stats.calories).toBe(0);
            expect(stats.protein).toBe(0);
            expect(stats.fat).toBe(0);
            expect(stats.carbs).toBe(0);
            expect(stats.entries_count).toBe(0);
        });

        test('should only count entries for specified date', async () => {
            const today = '2025-10-22';
            const yesterday = '2025-10-21';
            
            const product = await adapter.createProduct({
                name: 'Product',
                calories: 100,
                protein: 10,
                fat: 5,
                carbs: 8
            });

            await adapter.createLogEntry({
                product_id: product.id,
                quantity: 100,
                date: today
            });

            await adapter.createLogEntry({
                product_id: product.id,
                quantity: 100,
                date: yesterday
            });

            const stats = await adapter.getDailyStats(today);
            expect(stats.entries_count).toBe(1);
            expect(stats.calories).toBe(100);
        });
    });

    describe('getWeeklyStats', () => {
        test('should calculate statistics for a week', async () => {
            const product = await adapter.createProduct({
                name: 'Product',
                calories: 100,
                protein: 10,
                fat: 5,
                carbs: 8
            });

            // Add entries for 3 days
            await adapter.createLogEntry({
                product_id: product.id,
                quantity: 100,
                date: '2025-10-20'
            });

            await adapter.createLogEntry({
                product_id: product.id,
                quantity: 100,
                date: '2025-10-21'
            });

            await adapter.createLogEntry({
                product_id: product.id,
                quantity: 100,
                date: '2025-10-22'
            });

            const stats = await adapter.getWeeklyStats('2025-10-20', '2025-10-22');

            expect(stats).toHaveProperty('start_date');
            expect(stats).toHaveProperty('end_date');
            expect(stats.entries_count).toBe(3);
            expect(stats.calories).toBe(300);
        });

        test('should filter entries by date range', async () => {
            const product = await adapter.createProduct({
                name: 'Product',
                calories: 100,
                protein: 10,
                fat: 5,
                carbs: 8
            });

            // Add entries across multiple weeks
            await adapter.createLogEntry({
                product_id: product.id,
                quantity: 100,
                date: '2025-10-15'
            });

            await adapter.createLogEntry({
                product_id: product.id,
                quantity: 100,
                date: '2025-10-20'
            });

            await adapter.createLogEntry({
                product_id: product.id,
                quantity: 100,
                date: '2025-10-25'
            });

            const stats = await adapter.getWeeklyStats('2025-10-18', '2025-10-22');
            expect(stats.entries_count).toBe(1); // Only the Oct 20 entry
            expect(stats.calories).toBe(100);
        });
    });
});
