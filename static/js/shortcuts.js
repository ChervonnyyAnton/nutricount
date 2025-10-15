// Keyboard shortcuts - simple and useful

document.addEventListener('DOMContentLoaded', function() {
    // Global shortcuts
    document.addEventListener('keydown', function(e) {
        // Skip if user is typing in input field
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
            return;
        }
        
        // Alt + key combinations (won't interfere with browser shortcuts)
        if (e.altKey && !e.ctrlKey && !e.shiftKey) {
            switch(e.key) {
                case '1':
                    e.preventDefault();
                    switchTab('products');
                    break;
                case '2':
                    e.preventDefault(); 
                    switchTab('dishes');
                    break;
                case '3':
                    e.preventDefault();
                    switchTab('log');
                    break;
                case 'n':
                    e.preventDefault();
                    focusFirstInput();
                    break;
                case 's':
                    e.preventDefault();
                    showStats();
                    break;
                case 'b':
                    e.preventDefault();
                    createBackup();
                    break;
            }
        }
        
        // Escape key - universal cancel
        if (e.key === 'Escape') {
            clearAllForms();
            hideModals();
        }
        
        // Enter in empty form - focus first input
        if (e.key === 'Enter' && e.target === document.body) {
            focusFirstInput();
        }
    });
    
    // Add keyboard hints to UI
    addKeyboardHints();
});

function switchTab(tabName) {
    const tabButton = document.getElementById(tabName + '-tab');
    if (tabButton) {
        tabButton.click();
        // Focus first input in new tab after a brief delay
        setTimeout(focusFirstInput, 100);
    }
}

function focusFirstInput() {
    const activeTab = document.querySelector('.tab-pane.active');
    if (activeTab) {
        const firstInput = activeTab.querySelector('input:not([type="hidden"]), select, textarea');
        if (firstInput) {
            firstInput.focus();
        }
    }
}

function showStats() {
    // Highlight stats card briefly
    const statsCard = document.querySelector('.stats-card');
    if (statsCard) {
        statsCard.style.animation = 'pulse 0.5s ease-in-out';
        setTimeout(() => statsCard.style.animation = '', 500);
    }
}

function createBackup() {
    if (confirm('Create backup now?')) {
        fetch('/api/system/backup', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showNotification('✅ Backup created successfully!', 'success');
                }
            })
            .catch(() => showNotification('❌ Backup failed', 'error'));
    }
}

function clearAllForms() {
    document.querySelectorAll('form').forEach(form => {
        if (!form.querySelector('input[type="date"]')?.value) { // Don't clear date inputs
            form.reset();
        }
    });
}

function hideModals() {
    // Hide any open modals/dropdowns
    document.querySelectorAll('.modal, .dropdown-menu').forEach(el => {
        if (el.style.display !== 'none') {
            el.style.display = 'none';
        }
    });
}

function addKeyboardHints() {
    // Add subtle hints to the UI
    const footer = document.querySelector('footer');
    if (footer) {
        const hints = document.createElement('div');
        hints.className = 'keyboard-hints text-muted mt-2';
        hints.style.fontSize = '0.7rem';
        hints.innerHTML = `
            <details>
                <summary style="cursor: pointer;">⌨️ Keyboard Shortcuts</summary>
                <div class="mt-1">
                    <kbd>Alt+1</kbd> Products • 
                    <kbd>Alt+2</kbd> Dishes • 
                    <kbd>Alt+3</kbd> Log • 
                    <kbd>Alt+N</kbd> New Entry • 
                    <kbd>Alt+S</kbd> Show Stats • 
                    <kbd>Alt+B</kbd> Backup • 
                    <kbd>Esc</kbd> Clear
                </div>
            </details>
        `;
        footer.appendChild(hints);
    }
}

// Export for use in main app
window.NutritionShortcuts = {
    switchTab,
    focusFirstInput,
    createBackup,
    clearAllForms
};
