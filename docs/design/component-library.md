# 📦 Component Library

**Version:** 1.0.0  
**Last Updated:** October 23, 2025  
**Status:** ✅ Production Ready

## 📋 Overview

This document catalogs all reusable UI components in Nutricount. Each component includes HTML structure, CSS classes, JavaScript interactions, and usage examples.

## Component Categories

1. [Buttons](#buttons)
2. [Cards](#cards)
3. [Forms](#forms)
4. [Navigation](#navigation)
5. [Modals](#modals)
6. [Alerts & Notifications](#alerts--notifications)
7. [Progress & Loading](#progress--loading)
8. [Data Display](#data-display)
9. [Layout](#layout)

---

## Buttons

### Primary Button

**Purpose:** Main call-to-action  
**Usage:** Submit forms, primary actions

```html
<button type="button" class="btn btn-primary">
    Primary Action
</button>
```

**Variants:**
```html
<!-- Large -->
<button class="btn btn-primary btn-lg">Large Button</button>

<!-- Small -->
<button class="btn btn-primary btn-sm">Small Button</button>

<!-- Full width -->
<button class="btn btn-primary w-100">Full Width</button>

<!-- Disabled -->
<button class="btn btn-primary" disabled>Disabled</button>

<!-- With icon -->
<button class="btn btn-primary">
    <i class="bi bi-plus-circle"></i> Add Product
</button>
```

**States:**
- **Default:** `btn btn-primary`
- **Hover:** Elevated shadow, slight translate
- **Active:** Scale down effect
- **Disabled:** Reduced opacity, no interaction

### Secondary Button

**Purpose:** Secondary actions  
**Usage:** Cancel, close, alternative actions

```html
<button type="button" class="btn btn-secondary">
    Secondary Action
</button>
```

### Outline Button

**Purpose:** Less prominent actions  
**Usage:** Tertiary actions, alternative options

```html
<button type="button" class="btn btn-outline-primary">
    Outline Button
</button>
```

### Danger Button

**Purpose:** Destructive actions  
**Usage:** Delete, remove, irreversible actions

```html
<button type="button" class="btn btn-danger">
    <i class="bi bi-trash"></i> Delete
</button>
```

### Button Group

**Purpose:** Related actions grouped together

```html
<div class="btn-group" role="group">
    <button type="button" class="btn btn-primary">Left</button>
    <button type="button" class="btn btn-primary">Middle</button>
    <button type="button" class="btn btn-primary">Right</button>
</div>
```

---

## Cards

### Standard Card

**Purpose:** Container for related content  
**Usage:** Products, dishes, statistics

```html
<div class="card">
    <div class="card-header">
        <h5 class="card-title mb-0">Card Title</h5>
    </div>
    <div class="card-body">
        <p class="card-text">Card content goes here.</p>
    </div>
    <div class="card-footer text-end">
        <button class="btn btn-primary btn-sm">Action</button>
    </div>
</div>
```

**CSS:**
```css
.card {
    border-radius: 1rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: var(--transition-smooth);
}

.card:hover {
    box-shadow: var(--shadow-hover);
    transform: translateY(-2px);
}
```

### Target Card

**Purpose:** Display personal targets/goals  
**Usage:** Daily targets, macro goals

```html
<div class="target-item target-item-primary">
    <div class="target-value">2000</div>
    <div class="target-label">Calories</div>
    <div class="target-description">Daily target</div>
</div>
```

**CSS:**
```css
.target-item {
    text-align: center;
    padding: 1rem;
    background: rgba(var(--bs-white-rgb), 0.7);
    border-radius: 0.75rem;
    transition: var(--transition-smooth);
}

.target-item:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-hover);
}

.target-item-primary {
    background: linear-gradient(135deg, 
        rgba(var(--bs-primary-rgb), 0.1) 0%, 
        rgba(var(--bs-primary-rgb), 0.05) 100%);
}
```

### Macro Card

**Purpose:** Display macronutrient information  
**Usage:** Protein, fat, carbs display

```html
<div class="macro-target">
    <div class="macro-label">Protein</div>
    <div class="macro-value">150g</div>
</div>
```

---

## Forms

### Text Input

**Purpose:** Single-line text entry  
**Usage:** Name, description, search

```html
<div class="mb-3">
    <label for="productName" class="form-label">
        Product Name <span class="text-danger">*</span>
    </label>
    <input type="text" 
           class="form-control" 
           id="productName"
           name="name"
           placeholder="e.g., Chicken Breast"
           required
           aria-required="true">
    <div class="form-text">Enter the name of the product</div>
</div>
```

**Validation States:**
```html
<!-- Valid -->
<input type="text" class="form-control is-valid">
<div class="valid-feedback">Looks good!</div>

<!-- Invalid -->
<input type="text" class="form-control is-invalid">
<div class="invalid-feedback">Please provide a valid input.</div>
```

### Number Input

**Purpose:** Numeric values  
**Usage:** Weight, calories, macros

```html
<div class="mb-3">
    <label for="calories" class="form-label">Calories</label>
    <input type="number" 
           class="form-control" 
           id="calories"
           min="0"
           step="1"
           inputmode="decimal"
           placeholder="0">
</div>
```

### Select Dropdown

**Purpose:** Choose from predefined options  
**Usage:** Categories, meal times, fasting types

```html
<div class="mb-3">
    <label for="category" class="form-label">Category</label>
    <select class="form-select" id="category" required>
        <option value="">Choose...</option>
        <option value="meat">Meat & Poultry</option>
        <option value="dairy">Dairy</option>
        <option value="vegetables">Vegetables</option>
        <option value="grains">Grains</option>
    </select>
</div>
```

### Checkbox

**Purpose:** Boolean choice  
**Usage:** Enable/disable features, agree to terms

```html
<div class="form-check">
    <input class="form-check-input" 
           type="checkbox" 
           id="ketoFilter"
           value="keto">
    <label class="form-check-label" for="ketoFilter">
        Show only keto-friendly products
    </label>
</div>
```

### Radio Buttons

**Purpose:** Choose one from multiple options  
**Usage:** Fasting type, activity level

```html
<div class="mb-3">
    <label class="form-label">Fasting Type</label>
    
    <div class="form-check">
        <input class="form-check-input" type="radio" name="fastingType" 
               id="fasting16" value="16:8" checked>
        <label class="form-check-label" for="fasting16">
            16:8 (16 hours fasting)
        </label>
    </div>
    
    <div class="form-check">
        <input class="form-check-input" type="radio" name="fastingType" 
               id="fasting18" value="18:6">
        <label class="form-check-label" for="fasting18">
            18:6 (18 hours fasting)
        </label>
    </div>
</div>
```

### Form Layout

**Purpose:** Organize form fields  
**Usage:** Product creation, profile editing

```html
<form>
    <!-- Row with 2 columns -->
    <div class="row">
        <div class="col-md-6 mb-3">
            <label for="protein" class="form-label">Protein (g)</label>
            <input type="number" class="form-control" id="protein">
        </div>
        <div class="col-md-6 mb-3">
            <label for="fat" class="form-label">Fat (g)</label>
            <input type="number" class="form-control" id="fat">
        </div>
    </div>
    
    <!-- Actions -->
    <div class="d-flex justify-content-end gap-2">
        <button type="button" class="btn btn-secondary">Cancel</button>
        <button type="submit" class="btn btn-primary">Save</button>
    </div>
</form>
```

---

## Navigation

### Tab Navigation

**Purpose:** Switch between content sections  
**Usage:** Main app navigation (Products, Dishes, Log, Stats)

```html
<ul class="nav nav-tabs" role="tablist">
    <li class="nav-item" role="presentation">
        <button class="nav-link active" 
                id="products-tab" 
                data-bs-toggle="tab" 
                data-bs-target="#products-pane"
                type="button" 
                role="tab" 
                aria-controls="products-pane" 
                aria-selected="true">
            <i class="bi bi-basket"></i> Products
        </button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" 
                id="dishes-tab" 
                data-bs-toggle="tab" 
                data-bs-target="#dishes-pane"
                type="button" 
                role="tab" 
                aria-controls="dishes-pane" 
                aria-selected="false">
            <i class="bi bi-egg-fried"></i> Dishes
        </button>
    </li>
</ul>

<div class="tab-content" id="mainTabContent">
    <div class="tab-pane fade show active" 
         id="products-pane" 
         role="tabpanel" 
         aria-labelledby="products-tab">
        <!-- Products content -->
    </div>
    <div class="tab-pane fade" 
         id="dishes-pane" 
         role="tabpanel" 
         aria-labelledby="dishes-tab">
        <!-- Dishes content -->
    </div>
</div>
```

**Mobile Optimization:**
```css
.nav-tabs {
    overflow-x: auto;
    flex-wrap: nowrap;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
}

.nav-tabs::-webkit-scrollbar {
    display: none;
}

.nav-link {
    white-space: nowrap;
}
```

### Breadcrumbs

**Purpose:** Show navigation hierarchy  
**Usage:** Admin panel, settings

```html
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="/">Home</a></li>
        <li class="breadcrumb-item"><a href="/products">Products</a></li>
        <li class="breadcrumb-item active" aria-current="page">Edit</li>
    </ol>
</nav>
```

---

## Modals

### Standard Modal

**Purpose:** Display content in overlay  
**Usage:** Forms, confirmations, details

```html
<div class="modal fade" id="productModal" tabindex="-1" 
     aria-labelledby="productModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="productModalLabel">
                    Add Product
                </h5>
                <button type="button" class="btn-close" 
                        data-bs-dismiss="modal" 
                        aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <!-- Form or content -->
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" 
                        data-bs-dismiss="modal">
                    Cancel
                </button>
                <button type="button" class="btn btn-primary">
                    Save Changes
                </button>
            </div>
        </div>
    </div>
</div>
```

**Trigger:**
```html
<button type="button" class="btn btn-primary" 
        data-bs-toggle="modal" 
        data-bs-target="#productModal">
    Open Modal
</button>
```

### Confirmation Modal

**Purpose:** Confirm destructive actions  
**Usage:** Delete confirmations

```html
<div class="modal fade" id="confirmDelete">
    <div class="modal-dialog modal-dialog-centered modal-sm">
        <div class="modal-content">
            <div class="modal-header border-0">
                <h5 class="modal-title">Confirm Delete</h5>
                <button type="button" class="btn-close" 
                        data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <p>Are you sure you want to delete this product?</p>
                <p class="text-muted small">This action cannot be undone.</p>
            </div>
            <div class="modal-footer border-0">
                <button type="button" class="btn btn-secondary btn-sm" 
                        data-bs-dismiss="modal">
                    Cancel
                </button>
                <button type="button" class="btn btn-danger btn-sm" 
                        id="confirmDeleteBtn">
                    <i class="bi bi-trash"></i> Delete
                </button>
            </div>
        </div>
    </div>
</div>
```

---

## Alerts & Notifications

### Alert

**Purpose:** Display important messages  
**Usage:** Success, errors, warnings

```html
<!-- Success -->
<div class="alert alert-success" role="alert">
    <i class="bi bi-check-circle"></i>
    <strong>Success!</strong> Product created successfully.
</div>

<!-- Error -->
<div class="alert alert-danger" role="alert">
    <i class="bi bi-exclamation-triangle"></i>
    <strong>Error!</strong> Please fill in all required fields.
</div>

<!-- Warning -->
<div class="alert alert-warning" role="alert">
    <i class="bi bi-exclamation-circle"></i>
    <strong>Warning!</strong> Database backup recommended.
</div>

<!-- Info -->
<div class="alert alert-info" role="alert">
    <i class="bi bi-info-circle"></i>
    <strong>Note:</strong> Your data is stored locally.
</div>
```

**Dismissible:**
```html
<div class="alert alert-success alert-dismissible fade show" role="alert">
    Product saved successfully!
    <button type="button" class="btn-close" 
            data-bs-dismiss="alert" 
            aria-label="Close"></button>
</div>
```

### Toast Notification

**Purpose:** Brief, non-intrusive message  
**Usage:** Auto-dismissing notifications

```html
<div class="toast-container position-fixed top-0 end-0 p-3">
    <div class="toast" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="toast-header">
            <i class="bi bi-check-circle text-success me-2"></i>
            <strong class="me-auto">Success</strong>
            <small>Just now</small>
            <button type="button" class="btn-close" 
                    data-bs-dismiss="toast" 
                    aria-label="Close"></button>
        </div>
        <div class="toast-body">
            Product created successfully!
        </div>
    </div>
</div>
```

**JavaScript:**
```javascript
// Show toast
const toast = new bootstrap.Toast(document.getElementById('myToast'));
toast.show();
```

---

## Progress & Loading

### Progress Bar

**Purpose:** Show completion percentage  
**Usage:** Fasting progress, goal progress

```html
<!-- Standard -->
<div class="progress">
    <div class="progress-bar" 
         role="progressbar" 
         style="width: 75%"
         aria-valuenow="75" 
         aria-valuemin="0" 
         aria-valuemax="100">
        75%
    </div>
</div>

<!-- Success color -->
<div class="progress">
    <div class="progress-bar bg-success" style="width: 100%">
        Complete
    </div>
</div>

<!-- Multiple values -->
<div class="progress">
    <div class="progress-bar bg-success" style="width: 33%">Protein</div>
    <div class="progress-bar bg-warning" style="width: 33%">Fat</div>
    <div class="progress-bar bg-info" style="width: 34%">Carbs</div>
</div>
```

### Spinner

**Purpose:** Indicate loading state  
**Usage:** API requests, data loading

```html
<!-- Standard spinner -->
<div class="spinner-border" role="status">
    <span class="visually-hidden">Loading...</span>
</div>

<!-- Small spinner -->
<div class="spinner-border spinner-border-sm" role="status">
    <span class="visually-hidden">Loading...</span>
</div>

<!-- Spinner in button -->
<button class="btn btn-primary" type="button" disabled>
    <span class="spinner-border spinner-border-sm me-2" 
          role="status" 
          aria-hidden="true"></span>
    Loading...
</button>
```

---

## Data Display

### Badge

**Purpose:** Label or count indicator  
**Usage:** Tags, categories, counts

```html
<!-- Standard badges -->
<span class="badge bg-primary">Primary</span>
<span class="badge bg-success">Keto-Friendly</span>
<span class="badge bg-danger">High Carb</span>

<!-- Pill shape -->
<span class="badge rounded-pill bg-primary">14</span>

<!-- In button -->
<button class="btn btn-primary">
    Notifications <span class="badge bg-light text-dark">4</span>
</button>
```

### Table

**Purpose:** Display tabular data  
**Usage:** Product lists, log entries

```html
<div class="table-responsive">
    <table class="table table-hover">
        <thead>
            <tr>
                <th scope="col">Product</th>
                <th scope="col">Protein</th>
                <th scope="col">Fat</th>
                <th scope="col">Carbs</th>
                <th scope="col">Actions</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Chicken Breast</td>
                <td>31g</td>
                <td>3.6g</td>
                <td>0g</td>
                <td>
                    <button class="btn btn-sm btn-primary">Edit</button>
                    <button class="btn btn-sm btn-danger">Delete</button>
                </td>
            </tr>
        </tbody>
    </table>
</div>
```

### List Group

**Purpose:** Display list of items  
**Usage:** Navigation, selections

```html
<ul class="list-group">
    <li class="list-group-item">
        <i class="bi bi-check-circle text-success"></i> Item 1
    </li>
    <li class="list-group-item active" aria-current="true">
        <i class="bi bi-star-fill"></i> Active Item
    </li>
    <li class="list-group-item">Item 3</li>
</ul>
```

---

## Layout

### Container

**Purpose:** Main content container  
**Usage:** Wrap page content

```html
<div class="container">
    <!-- Fixed width container -->
</div>

<div class="container-fluid">
    <!-- Full width container -->
</div>
```

### Grid System

**Purpose:** Responsive columns  
**Usage:** Forms, cards, statistics

```html
<div class="row">
    <!-- 2 columns on tablet+, 1 on mobile -->
    <div class="col-12 col-md-6">
        Column 1
    </div>
    <div class="col-12 col-md-6">
        Column 2
    </div>
</div>

<!-- 4 columns on desktop, 2 on tablet, 1 on mobile -->
<div class="row">
    <div class="col-12 col-md-6 col-lg-3">Column 1</div>
    <div class="col-12 col-md-6 col-lg-3">Column 2</div>
    <div class="col-12 col-md-6 col-lg-3">Column 3</div>
    <div class="col-12 col-md-6 col-lg-3">Column 4</div>
</div>
```

### Spacing Utilities

**Purpose:** Add margin/padding  
**Usage:** Consistent spacing

```html
<!-- Margin -->
<div class="mb-3">Margin bottom 1rem</div>
<div class="mt-5">Margin top 3rem</div>

<!-- Padding -->
<div class="p-3">Padding 1rem all sides</div>
<div class="py-2">Padding 0.5rem top/bottom</div>

<!-- Gap in flex/grid -->
<div class="d-flex gap-3">
    <div>Item 1</div>
    <div>Item 2</div>
</div>
```

---

## Accessibility Guidelines

### Focus Management

```css
:focus-visible {
    outline: 2px solid var(--bs-primary);
    outline-offset: 2px;
}
```

### ARIA Labels

```html
<!-- Buttons with icons -->
<button aria-label="Close" class="btn-close"></button>

<!-- Form inputs -->
<input type="text" id="search" aria-label="Search products">

<!-- Loading states -->
<div role="status" aria-live="polite">
    <span class="spinner-border"></span>
    <span class="visually-hidden">Loading...</span>
</div>
```

### Semantic HTML

```html
<!-- Use proper heading hierarchy -->
<h1>Main Title</h1>
<h2>Section</h2>
<h3>Subsection</h3>

<!-- Use semantic elements -->
<nav>Navigation</nav>
<main>Main content</main>
<article>Article content</article>
<aside>Sidebar</aside>
```

---

## Component Usage Best Practices

### 1. Consistent Sizing

```html
<!-- Use Bootstrap size classes -->
<button class="btn btn-lg">Large</button>
<button class="btn">Default</button>
<button class="btn btn-sm">Small</button>
```

### 2. Proper Spacing

```html
<!-- Use spacing utilities -->
<div class="mb-3">Form group</div>
<div class="d-flex gap-2">Buttons with gap</div>
```

### 3. Responsive Design

```html
<!-- Hide on mobile, show on tablet+ -->
<div class="d-none d-md-block">Desktop only</div>

<!-- Full width on mobile, half on desktop -->
<div class="col-12 col-lg-6">Responsive column</div>
```

### 4. Accessibility

```html
<!-- Always include labels -->
<label for="input">Label</label>
<input id="input" type="text">

<!-- Use ARIA when needed -->
<button aria-label="Close modal" class="btn-close"></button>

<!-- Proper roles -->
<div role="alert">Important message</div>
```

---

## References

- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)
- [Bootstrap Icons](https://icons.getbootstrap.com/)
- [Design System](design-system.md)
- [Accessibility Checklist](accessibility-checklist.md)

---

**Maintained by:** Nutricount Frontend Team  
**Last Updated:** October 23, 2025  
**Contact:** See [CONTRIBUTING.md](../../CONTRIBUTING.md)
