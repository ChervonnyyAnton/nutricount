/**
 * Integration Tests for ApiAdapter
 * 
 * Tests the API adapter that communicates with the Flask backend.
 * Uses fetch mocking to simulate API responses.
 */

// Mock fetch globally
global.fetch = jest.fn();

// Mock localStorage
const localStorageMock = {
    store: {},
    getItem(key) {
        return this.store[key] || null;
    },
    setItem(key, value) {
        this.store[key] = value.toString();
    },
    removeItem(key) {
        delete this.store[key];
    },
    clear() {
        this.store = {};
    }
};
global.localStorage = localStorageMock;

// Import ApiAdapter
const BackendAdapter = require('../../src/adapters/backend-adapter.js');
const ApiAdapter = require('../../src/adapters/api-adapter.js');

describe('ApiAdapter - Token Management', () => {
    let adapter;

    beforeEach(() => {
        localStorage.clear();
        fetch.mockClear();
        adapter = new ApiAdapter('/api');
    });

    test('loads tokens from localStorage on initialization', () => {
        localStorage.setItem('access_token', 'test-access-token');
        localStorage.setItem('refresh_token', 'test-refresh-token');
        
        const newAdapter = new ApiAdapter('/api');
        expect(newAdapter.token).toBe('test-access-token');
        expect(newAdapter.refreshToken).toBe('test-refresh-token');
    });

    test('saves tokens after login', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({
                data: {
                    access_token: 'new-access-token',
                    refresh_token: 'new-refresh-token'
                }
            })
        });

        await adapter.login('testuser', 'testpass');

        expect(localStorage.getItem('access_token')).toBe('new-access-token');
        expect(localStorage.getItem('refresh_token')).toBe('new-refresh-token');
    });

    test('clears tokens on logout', async () => {
        localStorage.setItem('access_token', 'test-token');
        localStorage.setItem('refresh_token', 'test-refresh');

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ success: true })
        });

        await adapter.logout();

        expect(localStorage.getItem('access_token')).toBeNull();
        expect(localStorage.getItem('refresh_token')).toBeNull();
    });

    test('includes Authorization header when token exists', async () => {
        adapter.token = 'test-token';

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ data: [] })
        });

        await adapter.getProducts();

        expect(fetch).toHaveBeenCalledWith(
            '/api/products',
            expect.objectContaining({
                headers: expect.objectContaining({
                    'Authorization': 'Bearer test-token'
                })
            })
        );
    });
});

describe('ApiAdapter - Products Management', () => {
    let adapter;

    beforeEach(() => {
        localStorage.clear();
        fetch.mockClear();
        adapter = new ApiAdapter('/api');
    });

    test('getProducts() fetches all products', async () => {
        const mockProducts = [
            { id: 1, name: 'Product 1', calories: 100 },
            { id: 2, name: 'Product 2', calories: 200 }
        ];

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ data: mockProducts })
        });

        const result = await adapter.getProducts();

        expect(fetch).toHaveBeenCalledWith('/api/products', expect.any(Object));
        expect(result).toEqual(mockProducts);
    });

    test('createProduct() creates a new product', async () => {
        const newProduct = {
            name: 'Test Product',
            calories: 150,
            protein: 10,
            fats: 5,
            carbs: 15
        };

        const createdProduct = { id: 1, ...newProduct };

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ data: createdProduct })
        });

        const result = await adapter.createProduct(newProduct);

        expect(fetch).toHaveBeenCalledWith(
            '/api/products',
            expect.objectContaining({
                method: 'POST',
                body: JSON.stringify(newProduct)
            })
        );
        expect(result).toEqual(createdProduct);
    });

    test('updateProduct() updates existing product', async () => {
        const updatedProduct = {
            name: 'Updated Product',
            calories: 200
        };

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ data: { id: 1, ...updatedProduct } })
        });

        const result = await adapter.updateProduct(1, updatedProduct);

        expect(fetch).toHaveBeenCalledWith(
            '/api/products/1',
            expect.objectContaining({
                method: 'PUT',
                body: JSON.stringify(updatedProduct)
            })
        );
        expect(result.id).toBe(1);
        expect(result.name).toBe('Updated Product');
    });

    test('deleteProduct() deletes a product', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ success: true })
        });

        await adapter.deleteProduct(1);

        expect(fetch).toHaveBeenCalledWith(
            '/api/products/1',
            expect.objectContaining({
                method: 'DELETE'
            })
        );
    });
});

