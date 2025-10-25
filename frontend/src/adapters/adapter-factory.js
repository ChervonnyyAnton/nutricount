/**
 * Adapter Factory
 * 
 * Automatically detects the deployment environment and creates
 * the appropriate backend adapter:
 * 
 * - GitHub Pages (static) → StorageAdapter (localStorage)
 * - Raspberry Pi (server) → ApiAdapter (Flask API + database)
 * 
 * This implements the BFF (Backend For Frontend) pattern where
 * the frontend has a single interface but different implementations
 * based on deployment context.
 */

// Import adapters (for Node.js environment)
if (typeof require !== 'undefined' && typeof module !== 'undefined') {
    var ApiAdapter = require('./api-adapter.js');
    var StorageAdapter = require('./storage-adapter.js');
}

class AdapterFactory {
    /**
     * Detect deployment environment
     * 
     * @returns {string} 'static' for GitHub Pages, 'server' for Flask backend
     */
    static detectEnvironment() {
        // Check if we're in Node.js (for tests)
        if (typeof window === 'undefined') {
            return 'server'; // Default for tests
        }

        // Check for specific markers that indicate Flask backend is available
        const hostname = window.location.hostname;
        const pathname = window.location.pathname;
        
        // GitHub Pages detection
        if (hostname.includes('github.io') || pathname.includes('/nutricount/')) {
            return 'static';
        }
        
        // Local development with Flask
        if (hostname === 'localhost' && window.location.port === '5000') {
            return 'server';
        }
        
        // Raspberry Pi detection (local network)
        if (hostname.match(/^192\.168\.\d+\.\d+$/) || hostname.match(/\.local$/)) {
            return 'server';
        }
        
        // Try to detect Flask backend by checking if /api/health endpoint exists
        // This is synchronous detection - for better UX, could be async
        try {
            const xhr = new XMLHttpRequest();
            xhr.open('GET', '/api/health', false); // Synchronous request
            xhr.send();
            
            if (xhr.status === 200) {
                return 'server'; // Flask backend is available
            }
        } catch (e) {
            // Health check failed, assume static
        }
        
        // Default to static (safe fallback)
        return 'static';
    }

    /**
     * Create the appropriate adapter based on environment
     * 
     * @param {Object} options - Configuration options
     * @param {string} options.forceMode - Force specific mode: 'static' or 'server'
     * @param {string} options.apiBaseUrl - Base URL for API adapter (default: '/api')
     * @returns {BackendAdapter} Configured adapter instance
     */
    static create(options = {}) {
        const {
            forceMode = null,
            apiBaseUrl = '/api',
            ...adapterOptions
        } = options;

        // Determine environment
        const environment = forceMode || this.detectEnvironment();

        console.log(`🔧 AdapterFactory: Detected environment = ${environment}`);

        // Create appropriate adapter
        if (environment === 'static') {
            console.log('📦 Using StorageAdapter (localStorage)');
            return new StorageAdapter();
        } else {
            console.log('🌐 Using ApiAdapter (Flask backend)');
            return new ApiAdapter(apiBaseUrl, adapterOptions);
        }
    }

    /**
     * Check if backend API is available (async version)
     * 
     * @param {string} apiBaseUrl - Base URL for API
     * @returns {Promise<boolean>} True if API is available
     */
    static async isApiAvailable(apiBaseUrl = '/api') {
        try {
            const response = await fetch(`${apiBaseUrl}/health`, {
                method: 'GET',
                timeout: 3000,
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            return response.ok;
        } catch (error) {
            console.warn('API health check failed:', error.message);
            return false;
        }
    }

    /**
     * Create adapter with async detection (recommended)
     * 
     * @param {Object} options - Configuration options
     * @returns {Promise<BackendAdapter>} Configured adapter instance
     */
    static async createAsync(options = {}) {
        const {
            forceMode = null,
            apiBaseUrl = '/api',
            ...adapterOptions
        } = options;

        if (forceMode) {
            return this.create(options);
        }

        // Try to detect API availability
        const apiAvailable = await this.isApiAvailable(apiBaseUrl);

        console.log(`🔧 AdapterFactory (async): API available = ${apiAvailable}`);

        if (apiAvailable) {
            console.log('🌐 Using ApiAdapter (Flask backend)');
            return new ApiAdapter(apiBaseUrl, adapterOptions);
        } else {
            console.log('📦 Using StorageAdapter (localStorage)');
            return new StorageAdapter();
        }
    }
}

// Export for use in Node.js (tests) and browsers
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdapterFactory;
}
