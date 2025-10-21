/**
 * Backend Adapter Interface
 * 
 * This is the base interface for all backend adapters.
 * Both ApiAdapter (Local version) and StorageAdapter (Public version)
 * implement this interface to provide a consistent API to the frontend.
 * 
 * This allows the frontend to work with either backend without changes.
 */

class BackendAdapter {
    /**
     * Products Management
     */
    
    async getProducts() {
        throw new Error('getProducts() must be implemented by subclass');
    }
    
    async createProduct(product) {
        throw new Error('createProduct() must be implemented by subclass');
    }
    
    async updateProduct(id, product) {
        throw new Error('updateProduct() must be implemented by subclass');
    }
    
    async deleteProduct(id) {
        throw new Error('deleteProduct() must be implemented by subclass');
    }
    
    /**
     * Daily Log Management
     */
    
    async getLogEntries(date = null) {
        throw new Error('getLogEntries() must be implemented by subclass');
    }
    
    async createLogEntry(entry) {
        throw new Error('createLogEntry() must be implemented by subclass');
    }
    
    async updateLogEntry(id, entry) {
        throw new Error('updateLogEntry() must be implemented by subclass');
    }
    
    async deleteLogEntry(id) {
        throw new Error('deleteLogEntry() must be implemented by subclass');
    }
    
    /**
     * Statistics
     */
    
    async getDailyStats(date) {
        throw new Error('getDailyStats() must be implemented by subclass');
    }
    
    async getWeeklyStats(startDate, endDate) {
        throw new Error('getWeeklyStats() must be implemented by subclass');
    }
    
    /**
     * Settings Management
     */
    
    async getSettings() {
        throw new Error('getSettings() must be implemented by subclass');
    }
    
    async saveSettings(settings) {
        throw new Error('saveSettings() must be implemented by subclass');
    }
    
    /**
     * Dishes Management (for future implementation)
     */
    
    async getDishes() {
        throw new Error('getDishes() must be implemented by subclass');
    }
    
    async createDish(dish) {
        throw new Error('createDish() must be implemented by subclass');
    }
    
    async updateDish(id, dish) {
        throw new Error('updateDish() must be implemented by subclass');
    }
    
    async deleteDish(id) {
        throw new Error('deleteDish() must be implemented by subclass');
    }
}

// Export for use in Node.js (tests) and browsers
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BackendAdapter;
}