describe('ApiAdapter - Log Entries', () => {
    let adapter;

    beforeEach(() => {
        localStorage.clear();
        fetch.mockClear();
        adapter = new ApiAdapter('/api');
    });

    test('getLogEntries() fetches all entries', async () => {
        const mockEntries = [
            { id: 1, date: '2025-10-22', item_type: 'product' },
            { id: 2, date: '2025-10-22', item_type: 'dish' }
        ];

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ data: mockEntries })
        });

        const result = await adapter.getLogEntries();

        expect(fetch).toHaveBeenCalledWith('/api/log', expect.any(Object));
        expect(result).toEqual(mockEntries);
    });

    test('getLogEntries() fetches entries for specific date', async () => {
        const mockEntries = [{ id: 1, date: '2025-10-22' }];

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ data: mockEntries })
        });

        await adapter.getLogEntries('2025-10-22');

        expect(fetch).toHaveBeenCalledWith('/api/log?date=2025-10-22', expect.any(Object));
    });

    test('createLogEntry() creates a new entry', async () => {
        const newEntry = {
            date: '2025-10-22',
            item_type: 'product',
            item_id: 1,
            quantity: 100
        };

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ data: { id: 1, ...newEntry } })
        });

        const result = await adapter.createLogEntry(newEntry);

        expect(fetch).toHaveBeenCalledWith(
            '/api/log',
            expect.objectContaining({
                method: 'POST',
                body: JSON.stringify(newEntry)
            })
        );
        expect(result.id).toBe(1);
    });

    test('deleteLogEntry() deletes an entry', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ success: true })
        });

        await adapter.deleteLogEntry(1);

        expect(fetch).toHaveBeenCalledWith(
            '/api/log/1',
            expect.objectContaining({
                method: 'DELETE'
            })
        );
    });
});

describe('ApiAdapter - Dishes Management', () => {
    let adapter;

    beforeEach(() => {
        localStorage.clear();
        fetch.mockClear();
        adapter = new ApiAdapter('/api');
    });

    test('getDishes() fetches all dishes', async () => {
        const mockDishes = [
            { id: 1, name: 'Dish 1', ingredients: [] },
            { id: 2, name: 'Dish 2', ingredients: [] }
        ];

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ data: mockDishes })
        });

        const result = await adapter.getDishes();

        expect(fetch).toHaveBeenCalledWith('/api/dishes', expect.any(Object));
        expect(result).toEqual(mockDishes);
    });

    test('createDish() creates a new dish', async () => {
        const newDish = {
            name: 'Test Dish',
            ingredients: [
                { product_id: 1, quantity: 100 }
            ]
        };

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ data: { id: 1, ...newDish } })
        });

        const result = await adapter.createDish(newDish);

        expect(fetch).toHaveBeenCalledWith(
            '/api/dishes',
            expect.objectContaining({
                method: 'POST',
                body: JSON.stringify(newDish)
            })
        );
        expect(result.id).toBe(1);
    });

    test('updateDish() updates existing dish', async () => {
        const updatedDish = {
            name: 'Updated Dish',
            ingredients: []
        };

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ data: { id: 1, ...updatedDish } })
        });

        await adapter.updateDish(1, updatedDish);

        expect(fetch).toHaveBeenCalledWith(
            '/api/dishes/1',
            expect.objectContaining({
                method: 'PUT',
                body: JSON.stringify(updatedDish)
            })
        );
    });

    test('deleteDish() deletes a dish', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ success: true })
        });

        await adapter.deleteDish(1);

        expect(fetch).toHaveBeenCalledWith(
            '/api/dishes/1',
            expect.objectContaining({
                method: 'DELETE'
            })
        );
    });
});

