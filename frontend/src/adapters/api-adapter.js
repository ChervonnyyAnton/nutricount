/**
 * API Adapter for Local Version
 * 
 * Communicates with Flask backend via REST API.
 * This adapter is used for the production deployment with Docker.
 * 
 * Features:
 * - RESTful API communication
 * - JWT token management
 * - Error handling and retry logic
 * - Request/response transformation
 */

class ApiAdapter extends BackendAdapter {
    constructor(baseUrl = '/api', options = {}) {
        super();
        this.baseUrl = baseUrl.replace(/\/$/, ''); // Remove trailing slash
        this.token = null;
        this.refreshToken = null;
        
        // Configuration options
        this.options = {
            retryAttempts: 3,
            retryDelay: 1000,
            timeout: 30000,
            ...options
        };
        
        // Load tokens from localStorage if available
        this._loadTokens();
    }
    
    /**
     * Private: Load tokens from localStorage
     */
    _loadTokens() {
        if (typeof localStorage !== 'undefined') {
            this.token = localStorage.getItem('access_token');
            this.refreshToken = localStorage.getItem('refresh_token');
        }
    }
    
    /**
     * Private: Save tokens to localStorage
     */
    _saveTokens(accessToken, refreshToken) {
        this.token = accessToken;
        this.refreshToken = refreshToken;
        
        if (typeof localStorage !== 'undefined') {
            localStorage.setItem('access_token', accessToken);
            localStorage.setItem('refresh_token', refreshToken);
        }
    }
    
    /**
     * Private: Clear tokens
     */
    _clearTokens() {
        this.token = null;
        this.refreshToken = null;
        
        if (typeof localStorage !== 'undefined') {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
        }
    }
    
    /**
     * Private: Make HTTP request with retry logic
     */
    async _request(method, endpoint, data = null, retry = 0) {
        const url = `${this.baseUrl}${endpoint}`;
        
        const options = {
            method: method.toUpperCase(),
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        // Add authorization header if token exists
        if (this.token) {
            options.headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        // Add body for POST/PUT/PATCH requests
        if (data && ['POST', 'PUT', 'PATCH'].includes(options.method)) {
            options.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(url, options);
            
            // Handle 401 Unauthorized - try to refresh token
            if (response.status === 401 && this.refreshToken && retry < 1) {
                const refreshed = await this._refreshAccessToken();
                if (refreshed) {
                    return this._request(method, endpoint, data, retry + 1);
                }
            }
            
            // Parse JSON response
            const result = await response.json();
            
            // Check if response is successful
            if (!response.ok) {
                throw new Error(result.message || result.error || `HTTP ${response.status}`);
            }
            
            return result.data || result;
            
        } catch (error) {
            // Retry on network errors
            if (retry < this.options.retryAttempts && this._isRetryableError(error)) {
                await this._sleep(this.options.retryDelay * (retry + 1));
                return this._request(method, endpoint, data, retry + 1);
            }
            
            throw error;
        }
    }
    
    /**
     * Private: Check if error is retryable
     */
    _isRetryableError(error) {
        return error.message.includes('fetch') ||
               error.message.includes('network') ||
               error.message.includes('timeout');
    }
    
    /**
     * Private: Sleep utility
     */
    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    /**
     * Private: Refresh access token
     */
    async _refreshAccessToken() {
        try {
            const response = await fetch(`${this.baseUrl}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.refreshToken}`
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                this._saveTokens(result.data.access_token, this.refreshToken);
                return true;
            }
            
            // Refresh failed, clear tokens
            this._clearTokens();
            return false;
            
        } catch (error) {
            this._clearTokens();
            return false;
        }
    }
    
    /**
     * Authentication
     */
    
    async login(username, password) {
        const result = await this._request('POST', '/auth/login', { username, password });
        this._saveTokens(result.access_token, result.refresh_token);
        return result;
    }
    
    async logout() {
        try {
            await this._request('POST', '/auth/logout');
        } finally {
            this._clearTokens();
        }
    }
    
    /**
     * Products Management
     */
    
    async getProducts() {
        return await this._request('GET', '/products');
    }
    
    async createProduct(product) {
        return await this._request('POST', '/products', product);
    }
    
    async updateProduct(id, product) {
        return await this._request('PUT', `/products/${id}`, product);
    }
    
    async deleteProduct(id) {
        return await this._request('DELETE', `/products/${id}`);
    }
    
    /**
     * Daily Log Management
     */
    
    async getLogEntries(date = null) {
        const endpoint = date ? `/log?date=${date}` : '/log';
        return await this._request('GET', endpoint);
    }
    
    async createLogEntry(entry) {
        return await this._request('POST', '/log', entry);
    }
    
    async updateLogEntry(id, entry) {
        return await this._request('PUT', `/log/${id}`, entry);
    }
    
    async deleteLogEntry(id) {
        return await this._request('DELETE', `/log/${id}`);
    }
    
    /**
     * Statistics
     */
    
    async getDailyStats(date) {
        return await this._request('GET', `/stats/daily?date=${date}`);
    }
    
    async getWeeklyStats(startDate, endDate) {
        return await this._request('GET', `/stats/weekly?start=${startDate}&end=${endDate}`);
    }
    
    /**
     * Settings Management
     */
    
    async getSettings() {
        return await this._request('GET', '/settings');
    }
    
    async saveSettings(settings) {
        return await this._request('PUT', '/settings', settings);
    }
    
    /**
     * Dishes Management
     */
    
    async getDishes() {
        return await this._request('GET', '/dishes');
    }
    
    async createDish(dish) {
        return await this._request('POST', '/dishes', dish);
    }
    
    async updateDish(id, dish) {
        return await this._request('PUT', `/dishes/${id}`, dish);
    }
    
    async deleteDish(id) {
        return await this._request('DELETE', `/dishes/${id}`);
    }
    
    /**
     * Fasting Management
     */
    
    async getFastingStatus() {
        return await this._request('GET', '/fasting/status');
    }
    
    async startFasting(data) {
        return await this._request('POST', '/fasting/start', data);
    }
    
    async endFasting() {
        return await this._request('POST', '/fasting/end');
    }
    
    async getFastingStats() {
        return await this._request('GET', '/fasting/stats');
    }
    
    /**
     * Profile Management
     */
    
    async getProfile() {
        return await this._request('GET', '/profile');
    }
    
    async updateProfile(profile) {
        return await this._request('PUT', '/profile', profile);
    }
}

// Export for use in Node.js (tests) and browsers
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ApiAdapter;
}
