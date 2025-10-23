# 🎨 Nutricount Design System

**Version:** 1.0.0  
**Last Updated:** October 23, 2025  
**Status:** ✅ Complete

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Design Principles](#design-principles)
3. [Color System](#color-system)
4. [Typography](#typography)
5. [Spacing System](#spacing-system)
6. [Components](#components)
7. [Layout Patterns](#layout-patterns)
8. [Responsive Design](#responsive-design)
9. [Theming](#theming)
10. [Accessibility](#accessibility)

---

## Introduction

The Nutricount Design System provides a comprehensive set of design guidelines, components, and patterns to ensure consistency across the application. Built with Bootstrap 5 and custom CSS, it emphasizes accessibility, responsiveness, and user experience.

### Goals

- **Consistency:** Unified look and feel across all pages
- **Accessibility:** WCAG 2.2 AA compliance
- **Responsiveness:** Mobile-first design approach
- **Maintainability:** Clear documentation and reusable components
- **Performance:** Optimized CSS with minimal overhead

### Tech Stack

- **Framework:** Bootstrap 5.3+
- **Custom CSS:** `final-polish.css`, `responsive.css`
- **Icons:** Bootstrap Icons
- **Fonts:** System font stack (optimal performance)

---

## Design Principles

### 1. Mobile-First Approach
Start with mobile design and progressively enhance for larger screens.

```css
/* Mobile first - base styles */
.component { ... }

/* Tablet */
@media (min-width: 768px) { ... }

/* Desktop */
@media (min-width: 992px) { ... }
```

### 2. Progressive Enhancement
Core functionality works without JavaScript, enhanced experience with JS enabled.

### 3. Content-First Design
Focus on content hierarchy and readability before visual embellishments.

### 4. Performance Optimization
- Minimal CSS footprint (~1,000 lines total)
- CSS custom properties for theming
- Hardware-accelerated animations

### 5. Accessibility First
- Semantic HTML
- ARIA labels where needed
- Keyboard navigation support
- Screen reader friendly

---

## Color System

### Primary Palette

```css
:root {
    /* Primary Colors */
    --bs-primary: #667eea;          /* Primary action color */
    --bs-primary-rgb: 102, 126, 234;
    
    /* Secondary Colors */
    --bs-secondary: #6c757d;        /* Secondary elements */
    --bs-success: #56ab2f;          /* Success states */
    --bs-danger: #dc3545;           /* Error states */
    --bs-warning: #ffc107;          /* Warning states */
    --bs-info: #0dcaf0;             /* Info states */
    
    /* Neutral Colors */
    --bs-dark: #212529;             /* Text, headers */
    --bs-light: #f8f9fa;            /* Backgrounds */
    --bs-white: #ffffff;            /* Cards, containers */
}
```

### Gradients

```css
:root {
    --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --success-gradient: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
    --warning-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}
```

### Dark Theme

```css
[data-theme="dark"] {
    --bs-body-bg: #1a1a1a;          /* Dark background */
    --bs-body-color: #e0e0e0;       /* Light text */
    --bs-card-bg: #2d2d2d;          /* Card background */
    --bs-border-color: #404040;     /* Border color */
    --shadow-hover: 0 8px 25px rgba(0, 0, 0, 0.4);
}
```

### Color Usage Guidelines

| Color | Use Case | Example |
|-------|----------|---------|
| Primary | CTAs, links, active states | Submit buttons, navigation |
| Success | Positive feedback, completion | Success messages, checkmarks |
| Danger | Errors, destructive actions | Delete buttons, error messages |
| Warning | Cautions, alerts | Warning notices |
| Info | Informational content | Tips, help text |

---

## Typography

### Font Stack

```css
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
                 "Helvetica Neue", Arial, sans-serif;
}
```

**Rationale:** System fonts provide optimal performance and native feel on each platform.

### Type Scale

| Level | Size | Weight | Usage |
|-------|------|--------|-------|
| **H1** | 2.5rem (40px) | 700 | Page titles |
| **H2** | 2rem (32px) | 600 | Section headers |
| **H3** | 1.75rem (28px) | 600 | Subsection headers |
| **H4** | 1.5rem (24px) | 600 | Card titles |
| **H5** | 1.25rem (20px) | 600 | Small headings |
| **Body** | 1rem (16px) | 400 | Body text |
| **Small** | 0.875rem (14px) | 400 | Helper text |
| **Tiny** | 0.75rem (12px) | 400 | Labels, captions |

### Font Weights

```css
:root {
    --font-weight-light: 300;
    --font-weight-normal: 400;
    --font-weight-medium: 500;
    --font-weight-semibold: 600;
    --font-weight-bold: 700;
}
```

### Line Heights

```css
body {
    line-height: 1.6;  /* Body text */
}

h1, h2, h3, h4, h5, h6 {
    line-height: 1.2;  /* Headings */
}

.small-text {
    line-height: 1.4;  /* Helper text */
}
```

---

## Spacing System

### Spacing Scale (8px base unit)

```css
:root {
    --spacing-xs: 0.25rem;  /* 4px */
    --spacing-sm: 0.5rem;   /* 8px */
    --spacing-md: 1rem;     /* 16px */
    --spacing-lg: 1.5rem;   /* 24px */
    --spacing-xl: 2rem;     /* 32px */
    --spacing-2xl: 3rem;    /* 48px */
    --spacing-3xl: 4rem;    /* 64px */
}
```

### Margin & Padding Utilities

Bootstrap spacing utilities + custom:
- `.m-{size}` - Margin (all sides)
- `.mt-{size}`, `.mb-{size}` - Margin top/bottom
- `.p-{size}` - Padding (all sides)
- `.pt-{size}`, `.pb-{size}` - Padding top/bottom

Sizes: 0, 1 (4px), 2 (8px), 3 (16px), 4 (24px), 5 (48px)

---

## Components

### Buttons

#### Primary Button
```html
<button class="btn btn-primary">Primary Action</button>
```

**Styles:**
- Background: Primary gradient
- Hover: Elevated shadow
- Active: Slight scale-down
- Disabled: Reduced opacity

#### Variants

```html
<button class="btn btn-success">Success</button>
<button class="btn btn-danger">Delete</button>
<button class="btn btn-outline-primary">Secondary</button>
```

### Cards

#### Standard Card
```html
<div class="card">
    <div class="card-header">
        <h5 class="card-title">Title</h5>
    </div>
    <div class="card-body">
        Content
    </div>
</div>
```

**Styles:**
- Border-radius: 1rem (16px)
- Shadow: `0 2px 8px rgba(0,0,0,0.1)`
- Hover: Elevated shadow
- Padding: 1.5rem (24px)

#### Card Variants

```html
<div class="card target-item">...</div>          <!-- Target card -->
<div class="card target-item-primary">...</div>  <!-- Primary target -->
```

### Forms

#### Input Fields
```html
<div class="mb-3">
    <label for="input" class="form-label">Label</label>
    <input type="text" class="form-control" id="input">
</div>
```

**Styles:**
- Border-radius: 0.5rem (8px)
- Border: 1px solid #dee2e6
- Focus: Primary color border + shadow
- Invalid: Danger color border + message

#### Select Dropdowns
```html
<select class="form-select">
    <option>Option 1</option>
</select>
```

### Navigation

#### Tab Navigation
```html
<ul class="nav nav-tabs" role="tablist">
    <li class="nav-item">
        <button class="nav-link active" data-bs-toggle="tab">Tab 1</button>
    </li>
</ul>
```

**Styles:**
- Active: Primary color + bottom border
- Hover: Light background
- Transition: Smooth 0.3s

### Progress Bars

```html
<div class="progress">
    <div class="progress-bar" style="width: 75%">75%</div>
</div>
```

**Styles:**
- Height: 1.5rem (24px)
- Border-radius: 1rem (16px)
- Animated: Optional striped animation

### Modals

```html
<div class="modal fade" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Title</h5>
                <button type="button" class="btn-close"></button>
            </div>
            <div class="modal-body">...</div>
            <div class="modal-footer">...</div>
        </div>
    </div>
</div>
```

---

## Layout Patterns

### Grid System

Bootstrap 12-column grid:
```html
<div class="row">
    <div class="col-12 col-md-6 col-lg-4">Column</div>
</div>
```

### Container Widths

```css
.container {
    max-width: 1140px;  /* Desktop */
}

@media (min-width: 1400px) {
    .container {
        max-width: 1320px;  /* Extra large */
    }
}
```

### Custom Grids

#### Personal Targets Grid
```css
.personal-targets-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 1rem;
}
```

#### Macro Targets Grid
```css
.macro-targets {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 0.75rem;
}
```

---

## Responsive Design

### Breakpoints

```css
/* Bootstrap breakpoints */
--breakpoint-xs: 0;       /* Extra small (default) */
--breakpoint-sm: 576px;   /* Small devices */
--breakpoint-md: 768px;   /* Medium devices */
--breakpoint-lg: 992px;   /* Large devices */
--breakpoint-xl: 1200px;  /* Extra large */
--breakpoint-xxl: 1400px; /* Extra extra large */
```

### Mobile-First Media Queries

```css
/* Base styles (mobile) */
.component {
    font-size: 1rem;
}

/* Tablet and up */
@media (min-width: 768px) {
    .component {
        font-size: 1.125rem;
    }
}

/* Desktop and up */
@media (min-width: 992px) {
    .component {
        font-size: 1.25rem;
    }
}
```

### Responsive Typography

```css
html {
    font-size: 16px;  /* Base */
}

@media (max-width: 576px) {
    html {
        font-size: 14px;  /* Smaller on mobile */
    }
}
```

### Responsive Utilities

```html
<div class="d-none d-md-block">Visible on tablet+</div>
<div class="d-block d-md-none">Visible on mobile only</div>
```

---

## Theming

### Theme Toggle

```javascript
// Toggle between light and dark themes
document.documentElement.setAttribute('data-theme', 'dark');
```

### CSS Custom Properties

```css
:root {
    --transition-smooth: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    --border-radius-xl: 1.25rem;
    --shadow-hover: 0 8px 25px rgba(0, 0, 0, 0.15);
}
```

### Theme-Aware Components

```css
.card {
    background: var(--bs-white);
    color: var(--bs-dark);
}

[data-theme="dark"] .card {
    background: var(--bs-card-bg);
    color: var(--bs-body-color);
}
```

---

## Accessibility

### WCAG 2.2 Compliance

#### Color Contrast
- **AA Standard:** 4.5:1 for normal text, 3:1 for large text
- **AAA Standard:** 7:1 for normal text (aspirational)

Example:
```css
/* Good contrast */
.text-primary { color: #667eea; }  /* On white background */
.bg-dark .text-light { color: #e0e0e0; }  /* On dark background */
```

#### Focus Indicators

```css
:focus-visible {
    outline: 2px solid var(--bs-primary);
    outline-offset: 2px;
}
```

#### Keyboard Navigation

```html
<!-- Proper tab order -->
<button tabindex="0">First</button>
<button tabindex="0">Second</button>

<!-- Skip to content link -->
<a href="#main-content" class="skip-link">Skip to content</a>
```

#### ARIA Labels

```html
<!-- Icon buttons need labels -->
<button aria-label="Close modal">
    <i class="bi bi-x"></i>
</button>

<!-- Form inputs -->
<label for="email">Email</label>
<input id="email" type="email" aria-required="true">

<!-- Loading states -->
<div role="status" aria-live="polite">Loading...</div>
```

#### Semantic HTML

```html
<!-- Use semantic elements -->
<header>...</header>
<nav>...</nav>
<main>...</main>
<article>...</article>
<aside>...</aside>
<footer>...</footer>
```

### Screen Reader Support

```html
<!-- Hide decorative elements -->
<i class="bi bi-star" aria-hidden="true"></i>

<!-- Provide text alternatives -->
<img src="chart.png" alt="Weekly calorie intake chart">

<!-- Use sr-only for screen reader text -->
<span class="visually-hidden">Current: Dashboard</span>
```

---

## Component Library

### Target Item Component

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
    border: 1px solid rgba(var(--bs-border-color-rgb), 0.3);
    transition: var(--transition-smooth);
}

.target-item:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-hover);
}
```

### Macro Target Component

```html
<div class="macro-target">
    <div class="macro-label">Protein</div>
    <div class="macro-value">150g</div>
</div>
```

---

## Design Tokens

### Border Radius

```css
:root {
    --border-radius-sm: 0.25rem;   /* 4px */
    --border-radius-md: 0.5rem;    /* 8px */
    --border-radius-lg: 0.75rem;   /* 12px */
    --border-radius-xl: 1rem;      /* 16px */
    --border-radius-2xl: 1.25rem;  /* 20px */
}
```

### Shadows

```css
:root {
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 2px 8px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 4px 16px rgba(0, 0, 0, 0.15);
    --shadow-xl: 0 8px 32px rgba(0, 0, 0, 0.2);
    --shadow-hover: 0 8px 25px rgba(0, 0, 0, 0.15);
}
```

### Transitions

```css
:root {
    --transition-fast: 0.15s;
    --transition-base: 0.3s;
    --transition-slow: 0.5s;
    --transition-smooth: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
```

---

## Best Practices

### Do's ✅

1. **Use semantic HTML** - Helps with accessibility and SEO
2. **Mobile-first approach** - Start small, scale up
3. **Consistent spacing** - Use the 8px grid system
4. **Test with screen readers** - Ensure accessibility
5. **Use CSS custom properties** - Easier theming
6. **Optimize performance** - Minimize CSS, use modern techniques
7. **Follow naming conventions** - BEM or Bootstrap conventions

### Don'ts ❌

1. **Don't use fixed widths** - Use percentages or max-width
2. **Don't skip focus states** - Accessibility requirement
3. **Don't use color alone** - Add icons or text for clarity
4. **Don't forget dark mode** - Test both themes
5. **Don't hardcode colors** - Use CSS custom properties
6. **Don't ignore performance** - Optimize images and CSS
7. **Don't break responsive** - Test all breakpoints

---

## Tools & Resources

### Design Tools
- **Figma** - Design prototypes
- **Adobe XD** - Alternative design tool
- **Sketch** - Mac-specific design tool

### Development Tools
- **Chrome DevTools** - Inspect and debug
- **Firefox DevTools** - Accessibility inspector
- **Lighthouse** - Performance and accessibility audit

### Accessibility Testing
- **WAVE** - Web accessibility evaluation
- **axe DevTools** - Accessibility testing
- **NVDA/JAWS** - Screen reader testing

### Color Tools
- **Coolors.co** - Color palette generator
- **WebAIM Contrast Checker** - Contrast ratio checker

---

## Changelog

### Version 1.0.0 (October 23, 2025)
- Initial design system documentation
- Documented all components and patterns
- Added accessibility guidelines
- Created responsive design guidelines
- Documented theming system

---

## References

- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)
- [WCAG 2.2 Guidelines](https://www.w3.org/WAI/WCAG22/quickref/)
- [MDN Web Docs](https://developer.mozilla.org/en-US/)
- [CSS-Tricks](https://css-tricks.com/)

---

**Maintained by:** Nutricount Design Team  
**Contact:** See [CONTRIBUTING.md](../../CONTRIBUTING.md) for questions