describe('ApiAdapter - Statistics', () => {
    let adapter;

    beforeEach(() => {
        localStorage.clear();
        fetch.mockClear();
        adapter = new ApiAdapter('/api');
    });

    test('getDailyStats() fetches statistics for date', async () => {
        const mockStats = {
            calories: 2000,
            protein: 100,
            fats: 80,
            carbs: 200
        };

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ data: mockStats })
        });

        const result = await adapter.getDailyStats('2025-10-22');

        expect(fetch).toHaveBeenCalledWith(
            '/api/stats/daily?date=2025-10-22',
            expect.any(Object)
        );
        expect(result).toEqual(mockStats);
    });

    test('getWeeklyStats() fetches statistics for date range', async () => {
        const mockStats = {
            days: [
                { date: '2025-10-21', calories: 2000 },
                { date: '2025-10-22', calories: 2100 }
            ]
        };

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ data: mockStats })
        });

        const result = await adapter.getWeeklyStats('2025-10-21', '2025-10-22');

        expect(fetch).toHaveBeenCalledWith(
            '/api/stats/weekly?start=2025-10-21&end=2025-10-22',
            expect.any(Object)
        );
        expect(result).toEqual(mockStats);
    });
});

describe('ApiAdapter - Error Handling', () => {
    let adapter;

    beforeEach(() => {
        localStorage.clear();
        fetch.mockClear();
        adapter = new ApiAdapter('/api', {
            retryAttempts: 2,
            retryDelay: 100
        });
    });

    test('throws error on HTTP error response', async () => {
        fetch.mockResolvedValueOnce({
            ok: false,
            status: 400,
            json: async () => ({ error: 'Bad Request' })
        });

        await expect(adapter.getProducts()).rejects.toThrow('Bad Request');
    });

    test('retries on network error', async () => {
        const networkError = new Error('network timeout');
        
        fetch
            .mockRejectedValueOnce(networkError)
            .mockRejectedValueOnce(networkError)
            .mockResolvedValueOnce({
                ok: true,
                json: async () => ({ data: [] })
            });

        const result = await adapter.getProducts();

        expect(fetch).toHaveBeenCalledTimes(3);
        expect(result).toEqual([]);
    });

    test('throws error after max retries', async () => {
        const networkError = new Error('network timeout');
        fetch.mockRejectedValue(networkError);

        await expect(adapter.getProducts()).rejects.toThrow('network timeout');
        expect(fetch).toHaveBeenCalledTimes(3); // Initial + 2 retries
    });

    test('attempts token refresh on 401 error', async () => {
        localStorage.clear();
        fetch.mockClear();
        adapter = new ApiAdapter('/api');
        adapter.token = 'old-token';
        adapter.refreshToken = 'refresh-token';

        // First call fails with 401
        fetch.mockResolvedValueOnce({
            ok: false,
            status: 401,
            json: async () => ({ error: 'Unauthorized' })
        });

        // Refresh token call succeeds
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({
                data: { access_token: 'new-token' }
            })
        });

        // Retry with new token succeeds
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ data: [] })
        });

        const result = await adapter.getProducts();

        expect(fetch).toHaveBeenCalledTimes(3);
        expect(adapter.token).toBe('new-token');
        expect(result).toEqual([]);
    });

    test('clears tokens if refresh fails', async () => {
        localStorage.clear();
        fetch.mockClear();
        adapter = new ApiAdapter('/api');
        adapter.token = 'old-token';
        adapter.refreshToken = 'refresh-token';

        // First call fails with 401
        fetch.mockResolvedValueOnce({
            ok: false,
            status: 401,
            json: async () => ({ error: 'Unauthorized' })
        });

        // Refresh token call fails
        fetch.mockResolvedValueOnce({
            ok: false,
            status: 401,
            json: async () => ({ error: 'Invalid refresh token' })
        });

        // Retry after failed refresh also fails
        fetch.mockResolvedValueOnce({
            ok: false,
            status: 401,
            json: async () => ({ error: 'Unauthorized' })
        });

        await expect(adapter.getProducts()).rejects.toThrow();

        expect(adapter.token).toBeNull();
        expect(adapter.refreshToken).toBeNull();
    });
});

