# Unified Frontend Architecture Guide

**Date:** October 25, 2025  
**Status:** ✅ Implemented  
**Pattern:** BFF (Backend For Frontend) via Adapter Pattern

---

## 📋 Overview

This document explains how Nutricount implements a **single unified frontend (SPA)** that works with **multiple backends** using the **BFF (Backend For Frontend)** pattern.

### The Challenge

We need:
1. **Single frontend codebase** (no duplication)
2. **Works on GitHub Pages** (static hosting, no server)
3. **Works on Raspberry Pi** (with Flask backend and database)
4. **Automatic backend detection** (no manual configuration)

### The Solution

**Adapter Pattern + Auto-Detection**

```
                    Unified Frontend (SPA)
                            ↓
                    AdapterFactory
                    (Auto-Detection)
                    ↙             ↘
          StorageAdapter      ApiAdapter
          (localStorage)      (Flask API)
                ↓                   ↓
          GitHub Pages         Raspberry Pi
          (Static SPA)         (Server + DB)
```

---

## 🏗️ Architecture

### 1. BackendAdapter Interface (BFF Contract)

**File:** `frontend/src/adapters/backend-adapter.js`

This is the **BFF interface** - a single contract that all backends must implement:

```javascript
class BackendAdapter {
    // Products
    async getProducts()
    async createProduct(product)
    async updateProduct(id, product)
    async deleteProduct(id)
    
    // Logging
    async getLogEntries(date)
    async createLogEntry(entry)
    async updateLogEntry(id, entry)
    async deleteLogEntry(id)
    
    // Statistics
    async getDailyStats(date)
    async getWeeklyStats(startDate, endDate)
    
    // Settings
    async getSettings()
    async saveSettings(settings)
    
    // Dishes
    async getDishes()
    async createDish(dish)
    async updateDish(id, dish)
    async deleteDish(id)
}
```

### 2. StorageAdapter (For GitHub Pages)

**File:** `frontend/src/adapters/storage-adapter.js`

**Purpose:** BFF implementation for static hosting (no server)

**Storage:** Browser's localStorage

**Features:**
- All data stored client-side
- No server required
- Works offline
- Fast (no network calls)
- Perfect for GitHub Pages

**Example:**
```javascript
const adapter = new StorageAdapter();
const products = await adapter.getProducts(); // Reads from localStorage
await adapter.createProduct({ name: 'Chicken', ... }); // Saves to localStorage
```

### 3. ApiAdapter (For Raspberry Pi)

**File:** `frontend/src/adapters/api-adapter.js`

**Purpose:** BFF implementation for server deployment

**Storage:** Flask backend → SQLite database

**Features:**
- RESTful API communication
- JWT authentication
- Retry logic and error handling
- Server-side data persistence
- Multi-user support (future)

**Example:**
```javascript
const adapter = new ApiAdapter('/api');
const products = await adapter.getProducts(); // GET /api/products
await adapter.createProduct({ name: 'Chicken', ... }); // POST /api/products
```

### 4. AdapterFactory (Auto-Detection) ✨

**File:** `frontend/src/adapters/adapter-factory.js`

**Purpose:** Automatically detect environment and create appropriate adapter

**Detection Logic:**
1. Check if running on `github.io` → StorageAdapter
2. Check if running on `localhost:5000` → ApiAdapter
3. Check if running on local network (192.168.x.x or .local) → ApiAdapter
4. Try to ping `/api/health` endpoint → If success: ApiAdapter, else: StorageAdapter
5. Default fallback → StorageAdapter (safe)

**Usage:**
```javascript
// Synchronous detection (fast, good enough for most cases)
const adapter = AdapterFactory.create();

// Async detection (more reliable, pings API first)
const adapter = await AdapterFactory.createAsync();

// Force specific mode (for testing)
const adapter = AdapterFactory.create({ forceMode: 'static' });
const adapter = AdapterFactory.create({ forceMode: 'server' });
```

---

## 🚀 How to Use

### In Your Application

**Option 1: Simple Auto-Detection (Recommended)**

