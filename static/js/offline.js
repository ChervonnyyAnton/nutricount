// Offline status indicator - simple and unobtrusive

class OfflineIndicator {
    constructor() {
        this.isOnline = navigator.onLine;
        this.indicator = null;
        this.init();
    }
    
    init() {
        this.createIndicator();
        this.bindEvents();
        this.updateStatus();
    }
    
    createIndicator() {
        this.indicator = document.getElementById('network-status');
        if (!this.indicator) {
            // Create if doesn't exist
            this.indicator = document.createElement('div');
            this.indicator.id = 'network-status';
            this.indicator.className = 'network-status';
            document.body.appendChild(this.indicator);
        }
    }
    
    bindEvents() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.updateStatus();
            this.syncOfflineData();
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.updateStatus();
        });
    }
    
    updateStatus() {
        const indicator = this.indicator;
        const text = document.getElementById('network-text');
        
        if (this.isOnline) {
            indicator.className = 'network-status online';
            if (text) text.textContent = '🟢 Online';
        } else {
            indicator.className = 'network-status offline';
            if (text) text.textContent = '🔴 Offline';
        }
    }
    
    async syncOfflineData() {
        // Try to sync any pending offline data
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            try {
                const registration = await navigator.serviceWorker.ready;
                await registration.sync.register('sync-nutrition-data');
                console.log('🔄 Background sync registered');
            } catch (error) {
                console.log('❌ Background sync failed:', error);
            }
        }
        
        // Show brief success message
        this.showSyncMessage('🔄 Syncing offline changes...');
    }
    
    showSyncMessage(message) {
        const toast = document.createElement('div');
        toast.className = 'position-fixed top-0 end-0 m-3 alert alert-info alert-dismissible fade show';
        toast.style.zIndex = '9999';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 3000);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new OfflineIndicator();
});
