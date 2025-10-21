/**
 * Storage Adapter for Public Version
 * 
 * Uses browser's LocalStorage to store all data client-side.
 * This adapter is used for the GitHub Pages deployment where
 * no backend server is available.
 */

class StorageAdapter extends BackendAdapter {
    constructor() {
        super();
        this.storage = typeof window !== 'undefined' ? window.localStorage : null;
        this.keys = {
            products: 'nutricount_products',
            log: 'nutricount_log',
            dishes: 'nutricount_dishes',
            settings: 'nutricount_settings'
        };
        
        // Initialize storage if needed
        this._initializeStorage();
    }
    
    _initializeStorage() {
        if (!this.storage) return;
        
        // Initialize with empty arrays if not present
        Object.values(this.keys).forEach(key => {
            if (!this.storage.getItem(key)) {
                this.storage.setItem(key, JSON.stringify([]));
            }
        });
        
        // Initialize settings with defaults
        if (!this.storage.getItem(this.keys.settings)) {
            this.storage.setItem(this.keys.settings, JSON.stringify({
                theme: 'light',
                notifications: true
            }));
        }
    }
    
    _generateId() {
        return Date.now() + Math.random().toString(36).substr(2, 9);
    }
    
    /**
     * Products Management
     */
    
    async getProducts() {
        const data = this.storage.getItem(this.keys.products);
        return data ? JSON.parse(data) : [];
    }
    
    async createProduct(product) {
        const products = await this.getProducts();
        const newProduct = {
            ...product,
            id: this._generateId(),
            created_at: new Date().toISOString()
        };
        products.push(newProduct);
        this.storage.setItem(this.keys.products, JSON.stringify(products));
        return newProduct;
    }
    
    async updateProduct(id, product) {
        const products = await this.getProducts();
        const index = products.findIndex(p => p.id === id);
        if (index === -1) {
            throw new Error(`Product with id ${id} not found`);
        }
        products[index] = { ...products[index], ...product, updated_at: new Date().toISOString() };
        this.storage.setItem(this.keys.products, JSON.stringify(products));
        return products[index];
    }
    
    async deleteProduct(id) {
        const products = await this.getProducts();
        const filtered = products.filter(p => p.id !== id);
        this.storage.setItem(this.keys.products, JSON.stringify(filtered));
        return { success: true };
    }
    
    /**
     * Daily Log Management
     */
    
    async getLogEntries(date = null) {
        const data = this.storage.getItem(this.keys.log);
        let entries = data ? JSON.parse(data) : [];
        
        if (date) {
            entries = entries.filter(e => e.date === date);
        }
        
        return entries.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    }
    
    async createLogEntry(entry) {
        const entries = await this.getLogEntries();
        const newEntry = {
            ...entry,
            id: this._generateId(),
            created_at: new Date().toISOString()
        };
        entries.push(newEntry);
        this.storage.setItem(this.keys.log, JSON.stringify(entries));
        return newEntry;
    }
    
    async updateLogEntry(id, entry) {
        const entries = await this.getLogEntries();
        const index = entries.findIndex(e => e.id === id);
        if (index === -1) {
            throw new Error(`Log entry with id ${id} not found`);
        }
        entries[index] = { ...entries[index], ...entry, updated_at: new Date().toISOString() };
        this.storage.setItem(this.keys.log, JSON.stringify(entries));
        return entries[index];
    }
    
    async deleteLogEntry(id) {
        const entries = await this.getLogEntries();
        const filtered = entries.filter(e => e.id !== id);
        this.storage.setItem(this.keys.log, JSON.stringify(filtered));
        return { success: true };
    }
    
    /**
     * Statistics
     */
    
    async getDailyStats(date) {
        const entries = await this.getLogEntries(date);
        const products = await this.getProducts();
        
        // Calculate totals from entries
        const totals = entries.reduce((acc, entry) => {
            const product = products.find(p => p.id === entry.product_id);
            if (!product) return acc;
            
            const factor = entry.quantity / 100;
            return {
                calories: acc.calories + (product.calories * factor),
                protein: acc.protein + (product.protein * factor),
                fat: acc.fat + (product.fat * factor),
                carbs: acc.carbs + (product.carbs * factor)
            };
        }, { calories: 0, protein: 0, fat: 0, carbs: 0 });
        
        return {
            date,
            entries_count: entries.length,
            ...totals
        };
    }
    
    async getWeeklyStats(startDate, endDate) {
        const entries = await this.getLogEntries();
        const start = new Date(startDate);
        const end = new Date(endDate);
        
        const weekEntries = entries.filter(e => {
            const entryDate = new Date(e.date);
            return entryDate >= start && entryDate <= end;
        });
        
        const products = await this.getProducts();
        
        const totals = weekEntries.reduce((acc, entry) => {
            const product = products.find(p => p.id === entry.product_id);
            if (!product) return acc;
            
            const factor = entry.quantity / 100;
            return {
                calories: acc.calories + (product.calories * factor),
                protein: acc.protein + (product.protein * factor),
                fat: acc.fat + (product.fat * factor),
                carbs: acc.carbs + (product.carbs * factor)
            };
        }, { calories: 0, protein: 0, fat: 0, carbs: 0 });
        
        return {
            start_date: startDate,
            end_date: endDate,
            entries_count: weekEntries.length,
            ...totals
        };
    }
    
    /**
     * Settings Management
     */
    
    async getSettings() {
        const data = this.storage.getItem(this.keys.settings);
        return data ? JSON.parse(data) : { theme: 'light', notifications: true };
    }
    
    async saveSettings(settings) {
        this.storage.setItem(this.keys.settings, JSON.stringify(settings));
        return settings;
    }
    
    /**
     * Dishes Management
     */
    
    async getDishes() {
        const data = this.storage.getItem(this.keys.dishes);
        return data ? JSON.parse(data) : [];
    }
    
    async createDish(dish) {
        const dishes = await this.getDishes();
        const newDish = {
            ...dish,
            id: this._generateId(),
            created_at: new Date().toISOString()
        };
        dishes.push(newDish);
        this.storage.setItem(this.keys.dishes, JSON.stringify(dishes));
        return newDish;
    }
    
    async updateDish(id, dish) {
        const dishes = await this.getDishes();
        const index = dishes.findIndex(d => d.id === id);
        if (index === -1) {
            throw new Error(`Dish with id ${id} not found`);
        }
        dishes[index] = { ...dishes[index], ...dish, updated_at: new Date().toISOString() };
        this.storage.setItem(this.keys.dishes, JSON.stringify(dishes));
        return dishes[index];
    }
    
    async deleteDish(id) {
        const dishes = await this.getDishes();
        const filtered = dishes.filter(d => d.id !== id);
        this.storage.setItem(this.keys.dishes, JSON.stringify(filtered));
        return { success: true };
    }
    
    /**
     * Utility Methods
     */
    
    async clearAll() {
        Object.values(this.keys).forEach(key => {
            this.storage.removeItem(key);
        });
        this._initializeStorage();
        return { success: true };
    }
}

// Export for use in Node.js (tests) and browsers
if (typeof module !== 'undefined' && module.exports) {
    module.exports = StorageAdapter;
}