```javascript
// index.html or app.js
document.addEventListener('DOMContentLoaded', () => {
    // Auto-detect and create adapter
    const adapter = AdapterFactory.create();
    
    // Initialize your app with the adapter
    const app = new NutritionTracker(adapter);
    
    console.log('✅ App initialized with', adapter.constructor.name);
});
```

**Option 2: Async Detection (More Reliable)**

```javascript
document.addEventListener('DOMContentLoaded', async () => {
    // Async detection - pings API first
    const adapter = await AdapterFactory.createAsync();
    
    // Initialize app
    const app = new NutritionTracker(adapter);
    
    console.log('✅ App initialized with', adapter.constructor.name);
});
```

**Option 3: With Error Handling**

```javascript
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Try async detection
        const adapter = await AdapterFactory.createAsync();
        const app = new NutritionTracker(adapter);
        
        console.log('✅ App initialized with', adapter.constructor.name);
    } catch (error) {
        console.error('❌ Failed to initialize app:', error);
        
        // Fallback to localStorage
        const adapter = new StorageAdapter();
        const app = new NutritionTracker(adapter);
        
        console.log('✅ App initialized with fallback StorageAdapter');
    }
});
```

### In Your Application Class

```javascript
class NutritionTracker {
    constructor(adapter) {
        this.adapter = adapter; // BFF interface
        this.init();
    }
    
    async loadProducts() {
        // Works with ANY adapter (StorageAdapter or ApiAdapter)
        const products = await this.adapter.getProducts();
        this.renderProducts(products);
    }
    
    async addProduct(product) {
        // Works with ANY adapter
        const newProduct = await this.adapter.createProduct(product);
        this.loadProducts(); // Refresh
    }
}
```

---

## 📦 Deployment Scenarios

### Scenario 1: GitHub Pages (Static SPA)

**Deployment:**
```bash
# Build and deploy to Pages
cp demo/index.html docs/
git add docs/
git commit -m "Deploy to Pages"
git push
```

**Runtime:**
```
User opens: https://username.github.io/nutricount/
     ↓
AdapterFactory.create()
     ↓
Detects: "github.io" domain
     ↓
Creates: StorageAdapter
     ↓
App works with localStorage
```

**User Experience:**
- ✅ Instant loading
- ✅ Works offline
- ✅ All data private (stored locally)
- ✅ No server costs

### Scenario 2: Raspberry Pi (Server Deployment)

**Deployment:**
```bash
# Deploy with Docker
docker-compose up -d

# Or run Flask directly
export FLASK_ENV=production
python app.py
```

**Runtime:**
```
User opens: http://192.168.1.100:5000/
     ↓
AdapterFactory.create()
     ↓
Detects: Local network IP
     ↓
Creates: ApiAdapter
     ↓
App works with Flask backend + SQLite
```

**User Experience:**
- ✅ Server-side data storage
- ✅ Data survives browser clearing
- ✅ Can access from multiple devices
- ✅ Future: Multi-user support

### Scenario 3: Local Development

**Development:**
```bash
# Terminal 1: Start Flask backend
export PYTHONPATH=$(pwd)
python app.py

# Terminal 2: Serve frontend
cd demo
python -m http.server 8080
```

**Runtime:**
```
Developer opens: http://localhost:8080/
     ↓
AdapterFactory.createAsync()
     ↓
Pings: http://localhost:5000/api/health
     ↓
API responds: 200 OK
     ↓
Creates: ApiAdapter
     ↓
App works with Flask backend
```

---

## 🧪 Testing Different Modes

### Test localStorage Mode

```javascript
// Force localStorage (even if API is available)
const adapter = AdapterFactory.create({ forceMode: 'static' });
console.log(adapter instanceof StorageAdapter); // true
```

### Test API Mode

```javascript
// Force API mode (will fail if no API)
const adapter = AdapterFactory.create({ forceMode: 'server' });
console.log(adapter instanceof ApiAdapter); // true
```

### Test Auto-Detection

```javascript
// Let it decide automatically
const adapter = AdapterFactory.create();
console.log('Using:', adapter.constructor.name);
// StorageAdapter on Pages, ApiAdapter on RP
```

