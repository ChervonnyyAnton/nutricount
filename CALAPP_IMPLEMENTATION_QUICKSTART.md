# Quick Start: Implementing CalApp-Inspired Features

**Goal:** Start implementing high-value, low-complexity features from CalApp  
**Phase:** Phase 1 - Quick Wins  
**Timeline:** 1-2 weeks  
**Status:** Ready to start

---

## 🎯 Phase 1 Features (Priority Order)

### 1. Custom Daily Goals ⭐⭐⭐ (Days 1-3)

**Impact:** HIGH | **Complexity:** LOW | **Time:** 2-3 days

#### What to Build
- Database table for user goals
- API endpoints for setting/getting goals
- UI for goal configuration
- Visual progress indicators in stats
- Goal tracking and calculations

#### Technical Spec

**Database Schema:**
```sql
CREATE TABLE user_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    goal_type TEXT NOT NULL,  -- 'calories', 'protein', 'carbs', 'fat', 'fiber'
    target_value REAL NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, goal_type, is_active)
);

-- Index for fast lookups
CREATE INDEX idx_user_goals_lookup ON user_goals(user_id, is_active);
```

**API Endpoints:**
```
GET    /api/profile/goals         - Get all active goals
POST   /api/profile/goals         - Set/update goals
PUT    /api/profile/goals/:id     - Update specific goal
DELETE /api/profile/goals/:id     - Delete goal
GET    /api/profile/goals/progress/:date  - Get progress for date
```

**Request/Response Examples:**
```json
// POST /api/profile/goals
{
  "goals": [
    {"type": "calories", "target": 2000},
    {"type": "protein", "target": 150},
    {"type": "carbs", "target": 20},
    {"type": "fat", "target": 150}
  ]
}

// GET /api/profile/goals/progress/2025-10-26
{
  "date": "2025-10-26",
  "goals": {
    "calories": {"target": 2000, "current": 1450, "percentage": 72.5, "remaining": 550},
    "protein": {"target": 150, "current": 98, "percentage": 65.3, "remaining": 52},
    "carbs": {"target": 20, "current": 15, "percentage": 75.0, "remaining": 5},
    "fat": {"target": 150, "current": 82, "percentage": 54.7, "remaining": 68}
  }
}
```

**Frontend Components:**
- Goals settings page/modal
- Progress bars in stats view
- Goal indicators in daily log
- Quick goal adjustment buttons

**Implementation Steps:**
1. Create migration script for database
2. Create routes/goals.py with CRUD endpoints
3. Add goal calculation logic to stats.py
4. Create frontend UI components
5. Add visual progress indicators
6. Write unit tests
7. Write integration tests
8. Update documentation

**Test Cases:**
- Set single goal
- Set multiple goals
- Update existing goal
- Delete goal
- Get progress for current day
- Get progress for past days
- Goal over-achievement handling
- Invalid goal values
- Negative values
- Zero values

---

### 2. Quick Add Favorites ⭐⭐⭐ (Days 4-6)

**Impact:** HIGH | **Complexity:** LOW | **Time:** 2-3 days

#### What to Build
- Favorite flag for products and dishes
- Recently used items tracking
- Quick access UI elements
- Favorite toggle functionality
- Search filter for favorites

#### Technical Spec

**Database Schema:**
```sql
-- Add columns to existing tables
ALTER TABLE products ADD COLUMN is_favorite BOOLEAN DEFAULT 0;
ALTER TABLE products ADD COLUMN last_used TIMESTAMP;
ALTER TABLE dishes ADD COLUMN is_favorite BOOLEAN DEFAULT 0;
ALTER TABLE dishes ADD COLUMN last_used TIMESTAMP;

-- Indexes for performance
CREATE INDEX idx_products_favorite ON products(is_favorite, last_used);
CREATE INDEX idx_dishes_favorite ON dishes(is_favorite, last_used);
```

**API Endpoints:**
```
POST   /api/products/:id/favorite   - Toggle favorite
GET    /api/products/favorites      - Get favorite products
GET    /api/products/recent         - Get recently used products
POST   /api/dishes/:id/favorite     - Toggle favorite
GET    /api/dishes/favorites        - Get favorite dishes
GET    /api/dishes/recent           - Get recently used dishes
```

**Request/Response Examples:**
```json
// POST /api/products/123/favorite
{
  "is_favorite": true
}

// Response
{
  "success": true,
  "product_id": 123,
  "is_favorite": true
}

// GET /api/products/favorites
{
  "favorites": [
    {"id": 1, "name": "Chicken Breast", "calories": 165, "last_used": "2025-10-26T10:30:00"},
    {"id": 5, "name": "Avocado", "calories": 160, "last_used": "2025-10-25T14:20:00"}
  ]
}

// GET /api/products/recent?limit=10
{
  "recent": [
    {"id": 10, "name": "Eggs", "calories": 143, "last_used": "2025-10-26T08:15:00"},
    {"id": 1, "name": "Chicken Breast", "calories": 165, "last_used": "2025-10-26T10:30:00"}
  ]
}
```

