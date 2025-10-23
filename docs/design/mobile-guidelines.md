# 📱 Mobile-First Design Patterns

**Version:** 1.0.0  
**Last Updated:** October 23, 2025  
**Status:** ✅ Production Ready

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Mobile-First Philosophy](#mobile-first-philosophy)
3. [Responsive Breakpoints](#responsive-breakpoints)
4. [Layout Patterns](#layout-patterns)
5. [Navigation Patterns](#navigation-patterns)
6. [Touch Interactions](#touch-interactions)
7. [Performance Optimization](#performance-optimization)
8. [Progressive Web App](#progressive-web-app)
9. [Testing Guidelines](#testing-guidelines)

---

## Introduction

Mobile-first design means starting with the mobile experience and progressively enhancing for larger screens. This approach ensures:

- **Better Performance:** Lighter initial load on mobile devices
- **Content Prioritization:** Forces focus on essential features
- **Broader Accessibility:** Works well across all device sizes
- **Future-Proof:** Adapts to new device form factors

### Why Mobile-First for Nutricount?

1. **Target Audience:** Health-conscious users track nutrition on-the-go
2. **Use Case:** Quick food logging during meals
3. **Device Usage:** 60%+ of traffic expected from mobile devices
4. **Offline Capability:** PWA features enable offline food tracking

---

## Mobile-First Philosophy

### Core Principles

#### 1. Content First
**Start with the most important content and features.**

```css
/* Mobile: Single column, essential content only */
.dashboard {
    display: flex;
    flex-direction: column;
}

/* Desktop: Multi-column when space allows */
@media (min-width: 992px) {
    .dashboard {
        flex-direction: row;
        gap: 2rem;
    }
}
```

#### 2. Progressive Enhancement
**Add complexity as screen size increases.**

**Mobile:** Simple stacked list
```html
<div class="product-list">
    <div class="product-card">...</div>
    <div class="product-card">...</div>
</div>
```

**Desktop:** Grid with more details
```html
<div class="product-grid">
    <div class="product-card-detailed">...</div>
    <div class="product-card-detailed">...</div>
</div>
```

#### 3. Touch-First Interactions
**Design for touch, enhance for mouse.**

```css
/* Touch-friendly targets (minimum 44×44px) */
.btn {
    min-width: 44px;
    min-height: 44px;
    padding: 0.75rem 1.5rem;
}

/* Hover states for mouse users */
@media (hover: hover) {
    .btn:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
    }
}
```

#### 4. Performance Budget
**Optimize for mobile data and processing.**

- **Page Weight:** < 1MB initial load
- **Time to Interactive:** < 3 seconds on 3G
- **Images:** Responsive images with srcset
- **CSS/JS:** Critical path optimization

---

## Responsive Breakpoints

### Standard Breakpoints

Based on Bootstrap 5 + common device sizes:

```css
/* Extra small devices (phones, less than 576px) */
/* Default styles - no media query needed */

/* Small devices (landscape phones, 576px and up) */
@media (min-width: 576px) { }

/* Medium devices (tablets, 768px and up) */
@media (min-width: 768px) { }

/* Large devices (desktops, 992px and up) */
@media (min-width: 992px) { }

/* Extra large devices (large desktops, 1200px and up) */
@media (min-width: 1200px) { }

/* XXL devices (larger desktops, 1400px and up) */
@media (min-width: 1400px) { }
```

### Common Device Targets

| Device | Width | Orientation | Breakpoint |
|--------|-------|-------------|------------|
| iPhone SE | 375px | Portrait | XS |
| iPhone 12/13/14 | 390px | Portrait | XS |
| iPhone 12 Pro Max | 428px | Portrait | XS |
| iPad Mini | 768px | Portrait | MD |
| iPad Pro | 1024px | Portrait | LG |
| Desktop | 1920px | Landscape | XL |

### Testing Breakpoints

**Key test widths:**
- 320px (smallest phones)
- 375px (iPhone standard)
- 768px (tablet portrait)
- 1024px (tablet landscape / small desktop)
- 1920px (desktop)

---

## Layout Patterns

### 1. Stack to Grid

**Mobile:** Vertical stack
**Desktop:** Multi-column grid

```css
/* Mobile: Single column stack */
.stats-grid {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

/* Tablet: 2 columns */
@media (min-width: 768px) {
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1.5rem;
    }
}

/* Desktop: 3 or 4 columns */
@media (min-width: 992px) {
    .stats-grid {
        grid-template-columns: repeat(4, 1fr);
        gap: 2rem;
    }
}
```

**HTML:**
```html
<div class="stats-grid">
    <div class="stat-card">Calories</div>
    <div class="stat-card">Protein</div>
    <div class="stat-card">Fat</div>
    <div class="stat-card">Carbs</div>
</div>
```

### 2. Off-Canvas Navigation

**Mobile:** Hidden sidebar, toggle button
**Desktop:** Visible sidebar

```css
/* Mobile: Hidden off-canvas */
.sidebar {
    position: fixed;
    left: -250px;
    width: 250px;
    transition: left 0.3s;
}

.sidebar.open {
    left: 0;
}

/* Desktop: Always visible */
@media (min-width: 992px) {
    .sidebar {
        position: static;
        left: auto;
    }
}
```

**Example (Nutricount Tab Navigation):**
```html
<!-- Mobile: Horizontal scroll -->
<ul class="nav nav-tabs" role="tablist">
    <li class="nav-item">
        <button class="nav-link active">Products</button>
    </li>
    <!-- More tabs... -->
</ul>

<style>
/* Mobile: Scrollable tabs */
.nav-tabs {
    flex-wrap: nowrap;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

/* Desktop: Full width tabs */
@media (min-width: 768px) {
    .nav-tabs {
        overflow-x: visible;
    }
}
</style>
```

### 3. Collapsible Sections

**Mobile:** Collapsed by default
**Desktop:** Expanded by default

```html
<!-- Accordion on mobile, expanded on desktop -->
<div class="accordion" id="statsAccordion">
    <div class="accordion-item">
        <h2 class="accordion-header">
            <button class="accordion-button" data-bs-toggle="collapse">
                Daily Statistics
            </button>
        </h2>
        <div class="accordion-collapse collapse show">
            <div class="accordion-body">...</div>
        </div>
    </div>
</div>

<script>
// Auto-expand on desktop
if (window.innerWidth >= 992) {
    document.querySelectorAll('.accordion-collapse').forEach(el => {
        el.classList.add('show');
    });
}
</script>
```

### 4. Modal vs Inline Forms

**Mobile:** Full-screen modal
**Desktop:** Inline or centered modal

```css
/* Mobile: Full screen modal */
.modal-fullscreen-sm-down {
    width: 100vw;
    max-width: none;
    height: 100vh;
    margin: 0;
}

/* Desktop: Centered modal */
@media (min-width: 576px) {
    .modal-fullscreen-sm-down {
        width: auto;
        max-width: 500px;
        height: auto;
        margin: 1.75rem auto;
    }
}
```

### 5. Data Tables

**Mobile:** Card view or horizontal scroll
**Desktop:** Full table

**Approach 1: Responsive Table (Horizontal Scroll)**
```css
/* Mobile: Scroll horizontally */
.table-responsive {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

/* Desktop: No scroll needed */
@media (min-width: 768px) {
    .table-responsive {
        overflow-x: visible;
    }
}
```

**Approach 2: Card View on Mobile**
```html
<!-- Mobile: Card layout -->
<div class="product-item d-block d-md-none">
    <h5>Chicken Breast</h5>
    <p>Protein: 31g | Fat: 3.6g | Carbs: 0g</p>
</div>

<!-- Desktop: Table row -->
<tr class="d-none d-md-table-row">
    <td>Chicken Breast</td>
    <td>31g</td>
    <td>3.6g</td>
    <td>0g</td>
</tr>
```

---

## Navigation Patterns

### 1. Tab Navigation (Current Implementation)

**Mobile:** Horizontal scroll tabs
**Desktop:** Full-width tabs

```css
.nav-tabs {
    border-bottom: 2px solid #dee2e6;
    overflow-x: auto;
    flex-wrap: nowrap;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;  /* Firefox */
}

.nav-tabs::-webkit-scrollbar {
    display: none;  /* Chrome/Safari */
}

.nav-link {
    white-space: nowrap;
    min-width: fit-content;
}

@media (min-width: 768px) {
    .nav-tabs {
        overflow-x: visible;
        flex-wrap: wrap;
    }
}
```

### 2. Bottom Navigation (Alternative)

**Best for:** 3-5 primary sections

```html
<nav class="bottom-nav d-md-none">
    <a href="#products" class="nav-item active">
        <i class="bi bi-basket"></i>
        <span>Products</span>
    </a>
    <a href="#dishes" class="nav-item">
        <i class="bi bi-egg-fried"></i>
        <span>Dishes</span>
    </a>
    <a href="#log" class="nav-item">
        <i class="bi bi-journal-text"></i>
        <span>Log</span>
    </a>
    <a href="#stats" class="nav-item">
        <i class="bi bi-graph-up"></i>
        <span>Stats</span>
    </a>
</nav>

<style>
.bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--bs-white);
    border-top: 1px solid var(--bs-border-color);
    display: flex;
    justify-content: space-around;
    padding: 0.5rem 0;
    z-index: 1000;
}

.bottom-nav .nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0.5rem;
    color: var(--bs-secondary);
    text-decoration: none;
    font-size: 0.75rem;
}

.bottom-nav .nav-item.active {
    color: var(--bs-primary);
}

.bottom-nav .nav-item i {
    font-size: 1.5rem;
    margin-bottom: 0.25rem;
}

/* Add bottom padding to body to prevent content hiding */
body {
    padding-bottom: 70px;
}

@media (min-width: 768px) {
    .bottom-nav {
        display: none;
    }
    
    body {
        padding-bottom: 0;
    }
}
</style>
```

### 3. Hamburger Menu

**Mobile:** Collapsible menu
**Desktop:** Horizontal navigation

```html
<nav class="navbar navbar-expand-lg">
    <div class="container-fluid">
        <a class="navbar-brand" href="#">Nutricount</a>
        
        <!-- Mobile toggle -->
        <button class="navbar-toggler" type="button" 
                data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        
        <!-- Collapsible nav -->
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav">
                <li class="nav-item"><a class="nav-link" href="#">Products</a></li>
                <li class="nav-item"><a class="nav-link" href="#">Dishes</a></li>
                <li class="nav-item"><a class="nav-link" href="#">Log</a></li>
            </ul>
        </div>
    </div>
</nav>
```

---

## Touch Interactions

### 1. Touch Target Sizes

**Minimum Size:** 44×44 CSS pixels (iOS HIG, Material Design)

```css
/* Ensure all interactive elements meet minimum */
.btn,
.nav-link,
a,
button,
input[type="checkbox"],
input[type="radio"] {
    min-width: 44px;
    min-height: 44px;
}

/* Spacing between touch targets */
.btn-group .btn {
    margin: 0 4px;  /* 8px gap between buttons */
}
```

### 2. Tap vs Long Press

```javascript
// Detect tap vs long press
let pressTimer;

element.addEventListener('touchstart', (e) => {
    pressTimer = setTimeout(() => {
        // Long press action (e.g., show context menu)
        showContextMenu(e.target);
    }, 500);
});

element.addEventListener('touchend', () => {
    clearTimeout(pressTimer);
    // Normal tap action
});
```

### 3. Swipe Gestures

```javascript
// Simple swipe detection
let touchStartX = 0;
let touchEndX = 0;

element.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
});

element.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
});

function handleSwipe() {
    if (touchEndX < touchStartX - 50) {
        // Swipe left
        console.log('Swiped left');
    }
    if (touchEndX > touchStartX + 50) {
        // Swipe right
        console.log('Swiped right');
    }
}
```

**Use Cases in Nutricount:**
- Swipe to delete log entries
- Swipe between tabs
- Pull to refresh statistics

### 4. Prevent Double-Tap Zoom

```css
/* Prevent accidental zoom on double-tap */
button,
a {
    touch-action: manipulation;
}
```

### 5. Active States

```css
/* Visual feedback on touch */
.btn:active {
    transform: scale(0.98);
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Hover only on devices with hover capability */
@media (hover: hover) {
    .btn:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
    }
}
```

---

## Performance Optimization

### 1. Responsive Images

```html
<!-- Serve different image sizes based on screen width -->
<img srcset="product-small.jpg 320w,
             product-medium.jpg 768w,
             product-large.jpg 1200w"
     sizes="(max-width: 576px) 100vw,
            (max-width: 992px) 50vw,
            33vw"
     src="product-medium.jpg"
     alt="Product image">
```

### 2. Critical CSS

**Inline critical styles for above-the-fold content:**

```html
<head>
    <!-- Critical CSS inline -->
    <style>
        body { margin: 0; font-family: system-ui; }
        .header { background: #667eea; padding: 1rem; }
        /* Only styles needed for initial render */
    </style>
    
    <!-- Non-critical CSS loaded asynchronously -->
    <link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
    <noscript><link rel="stylesheet" href="styles.css"></noscript>
</head>
```

### 3. Lazy Loading

```html
<!-- Lazy load images -->
<img src="placeholder.jpg" 
     data-src="actual-image.jpg"
     loading="lazy"
     alt="Product">

<!-- Lazy load iframes -->
<iframe src="..." loading="lazy"></iframe>
```

### 4. Font Loading

```css
/* System font stack (instant load) */
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
                 "Helvetica Neue", Arial, sans-serif;
}

/* If using web fonts, optimize loading */
@font-face {
    font-family: 'CustomFont';
    src: url('font.woff2') format('woff2');
    font-display: swap;  /* Show fallback immediately */
}
```

### 5. Reduce HTTP Requests

```html
<!-- Combine CSS files -->
<link rel="stylesheet" href="combined.min.css">

<!-- Use SVG sprites for icons -->
<svg><use xlink:href="#icon-star"></use></svg>

<!-- Use data URIs for small images -->
<img src="data:image/svg+xml;base64,..." alt="Icon">
```

---

## Progressive Web App

### 1. Manifest File

```json
{
  "name": "Nutricount - Nutrition Tracker",
  "short_name": "Nutricount",
  "description": "Track your nutrition and fasting",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#667eea",
  "icons": [
    {
      "src": "icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "orientation": "portrait-primary"
}
```

### 2. Service Worker

```javascript
// Cache-first strategy for static assets
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});

// Offline fallback
self.addEventListener('fetch', (event) => {
    event.respondWith(
        fetch(event.request).catch(() => {
            return caches.match('/offline.html');
        })
    );
});
```

### 3. Install Prompt

```javascript
// Capture install prompt
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    
    // Show install button
    document.getElementById('installBtn').style.display = 'block';
});

document.getElementById('installBtn').addEventListener('click', async () => {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        console.log(`User response: ${outcome}`);
        deferredPrompt = null;
    }
});
```

### 4. Offline Support

```javascript
// Check online/offline status
window.addEventListener('online', () => {
    document.getElementById('offlineBanner').style.display = 'none';
});

window.addEventListener('offline', () => {
    document.getElementById('offlineBanner').style.display = 'block';
});

// Sync data when back online
if ('serviceWorker' in navigator && 'SyncManager' in window) {
    navigator.serviceWorker.ready.then(async (registration) => {
        await registration.sync.register('sync-data');
    });
}
```

---

## Testing Guidelines

### 1. Device Testing

**Physical Devices (Recommended):**
- iPhone SE (smallest modern iPhone)
- iPhone 12/13/14 (standard size)
- iPad (tablet experience)
- Android phone (Samsung Galaxy, Pixel)
- Android tablet

**Emulators/Simulators:**
- Chrome DevTools Device Mode
- iOS Simulator (Xcode)
- Android Emulator (Android Studio)

### 2. Browser Testing

**Mobile Browsers:**
- Safari (iOS)
- Chrome (iOS & Android)
- Samsung Internet (Android)
- Firefox (Android)

**Desktop Browsers:**
- Chrome
- Firefox
- Safari
- Edge

### 3. Testing Checklist

#### Layout
- [ ] Content readable at 320px width
- [ ] No horizontal scroll (except data tables)
- [ ] Text doesn't overflow containers
- [ ] Images scale properly
- [ ] Buttons don't overlap

#### Touch Interactions
- [ ] All buttons/links easily tappable (44×44px)
- [ ] Swipe gestures work smoothly
- [ ] No accidental double-tap zoom
- [ ] Forms easy to fill on mobile

#### Performance
- [ ] Page loads in < 3 seconds on 3G
- [ ] Smooth scrolling (60 FPS)
- [ ] No layout shifts (CLS < 0.1)
- [ ] Images lazy load properly

#### Orientation
- [ ] Works in portrait mode
- [ ] Works in landscape mode
- [ ] Graceful transition between orientations

#### Offline
- [ ] PWA installs correctly
- [ ] App works offline
- [ ] Data syncs when back online

### 4. Testing Tools

```bash
# Lighthouse (Performance & PWA audit)
lighthouse https://yoursite.com --view

# Chrome DevTools Device Mode
# F12 → Toggle Device Toolbar (Ctrl+Shift+M)

# Network throttling (simulate 3G)
# DevTools → Network → Throttling → Fast 3G
```

---

## Best Practices Summary

### Do's ✅

1. **Design mobile-first** - Start with smallest screen
2. **Use system fonts** - Faster loading
3. **Touch targets 44×44px** - Easy tapping
4. **Test on real devices** - Emulators miss issues
5. **Optimize images** - Use srcset and lazy loading
6. **Enable PWA features** - Better mobile experience
7. **Provide offline fallback** - Graceful degradation
8. **Use CSS Grid/Flexbox** - Modern, responsive layouts

### Don'ts ❌

1. **Don't use fixed widths** - Breaks responsiveness
2. **Don't rely on hover** - Doesn't work on touch
3. **Don't ignore performance** - Mobile users have slower connections
4. **Don't use tiny text** - Minimum 16px for body text
5. **Don't hide content** - Don't assume desktop-only users
6. **Don't forget landscape** - Test both orientations
7. **Don't use flash** - Not supported on mobile
8. **Don't ignore battery** - Avoid CPU-intensive animations

---

## Mobile-Specific Features for Nutricount

### 1. Quick Add Buttons

**Large, thumb-friendly buttons for frequent actions:**

```html
<div class="quick-actions">
    <button class="btn btn-lg btn-primary w-100 mb-2">
        <i class="bi bi-plus-circle"></i> Log Food
    </button>
    <button class="btn btn-lg btn-success w-100 mb-2">
        <i class="bi bi-play-circle"></i> Start Fasting
    </button>
</div>
```

### 2. Swipe to Delete

**Natural mobile interaction for managing entries:**

```javascript
// Swipe left to reveal delete button
const logEntry = document.querySelector('.log-entry');
let startX;

logEntry.addEventListener('touchstart', (e) => {
    startX = e.touches[0].clientX;
});

logEntry.addEventListener('touchmove', (e) => {
    const currentX = e.touches[0].clientX;
    const diff = startX - currentX;
    
    if (diff > 50) {
        logEntry.classList.add('swiped');
        logEntry.querySelector('.delete-btn').style.display = 'block';
    }
});
```

### 3. Numeric Keyboard for Inputs

```html
<!-- Show numeric keyboard on mobile -->
<input type="number" 
       inputmode="decimal" 
       pattern="[0-9]*"
       placeholder="Weight (g)">

<!-- Email keyboard for email inputs -->
<input type="email" 
       inputmode="email"
       autocomplete="email"
       placeholder="Email">
```

### 4. Voice Input (Future Enhancement)

```html
<button id="voiceBtn" aria-label="Voice input">
    <i class="bi bi-mic"></i>
</button>

<script>
if ('webkitSpeechRecognition' in window) {
    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'en-US';
    
    document.getElementById('voiceBtn').addEventListener('click', () => {
        recognition.start();
    });
    
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById('foodInput').value = transcript;
    };
}
</script>
```

---

## Responsive Typography

### Scale Based on Screen Size

```css
/* Base size (mobile) */
html {
    font-size: 16px;
}

/* Tablet */
@media (min-width: 768px) {
    html {
        font-size: 17px;
    }
}

/* Desktop */
@media (min-width: 1200px) {
    html {
        font-size: 18px;
    }
}

/* Use rem units for scalability */
h1 { font-size: 2rem; }     /* 32px on mobile, 36px on desktop */
h2 { font-size: 1.5rem; }   /* 24px on mobile, 27px on desktop */
body { font-size: 1rem; }   /* 16px on mobile, 18px on desktop */
```

### Fluid Typography (Advanced)

```css
/* Fluid typography using clamp() */
h1 {
    font-size: clamp(1.5rem, 5vw, 2.5rem);
}

body {
    font-size: clamp(0.875rem, 2vw, 1rem);
}
```

---

## Resources

### Tools
- [Chrome DevTools Device Mode](https://developers.google.com/web/tools/chrome-devtools/device-mode)
- [Responsive Image Breakpoints Generator](https://www.responsivebreakpoints.com/)
- [PWA Builder](https://www.pwabuilder.com/)

### Testing
- [BrowserStack](https://www.browserstack.com/) - Real device testing
- [Responsively App](https://responsively.app/) - Multi-viewport testing
- [Lighthouse](https://developers.google.com/web/tools/lighthouse) - Performance audit

### Guidelines
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Material Design (Google)](https://material.io/design)
- [Progressive Web Apps (Google)](https://web.dev/progressive-web-apps/)

---

**Maintained by:** Nutricount Mobile Team  
**Next Review:** January 2026  
**Contact:** See [CONTRIBUTING.md](../../CONTRIBUTING.md)
