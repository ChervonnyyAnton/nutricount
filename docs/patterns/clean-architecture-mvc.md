# 🏛️ Clean Architecture & MVC in Nutricount

**Version:** 1.0.0  
**Last Updated:** October 23, 2025  
**Status:** ✅ Documented

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Clean Architecture Overview](#clean-architecture-overview)
3. [MVC Pattern in Nutricount](#mvc-pattern-in-nutricount)
4. [Layer Architecture](#layer-architecture)
5. [Dependency Flow](#dependency-flow)
6. [Implementation Examples](#implementation-examples)
7. [Best Practices](#best-practices)

---

## Introduction

This document describes the architectural patterns used in Nutricount, combining Clean Architecture principles with the MVC (Model-View-Controller) pattern. This hybrid approach ensures:

- **Separation of Concerns:** Clear boundaries between layers
- **Testability:** Isolated, testable components
- **Maintainability:** Easy to understand and modify
- **Scalability:** Can grow without becoming complex

---

## Clean Architecture Overview

### Core Principles

#### 1. Independence of Frameworks
Business logic doesn't depend on Flask, React, or any specific framework.

```python
# ❌ Bad: Business logic coupled to Flask
from flask import request

def calculate_calories(product_id):
    weight = request.form.get('weight')  # Coupled to Flask
    # ... calculation logic
```

```python
# ✅ Good: Pure business logic
def calculate_calories(product_data, weight):
    """Calculate calories for a product.
    
    Args:
        product_data: Dict with product nutrition info
        weight: Weight in grams (float)
        
    Returns:
        Calculated calories (float)
    """
    calories_per_100g = product_data['calories']
    return (calories_per_100g * weight) / 100
```

#### 2. Testability
Core business logic can be tested without external dependencies.

```python
# Easy to test - no mocks needed
def test_calculate_calories():
    product = {'calories': 165}
    result = calculate_calories(product, 100)
    assert result == 165.0
```

#### 3. Independence of UI
Same business logic works with web UI, API, CLI, or mobile app.

```python
# src/nutrition_calculator.py - Framework-independent
def calculate_macros(weight, protein_per_100g, fat_per_100g, carbs_per_100g):
    """Calculate macronutrients for given weight."""
    factor = weight / 100
    return {
        'protein': protein_per_100g * factor,
        'fat': fat_per_100g * factor,
        'carbs': carbs_per_100g * factor
    }

# Can be used by any interface:
# - Flask API: return jsonify(calculate_macros(...))
# - CLI: print(calculate_macros(...))
# - Mobile app: JSON response from API
```

#### 4. Independence of Database
Business logic doesn't know about SQLite, PostgreSQL, or MongoDB.

```python
# ✅ Repository pattern abstracts data access
class ProductRepository:
    """Abstract interface for product data access."""
    
    def get_by_id(self, product_id: int) -> dict:
        """Get product by ID. Implementation varies by database."""
        pass
    
    def save(self, product: dict) -> int:
        """Save product. Returns product ID."""
        pass

# SQLite implementation
class SQLiteProductRepository(ProductRepository):
    def get_by_id(self, product_id: int) -> dict:
        # SQLite-specific code
        conn = sqlite3.connect(DB_PATH)
        # ... query logic
        
# Future: PostgreSQL implementation
class PostgresProductRepository(ProductRepository):
    def get_by_id(self, product_id: int) -> dict:
        # PostgreSQL-specific code
        pass
```

### Layer Diagram

```
┌─────────────────────────────────────────┐
│           External Interfaces           │
│  (Web UI, API, CLI, Mobile App)        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Controllers (Routes)            │
│  Flask blueprints, request handling     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│          Services Layer                 │
│  Business logic, orchestration          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        Domain Layer (Core)              │
│  Pure business logic, calculations      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        Data Access Layer                │
│  Repositories, database operations      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        Infrastructure Layer             │
│  Database, cache, external APIs         │
└─────────────────────────────────────────┘
```

---

## MVC Pattern in Nutricount

### Traditional MVC

```
┌────────┐      ┌────────────┐      ┌────────┐
│  View  │ ◄──► │ Controller │ ◄──► │ Model  │
└────────┘      └────────────┘      └────────┘
    │                                    │
    └────────────────────────────────────┘
```

### Nutricount MVC Implementation

#### Model (Data + Business Logic)
- **Location:** `src/`, repositories, services
- **Responsibility:** Data structure, business rules, calculations
- **Examples:** `nutrition_calculator.py`, `fasting_manager.py`

```python
# src/nutrition_calculator.py (Model - Business Logic)
def calculate_keto_index(protein, fat, carbs):
    """Calculate keto-friendliness index (0-100)."""
    total = protein + fat + carbs
    if total == 0:
        return 0
    
    fat_ratio = fat / total
    carb_ratio = carbs / total
    
    # Higher fat, lower carbs = higher keto index
    keto_index = (fat_ratio * 70) + ((1 - carb_ratio) * 30)
    return min(100, max(0, keto_index))
```

#### View (User Interface)
- **Location:** `templates/`, `static/`, `demo/`
- **Responsibility:** Presentation, user interaction
- **Examples:** `index.html`, `app.js`, `final-polish.css`

```html
<!-- templates/index.html (View) -->
<div class="product-card">
    <h5 class="card-title">{{ product.name }}</h5>
    <div class="nutrition-info">
        <span class="badge">Protein: {{ product.protein }}g</span>
        <span class="badge">Fat: {{ product.fat }}g</span>
        <span class="badge">Carbs: {{ product.carbs }}g</span>
    </div>
    <div class="keto-index" data-index="{{ product.keto_index }}">
        Keto Index: {{ product.keto_index }}
    </div>
</div>
```

```javascript
// static/js/app.js (View Logic)
function renderProduct(product) {
    return `
        <div class="product-card">
            <h5>${product.name}</h5>
            <div class="nutrition-info">
                <span>Protein: ${product.protein}g</span>
                <span>Fat: ${product.fat}g</span>
                <span>Carbs: ${product.carbs}g</span>
            </div>
        </div>
    `;
}
```

#### Controller (Request Handling)
- **Location:** `routes/`, `app.py`
- **Responsibility:** Handle requests, coordinate model and view
- **Examples:** `routes/products.py`, `routes/dishes.py`

```python
# routes/products.py (Controller)
from flask import Blueprint, request, jsonify
from repositories.product_repository import ProductRepository
from services.product_service import ProductService

products_bp = Blueprint('products', __name__)
product_service = ProductService(ProductRepository())

@products_bp.route('/api/products', methods=['GET'])
def get_products():
    """Get all products (Controller)."""
    # 1. Get request parameters
    search = request.args.get('search', '')
    
    # 2. Call service layer (orchestration)
    products = product_service.search_products(search)
    
    # 3. Return view response (JSON)
    return jsonify({
        'success': True,
        'data': products
    })

@products_bp.route('/api/products', methods=['POST'])
def create_product():
    """Create new product (Controller)."""
    # 1. Get and validate request data
    data = request.get_json()
    
    # 2. Call service layer
    result = product_service.create_product(data)
    
    # 3. Return appropriate response
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400
```

---

## Layer Architecture

### 1. Presentation Layer (UI)

**Responsibilities:**
- Display data to user
- Capture user input
- Client-side validation
- User experience (UX)

**Technologies:**
- HTML5, CSS3, Bootstrap 5
- Vanilla JavaScript
- Service Worker (PWA)

**Example:**
```javascript
// static/js/app.js
class ProductUI {
    constructor() {
        this.productList = document.getElementById('product-list');
    }
    
    render(products) {
        this.productList.innerHTML = products.map(p => `
            <div class="product-card" data-id="${p.id}">
                <h5>${p.name}</h5>
                <p>Calories: ${p.calories} kcal</p>
            </div>
        `).join('');
    }
    
    showError(message) {
        // Display error to user
        alert(message);  // In production: use toast/modal
    }
}
```

### 2. Application Layer (Controllers)

**Responsibilities:**
- Route HTTP requests
- Validate input data
- Call appropriate services
- Format responses
- Error handling

**Technologies:**
- Flask Blueprints
- Flask-CORS (API)

**Example:**
```python
# routes/products.py
@products_bp.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get product by ID."""
    try:
        # Validate input
        if product_id < 1:
            return jsonify({'error': 'Invalid product ID'}), 400
        
        # Call service
        product = product_service.get_product(product_id)
        
        # Check result
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Return success
        return jsonify({'success': True, 'data': product})
        
    except Exception as e:
        logger.error(f"Error getting product: {e}")
        return jsonify({'error': 'Internal server error'}), 500
```

### 3. Service Layer (Business Logic Orchestration)

**Responsibilities:**
- Orchestrate business operations
- Transaction management
- Business rule enforcement
- Call multiple repositories
- Complex workflows

**Technologies:**
- Pure Python classes

**Example:**
```python
# services/product_service.py
class ProductService:
    """Service for product business logic."""
    
    def __init__(self, product_repo, cache_manager=None):
        self.product_repo = product_repo
        self.cache = cache_manager
    
    def create_product(self, data):
        """Create a new product with validation."""
        # 1. Validate business rules
        if not self._validate_product(data):
            return {'success': False, 'error': 'Validation failed'}
        
        # 2. Calculate derived values
        data['keto_index'] = self._calculate_keto_index(data)
        
        # 3. Save to database
        product_id = self.product_repo.save(data)
        
        # 4. Invalidate cache
        if self.cache:
            self.cache.invalidate('products')
        
        # 5. Return result
        return {
            'success': True,
            'data': {'id': product_id, **data}
        }
    
    def _validate_product(self, data):
        """Validate product data (business rules)."""
        required_fields = ['name', 'protein', 'fat', 'carbs', 'calories']
        
        # Check required fields
        if not all(field in data for field in required_fields):
            return False
        
        # Check value ranges
        if data['protein'] < 0 or data['fat'] < 0 or data['carbs'] < 0:
            return False
        
        # Check calories consistency (Atwater system)
        calculated = (data['protein'] * 4) + (data['fat'] * 9) + (data['carbs'] * 4)
        tolerance = 10  # Allow 10 kcal difference
        if abs(calculated - data['calories']) > tolerance:
            return False
        
        return True
    
    def _calculate_keto_index(self, data):
        """Calculate keto index for product."""
        from src.nutrition_calculator import calculate_keto_index
        return calculate_keto_index(
            data['protein'],
            data['fat'],
            data['carbs']
        )
```

### 4. Domain Layer (Core Business Logic)

**Responsibilities:**
- Pure business logic
- Calculations
- Domain rules
- No dependencies on frameworks

**Technologies:**
- Pure Python functions

**Example:**
```python
# src/nutrition_calculator.py (Domain Layer)
def calculate_calories(protein, fat, carbs, fiber=0):
    """Calculate calories using Atwater system.
    
    Args:
        protein: Protein in grams
        fat: Fat in grams
        carbs: Total carbohydrates in grams
        fiber: Fiber in grams (optional)
        
    Returns:
        Total calories (kcal)
    """
    # Atwater factors: Protein=4, Fat=9, Carbs=4
    # Fiber is not fully digestible, subtract from carbs
    digestible_carbs = max(0, carbs - fiber)
    
    return (protein * 4) + (fat * 9) + (digestible_carbs * 4)

def calculate_macros_percentage(protein, fat, carbs):
    """Calculate macronutrient percentages.
    
    Returns:
        Dict with protein_pct, fat_pct, carbs_pct
    """
    total = protein + fat + carbs
    if total == 0:
        return {'protein_pct': 0, 'fat_pct': 0, 'carbs_pct': 0}
    
    return {
        'protein_pct': round((protein / total) * 100, 1),
        'fat_pct': round((fat / total) * 100, 1),
        'carbs_pct': round((carbs / total) * 100, 1)
    }

def is_keto_friendly(fat_pct, carbs_pct):
    """Determine if macros are keto-friendly.
    
    Keto guidelines: Fat 60-75%, Carbs <10%
    """
    return fat_pct >= 60 and carbs_pct <= 10
```

### 5. Data Access Layer (Repositories)

**Responsibilities:**
- Database queries
- Data persistence
- Data retrieval
- Abstract database implementation

**Technologies:**
- SQLite (current)
- Abstracted for future database changes

**Example:**
```python
# repositories/product_repository.py
import sqlite3
from typing import List, Optional, Dict

class ProductRepository:
    """Repository for product data access."""
    
    def __init__(self, db_path='nutrition.db'):
        self.db_path = db_path
    
    def get_all(self) -> List[Dict]:
        """Get all products."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute('''
            SELECT id, name, protein, fat, carbs, calories, 
                   fiber, category, keto_index
            FROM products
            ORDER BY name
        ''')
        
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return products
    
    def get_by_id(self, product_id: int) -> Optional[Dict]:
        """Get product by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute('''
            SELECT * FROM products WHERE id = ?
        ''', (product_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def save(self, product: Dict) -> int:
        """Save product to database."""
        conn = sqlite3.connect(self.db_path)
        
        if 'id' in product and product['id']:
            # Update existing
            conn.execute('''
                UPDATE products
                SET name=?, protein=?, fat=?, carbs=?, calories=?,
                    fiber=?, category=?, keto_index=?
                WHERE id=?
            ''', (
                product['name'], product['protein'], product['fat'],
                product['carbs'], product['calories'], product.get('fiber', 0),
                product.get('category', ''), product.get('keto_index', 0),
                product['id']
            ))
            product_id = product['id']
        else:
            # Insert new
            cursor = conn.execute('''
                INSERT INTO products (name, protein, fat, carbs, calories,
                                    fiber, category, keto_index)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product['name'], product['protein'], product['fat'],
                product['carbs'], product['calories'], product.get('fiber', 0),
                product.get('category', ''), product.get('keto_index', 0)
            ))
            product_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return product_id
    
    def delete(self, product_id: int) -> bool:
        """Delete product from database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
        rows_affected = conn.total_changes
        conn.commit()
        conn.close()
        return rows_affected > 0
```

### 6. Infrastructure Layer

**Responsibilities:**
- External dependencies
- Database connections
- Cache (Redis)
- File system
- Third-party APIs

**Technologies:**
- SQLite
- Redis (optional)
- File system

**Example:**
```python
# src/cache_manager.py (Infrastructure)
import redis
from typing import Optional

class CacheManager:
    """Manages application caching."""
    
    def __init__(self):
        try:
            self.redis = redis.Redis(host='localhost', port=6379, db=0)
            self.redis.ping()
            self.available = True
        except:
            self.redis = None
            self.available = False
            # Fallback to in-memory cache
            self._memory_cache = {}
    
    def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if self.available:
            return self.redis.get(key)
        else:
            return self._memory_cache.get(key)
    
    def set(self, key: str, value: str, ttl: int = 3600):
        """Set value in cache with TTL."""
        if self.available:
            self.redis.setex(key, ttl, value)
        else:
            self._memory_cache[key] = value
    
    def invalidate(self, pattern: str):
        """Invalidate cache by pattern."""
        if self.available:
            keys = self.redis.keys(pattern + '*')
            if keys:
                self.redis.delete(*keys)
        else:
            # Clear matching keys from memory cache
            to_delete = [k for k in self._memory_cache if k.startswith(pattern)]
            for k in to_delete:
                del self._memory_cache[k]
```

---

## Dependency Flow

### The Dependency Rule

**Dependencies point inward:**
- Outer layers depend on inner layers
- Inner layers never depend on outer layers
- Core business logic has no dependencies

```
┌───────────────────────────────────────┐
│   UI / Controllers (outer)            │
│   ↓ depends on                        │
│   Services                            │
│   ↓ depends on                        │
│   Domain Logic (core - no deps)       │
│   ↑ used by                           │
│   Repositories                        │
│   ↑ used by                           │
│   Infrastructure (outer)              │
└───────────────────────────────────────┘
```

### Example: Calculate Daily Stats

**Bad (Tight Coupling):**
```python
# ❌ Controller directly accesses database
@routes_bp.route('/api/stats/daily')
def daily_stats():
    conn = sqlite3.connect('nutrition.db')  # Tight coupling
    cursor = conn.execute('SELECT * FROM log WHERE date = ?', (today,))
    entries = cursor.fetchall()
    
    total_calories = sum(e['calories'] for e in entries)  # Business logic in controller
    return jsonify({'calories': total_calories})
```

**Good (Layered Architecture):**
```python
# ✅ Domain Layer (Pure Logic)
# src/nutrition_calculator.py
def calculate_daily_totals(log_entries):
    """Calculate daily nutrition totals."""
    totals = {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}
    
    for entry in log_entries:
        totals['calories'] += entry['calories']
        totals['protein'] += entry['protein']
        totals['fat'] += entry['fat']
        totals['carbs'] += entry['carbs']
    
    return totals

# ✅ Repository (Data Access)
# repositories/log_repository.py
class LogRepository:
    def get_by_date(self, date):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('SELECT * FROM log WHERE date = ?', (date,))
        return [dict(row) for row in cursor.fetchall()]

# ✅ Service (Orchestration)
# services/stats_service.py
class StatsService:
    def __init__(self, log_repo):
        self.log_repo = log_repo
    
    def get_daily_stats(self, date):
        entries = self.log_repo.get_by_date(date)
        totals = calculate_daily_totals(entries)  # Use domain logic
        return totals

# ✅ Controller (Request Handling)
# routes/stats.py
@stats_bp.route('/api/stats/daily')
def daily_stats():
    date = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))
    stats = stats_service.get_daily_stats(date)
    return jsonify({'success': True, 'data': stats})
```

---

## Implementation Examples

### Example 1: Complete Feature Flow

**Feature:** Calculate product macros at different weights

**1. Domain Layer (Pure Logic):**
```python
# src/nutrition_calculator.py
def scale_nutrition(base_nutrition, base_weight, target_weight):
    """Scale nutrition values for different weight.
    
    Args:
        base_nutrition: Dict with nutrition per base_weight
        base_weight: Base weight in grams (e.g., 100g)
        target_weight: Target weight in grams
        
    Returns:
        Dict with scaled nutrition values
    """
    factor = target_weight / base_weight
    
    return {
        'protein': round(base_nutrition['protein'] * factor, 1),
        'fat': round(base_nutrition['fat'] * factor, 1),
        'carbs': round(base_nutrition['carbs'] * factor, 1),
        'calories': round(base_nutrition['calories'] * factor, 0),
        'fiber': round(base_nutrition.get('fiber', 0) * factor, 1)
    }
```

**2. Service Layer (Orchestration):**
```python
# services/product_service.py
class ProductService:
    def get_product_nutrition_at_weight(self, product_id, weight):
        """Get nutrition info for product at specific weight."""
        # Get product from repository
        product = self.product_repo.get_by_id(product_id)
        
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        # Use domain logic to scale
        base_nutrition = {
            'protein': product['protein'],
            'fat': product['fat'],
            'carbs': product['carbs'],
            'calories': product['calories'],
            'fiber': product.get('fiber', 0)
        }
        
        scaled = scale_nutrition(base_nutrition, 100, weight)
        
        return {
            'product_id': product_id,
            'product_name': product['name'],
            'weight': weight,
            **scaled
        }
```

**3. Controller (API Endpoint):**
```python
# routes/products.py
@products_bp.route('/api/products/<int:product_id>/nutrition')
def get_product_nutrition(product_id):
    """Get nutrition for product at specified weight."""
    try:
        # Get weight from query params (default 100g)
        weight = float(request.args.get('weight', 100))
        
        # Validate input
        if weight <= 0:
            return jsonify({'error': 'Weight must be positive'}), 400
        
        # Call service
        nutrition = product_service.get_product_nutrition_at_weight(
            product_id, weight
        )
        
        # Return response
        return jsonify({'success': True, 'data': nutrition})
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': 'Internal error'}), 500
```

**4. View (Frontend):**
```javascript
// static/js/app.js
async function showProductNutrition(productId, weight) {
    try {
        const response = await fetch(
            `/api/products/${productId}/nutrition?weight=${weight}`
        );
        
        if (!response.ok) {
            throw new Error('Failed to fetch nutrition');
        }
        
        const data = await response.json();
        
        // Display in UI
        document.getElementById('nutrition-display').innerHTML = `
            <h5>${data.data.product_name} (${weight}g)</h5>
            <p>Calories: ${data.data.calories} kcal</p>
            <p>Protein: ${data.data.protein}g</p>
            <p>Fat: ${data.data.fat}g</p>
            <p>Carbs: ${data.data.carbs}g</p>
        `;
        
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to load nutrition information');
    }
}
```

---

## Best Practices

### 1. Keep Controllers Thin

**Controllers should only:**
- Validate HTTP input
- Call services
- Format HTTP responses

```python
# ❌ Bad: Fat controller with business logic
@products_bp.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    
    # ❌ Validation in controller
    if not data.get('name'):
        return jsonify({'error': 'Name required'}), 400
    
    # ❌ Business logic in controller
    keto_index = (data['fat'] / (data['protein'] + data['fat'] + data['carbs'])) * 100
    
    # ❌ Database access in controller
    conn = sqlite3.connect('nutrition.db')
    cursor = conn.execute('INSERT INTO products ...')
    
    return jsonify({'success': True})

# ✅ Good: Thin controller delegates to service
@products_bp.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    result = product_service.create_product(data)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400
```

### 2. Pure Business Logic

**Domain functions should be pure:**
- No side effects
- No external dependencies
- Easy to test

```python
# ✅ Pure function
def calculate_bmi(weight_kg, height_m):
    """Calculate BMI. Pure function, easy to test."""
    if height_m <= 0:
        raise ValueError("Height must be positive")
    return weight_kg / (height_m ** 2)

# ❌ Impure function
def calculate_bmi_and_save(user_id):
    """Not pure: has side effects (database access)."""
    user = db.query('SELECT weight, height FROM users WHERE id = ?', user_id)
    bmi = user['weight'] / (user['height'] ** 2)
    db.execute('UPDATE users SET bmi = ? WHERE id = ?', bmi, user_id)
    return bmi
```

### 3. Dependency Injection

**Inject dependencies instead of creating them:**

```python
# ❌ Bad: Creates own dependencies
class ProductService:
    def __init__(self):
        self.repo = ProductRepository()  # Hard-coded dependency
        self.cache = CacheManager()      # Hard to test

# ✅ Good: Dependencies injected
class ProductService:
    def __init__(self, repo, cache=None):
        self.repo = repo      # Injected, easy to mock
        self.cache = cache    # Optional, can inject fake for tests

# Usage
# Production
service = ProductService(ProductRepository(), CacheManager())

# Testing
service = ProductService(FakeRepository(), FakeCache())
```

### 4. Interface Segregation

**Small, focused interfaces:**

```python
# ❌ Bad: God interface
class DataService:
    def get_product(self): pass
    def save_product(self): pass
    def get_dish(self): pass
    def save_dish(self): pass
    def get_log(self): pass
    def save_log(self): pass
    # ... 50 more methods

# ✅ Good: Segregated interfaces
class ProductRepository:
    def get_by_id(self, id): pass
    def save(self, product): pass

class DishRepository:
    def get_by_id(self, id): pass
    def save(self, dish): pass

class LogRepository:
    def get_by_date(self, date): pass
    def save(self, entry): pass
```

### 5. Single Responsibility

**Each class/function has one reason to change:**

```python
# ❌ Bad: Multiple responsibilities
class ProductManager:
    def get_product(self, id):
        # Database access
        conn = sqlite3.connect('db.db')
        # HTTP request
        response = requests.get(f'/api/products/{id}')
        # Business logic
        keto_index = self.calculate_keto_index(product)
        # Caching
        redis.set(f'product:{id}', json.dumps(product))
        return product

# ✅ Good: Single responsibility per class
class ProductRepository:
    """Responsible for data access only."""
    def get_by_id(self, id): pass

class ProductService:
    """Responsible for business logic only."""
    def calculate_keto_index(self, product): pass

class ProductCache:
    """Responsible for caching only."""
    def get(self, id): pass
    def set(self, id, product): pass
```

---

## Benefits of This Architecture

### 1. Testability

**Easy to test each layer in isolation:**

```python
# Test domain logic - no mocks needed
def test_calculate_calories():
    result = calculate_calories(protein=20, fat=5, carbs=30)
    assert result == 185  # (20*4) + (5*9) + (30*4)

# Test service - mock repository
def test_product_service():
    mock_repo = Mock()
    mock_repo.get_by_id.return_value = {'name': 'Chicken', ...}
    
    service = ProductService(mock_repo)
    result = service.get_product(1)
    
    assert result['name'] == 'Chicken'

# Test controller - mock service
def test_products_endpoint(client):
    with patch('routes.products.product_service') as mock_service:
        mock_service.get_all.return_value = [{'id': 1}]
        
        response = client.get('/api/products')
        assert response.status_code == 200
```

### 2. Maintainability

**Easy to understand and modify:**
- Clear separation of concerns
- Each layer has specific responsibilities
- Changes isolated to relevant layer

### 3. Flexibility

**Easy to swap implementations:**

```python
# Currently: SQLite
product_service = ProductService(SQLiteProductRepository())

# Future: PostgreSQL
product_service = ProductService(PostgresProductRepository())

# Testing: In-memory
product_service = ProductService(InMemoryProductRepository())
```

### 4. Scalability

**Can grow without becoming complex:**
- Add new features without affecting existing code
- New repositories, services, controllers
- Parallel development (different teams, different layers)

---

## References

- [Clean Architecture (Robert C. Martin)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [MVC Pattern](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)

---

**Maintained by:** Nutricount Architecture Team  
**Next Review:** December 2025  
**Contact:** See [CONTRIBUTING.md](../../CONTRIBUTING.md)