**Frontend Components:**
- Star icon button for favorites
- Favorites tab/section
- Recent items list
- Quick add button
- Filter toggle in search

**Implementation Steps:**
1. Database migration (add columns)
2. Update products.py routes with favorite endpoints
3. Update dishes.py routes with favorite endpoints
4. Update log.py to track last_used timestamp
5. Create frontend favorite toggle
6. Add favorites section to UI
7. Add recent items list
8. Implement search filters
9. Write unit tests
10. Write integration tests
11. Update documentation

**Test Cases:**
- Toggle favorite on/off
- Get favorites list
- Get recent items
- Update last_used on log entry
- Search with favorites filter
- Sort by last used
- Empty favorites list
- Empty recent list
- Concurrent favorite updates

---

### 3. Meal Templates ⭐⭐ (Days 7-10)

**Impact:** MEDIUM | **Complexity:** LOW | **Time:** 3-4 days

#### What to Build
- Template creation from scratch
- Template creation from log entries
- Template categories
- Quick add template to log
- Template management UI

#### Technical Spec

**Database Schema:**
```sql
CREATE TABLE meal_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    name TEXT NOT NULL,
    category TEXT DEFAULT 'other',  -- 'breakfast', 'lunch', 'dinner', 'snack', 'other'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE meal_template_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    item_type TEXT NOT NULL,  -- 'product' or 'dish'
    item_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    notes TEXT,
    FOREIGN KEY (template_id) REFERENCES meal_templates(id) ON DELETE CASCADE
);

CREATE INDEX idx_templates_user ON meal_templates(user_id);
CREATE INDEX idx_template_items ON meal_template_items(template_id);
```

**API Endpoints:**
```
GET    /api/meals/templates              - Get all templates
POST   /api/meals/templates              - Create template
GET    /api/meals/templates/:id          - Get template details
PUT    /api/meals/templates/:id          - Update template
DELETE /api/meals/templates/:id          - Delete template
POST   /api/meals/templates/:id/add-to-log  - Add template to log
POST   /api/meals/templates/from-log     - Create template from log entries
```

**Request/Response Examples:**
```json
// POST /api/meals/templates
{
  "name": "Keto Breakfast",
  "category": "breakfast",
  "description": "My standard keto breakfast",
  "items": [
    {"type": "product", "id": 10, "quantity": 200, "notes": "3 eggs"},
    {"type": "product", "id": 5, "quantity": 50, "notes": "Half avocado"},
    {"type": "product", "id": 23, "quantity": 30, "notes": "Cheese"}
  ]
}

// Response
{
  "success": true,
  "template_id": 1,
  "name": "Keto Breakfast",
  "total_calories": 450,
  "total_protein": 35,
  "total_carbs": 8,
  "total_fat": 32
}

// POST /api/meals/templates/1/add-to-log
{
  "date": "2025-10-26",
  "meal_time": "breakfast"
}

// Response
{
  "success": true,
  "entries_added": 3,
  "total_calories": 450
}

// POST /api/meals/templates/from-log
{
  "name": "Today's Dinner",
  "category": "dinner",
  "date": "2025-10-26",
  "meal_time": "dinner"
}
```

**Frontend Components:**
- Templates management page
- Template creation modal
- Quick add template button
- Template categories
- Template preview
- "Save as template" button in log

**Implementation Steps:**
1. Create database schema
2. Create routes/meals.py with endpoints
3. Add template CRUD operations
4. Add template to log functionality
5. Create from log functionality
6. Calculate template nutrition
7. Create frontend UI
8. Add template management page
9. Add quick add buttons
10. Write unit tests
11. Write integration tests
12. Update documentation

**Test Cases:**
- Create empty template
- Create template with items
- Create template from log
- Add template to log
- Update template
- Delete template
- Get template nutrition
- Template with products only
- Template with dishes only
- Template with both
- Invalid template data
- Missing items
- Duplicate template names

---

### 4. Enhanced Charts ⭐⭐ (Days 11-13)

**Impact:** MEDIUM | **Complexity:** LOW | **Time:** 2-3 days

#### What to Build
- Chart.js integration
- Weekly trend charts
- Macro distribution pie charts
- Goal progress rings
- Interactive tooltips
- Export charts as images

#### Technical Spec

**Frontend Library:**
```json
{
  "chart.js": "^4.4.0"
}
```

**Chart Types to Add:**
1. **Weekly Calorie Trend** (Bar Chart)
   - X-axis: Days of week
   - Y-axis: Calories
   - Show goal line
   - Color-code above/below goal