describe('ApiAdapter - Fasting Management', () => {
    let adapter;

    beforeEach(() => {
        localStorage.clear();
        fetch.mockClear();
        fetch.mockReset();
        adapter = new ApiAdapter('/api');
    });

    test('getFastingStatus() fetches current status', async () => {
        const mockStatus = {
            is_fasting: true,
            start_time: '2025-10-22T10:00:00',
            fasting_type: '16:8'
        };

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ data: mockStatus })
        });

        const result = await adapter.getFastingStatus();

        expect(fetch).toHaveBeenCalledWith('/api/fasting/status', expect.any(Object));
        expect(result).toEqual(mockStatus);
    });

    test('startFasting() starts a new fasting session', async () => {
        const fastingData = {
            fasting_type: '16:8',
            notes: 'Test session'
        };

        const createdSession = { id: 1, ...fastingData };

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ data: createdSession })
        });

        const result = await adapter.startFasting(fastingData);

        expect(fetch).toHaveBeenCalledWith(
            '/api/fasting/start',
            expect.objectContaining({
                method: 'POST',
                body: JSON.stringify(fastingData)
            })
        );
        expect(result).toEqual(createdSession);
    });

    test('endFasting() ends current session', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ success: true })
        });

        await adapter.endFasting();

        expect(fetch).toHaveBeenCalledWith(
            '/api/fasting/end',
            expect.objectContaining({
                method: 'POST'
            })
        );
    });

    test('getFastingStats() fetches fasting statistics', async () => {
        const mockStats = {
            total_sessions: 10,
            average_duration: 16.5,
            current_streak: 5
        };

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ data: mockStats })
        });

        const result = await adapter.getFastingStats();

        expect(fetch).toHaveBeenCalledWith('/api/fasting/stats', expect.any(Object));
        expect(result).toEqual(mockStats);
    });
});

describe('ApiAdapter - Settings & Profile', () => {
    let adapter;

    beforeEach(() => {
        localStorage.clear();
        fetch.mockClear();
        fetch.mockReset();
        adapter = new ApiAdapter('/api');
    });

    test('getSettings() fetches user settings', async () => {
        const mockSettings = {
            theme: 'dark',
            language: 'en',
            units: 'metric'
        };

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ data: mockSettings })
        });

        const result = await adapter.getSettings();

        expect(fetch).toHaveBeenCalledWith('/api/settings', expect.any(Object));
        expect(result).toEqual(mockSettings);
    });

    test('saveSettings() updates user settings', async () => {
        const newSettings = {
            theme: 'light',
            language: 'ru'
        };

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ data: newSettings })
        });

        await adapter.saveSettings(newSettings);

        expect(fetch).toHaveBeenCalledWith(
            '/api/settings',
            expect.objectContaining({
                method: 'PUT',
                body: JSON.stringify(newSettings)
            })
        );
    });

    test('getProfile() fetches user profile', async () => {
        const mockProfile = {
            username: 'testuser',
            email: 'test@example.com',
            name: 'Test User'
        };

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ data: mockProfile })
        });

        const result = await adapter.getProfile();

        expect(fetch).toHaveBeenCalledWith('/api/profile', expect.any(Object));
        expect(result).toEqual(mockProfile);
    });

    test('updateProfile() updates user profile', async () => {
        const updatedProfile = {
            name: 'Updated Name',
            email: 'updated@example.com'
        };

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ data: updatedProfile })
        });

        await adapter.updateProfile(updatedProfile);

        expect(fetch).toHaveBeenCalledWith(
            '/api/profile',
            expect.objectContaining({
                method: 'PUT',
                body: JSON.stringify(updatedProfile)
            })
        );
    });
});

describe('ApiAdapter - Configuration', () => {
    beforeEach(() => {
        localStorage.clear();
        fetch.mockClear();
    });

    test('removes trailing slash from baseUrl', () => {
        const adapter = new ApiAdapter('/api/');
        expect(adapter.baseUrl).toBe('/api');
    });

    test('uses custom configuration options', () => {
        const adapter = new ApiAdapter('/api', {
            retryAttempts: 5,
            retryDelay: 2000,
            timeout: 60000
        });

        expect(adapter.options.retryAttempts).toBe(5);
        expect(adapter.options.retryDelay).toBe(2000);
        expect(adapter.options.timeout).toBe(60000);
    });

    test('merges custom options with defaults', () => {
        const adapter = new ApiAdapter('/api', {
            retryAttempts: 5
        });

        expect(adapter.options.retryAttempts).toBe(5);
        expect(adapter.options.retryDelay).toBe(1000); // default
        expect(adapter.options.timeout).toBe(30000); // default
    });
});
