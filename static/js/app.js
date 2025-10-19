// Nutrition Tracker Main Application
// WCAG 2.2 AA Compliant with full accessibility support

class NutritionTracker {
    constructor() {
        this.products = [];
        this.dishes = [];
        this.logEntries = [];
        this.apiBaseUrl = '/api';
        this.currentStats = {};

        // Bind methods
        this.init = this.init.bind(this);
        this.loadProducts = this.loadProducts.bind(this);
        this.loadDishes = this.loadDishes.bind(this);
        this.loadLogEntries = this.loadLogEntries.bind(this);
        this.loadStats = this.loadStats.bind(this);
    }

    async init() {
        console.log('🥗 Initializing Nutrition Tracker...');

        try {
            // Load initial data
            await Promise.all([
                this.loadProducts(),
                this.loadDishes(),
                this.loadLogEntries(),
                this.loadStats()
            ]);

            // Setup event listeners
            this.setupEventListeners();

            // Setup form handlers
            this.setupFormHandlers();

            // Setup search functionality
            this.setupSearch();

            // Setup auto-calculation for product form
            this.setupProductFormAutoCalculation();

            console.log('✅ App initialized successfully');

            // Show success message
            if (window.showSuccess) {
                showSuccess('Welcome to Nutrition Tracker!');
            }
        } catch (error) {
            console.error('❌ Failed to initialize app:', error);
            if (window.showError) {
                showError('Failed to initialize application');
            }
        }
    }