---

## 🎯 Benefits

### 1. Single Codebase ✅
- Write frontend once
- Works everywhere (Pages, RP, local)
- No code duplication

### 2. Automatic Detection ✅
- No manual configuration
- Works out of the box
- User doesn't see complexity

### 3. BFF Pattern ✅
- Clean architecture
- Easy to test (mock adapters)
- Easy to add new backends

### 4. Best of Both Worlds ✅
- Pages: Fast, free, offline-capable
- RP: Server storage, multi-device access

---

## 🔧 How It Works for GitHub Pages

### The "BFF Problem" on Pages

**Challenge:** GitHub Pages only serves static files. You can't run a server.

**Traditional Solution:**
- Put all logic in frontend (localStorage only)
- **Problem:** Can't have server features

**Our Solution:**
- BFF runs **IN THE BROWSER** for Pages (StorageAdapter)
- BFF runs **ON THE SERVER** for RP (Flask + ApiAdapter)
- **Same frontend interface works with both!**

### StorageAdapter = Client-Side BFF

The StorageAdapter IS your BFF for static deployment:

```javascript
class StorageAdapter extends BackendAdapter {
    // BFF logic runs in browser
    async getProducts() {
        const data = localStorage.getItem('nutricount_products');
        return JSON.parse(data) || [];
    }
    
    async createProduct(product) {
        // Validation (BFF logic)
        if (!product.name) throw new Error('Name required');
        
        // Generate ID (BFF logic)
        product.id = Date.now() + Math.random();
        
        // Store (BFF storage)
        const products = await this.getProducts();
        products.push(product);
        localStorage.setItem('nutricount_products', JSON.stringify(products));
        
        return product;
    }
}
```

**Key Insight:** The BFF pattern doesn't require a server. It's about **abstraction** and **single interface**, not about where the code runs.

---

## 📚 Architecture Comparison

### Traditional Approach (Problematic)

```
Pages Version:
├── demo/index.html (localStorage logic)
└── Different UI code

RP Version:
├── templates/index.html (API logic)
└── Different UI code

❌ Two codebases
❌ Manual maintenance
❌ Features diverge
```

### Our Approach (Clean)

```
Unified Frontend:
├── index.html (same UI)
├── AdapterFactory (auto-detect)
├── StorageAdapter (for Pages)
└── ApiAdapter (for RP)

✅ One codebase
✅ Auto-detection
✅ Feature parity
```

---

## 🎓 Educational Value

This architecture demonstrates:

1. **Adapter Pattern** - Multiple implementations, single interface
2. **BFF Pattern** - Backend optimized for frontend needs
3. **Strategy Pattern** - Runtime algorithm selection
4. **Dependency Injection** - Adapter injected into app
5. **Factory Pattern** - Centralized object creation
6. **Progressive Enhancement** - Works with/without server

---

## 🚦 Next Steps

### Current Status ✅
- [x] BackendAdapter interface defined
- [x] StorageAdapter implemented (for Pages)
- [x] ApiAdapter implemented (for RP)
- [x] AdapterFactory with auto-detection
- [x] Documentation complete

### To Complete Unification
- [ ] Update demo/index.html to use AdapterFactory
- [ ] Update templates/index.html to use AdapterFactory
- [ ] Test on GitHub Pages
- [ ] Test on Raspberry Pi
- [ ] Update build scripts

---

## 📖 References

### Code Files
- `frontend/src/adapters/backend-adapter.js` - BFF interface
- `frontend/src/adapters/storage-adapter.js` - localStorage BFF
- `frontend/src/adapters/api-adapter.js` - Flask API BFF
- `frontend/src/adapters/adapter-factory.js` - Auto-detection

### Documentation
- `frontend/README.md` - Frontend overview
- `INTEGRATED_ROADMAP.md` - Project roadmap
- `ARCHITECTURE.md` - System architecture

---

**Status:** ✅ Architecture Implemented  
**Last Updated:** October 25, 2025  
**Next:** Integrate AdapterFactory into demo and templates
