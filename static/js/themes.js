/**
 * Simple theme system for Nutrition Tracker - Light and Dark themes only
 */
class ThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.themes = {
            light: {
                name: 'Light',
                colors: {
                    primary: '#007bff',
                    secondary: '#6c757d',
                    success: '#28a745',
                    danger: '#dc3545',
                    warning: '#ffc107',
                    info: '#17a2b8',
                    light: '#f8f9fa',
                    dark: '#343a40',
                    background: '#ffffff',
                    surface: '#f8f9fa',
                    text: '#212529',
                    textSecondary: '#6c757d',
                    border: '#dee2e6',
                    shadow: 'rgba(0, 0, 0, 0.1)'
                }
            },
            dark: {
                name: 'Dark',
                colors: {
                    primary: '#0d6efd',
                    secondary: '#6c757d',
                    success: '#198754',
                    danger: '#dc3545',
                    warning: '#fd7e14',
                    info: '#0dcaf0',
                    light: '#f8f9fa',
                    dark: '#212529',
                    background: '#121212',
                    surface: '#1e1e1e',
                    text: '#ffffff',
                    textSecondary: '#adb5bd',
                    border: '#495057',
                    shadow: 'rgba(0, 0, 0, 0.3)'
                }
            }
        };
        
        this.init();
    }
    
    init() {
        this.applyTheme(this.currentTheme);
        this.setupThemeToggle();
    }
    
    applyTheme(themeName) {
        const theme = this.themes[themeName];
        if (!theme) return;
        
        const root = document.documentElement;
        const colors = theme.colors;
        
        // Apply CSS custom properties
        root.style.setProperty('--bs-primary', colors.primary);
        root.style.setProperty('--bs-secondary', colors.secondary);
        root.style.setProperty('--bs-success', colors.success);
        root.style.setProperty('--bs-danger', colors.danger);
        root.style.setProperty('--bs-warning', colors.warning);
        root.style.setProperty('--bs-info', colors.info);
        root.style.setProperty('--bs-light', colors.light);
        root.style.setProperty('--bs-dark', colors.dark);
        
        // Apply custom theme properties
        root.style.setProperty('--theme-background', colors.background);
        root.style.setProperty('--theme-surface', colors.surface);
        root.style.setProperty('--theme-text', colors.text);
        root.style.setProperty('--theme-text-secondary', colors.textSecondary);
        root.style.setProperty('--theme-border', colors.border);
        root.style.setProperty('--theme-shadow', colors.shadow);
        
        // Update body data-theme attribute
        document.body.setAttribute('data-theme', themeName);
        
        this.currentTheme = themeName;
        localStorage.setItem('theme', themeName);
        
        // Update toggle button
        this.updateToggleButton();
    }
    
    
    setupThemeToggle() {
        // Add event listener to theme toggle button
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
        
        // Add keyboard shortcut for theme toggle
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'T') {
                e.preventDefault();
                this.toggleTheme();
            }
        });
    }
    
    toggleTheme() {
        // Simple toggle between light and dark
        const nextTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(nextTheme);
    }
    
    updateToggleButton() {
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            const isDark = this.currentTheme === 'dark';
            themeToggle.innerHTML = isDark ? '🌙 Dark' : '☀️ Light';
            themeToggle.title = isDark ? 'Switch to light theme' : 'Switch to dark theme';
        }
    }
    
    getCurrentTheme() {
        return this.currentTheme;
    }
    
    getThemeColors() {
        return this.themes[this.currentTheme].colors;
    }
}

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}