2. **Macro Distribution** (Pie/Doughnut Chart)
   - Protein percentage
   - Carbs percentage
   - Fat percentage
   - Color-coded by macro

3. **Goal Progress** (Radial/Gauge Charts)
   - Daily goal completion
   - Multiple gauges for each macro
   - Color gradient based on progress

4. **Monthly Overview** (Line Chart)
   - Trend over 30 days
   - Multiple lines (calories, protein, carbs, fat)
   - Smoothed curves

**Implementation Steps:**
1. Add Chart.js to dependencies
2. Create chart wrapper components
3. Enhance stats API with chart data
4. Create weekly trend chart
5. Create macro distribution chart
6. Create goal progress charts
7. Create monthly overview chart
8. Add chart export functionality
9. Make charts responsive
10. Add accessibility labels
11. Write tests
12. Update documentation

**Test Cases:**
- Chart renders correctly
- Data updates on date change
- Charts are responsive
- Export works
- Accessibility labels present
- Empty data handling
- Large dataset handling

---

## 📋 Development Workflow

### Day-by-Day Plan

**Week 1:**
- **Day 1:** Custom Goals - Database & Backend
- **Day 2:** Custom Goals - Frontend & Integration
- **Day 3:** Custom Goals - Testing & Polish
- **Day 4:** Favorites - Database & Backend
- **Day 5:** Favorites - Frontend & Integration
- **Day 6:** Favorites - Testing & Polish
- **Day 7:** Weekend - Buffer / Documentation

**Week 2:**
- **Day 8:** Meal Templates - Database & Backend
- **Day 9:** Meal Templates - Frontend (Part 1)
- **Day 10:** Meal Templates - Frontend (Part 2) & Testing
- **Day 11:** Enhanced Charts - Setup & Bar Charts
- **Day 12:** Enhanced Charts - Pie & Gauge Charts
- **Day 13:** Enhanced Charts - Testing & Polish
- **Day 14:** Weekend - Buffer / Final Testing

---

## 🧪 Testing Strategy

### Unit Tests (TDD Approach)
- Write tests before implementation
- Test all edge cases
- Mock database calls
- Test validation logic
- Aim for >90% coverage

### Integration Tests
- Test API endpoints end-to-end
- Test with real database (in-memory)
- Test error scenarios
- Test concurrent operations

### Manual Testing Checklist
- [ ] Goals can be set and displayed
- [ ] Progress bars update correctly
- [ ] Favorites toggle works
- [ ] Recent items populate
- [ ] Templates save and load
- [ ] Templates add to log correctly
- [ ] Charts render properly
- [ ] Charts are responsive
- [ ] All forms validate input
- [ ] Error messages are user-friendly

---

## 📦 Dependencies

### Python (Backend)
No new dependencies needed! ✅
All features use existing Flask infrastructure.

### JavaScript (Frontend)
```json
{
  "chart.js": "^4.4.0"
}
```

**Installation:**
```bash
npm install chart.js@^4.4.0
# or add to existing package.json
```

---

## 🚀 Getting Started

### Step 1: Create Feature Branch
```bash
git checkout -b feature/calapp-phase1
```

### Step 2: Set Up Environment
```bash
export PYTHONPATH=/home/runner/work/nutricount/nutricount
mkdir -p logs
```

### Step 3: Run Tests (Baseline)
```bash
pytest tests/ -v
# Ensure all 844 tests pass
```

### Step 4: Start with Custom Goals
```bash
# Create database migration
touch scripts/migrations/add_user_goals.sql

# Create routes file
touch routes/goals.py

# Create tests
touch tests/unit/test_goals.py
touch tests/integration/test_goals_api.py
```

### Step 5: Test-Driven Development
```bash
# Write test first
# Run test (should fail)
pytest tests/unit/test_goals.py -v

# Implement feature
# Run test (should pass)
pytest tests/unit/test_goals.py -v

# Refactor
# Run all tests
pytest tests/ -v
```

---

## 📊 Success Criteria

### Phase 1 Complete When:
- [ ] All 4 features implemented
- [ ] All tests pass (>90% coverage)
- [ ] Documentation updated
- [ ] Manual testing checklist complete
- [ ] Code reviewed
- [ ] No regressions in existing features
- [ ] Performance acceptable (<200ms response)
- [ ] Accessible (WCAG 2.2 AA)
- [ ] Works on mobile devices
- [ ] Works offline (PWA)

---

## 🎯 Next Steps After Phase 1

1. User feedback collection
2. Performance optimization
3. UI/UX polish
4. Start Phase 2 planning (Voice Input & Barcode Scanner)

---

**Ready to start?** Begin with Custom Daily Goals! 🚀

See `CALAPP_REFERENCE_ANALYSIS.md` for full feature list and `docs/CALAPP_FEATURE_COMPARISON.md` for detailed comparison.
