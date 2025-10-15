// Simple toast notifications - lightweight and pretty

class NotificationManager {
    constructor() {
        this.container = null;
        this.init();
    }
    
    init() {
        this.createContainer();
    }
    
    createContainer() {
        this.container = document.getElementById('toast-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'position-fixed top-0 end-0 p-3';
            this.container.style.zIndex = '1055';
            document.body.appendChild(this.container);
        }
    }
    
    show(message, type = 'info', duration = 3000) {
        const toast = this.createToast(message, type);
        this.container.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Auto-remove
        setTimeout(() => this.remove(toast), duration);
        
        return toast;
    }
    
    createToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-bg-${this.getBootstrapClass(type)} border-0`;
        toast.role = 'alert';
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${this.getIcon(type)} ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        
        return toast;
    }
    
    getBootstrapClass(type) {
        const classes = {
            'success': 'success',
            'error': 'danger', 
            'warning': 'warning',
            'info': 'info'
        };
        return classes[type] || 'info';
    }
    
    getIcon(type) {
        const icons = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️', 
            'info': 'ℹ️'
        };
        return icons[type] || 'ℹ️';
    }
    
    remove(toast) {
        if (toast && toast.parentNode) {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }
    }
    
    // Convenience methods
    success(message, duration) { return this.show(message, 'success', duration); }
    error(message, duration) { return this.show(message, 'error', duration); }
    warning(message, duration) { return this.show(message, 'warning', duration); }
    info(message, duration) { return this.show(message, 'info', duration); }
}

// Global notification manager
window.showNotification = function(message, type, duration) {
    if (!window.notificationManager) {
        window.notificationManager = new NotificationManager();
    }
    return window.notificationManager.show(message, type, duration);
};

// Shortcuts
window.showSuccess = (msg) => showNotification(msg, 'success');
window.showError = (msg) => showNotification(msg, 'error');
window.showWarning = (msg) => showNotification(msg, 'warning');
window.showInfo = (msg) => showNotification(msg, 'info');
