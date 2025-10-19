// Simple Admin Panel JavaScript

function openAdminPanel() {
    const modal = new bootstrap.Modal(document.getElementById('adminModal'));

    // Add event listeners for proper accessibility
    const modalElement = document.getElementById('adminModal');

    modalElement.addEventListener('shown.bs.modal', function () {
        // Set proper ARIA attributes when modal is shown
        modalElement.removeAttribute('aria-hidden');

        // Focus on the first focusable element
        const firstFocusable = modalElement.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (firstFocusable) {
            firstFocusable.focus();
        }

        // Initialize profile form after modal is shown
        setTimeout(initializeProfileForm, 100);
        
        // Initialize fasting settings form
        setTimeout(initializeFastingSettingsForm, 100);
    });

    modalElement.addEventListener('hidden.bs.modal', function () {
        // Set proper ARIA attributes when modal is hidden
        modalElement.setAttribute('aria-hidden', 'true');
    });

    loadAdminData();
    modal.show();
}

async function loadAdminData() {
    try {
        // Load system status
        const response = await fetch('/api/system/status');
        const data = await response.json();

        if (data.status === 'success') {
            const info = data.data;

            // Update counts
            document.getElementById('admin-products-count').textContent = info.database.products_count;
            document.getElementById('admin-dishes-count').textContent = info.database.dishes_count;
            document.getElementById('admin-log-count').textContent = info.database.log_entries_count;
            document.getElementById('admin-db-size').textContent = info.database.size_mb + ' MB';

            // Update system info
            document.getElementById('admin-system-info').textContent = JSON.stringify(info, null, 2);
        }
    } catch (error) {
        showError('Failed to load admin data');
        console.error('Admin data error:', error);
    }
}

async function adminCreateBackup() {
    if (!confirm('Create a backup now?')) return;

    try {
        const response = await fetch('/api/system/backup', { method: 'POST' });
        const data = await response.json();

        if (data.status === 'success') {
            showSuccess(`Backup created: ${data.data.backup_id}`);

            // Automatically download the backup
            const downloadUrl = data.data.download_url;
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = data.data.backup_id;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

        } else {
            showError('Backup failed');
        }
    } catch (error) {
        showError('Backup failed');
    }
}

async function adminRestoreBackup() {
    if (!confirm('Restore from backup? This will replace current database!')) return;

    const fileInput = document.getElementById('restoreFileInput');
    if (!fileInput) {
        showError('File input not found');
        return;
    }

    // Trigger file selection
    fileInput.click();

    fileInput.onchange = async function (event) {
        const file = event.target.files[0];
        if (!file) return;

        if (!file.name.endsWith('.db')) {
            showError('Please select a .db backup file');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('backup_file', file);

            const response = await fetch('/api/system/restore', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.status === 'success') {
                showSuccess(`Database restored from: ${data.data.restored_file}`);
                // Reload page to reflect changes
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                showError(data.message || 'Restore failed');
            }
        } catch (error) {
            showError('Restore failed: ' + error.message);
        }

        // Clear file input
        fileInput.value = '';
    };
}

async function adminOptimizeDB() {
    if (!confirm('Optimize database? This may take a moment.')) return;

    try {
        const response = await fetch('/api/maintenance/vacuum', { method: 'POST' });
        const data = await response.json();

        if (data.status === 'success') {
            showSuccess(`Database optimized! Saved ${data.data.space_saved_mb} MB`);
            loadAdminData(); // Refresh stats
        } else {
            showError('Optimization failed');
        }
    } catch (error) {
        showError('Optimization failed');
    }
}

async function adminCleanup() {
    if (!confirm('Clean up temporary files?')) return;

    try {
        const response = await fetch('/api/maintenance/cleanup', { method: 'POST' });
        const data = await response.json();

        if (data.status === 'success') {
            showSuccess(`Cleanup completed! Removed ${data.data.files_cleaned} files`);
        } else {
            showError('Cleanup failed');
        }
    } catch (error) {
        showError('Cleanup failed');
    }
}

