# Phase 4: Code Modularization - Next Steps

## Current Progress (October 21, 2025)

### ✅ Completed
1. **Products Blueprint** - COMPLETE
   - Created `routes/products.py` (480 lines)
   - 2 endpoints extracted:
     - `GET/POST /api/products`
     - `GET/PUT/DELETE /api/products/<id>`
   - Registered in app.py
   - All 574 tests passing ✅
   - Zero linting errors ✅

2. **App.py Reduction**
   - Before: 2401 lines
   - After: 1986 lines
   - **Reduction: -415 lines (-17%)**

### 📋 Remaining Work

#### Blueprints to Create (Est. 1500+ lines to extract)

1. **routes/dishes.py** (Est. 410 lines)
   - `GET/POST /api/dishes` - List and create dishes
   - `GET/PUT/DELETE /api/dishes/<id>` - Get, update, delete dish
   - Current location: app.py lines ~283-692
   - Dependencies: validate_dish_data, RecipeIngredient, calculate_recipe_nutrition

2. **routes/log.py** (Est. 350 lines)
   - `GET/POST /api/log` - List and create log entries
   - `GET/PUT/DELETE /api/log/<id>` - Get, update, delete log entry
   - Current location: app.py lines ~693-1042
   - Dependencies: validate_log_data, MEAL_TYPES

3. **routes/stats.py** (Est. 550 lines)
   - `GET /api/stats/<date_str>` - Daily statistics
   - `GET /api/stats/weekly/<date_str>` - Weekly statistics
   - Current location: app.py lines ~1022-1572
   - Dependencies: calculate_gki, calculate_keto_index_advanced
   - Note: Very large functions, good candidates for further refactoring

4. **routes/profile.py** (Est. 280 lines)
   - `POST /api/gki` - Calculate GKI
   - `GET/POST/PUT /api/profile` - User profile management
   - `GET /api/profile/macros` - Calculate macros
   - Current location: app.py lines ~1565-1845
   - Dependencies: calculate_bmr_*, calculate_tdee, calculate_*_macros

### Execution Strategy

#### Step-by-Step Approach (Recommended)

Extract one blueprint at a time, testing after each:

1. **Create routes/dishes.py** (1-2 hours)
   - Copy dishes routes from app.py
   - Convert to blueprint format (change `@app.route` to `@dishes_bp.route`)
   - Add helper functions (safe_get_json, get_db)
   - Import all dependencies
   - Test extraction

2. **Register dishes blueprint** (15 minutes)
   - Import in app.py: `from routes.dishes import dishes_bp`
   - Register: `app.register_blueprint(dishes_bp)`
   - Delete old routes from app.py
   - Clean up unused imports
   - Run tests (should pass 574/574)

3. **Repeat for log.py** (1-2 hours)
   - Follow same pattern as dishes
   - Test after extraction

4. **Repeat for stats.py** (2-3 hours)
   - **Note**: Stats routes are very large (daily_stats: 247 lines, weekly_stats: 296 lines)
   - Consider splitting into smaller functions during extraction
   - May require additional refactoring

5. **Repeat for profile.py** (1-2 hours)
   - Includes GKI calculator endpoint
   - Follow same pattern

**Total Time Estimate: 6-10 hours**

#### Batch Approach (Alternative)

Create all blueprints at once, then test:
- Faster but riskier (harder to debug if issues arise)
- Not recommended due to code complexity

### Expected Results

After completing all extractions:

- **app.py**: 1986 → ~500 lines (-75%)
- **Blueprints**: 5 → 10 modules
- **Code organization**: Significantly improved
- **Maintainability**: Much easier to navigate
- **Tests**: 574/574 passing (maintained)
- **Coverage**: 93.48% (maintained)

### Blueprint Template

For consistency, each blueprint should follow this structure:

```python
"""
[Resource] routes for Nutricount application.
Handles CRUD operations for [resource].
"""

import sqlite3
from flask import Blueprint, current_app, jsonify, request
from werkzeug.exceptions import BadRequest

# Import dependencies
from src.config import Config
from src.constants import ERROR_MESSAGES, HTTP_*, SUCCESS_MESSAGES
from src.monitoring import monitor_http_request
from src.security import rate_limit
from src.utils import json_response, safe_float, validate_*_data

# Helper functions
def safe_get_json():
    """Safely get JSON data from request"""
    try:
        return request.get_json() or {}
    except BadRequest:
        return None

def get_db():
    """Get database connection with proper configuration"""
    db = sqlite3.connect(current_app.config["DATABASE"])
    db.row_factory = sqlite3.Row
    if current_app.config["DATABASE"] != ":memory:":
        db.execute("PRAGMA journal_mode = WAL")
        db.execute("PRAGMA synchronous = NORMAL")
    db.execute("PRAGMA foreign_keys = ON")
    return db

# Create blueprint
[resource]_bp = Blueprint("[resource]", __name__, url_prefix="/api/[resource]")

@[resource]_bp.route("", methods=["GET", "POST"])
@monitor_http_request
@rate_limit("api")
def [resource]_api():
    """[Resource] CRUD endpoint"""
    # Implementation here
    pass

@[resource]_bp.route("/<int:[resource]_id>", methods=["GET", "PUT", "DELETE"])
def [resource]_detail_api([resource]_id):
    """Individual [resource] operations"""
    # Implementation here
    pass
```

### Notes

- Always run tests after each extraction
- Check linting after each change
- Commit after each successful extraction
- Document any issues or deviations
- Consider extracting service layer in future phases

### Success Criteria

- ✅ All 574 tests passing
- ✅ Zero linting errors
- ✅ Coverage maintained at 93%+
- ✅ app.py reduced by 70%+
- ✅ All endpoints working correctly
- ✅ Clean, maintainable code structure

---

**Status**: Products extraction complete, 4 blueprints remaining
**Next Action**: Extract dishes blueprint
**Priority**: Medium (code organization improvement)
**Risk**: Low (proven pattern, comprehensive tests)