    setupEventListeners() {
        // Item type change handler for log form
        const itemTypeSelect = document.getElementById('logItemType');
        if (itemTypeSelect) {
            itemTypeSelect.addEventListener('change', (e) => {
                this.updateItemOptions(e.target.value);
            });
        }

        // Date filter handlers
        const logFilterDate = document.getElementById('logFilterDate');
        if (logFilterDate) {
            logFilterDate.addEventListener('change', (e) => {
                this.filterLogEntries(e.target.value);
            });
        }

        const statsDate = document.getElementById('statsDate');
        if (statsDate) {
            statsDate.addEventListener('change', (e) => {
                this.loadStats(e.target.value);
            });
        }

        // Stats period toggle handlers
        document.querySelectorAll('input[name="statsPeriod"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.loadStats();
            });
        });

        // Tab switch handlers
        document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                const tabId = e.target.getAttribute('aria-controls');
                this.onTabSwitch(tabId);
            });
        });
    }

    setupFormHandlers() {
        // Product form
        const productForm = document.getElementById('productForm');
        if (productForm) {
            productForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleProductSubmit(e);
            });
        }

        // Dish form
        const dishForm = document.getElementById('dishForm');
        if (dishForm) {
            dishForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleDishSubmit(e);
            });
        }

        // Log form
        const logForm = document.getElementById('logForm');
        if (logForm) {
            logForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleLogSubmit(e);
            });
        }

        // Add ingredient button
        const addIngredientBtn = document.getElementById('addIngredientBtn');
        if (addIngredientBtn) {
            addIngredientBtn.addEventListener('click', () => {
                this.addIngredientRow();
            });
        }
    }

    setupSearch() {
        const productSearch = document.getElementById('productSearch');
        if (productSearch) {
            productSearch.addEventListener('input', (e) => {
                this.searchProducts(e.target.value);
            });
        }
    }

    async loadProducts() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/products`);
            if (!response.ok) throw new Error('Failed to load products');

            const data = await response.json();
            this.products = data.data || [];
            this.renderProducts();
            this.updateProductOptions();
        } catch (error) {
            console.error('Error loading products:', error);
            if (window.showError) {
                showError('Failed to load products');
            }
        }
    }

    async loadDishes() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/dishes`);
            if (!response.ok) throw new Error('Failed to load dishes');

            const data = await response.json();
            this.dishes = data.data || [];
            this.renderDishes();
            this.updateDishOptions();
        } catch (error) {
            console.error('Error loading dishes:', error);
            if (window.showError) {
                showError('Failed to load dishes');
            }
        }
    }

    async loadLogEntries(date = null) {
        try {
            let url = `${this.apiBaseUrl}/log`;
            if (date) {
                url += `?date=${date}`;
            }

            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to load log entries');

            const data = await response.json();
            this.logEntries = data.data || [];
            this.renderLogEntries();
        } catch (error) {
            console.error('Error loading log entries:', error);
            if (window.showError) {
                showError('Failed to load log entries');
            }
        }
    }

    async loadStats(date = null) {
        try {
            const statsDate = date || document.getElementById('statsDate')?.value || new Date().toISOString().split('T')[0];
            const statsPeriod = document.querySelector('input[name="statsPeriod"]:checked')?.value || 'daily';

            let apiUrl;
            if (statsPeriod === 'weekly') {
                apiUrl = `${this.apiBaseUrl}/stats/weekly/${statsDate}`;
            } else {
                apiUrl = `${this.apiBaseUrl}/stats/${statsDate}`;
            }

            const response = await fetch(apiUrl);
            if (!response.ok) throw new Error('Failed to load stats');

            const data = await response.json();
            this.currentStats = data.data || {};
            this.currentStatsPeriod = statsPeriod;
            this.renderStats();
        } catch (error) {
            console.error('Error loading stats:', error);
            if (window.showError) {
                showError('Failed to load statistics');
            }
        }
    }

    renderProducts() {
        const tbody = document.getElementById('productsTableBody');
        if (!tbody) return;

        tbody.innerHTML = '';

        this.products.forEach(product => {
            // Use calculated keto index from API if available, otherwise calculate locally
            const ketoIndex = product.keto_index || this.calculateKetoIndex(product.fat_per_100g, product.protein_per_100g, product.carbs_per_100g);
            const ketoIndexValue = typeof ketoIndex === 'object' ? (ketoIndex?.keto_index || 0) : ketoIndex;
            // Always use calculated rating for consistent badge colors
            const ketoRating = this.getKetoRating(ketoIndexValue);
            const badgeClass = this.getKetoBadgeClass(ketoRating);

            // Get net carbs from API or calculate
            const netCarbs = product.net_carbs || product.carbs_per_100g;
            const fiberEstimated = product.fiber_estimated || false;
            const fiberDeductionCoeff = product.fiber_deduction_coefficient || 0;

            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="fw-medium">${this.escapeHtml(product.name)}</td>
                <td>${product.calories_per_100g}</td>
                <td>${product.protein_per_100g}g</td>
                <td>${product.fat_per_100g}g</td>
                <td>${product.carbs_per_100g}g</td>
                <td>
                    ${netCarbs}g
                    ${fiberEstimated ? '<small class="text-muted d-block">*estimated</small>' : ''}
                    ${fiberDeductionCoeff > 0 ? `<small class="text-info d-block">coeff: ${fiberDeductionCoeff}</small>` : ''}
                </td>
                <td>
                    <span class="badge bg-${badgeClass}" 
                          title="Keto rating: ${ketoRating}${product.keto_category ? ` (${product.keto_category})` : ''}${product.carbs_score ? ` (Carbs: ${product.carbs_score}, Fat: ${product.fat_score}, Quality: ${product.quality_score}, GI: ${product.gi_score})` : ''}">
                        ${ketoIndexValue}
                    </span>
                </td>
                <td class="no-print">
                    <div class="btn-group" role="group">
                        <button class="btn btn-primary btn-sm edit-btn" onclick="app.editProduct(${product.id})"
                                aria-label="Edit ${this.escapeHtml(product.name)}">
                            ✏️
                        </button>
                        <button class="btn btn-danger btn-sm delete-btn" onclick="app.deleteProduct(${product.id})"
                                aria-label="Delete ${this.escapeHtml(product.name)}">
                            ✕
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    renderDishes() {
        const container = document.getElementById('dishesContainer');
        if (!container) return;

        if (this.dishes.length === 0) {
            container.innerHTML = '<p class="text-muted">No dishes created yet. Create your first dish using the form.</p>';
            return;
        }

        container.innerHTML = '';

        this.dishes.forEach(dish => {
            // Use keto index from API if available, otherwise calculate locally
            const ketoIndex = dish.keto_index || this.calculateKetoIndex(dish.total_fat || 0, dish.total_protein || 0, dish.total_carbs || 0);
            const ketoRating = this.getKetoRating(ketoIndex);

            const dishCard = document.createElement('div');
            dishCard.className = 'card mb-3';
            dishCard.innerHTML = `
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="card-title">${this.escapeHtml(dish.name)}</h6>
                            ${dish.description ? `<p class="card-text text-muted">${this.escapeHtml(dish.description)}</p>` : ''}
                            <div class="nutrition-info">
                                <small class="text-muted">
                                    Calories: ${dish.total_calories || 0} | 
                                    Protein: ${dish.total_protein || 0}g | 
                                    Fat: ${dish.total_fat || 0}g | 
                                    Carbs: ${dish.total_carbs || 0}g
                                    ${dish.total_net_carbs ? ` | Net Carbs: ${dish.total_net_carbs}g` : ''}
                                </small>
                            </div>
                            <div class="mt-2">
                                <span class="badge bg-${this.getKetoBadgeClass(ketoRating)}" title="Keto rating: ${ketoRating}">
                                    Keto Index: ${ketoIndex}
                                </span>
                                ${dish.cooking_method ? `<span class="badge bg-secondary ms-1">${dish.cooking_method}</span>` : ''}
                                ${dish.yield_factor && dish.yield_factor !== 1.0 ? `<span class="badge bg-info ms-1">Yield: ${dish.yield_factor}x</span>` : ''}
                            </div>
                        </div>
                        <div class="btn-group no-print" role="group">
                            <button class="btn btn-primary btn-sm edit-btn" onclick="app.editDish(${dish.id})"
                                    aria-label="Edit ${this.escapeHtml(dish.name)}">
                                ✏️
                            </button>
                            <button class="btn btn-danger btn-sm delete-btn" onclick="app.deleteDish(${dish.id})"
                                    aria-label="Delete ${this.escapeHtml(dish.name)}">
                                ✕
                            </button>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(dishCard);
        });
    }

    renderLogEntries() {
        const tbody = document.getElementById('logTableBody');
        if (!tbody) return;

        tbody.innerHTML = '';

        this.logEntries.forEach(entry => {
            const row = document.createElement('tr');
            const mealEmoji = this.getMealEmoji(entry.meal_time);
            const calculatedCalories = this.calculateEntryCalories(entry);

            // Calculate keto index for the entry
            let ketoIndexValue = 0;
            let ketoRating = 'poor';
            let badgeClass = 'danger';

            if (entry.item_type === 'product') {
                // For products, use the product's keto index
                const product = this.products.find(p => p.id === entry.item_id);
                if (product && product.keto_index) {
                    ketoIndexValue = typeof product.keto_index === 'object'
                        ? (product.keto_index?.keto_index || 0)
                        : product.keto_index;
                    ketoRating = this.getKetoRating(ketoIndexValue);
                    badgeClass = this.getKetoBadgeClass(ketoRating);
                }
            } else if (entry.item_type === 'dish') {
                // For dishes, calculate keto index from nutrition data
                const protein = entry.protein || 0;
                const fat = entry.fat || 0;
                const carbs = entry.carbs || 0;

                if (protein > 0 || fat > 0 || carbs > 0) {
                    // Calculate per 100g values
                    const quantity_factor = entry.quantity_grams / 100.0;
                    const protein_per_100g = protein / quantity_factor;
                    const fat_per_100g = fat / quantity_factor;
                    const carbs_per_100g = carbs / quantity_factor;

                    ketoIndexValue = this.calculateKetoIndex(fat_per_100g, protein_per_100g, carbs_per_100g);
                    ketoRating = this.getKetoRating(ketoIndexValue);
                    badgeClass = this.getKetoBadgeClass(ketoRating);
                }
            }

            row.innerHTML = `
                <td>${entry.date}</td>
                <td>${mealEmoji} ${entry.meal_time || 'Unspecified'}</td>
                <td>
                    ${entry.item_type === 'product' ? '🥩' : '🍽️'} 
                    ${this.escapeHtml(entry.item_name || 'Unknown')}
                </td>
                <td>${entry.quantity_grams}g</td>
                <td>${calculatedCalories} cal</td>
                <td>
                    <span class="badge bg-${badgeClass}" title="Keto rating: ${ketoRating}">
                        ${ketoIndexValue.toFixed(1)}
                    </span>
                </td>
                <td class="no-print">
                    <div class="btn-group" role="group">
                        <button class="btn btn-primary btn-sm edit-btn" onclick="app.editLogEntry(${entry.id})"
                                aria-label="Edit log entry">
                            ✏️
                        </button>
                        <button class="btn btn-danger btn-sm delete-btn" onclick="app.deleteLogEntry(${entry.id})"
                                aria-label="Delete log entry">
                            ✕
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    renderStats() {
        const container = document.getElementById('statsContainer');
        if (!container) return;

        const stats = this.currentStats;
        // Handle keto_index as object or number
        const ketoIndexValue = typeof stats.keto_index === 'object'
            ? (stats.keto_index?.keto_index || 0)
            : (stats.keto_index || 0);
        const ketoRating = this.getKetoRating(ketoIndexValue);

        // Check if we have personal macros and goal comparison
        const hasPersonalMacros = stats.personal_macros && stats.goal_comparison;

        let statsHTML = `
            <div class="stat-item">
                <div class="stat-value">${stats.calories || 0}</div>
                <div class="stat-label">🔥 Calories</div>
                ${hasPersonalMacros ? this.renderGoalComparison(stats.goal_comparison.calories, 'calories') : ''}
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.protein || 0}g</div>
                <div class="stat-label">💪 Protein</div>
                ${hasPersonalMacros ? this.renderGoalComparison(stats.goal_comparison.protein, 'protein') : ''}
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.fat || 0}g</div>
                <div class="stat-label">🧈 Fat</div>
                ${hasPersonalMacros ? this.renderGoalComparison(stats.goal_comparison.fat, 'fat') : ''}
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.carbs || 0}g</div>
                <div class="stat-label">🍞 Carbs</div>
                ${hasPersonalMacros ? this.renderGoalComparison(stats.goal_comparison.carbs, 'carbs') : ''}
            </div>
            <div class="stat-item">
                <div class="stat-value">${ketoIndexValue}</div>
                <div class="stat-label">🥑 Keto Index</div>
                <div class="mt-1">
                    <span class="badge bg-${this.getKetoBadgeClass(ketoRating)}">${ketoRating}</span>
                </div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.entries_count || 0}</div>
                <div class="stat-label">📝 Entries</div>
            </div>
        `;

        // Add personal macros section if available
        if (hasPersonalMacros) {
            const periodLabel = this.currentStatsPeriod === 'weekly' ? 'Weekly' : 'Daily';
            statsHTML += `
                <div class="stat-item stat-item-wide personal-targets">
                    <div class="personal-targets-header">
                        <div class="stat-label">🎯 Personal Targets (${periodLabel})</div>
                        <small class="text-muted">Based on your profile</small>
                    </div>
                    <div class="personal-targets-grid">
                        <div class="target-item">
                            <div class="target-value">${stats.personal_macros.bmr}</div>
                            <div class="target-label">BMR</div>
                            <div class="target-description">Base Metabolic Rate</div>
                        </div>
                        <div class="target-item">
                            <div class="target-value">${stats.personal_macros.tdee}</div>
                            <div class="target-label">TDEE</div>
                            <div class="target-description">Total Daily Energy</div>
                        </div>
                        <div class="target-item target-item-primary">
                            <div class="target-value">${stats.personal_macros.target_calories}</div>
                            <div class="target-label">Target</div>
                            <div class="target-description">${periodLabel} Goal</div>
                        </div>
                    </div>
                    <div class="macro-targets">
                        <div class="macro-target">
                            <div class="macro-label">💪 Protein</div>
                            <div class="macro-value">${stats.personal_macros.protein}g</div>
                            <div class="macro-percentage">${stats.personal_macros.protein_percentage}%</div>
                        </div>
                        <div class="macro-target">
                            <div class="macro-label">🧈 Fat</div>
                            <div class="macro-value">${stats.personal_macros.fats}g</div>
                            <div class="macro-percentage">${stats.personal_macros.fats_percentage}%</div>
                        </div>
                        <div class="macro-target">
                            <div class="macro-label">🍞 Carbs</div>
                            <div class="macro-value">${stats.personal_macros.carbs}g</div>
                            <div class="macro-percentage">${stats.personal_macros.carbs_percentage}%</div>
                        </div>
                    </div>
                </div>
            `;
        }

        // Add weekly breakdown if available
        if (this.currentStatsPeriod === 'weekly' && stats.daily_breakdown) {
            statsHTML += `
                <div class="stat-item stat-item-wide weekly-breakdown">
                    <div class="weekly-breakdown-header">
                        <div class="stat-label">📅 Weekly Breakdown</div>
                        <small class="text-muted">${stats.week_start} to ${stats.week_end}</small>
                    </div>
                    <div class="weekly-breakdown-grid">
                        ${Object.entries(stats.daily_breakdown).map(([date, dayStats]) => {
                const dateObj = new Date(date);
                const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'short' });
                const dayNumber = dateObj.getDate();
                return `
                                <div class="day-item">
                                    <div class="day-header">
                                        <div class="day-name">${dayName}</div>
                                        <div class="day-number">${dayNumber}</div>
                                    </div>
                                    <div class="day-stats">
                                        <div class="day-calories">${dayStats.calories} cal</div>
                                        <div class="day-macros">
                                            <span>P: ${dayStats.protein}g</span>
                                            <span>F: ${dayStats.fat}g</span>
                                            <span>C: ${dayStats.carbs}g</span>
                                        </div>
                                        <div class="day-entries">${dayStats.entries_count} entries</div>
                                    </div>
                                </div>
                            `;
            }).join('')}
                    </div>
                </div>
            `;
        }

        container.innerHTML = statsHTML;
    }

    renderGoalComparison(comparison, type) {
        if (!comparison) return '';

        const statusClass = this.getGoalStatusClass(comparison.status);
        const statusIcon = this.getGoalStatusIcon(comparison.status);

        return `
            <div class="goal-comparison mt-1">
                <small class="text-${statusClass}">
                    ${statusIcon} ${comparison.percentage}% of target
                </small>
                <div class="progress mt-1" style="height: 4px;">
                    <div class="progress-bar bg-${statusClass}" 
                         style="width: ${Math.min(comparison.percentage, 150)}%"
                         title="${comparison.actual} / ${comparison.target}">
                    </div>
                </div>
            </div>
        `;
    }

    getGoalStatusClass(status) {
        switch (status) {
            case 'good': return 'success';
            case 'low': return 'warning';
            case 'high': return 'danger';
            default: return 'secondary';
        }
    }

    getGoalStatusIcon(status) {
        switch (status) {
            case 'good': return '✅';
            case 'low': return '⚠️';
            case 'high': return '❌';
            default: return '📊';
        }
    }

    async handleProductSubmit(event) {
        const form = event.target;
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        const spinner = submitBtn.querySelector('.spinner-border');

        try {
            const productData = {
                name: formData.get('name'),
                calories_per_100g: parseFloat(formData.get('calories_per_100g')) || 0,
                protein_per_100g: parseFloat(formData.get('protein_per_100g')) || 0,
                fat_per_100g: parseFloat(formData.get('fat_per_100g')) || 0,
                carbs_per_100g: parseFloat(formData.get('carbs_per_100g')) || 0,
                // New fields according to NUTRIENTS.md
                fiber_per_100g: parseFloat(formData.get('fiber_per_100g')) || null,
                sugars_per_100g: parseFloat(formData.get('sugars_per_100g')) || null,
                category: (formData.get('category') === 'Select category') ? null : formData.get('category'),
                processing_level: (formData.get('processing_level') === 'Select processing level') ? null : formData.get('processing_level'),
                glycemic_index: parseFloat(formData.get('glycemic_index')) || null,
                region: formData.get('region') || 'US'
            };

            // Validate required fields
            if (!productData.name || productData.name.trim() === '') {
                if (window.showError) {
                    showError('Product name is required');
                }
                return;
            }

            // Check if we're editing an existing product
            const editId = form.dataset.editId;
            const isEdit = editId !== undefined;

            const url = isEdit ? `${this.apiBaseUrl}/products/${editId}` : `${this.apiBaseUrl}/products`;
            const method = isEdit ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(productData)
            });

            const data = await response.json();

            if (response.ok) {
                if (window.showSuccess) {
                    showSuccess(data.message || (isEdit ? 'Product updated successfully!' : 'Product created successfully!'));
                }
                form.reset();
                delete form.dataset.editId;
                form.querySelector('button[type="submit"]').textContent = 'Add Product';

                // Reset form title
                const formTitle = document.getElementById('productFormTitle');
                if (formTitle) {
                    formTitle.textContent = 'Add New Product';
                }

                await this.loadProducts();
            } else {
                // Handle validation errors
                if (data.errors && data.errors.length > 0) {
                    const errorMessage = data.errors.join('\n• ');
                    if (window.showError) {
                        showError(`Validation failed:\n• ${errorMessage}`);
                    }
                } else {
                    throw new Error(data.message || 'Failed to create product');
                }
            }
        } catch (error) {
            console.error('Error creating product:', error);
            if (window.showError) {
                showError(error.message);
            }
        } finally {
            if (spinner) spinner.classList.add('d-none');
            submitBtn.disabled = false;
        }
    }

    addIngredientRow(productId = null, quantity = null, productName = null, preparationMethod = 'raw', ediblePortion = 1.0) {
        const ingredientsList = document.getElementById('ingredientsList');
        if (!ingredientsList) return;

        const ingredientDiv = document.createElement('div');
        ingredientDiv.className = 'row mb-2';

        // Find product name if not provided but productId is
        if (productId && !productName) {
            const product = this.products.find(p => p.id == productId);
            productName = product ? product.name : '';
        }

        ingredientDiv.innerHTML = `
            <div class="col-md-4">
                <select class="form-select ingredient-product-select" name="ingredient_product_id" required>
                    <option value="">Select Product</option>
                    ${this.products.map(product =>
            `<option value="${product.id}" ${productId && product.id == productId ? 'selected' : ''}>${this.escapeHtml(product.name)}</option>`
        ).join('')}
                </select>
            </div>
            <div class="col-md-2">
                <input type="number" class="form-control" name="ingredient_quantity" 
                       placeholder="Grams" min="1" step="0.1" required value="${quantity || ''}">
            </div>
            <div class="col-md-2">
                <select class="form-select" name="ingredient_preparation_method">
                    <option value="raw" ${preparationMethod === 'raw' ? 'selected' : ''}>Raw</option>
                    <option value="boiled" ${preparationMethod === 'boiled' ? 'selected' : ''}>Boiled</option>
                    <option value="steamed" ${preparationMethod === 'steamed' ? 'selected' : ''}>Steamed</option>
                    <option value="grilled" ${preparationMethod === 'grilled' ? 'selected' : ''}>Grilled</option>
                    <option value="fried" ${preparationMethod === 'fried' ? 'selected' : ''}>Fried</option>
                    <option value="baked" ${preparationMethod === 'baked' ? 'selected' : ''}>Baked</option>
                </select>
            </div>
            <div class="col-md-2">
                <input type="number" class="form-control" name="ingredient_edible_portion" 
                       placeholder="Edible %" min="0.1" max="1" step="0.1" 
                       title="Edible portion (0.1-1.0)" value="${ediblePortion}">
            </div>
            <div class="col-md-2">
                <button type="button" class="btn btn-outline-danger btn-sm" 
                        onclick="this.parentElement.parentElement.remove()">
                    ×
                </button>
            </div>
        `;

        ingredientsList.appendChild(ingredientDiv);
    }


    async handleDishSubmit(event) {
        const form = event.target;
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        const spinner = submitBtn.querySelector('.spinner-border');

        try {
            // Collect ingredients
            const ingredients = [];
            const ingredientDivs = form.querySelectorAll('#ingredientsList .row');

            ingredientDivs.forEach(div => {
                const productId = div.querySelector('select[name="ingredient_product_id"]').value;
                const quantity = div.querySelector('input[name="ingredient_quantity"]').value;
                const preparationMethod = div.querySelector('select[name="ingredient_preparation_method"]').value;
                const ediblePortion = div.querySelector('input[name="ingredient_edible_portion"]').value;

                if (productId && quantity) {
                    ingredients.push({
                        product_id: parseInt(productId),
                        quantity_grams: parseFloat(quantity),
                        preparation_method: preparationMethod || 'raw',
                        edible_portion: parseFloat(ediblePortion) || 1.0
                    });
                }
            });

            const dishData = {
                name: formData.get('name'),
                description: formData.get('description') || '',
                ingredients: ingredients
            };

            const isEdit = form.dataset.editId;
            const url = isEdit ? `${this.apiBaseUrl}/dishes/${isEdit}` : `${this.apiBaseUrl}/dishes`;
            const method = isEdit ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(dishData)
            });

            const data = await response.json();

            if (response.ok) {
                if (window.showSuccess) {
                    showSuccess(data.message || (isEdit ? 'Dish updated successfully!' : 'Dish created successfully!'));
                }
                this.resetDishForm();
                await this.loadDishes();
            } else {
                if (window.showError) {
                    showError(data.message || (isEdit ? 'Failed to update dish' : 'Failed to create dish'));
                }
            }
        } catch (error) {
            console.error('Error creating dish:', error);
            if (window.showError) {
                showError('Failed to create dish');
            }
        } finally {
            if (spinner) {
                spinner.classList.add('d-none');
            }
            submitBtn.disabled = false;
        }
    }

    async handleLogSubmit(event) {
        const form = event.target;
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        const spinner = submitBtn.querySelector('.spinner-border');

        try {
            const logData = {
                date: formData.get('date'),
                item_type: formData.get('item_type'),
                item_id: parseInt(formData.get('item_id')),
                quantity_grams: parseInt(formData.get('quantity_grams')),
                meal_time: formData.get('meal_time') || null,
                notes: formData.get('notes') || null
            };

            const isEdit = form.dataset.editId;
            const url = isEdit ? `${this.apiBaseUrl}/log/${isEdit}` : `${this.apiBaseUrl}/log`;
            const method = isEdit ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(logData)
            });

            const data = await response.json();

            if (response.ok) {
                if (window.showSuccess) {
                    showSuccess(data.message || (isEdit ? 'Log entry updated successfully!' : 'Food logged successfully!'));
                }
                this.resetLogForm();
                await Promise.all([
                    this.loadLogEntries(),
                    this.loadStats()
                ]);
            } else {
                // Handle validation errors
                if (data.errors && data.errors.length > 0) {
                    const errorMessage = data.errors.join('\n• ');
                    if (window.showError) {
                        showError(`Validation failed:\n• ${errorMessage}`);
                    }
                } else {
                    throw new Error(data.message || (isEdit ? 'Failed to update log entry' : 'Failed to log food entry'));
                }
            }
        } catch (error) {
            console.error('Error logging food:', error);
            if (window.showError) {
                showError(error.message);
            }
        } finally {
            if (spinner) spinner.classList.add('d-none');
            submitBtn.disabled = false;
        }
    }

    async editProduct(productId) {
        try {
            // Get product data
            const response = await fetch(`${this.apiBaseUrl}/products/${productId}`);
            if (!response.ok) throw new Error('Failed to load product data');

            const data = await response.json();
            const product = data.data;

            // Fill the form with existing data
            const nameField = document.getElementById('productName');
            const caloriesField = document.getElementById('calories');
            const proteinField = document.getElementById('protein');
            const fatField = document.getElementById('fat');
            const carbsField = document.getElementById('carbs');
            // New fields according to NUTRIENTS.md
            const fiberField = document.getElementById('fiber');
            const sugarsField = document.getElementById('sugars');
            const categoryField = document.getElementById('category');
            const processingLevelField = document.getElementById('processing_level');
            const glycemicIndexField = document.getElementById('glycemic_index');
            const regionField = document.getElementById('region');

            if (!nameField || !caloriesField || !proteinField || !fatField || !carbsField) {
                throw new Error('Form fields not found');
            }

            nameField.value = product.name;
            proteinField.value = product.protein_per_100g;
            fatField.value = product.fat_per_100g;
            carbsField.value = product.carbs_per_100g;

            // Fill new fields if they exist
            if (fiberField) fiberField.value = product.fiber_per_100g || '';
            if (sugarsField) sugarsField.value = product.sugars_per_100g || '';
            if (categoryField) categoryField.value = product.category || '';
            if (processingLevelField) processingLevelField.value = product.processing_level || '';
            if (glycemicIndexField) glycemicIndexField.value = product.glycemic_index || '';
            if (regionField) regionField.value = product.region || 'US';

            // Calculate calories from macros (will be updated by event listener)
            this.updateCaloriesField();

            // Change form to edit mode
            const form = document.getElementById('productForm');
            if (!form) {
                throw new Error('Product form not found');
            }

            form.dataset.editId = productId;
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Update Product';
            }

            // Change form title
            const formTitle = document.getElementById('productFormTitle');
            if (formTitle) {
                formTitle.textContent = `Edit Product: ${product.name}`;
            }

            // Scroll to form
            form.scrollIntoView({ behavior: 'smooth' });

            if (window.showSuccess) {
                showSuccess('Product loaded for editing');
            }
        } catch (error) {
            console.error('Error loading product for edit:', error);
            if (window.showError) {
                showError('Failed to load product for editing: ' + error.message);
            }
        }
    }

    resetProductForm() {
        const form = document.getElementById('productForm');
        if (form) {
            form.reset();
            delete form.dataset.editId;

            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Add Product';
            }

            const formTitle = document.getElementById('productFormTitle');
            if (formTitle) {
                formTitle.textContent = 'Add New Product';
            }
        }
    }

    resetDishForm() {
        const form = document.getElementById('dishForm');
        if (form) {
            form.reset();
            delete form.dataset.editId;

            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Add Dish';
            }

            const formTitle = document.getElementById('dishFormTitle');
            if (formTitle) {
                formTitle.textContent = 'Add New Dish';
            }

            // Clear ingredients
            const ingredientsContainer = document.getElementById('ingredientsList');
            if (ingredientsContainer) {
                ingredientsContainer.innerHTML = '';
                this.addIngredientRow(); // Add one empty row
            }
        }
    }

    resetLogForm() {
        const form = document.getElementById('logForm');
        if (form) {
            form.reset();
            delete form.dataset.editId;

            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Log Food';
            }

            const formTitle = document.getElementById('logFormTitle');
            if (formTitle) {
                formTitle.textContent = 'Log Food Entry';
            }

            // Reset date to today
            document.getElementById('logDate').value = new Date().toISOString().split('T')[0];
            document.getElementById('logQuantity').value = 100;
        }
    }

    async editDish(dishId) {
        try {
            // Ensure products are loaded first
            if (!this.products || this.products.length === 0) {
                await this.loadProducts();
            }

            // Get dish data
            const response = await fetch(`${this.apiBaseUrl}/dishes/${dishId}`);
            if (!response.ok) throw new Error('Failed to load dish data');

            const data = await response.json();
            const dish = data.data;

            // Fill the form with existing data
            const nameField = document.getElementById('dishName');
            if (!nameField) {
                throw new Error('Dish name field not found');
            }

            nameField.value = dish.name;

            // Change form to edit mode
            const form = document.getElementById('dishForm');
            if (!form) {
                throw new Error('Dish form not found');
            }

            form.dataset.editId = dishId;
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Update Dish';
            }

            // Change form title
            const formTitle = document.getElementById('dishFormTitle');
            if (formTitle) {
                formTitle.textContent = `Edit Dish: ${dish.name}`;
            }

            // Clear existing ingredients
            const ingredientsContainer = document.getElementById('ingredientsList');
            if (ingredientsContainer) {
                ingredientsContainer.innerHTML = '';

                // Add existing ingredients
                if (dish.ingredients && dish.ingredients.length > 0) {
                    dish.ingredients.forEach(ingredient => {
                        this.addIngredientRow(
                            ingredient.product_id,
                            ingredient.quantity_grams,
                            ingredient.product_name,
                            ingredient.preparation_method || 'raw',
                            ingredient.edible_portion || 1.0
                        );
                    });
                } else {
                    // Add at least one empty row
                    this.addIngredientRow();
                }
            }

            // Scroll to form
            form.scrollIntoView({ behavior: 'smooth' });

            if (window.showSuccess) {
                showSuccess('Dish loaded for editing');
            }
        } catch (error) {
            console.error('Error loading dish for edit:', error);
            if (window.showError) {
                showError('Failed to load dish for editing: ' + error.message);
            }
        }
    }

    async editLogEntry(logId) {
        try {
            // Get log entry data
            const response = await fetch(`${this.apiBaseUrl}/log/${logId}`);
            if (!response.ok) throw new Error('Failed to load log entry data');

            const data = await response.json();
            const entry = data.data;

            // Fill the form with existing data
            const dateField = document.getElementById('logDate');
            const itemTypeField = document.getElementById('logItemType');
            const itemIdField = document.getElementById('logItem');
            const quantityField = document.getElementById('logQuantity');
            const mealTimeField = document.getElementById('logMealTime');
            const notesField = document.getElementById('logNotes');

            if (!dateField || !itemTypeField || !itemIdField || !quantityField || !mealTimeField) {
                throw new Error('Log form fields not found');
            }

            dateField.value = entry.date;
            itemTypeField.value = entry.item_type;
            itemIdField.value = entry.item_id;
            quantityField.value = entry.quantity_grams;
            mealTimeField.value = entry.meal_time;
            if (notesField) {
                notesField.value = entry.notes || '';
            }

            // Update item options based on type
            this.updateLogItemOptions(entry.item_type, entry.item_id);

            // Change form to edit mode
            const form = document.getElementById('logForm');
            if (!form) {
                throw new Error('Log form not found');
            }

            form.dataset.editId = logId;
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Update Entry';
            }

            // Change form title
            const formTitle = document.getElementById('logFormTitle');
            if (formTitle) {
                formTitle.textContent = `Edit Log Entry: ${entry.item_name}`;
            }

            // Scroll to form
            form.scrollIntoView({ behavior: 'smooth' });

            if (window.showSuccess) {
                showSuccess('Log entry loaded for editing');
            }
        } catch (error) {
            console.error('Error loading log entry for edit:', error);
            if (window.showError) {
                showError('Failed to load log entry for editing: ' + error.message);
            }
        }
    }

    async deleteDish(dishId) {
        if (!confirm('Are you sure you want to delete this dish?')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/dishes/${dishId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (response.ok) {
                if (window.showSuccess) {
                    showSuccess(data.message || 'Dish deleted successfully!');
                }
                await this.loadDishes();
            } else {
                throw new Error(data.message || 'Failed to delete dish');
            }
        } catch (error) {
            console.error('Error deleting dish:', error);
            if (window.showError) {
                showError(error.message);
            }
        }
    }

    async deleteLogEntry(entryId) {
        if (!confirm('Are you sure you want to delete this log entry?')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/log/${entryId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (response.ok) {
                if (window.showSuccess) {
                    showSuccess(data.message || 'Log entry deleted successfully!');
                }
                await Promise.all([
                    this.loadLogEntries(),
                    this.loadStats()
                ]);
            } else {
                throw new Error(data.message || 'Failed to delete log entry');
            }
        } catch (error) {
            console.error('Error deleting log entry:', error);
            if (window.showError) {
                showError(error.message);
            }
        }
    }

    updateItemOptions(itemType) {
        const itemSelect = document.getElementById('logItem');
        if (!itemSelect) return;

        itemSelect.innerHTML = '<option value="">Select item</option>';

        if (itemType === 'product') {
            this.products.forEach(product => {
                const option = document.createElement('option');
                option.value = product.id;
                option.textContent = product.name;
                itemSelect.appendChild(option);
            });
        } else if (itemType === 'dish') {
            this.dishes.forEach(dish => {
                const option = document.createElement('option');
                option.value = dish.id;
                option.textContent = dish.name;
                itemSelect.appendChild(option);
            });
        }
    }

    updateProductOptions() {
        // Update product options in ingredient selects
        document.querySelectorAll('.ingredient-product-select').forEach(select => {
            const currentValue = select.value;
            select.innerHTML = '<option value="">Select product</option>';

            this.products.forEach(product => {
                const option = document.createElement('option');
                option.value = product.id;
                option.textContent = product.name;
                if (product.id == currentValue) {
                    option.selected = true;
                }
                select.appendChild(option);
            });
        });
    }

    updateDishOptions() {
        // Update dish options in log form
        const dishSelects = document.querySelectorAll('select[name="dish_item_id"]');
        dishSelects.forEach(select => {
            const currentValue = select.value;
            select.innerHTML = '<option value="">Select Dish</option>';

            this.dishes.forEach(dish => {
                const option = document.createElement('option');
                option.value = dish.id;
                option.textContent = dish.name;
                if (dish.id == currentValue) {
                    option.selected = true;
                }
                select.appendChild(option);
            });
        });
    }

    updateLogItemOptions(itemType, selectedId = null) {
        // Update item options in log form based on type
        const itemSelect = document.getElementById('logItem');
        if (!itemSelect) return;

        itemSelect.innerHTML = '<option value="">Select Item</option>';

        if (itemType === 'product') {
            this.products.forEach(product => {
                const option = document.createElement('option');
                option.value = product.id;
                option.textContent = product.name;
                if (selectedId && product.id == selectedId) {
                    option.selected = true;
                }
                itemSelect.appendChild(option);
            });
        } else if (itemType === 'dish') {
            this.dishes.forEach(dish => {
                const option = document.createElement('option');
                option.value = dish.id;
                option.textContent = dish.name;
                if (selectedId && dish.id == selectedId) {
                    option.selected = true;
                }
                itemSelect.appendChild(option);
            });
        }
    }

    searchProducts(searchTerm) {
        const tbody = document.getElementById('productsTableBody');
        if (!tbody) return;

        const rows = tbody.querySelectorAll('tr');
        const term = searchTerm.toLowerCase();

        rows.forEach(row => {
            const productName = row.querySelector('td:first-child').textContent.toLowerCase();
            const matches = productName.includes(term);
            row.style.display = matches ? '' : 'none';
        });
    }

    filterLogEntries(date) {
        this.loadLogEntries(date);
    }

    onTabSwitch(tabId) {
        // Handle tab-specific logic
        switch (tabId) {
            case 'stats':
                this.loadStats();
                break;
            case 'log':
                this.loadLogEntries();
                break;
        }
    }

    // Utility functions - updated according to NUTRIENTS.md
    calculateKetoIndex(fat, protein, carbs, fiber = null, category = null, glycemicIndex = null) {
        // Frontend uses simplified calculation - backend does advanced calculations
        // This is only for display purposes when backend data is not available

        const denominator = protein + carbs;
        if (denominator === 0) {
            return fat === 0 ? 0 : 99.9;
        }

        // Basic keto index calculation (backend does advanced version with weights)
        const basicKetoIndex = (fat * 2) / denominator;

        // Apply basic adjustments based on available data
        let adjustedIndex = basicKetoIndex;

        if (fiber && carbs > 0) {
            const netCarbs = Math.max(0, carbs - fiber);
            const netCarbsRatio = netCarbs / carbs;
            adjustedIndex *= netCarbsRatio;
        }

        if (glycemicIndex && glycemicIndex > 50) {
            adjustedIndex *= 0.8; // Penalty for high GI
        }

        return Math.round(adjustedIndex * 100) / 100;
    }

    getKetoRating(ketoIndex) {
        // Updated according to NUTRIENTS.md categories
        if (ketoIndex >= 90) return 'excellent';  // Идеально для кето
        if (ketoIndex >= 80) return 'excellent';  // Отлично для кето
        if (ketoIndex >= 70) return 'good';       // Хорошо для кето
        if (ketoIndex >= 60) return 'moderate';    // Умеренно подходит
        if (ketoIndex >= 40) return 'limited';     // Ограниченно
        if (ketoIndex >= 20) return 'avoid';       // Избегать
        return 'poor';                             // Исключить
    }

    getKetoBadgeClass(rating) {
        switch (rating) {
            case 'excellent': return 'success';
            case 'good': return 'success';
            case 'moderate': return 'warning';
            case 'limited': return 'warning';
            case 'avoid': return 'danger';
            case 'poor': return 'danger';
            default: return 'secondary';
        }
    }

    getMealEmoji(mealTime) {
        const emojis = {
            'breakfast': '🌅',
            'lunch': '☀️',
            'dinner': '🌙',
            'snack': '🍎'
        };
        return emojis[mealTime] || '🍽️';
    }

    // Auto-calculate calories from macros using Atwater system (NUTRIENTS.md)
    calculateCaloriesFromMacros(protein, fat, carbs) {
        // Using Atwater system: Protein=4, Fat=9, Carbs=4 kcal/g
        // According to NUTRIENTS.md - система Этуотера
        return (protein * 4.0) + (fat * 9.0) + (carbs * 4.0);
    }

    // Update calories field when macros change
    updateCaloriesField() {
        const proteinInput = document.getElementById('protein');
        const fatInput = document.getElementById('fat');
        const carbsInput = document.getElementById('carbs');
        const caloriesInput = document.getElementById('calories');

        if (proteinInput && fatInput && carbsInput && caloriesInput) {
            const protein = parseFloat(proteinInput.value) || 0;
            const fat = parseFloat(fatInput.value) || 0;
            const carbs = parseFloat(carbsInput.value) || 0;

            const calories = this.calculateCaloriesFromMacros(protein, fat, carbs);
            caloriesInput.value = calories.toFixed(1);
        }
    }

    // Setup auto-calculation for product form
    setupProductFormAutoCalculation() {
        const proteinInput = document.getElementById('protein');
        const fatInput = document.getElementById('fat');
        const carbsInput = document.getElementById('carbs');

        if (proteinInput && fatInput && carbsInput) {
            // Add event listeners to all macro inputs
            [proteinInput, fatInput, carbsInput].forEach(input => {
                input.addEventListener('input', () => this.updateCaloriesField());
                input.addEventListener('change', () => this.updateCaloriesField());
            });

            // Calculate initial value
            this.updateCaloriesField();
        }
    }

    calculateEntryCalories(entry) {
        // Debug logging
        console.log('calculateEntryCalories called with:', {
            item_name: entry.item_name,
            calories: entry.calories,
            calories_per_100g: entry.calories_per_100g,
            quantity_grams: entry.quantity_grams,
            item_type: entry.item_type
        });
        
        // Use the calories already calculated by the server
        if (entry.calories !== undefined && entry.calories !== null) {
            console.log('Using server calories:', entry.calories);
            return Math.round(entry.calories);
        }
        
        // Fallback calculation if server data is missing
        if (entry.item_type === 'product') {
            const calculated = Math.round((entry.calories_per_100g || 0) * entry.quantity_grams / 100);
            console.log('Fallback calculation for product:', calculated);
            return calculated;
        } else if (entry.item_type === 'dish') {
            const calculated = Math.round(entry.calculated_calories || 0);
            console.log('Fallback calculation for dish:', calculated);
            return calculated;
        }
        return 0;
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, function (m) { return map[m]; });
    }
}

// Initialize the app
window.NutritionApp = new NutritionTracker();

// Export for global access
window.app = window.NutritionApp;