async function adminExportData() {
    try {
        const response = await fetch('/api/export/all');
        const data = await response.json();

        // Create download link
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `nutrition-export-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);

        showSuccess('Data exported successfully!');
    } catch (error) {
        showError('Export failed');
    }
}

// Add admin button to navbar (if admin key pressed)
document.addEventListener('keydown', function (e) {
    if (e.ctrlKey && e.altKey && e.key === 'a') {
        e.preventDefault();
        openAdminPanel();
    }
});

// Add secret admin access (triple-click on app title)
document.addEventListener('DOMContentLoaded', function () {
    const title = document.querySelector('h1');
    let clickCount = 0;

    if (title) {
        title.addEventListener('click', function () {
            clickCount++;
            if (clickCount === 3) {
                openAdminPanel();
                clickCount = 0;
            }
            setTimeout(() => { clickCount = 0; }, 1000);
        });

        // Add subtle cursor change on hover
        title.style.cursor = 'pointer';
        title.title = 'Triple-click for admin panel';
    }
});

// Data list functions
async function showProductsList() {
    try {
        const response = await fetch('/api/products');
        const data = await response.json();

        if (data.status === 'success') {
            displayDataList('Products', data.data, (product) =>
                `${product.name} - ${product.calories_per_100g} cal/100g`
            );
        } else {
            showError('Failed to load products');
        }
    } catch (error) {
        showError('Failed to load products: ' + error.message);
    }
}

async function showDishesList() {
    try {
        const response = await fetch('/api/dishes');
        const data = await response.json();

        if (data.status === 'success') {
            displayDataList('Dishes', data.data, (dish) =>
                `${dish.name} - ${dish.total_weight_grams}g total`
            );
        } else {
            showError('Failed to load dishes');
        }
    } catch (error) {
        showError('Failed to load dishes: ' + error.message);
    }
}

async function showLogEntriesList() {
    try {
        const response = await fetch('/api/log');
        const data = await response.json();

        if (data.status === 'success') {
            displayDataList('Log Entries', data.data, (entry) =>
                `${entry.date} - ${entry.item_name} (${entry.quantity_grams}g) - ${entry.meal_time}`
            );
        } else {
            showError('Failed to load log entries');
        }
    } catch (error) {
        showError('Failed to load log entries: ' + error.message);
    }
}

function displayDataList(title, items, formatter) {
    const section = document.getElementById('dataListsSection');
    const titleEl = document.getElementById('listTitle');
    const contentEl = document.getElementById('dataListContent');

    titleEl.textContent = `${title} (${items.length})`;

    if (items.length === 0) {
        contentEl.innerHTML = '<p class="text-muted">No items found</p>';
    } else {
        const listHtml = items.map(item =>
            `<div class="mb-2 p-2 border rounded">${formatter(item)}</div>`
        ).join('');
        contentEl.innerHTML = listHtml;
    }

    section.style.display = 'block';
    section.scrollIntoView({ behavior: 'smooth' });
}

function hideDataLists() {
    document.getElementById('dataListsSection').style.display = 'none';
}

// Database management functions
async function adminCleanupTestData() {
    if (!confirm('Clean up test data? This will delete all items with "TEST" prefix!\n\nThis action cannot be undone.')) return;

    try {
        const response = await fetch('/api/maintenance/cleanup-test-data', { method: 'POST' });
        const data = await response.json();

        if (data.status === 'success') {
            showSuccess(`Test data cleanup completed! Removed ${data.data.total_deleted} items`);
            loadAdminData(); // Refresh stats
        } else {
            showError('Test data cleanup failed');
        }
    } catch (error) {
        showError('Test data cleanup failed: ' + error.message);
    }
}

async function adminWipeDatabase() {
    const confirmMessage = 'WIPE ENTIRE DATABASE?\n\n' +
        'This will delete ALL data:\n' +
        '• All products\n' +
        '• All dishes\n' +
        '• All log entries\n' +
        '• Reset to initial state\n\n' +
        'This action CANNOT be undone!\n\n' +
        'Type "WIPE" to confirm:';

    const userInput = prompt(confirmMessage);
    if (userInput !== 'WIPE') {
        showError('Database wipe cancelled');
        return;
    }

    try {
        const response = await fetch('/api/maintenance/wipe-database', { method: 'POST' });
        const data = await response.json();

        if (data.status === 'success') {
            showSuccess(`Database wiped! Removed ${data.data.total_deleted} items`);
            loadAdminData(); // Refresh stats
            // Reload page to reflect changes
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            showError('Database wipe failed');
        }
    } catch (error) {
        showError('Database wipe failed: ' + error.message);
    }
}

// Profile management functions
async function loadProfileData() {
    try {
        const response = await fetch('/api/profile');
        const data = await response.json();

        if (data.status === 'success' && data.data) {
            const profile = data.data;

            // Populate form fields
            document.getElementById('profileGender').value = profile.gender;
            document.getElementById('profileBirthDate').value = profile.birth_date;
            document.getElementById('profileHeight').value = profile.height_cm;
            document.getElementById('profileWeight').value = profile.weight_kg;
            document.getElementById('profileActivity').value = profile.activity_level;
            document.getElementById('profileGoal').value = profile.goal;
            document.getElementById('profileKetoType').value = profile.keto_type || 'standard';

            // Populate optional fields
            if (profile.body_fat_percentage) {
                document.getElementById('profileBodyFat').value = profile.body_fat_percentage;
            }
            if (profile.lean_body_mass_kg) {
                document.getElementById('profileLeanBodyMass').value = profile.lean_body_mass_kg;
            }

            // Load calculated macros
            await loadCalculatedMacros();
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

async function loadCalculatedMacros() {
    try {
        const response = await fetch('/api/profile/macros');
        const data = await response.json();

        if (data.status === 'success' && data.data) {
            const macros = data.data;

            // Update macro display
            document.getElementById('macro-bmr').textContent = macros.bmr;
            document.getElementById('macro-tdee').textContent = macros.tdee;
            document.getElementById('macro-target').textContent = macros.target_calories;
            document.getElementById('macro-carbs').textContent = macros.carbs;
            document.getElementById('macro-protein').textContent = macros.protein;
            document.getElementById('macro-fats').textContent = macros.fats;

            // Show macros section
            document.getElementById('calculatedMacros').style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading macros:', error);
        document.getElementById('calculatedMacros').style.display = 'none';
    }
}

async function handleProfileSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    const spinner = submitBtn.querySelector('.spinner-border');

    try {
        // Show loading state
        spinner.classList.remove('d-none');
        submitBtn.disabled = true;

        const profileData = {
            gender: formData.get('gender'),
            birth_date: formData.get('birth_date'),
            height_cm: parseInt(formData.get('height_cm')),
            weight_kg: parseFloat(formData.get('weight_kg')),
            activity_level: formData.get('activity_level'),
            goal: formData.get('goal'),
            keto_type: formData.get('keto_type')
        };

        // Add optional fields if provided
        const bodyFat = formData.get('body_fat_percentage');
        if (bodyFat && bodyFat.trim() !== '') {
            profileData.body_fat_percentage = parseFloat(bodyFat);
        }

        const leanBodyMass = formData.get('lean_body_mass_kg');
        if (leanBodyMass && leanBodyMass.trim() !== '') {
            profileData.lean_body_mass_kg = parseFloat(leanBodyMass);
        }

        // Check if profile exists to determine method
        const checkResponse = await fetch('/api/profile');
        const checkData = await checkResponse.json();
        const method = (checkData.status === 'success' && checkData.data) ? 'PUT' : 'POST';

        const response = await fetch('/api/profile', {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(profileData)
        });

        const data = await response.json();

        if (response.ok) {
            if (window.showSuccess) {
                showSuccess(data.message || 'Profile saved successfully!');
            }
            // Reload macros after saving
            await loadCalculatedMacros();
        } else {
            // Handle validation errors
            if (data.errors && data.errors.length > 0) {
                const errorMessage = data.errors.join('\n• ');
                if (window.showError) {
                    showError(`Validation failed:\n• ${errorMessage}`);
                }
            } else {
                throw new Error(data.message || 'Failed to save profile');
            }
        }
    } catch (error) {
        console.error('Error saving profile:', error);
        if (window.showError) {
            showError(error.message);
        }
    } finally {
        // Hide loading state
        spinner.classList.add('d-none');
        submitBtn.disabled = false;
    }
}

// Calculate LBM from body fat percentage
function calculateLBMFromBodyFat() {
    const weightInput = document.getElementById('profileWeight');
    const bodyFatInput = document.getElementById('profileBodyFat');
    const lbmInput = document.getElementById('profileLeanBodyMass');

    if (weightInput && bodyFatInput && lbmInput) {
        const weight = parseFloat(weightInput.value);
        const bodyFat = parseFloat(bodyFatInput.value);

        if (weight && bodyFat && bodyFat > 0 && bodyFat < 100) {
            const lbm = weight * (1 - bodyFat / 100);
            lbmInput.value = lbm.toFixed(1);
        }
    }
}

// Initialize profile form when admin panel opens
function initializeProfileForm() {
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', handleProfileSubmit);
        loadProfileData();

        // Add event listeners for automatic LBM calculation
        const bodyFatInput = document.getElementById('profileBodyFat');
        const weightInput = document.getElementById('profileWeight');

        if (bodyFatInput) {
            bodyFatInput.addEventListener('input', calculateLBMFromBodyFat);
        }
        if (weightInput) {
            weightInput.addEventListener('input', calculateLBMFromBodyFat);
        }
    }
}

// Fasting settings management functions
async function loadFastingSettings() {
    try {
        const response = await fetch('/api/fasting/settings');
        const data = await response.json();

        if (data.status === 'success' && data.data) {
            const settings = data.data;

            // Populate form fields
            document.getElementById('fastingGoal').value = settings.fasting_goal || '';
            document.getElementById('fastingStartTime').value = settings.preferred_start_time || '';
            document.getElementById('fastingReminders').checked = settings.enable_reminders || false;
            document.getElementById('fastingNotifications').checked = settings.enable_notifications || false;
            document.getElementById('fastingNotes').value = settings.default_notes || '';

            // Load fasting statistics
            await loadFastingStatistics();
        }
    } catch (error) {
        console.error('Error loading fasting settings:', error);
    }
}

async function loadFastingStatistics() {
    try {
        const response = await fetch('/api/fasting/stats');
        const data = await response.json();

        if (data.status === 'success' && data.data) {
            const stats = data.data;

            // Update statistics display
            document.getElementById('fasting-total-sessions').textContent = stats.total_sessions || 0;
            document.getElementById('fasting-completed').textContent = stats.completed_sessions || 0;
            document.getElementById('fasting-avg-duration').textContent = stats.average_duration || '0h';
            document.getElementById('fasting-success-rate').textContent = stats.success_rate || '0%';

            // Show statistics section
            document.getElementById('fastingStats').style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading fasting statistics:', error);
        document.getElementById('fastingStats').style.display = 'none';
    }
}

async function handleFastingSettingsSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    const spinner = submitBtn.querySelector('.spinner-border');

    try {
        // Show loading state
        spinner.classList.remove('d-none');
        submitBtn.disabled = true;

        const settingsData = {
            fasting_goal: formData.get('fasting_goal'),
            preferred_start_time: formData.get('preferred_start_time'),
            enable_reminders: formData.get('enable_reminders') === 'on',
            enable_notifications: formData.get('enable_notifications') === 'on',
            default_notes: formData.get('default_notes')
        };

        // Check if settings exist to determine method
        const checkResponse = await fetch('/api/fasting/settings');
        const checkData = await checkResponse.json();
        const method = (checkData.status === 'success' && checkData.data) ? 'PUT' : 'POST';

        const response = await fetch('/api/fasting/settings', {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(settingsData)
        });

        const data = await response.json();

        if (response.ok) {
            if (window.showSuccess) {
                showSuccess(data.message || 'Fasting settings saved successfully!');
            }
            // Reload statistics after saving
            await loadFastingStatistics();
        } else {
            // Handle validation errors
            if (data.errors && data.errors.length > 0) {
                const errorMessage = data.errors.join('\n• ');
                if (window.showError) {
                    showError(`Validation failed:\n• ${errorMessage}`);
                }
            } else {
                throw new Error(data.message || 'Failed to save fasting settings');
            }
        }
    } catch (error) {
        console.error('Error saving fasting settings:', error);
        if (window.showError) {
            showError(error.message);
        }
    } finally {
        // Hide loading state
        spinner.classList.add('d-none');
        submitBtn.disabled = false;
    }
}

// Initialize fasting settings form when admin panel opens
function initializeFastingSettingsForm() {
    const fastingSettingsForm = document.getElementById('fastingSettingsForm');
    if (fastingSettingsForm) {
        fastingSettingsForm.addEventListener('submit', handleFastingSettingsSubmit);
        loadFastingSettings();
    }
}
