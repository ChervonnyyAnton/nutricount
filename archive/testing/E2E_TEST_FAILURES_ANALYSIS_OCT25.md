# E2E Test Failures Analysis - October 25, 2025

**Workflow Run**: #61 (18804187590)  
**Branch**: main  
**Trigger**: Manual (workflow_dispatch)  
**Date**: October 25, 2025 at 14:13 UTC  
**Status**: ❌ FAILED  
**Link**: https://github.com/ChervonnyyAnton/nutricount/actions/runs/18804187590

---

## 📊 Test Results Summary

### Local Version (Flask Backend) - Job #1
- **Status**: ❌ FAILED
- **Results**: 20 failed, 100 passed
- **Pass Rate**: 83.3% (100/120 tests)
- **Duration**: ~11 minutes

### Public Version (Demo SPA) - Job #2
- **Status**: ❌ FAILED  
- **Results**: 10 failed, 76 passed, 34 skipped
- **Pass Rate**: 88.4% (76/86 runnable tests)
- **Duration**: ~7 minutes

### Overall Statistics
- **Total Tests**: 120 (local) + 86 (public) = 206 tests
- **Total Failures**: 30 tests
- **Combined Pass Rate**: 85.4% (176/206 tests)

---

## 🔍 Root Cause Analysis

### Critical Issue #1: Invalid Playwright API Usage ⚠️ **WIDESPREAD**

**Problem**: Helper function uses invalid `state: 'enabled'` parameter

**Location**: `tests/e2e-playwright/helpers/page-helpers.js`

**Error**:
```javascript
// INCORRECT - 'enabled' is not a valid Playwright state
page.waitForSelector(selector, { state: 'enabled' })
```

**Valid States in Playwright**:
- `'attached'` - Element is attached to DOM
- `'detached'` - Element is detached from DOM
- `'visible'` - Element is visible
- `'hidden'` - Element is hidden

**Impact**: 
- **Affects multiple test files**: logging-workflow.spec.js, product-workflow.spec.js, others
- **Cascading failures**: This causes early test failures that prevent subsequent assertions
- **Severity**: HIGH - This is a **fundamental API usage error**

**Fix Required**:
```javascript
// Option 1: Wait for visible state + check enabled separately
await page.waitForSelector(selector, { state: 'visible' });
const isEnabled = await page.locator(selector).isEnabled();

// Option 2: Use locator API with explicit wait
await page.locator(selector).waitFor({ state: 'visible' });
const isEnabled = await page.locator(selector).isEnabled();

// Option 3: Combined approach
await expect(page.locator(selector)).toBeVisible();
await expect(page.locator(selector)).toBeEnabled();
```

**Files to Fix**:
- `tests/e2e-playwright/helpers/page-helpers.js` - Update helper function
- All test files that call this helper

---

### Critical Issue #2: Modal Visibility Timeouts ⏱️ **HIGH FREQUENCY**

**Problem**: Tests time out waiting for modals to become visible

**Error Pattern**:
```
Test timeout of 30000ms exceeded while waiting for locator('.modal:visible') to be visible
```

**Affected Tests**:
- smoke.spec.js - Modal visibility checks
- product-workflow.spec.js - Product modals
- dish-workflow.spec.js - Dish modals
- Various other modal-based interactions

**Possible Causes**:
1. **Selector mismatch**: The `.modal:visible` selector may not match actual modal elements
2. **Timing issues**: Modals may take longer to appear in CI environment
3. **Animation delays**: Bootstrap modal animations not completing before visibility check
4. **Race conditions**: Modal DOM may exist but not yet visible due to CSS transitions

**Current Timeout**: 30 seconds (reasonable, but may need adjustment)

**Investigation Needed**:
1. Check actual modal HTML structure and classes
2. Verify Bootstrap modal animation timing
3. Review if modal backdrop is interfering
4. Check for any JavaScript errors preventing modal display

**Potential Fixes**:
```javascript
// Option 1: Wait for modal to be present AND visible
await page.waitForSelector('.modal.show', { state: 'visible', timeout: 15000 });

// Option 2: Wait for backdrop + modal
await Promise.all([
  page.waitForSelector('.modal-backdrop.show', { state: 'visible' }),
  page.waitForSelector('.modal.show', { state: 'visible' })
]);

// Option 3: Use Playwright's auto-waiting with locator
await expect(page.locator('.modal.show')).toBeVisible({ timeout: 15000 });
```

---

### Issue #3: Rate Limiting Errors (429) 🚦 **INFORMATIONAL**

**Problem**: Multiple API calls returning 429 (Too Many Requests)

**Observed Pattern**:
```
GET /api/products HTTP/1.1 429
GET /api/dishes HTTP/1.1 429
GET /api/log HTTP/1.1 429
GET /api/stats/2025-10-25 HTTP/1.1 429
GET /api/fasting/status HTTP/1.1 429
```

**Analysis**:
- These appear repeatedly in **both jobs**
- Happens during page load when multiple API calls fire simultaneously
- May be related to rate limiting in the Flask application

**Impact**: 
- **Low to Medium** - May cause flaky test behavior
- Could lead to empty data states in tests
- Not the primary cause of test failures (tests handle this gracefully)

**Note**: This is likely expected behavior for rapid-fire API calls during test execution. Consider:
1. Increasing rate limits for test environment
2. Adding retry logic to handle 429 responses
3. Sequencing API calls instead of parallel requests

---

### Issue #4: Assertion Failures - App Behavior 📉 **TEST-SPECIFIC**

#### A. Fasting Streak Assertion Failure

**Test**: `fasting.spec.js` - Fasting streak display  
**Error**: Assertion expecting text to contain a number failed (hasNumber: false)

**Expected**: Streak counter should display a number  
**Actual**: Text does not contain a number

**Possible Causes**:
1. UI rendering issue - streak not calculating correctly
2. Data not loading before assertion
3. Timing - asserting before fasting data fully loaded
4. Regression in fasting streak calculation logic

**Investigation Needed**:
- Check fasting streak calculation in `src/fasting_manager.py`
- Verify UI rendering in fasting templates
- Review timing of assertions vs data loading

#### B. Console Error Count Failures

**Test**: Multiple tests asserting zero console errors  
**Error**: Expected 0 console errors, but got 6 (or other non-zero count)

**Console Errors Observed** (from logs):
- Favicon 404 errors (expected, non-critical)
- Service Worker registration warnings
- Possibly other non-critical warnings

**Current Behavior**: Tests fail on ANY console error

**Fix Options**:
1. **Filter known non-critical errors** (recommended)
   ```javascript
   const knownNonCritical = [
     'favicon.ico',
     'Service Worker',
     // Add other known safe errors
   ];
   const criticalErrors = consoleErrors.filter(err => 
     !knownNonCritical.some(pattern => err.includes(pattern))
   );
   expect(criticalErrors).toHaveLength(0);
   ```

2. **Use error filtering helper** (already exists)
   - `tests/e2e-playwright/helpers/test-helpers.js` has `captureConsoleErrors()`
   - Ensure all tests use this helper

---

## 🎯 Recommended Fix Priority

### Priority 1: Critical API Fix (1-2 hours)
**Impact**: Fixes ~15-20 tests immediately

1. **Fix waitForSelector state parameter**
   - File: `tests/e2e-playwright/helpers/page-helpers.js`
   - Change: Replace `state: 'enabled'` with valid Playwright state
   - Test: Run affected tests locally to verify fix

### Priority 2: Modal Timeout Investigation (2-3 hours)
**Impact**: Fixes ~8-10 tests

1. **Investigate modal visibility timing**
   - Add debug logging to understand why modals aren't appearing
   - Check for CSS animation timing issues
   - Verify selector accuracy

2. **Implement robust modal waiting helper**
   - Create dedicated `waitForModal()` helper
   - Handle Bootstrap-specific modal behavior
   - Add retries with backoff

### Priority 3: Test Assertion Improvements (1-2 hours)
**Impact**: Fixes ~3-5 tests

1. **Update console error filtering**
   - Ensure `KNOWN_NON_CRITICAL_ERRORS` is comprehensive
   - Apply filtering consistently across all tests

2. **Fix fasting streak test**
   - Investigate why streak number isn't rendering
   - Add proper wait for data loading
   - Verify fasting calculation logic

---

## 📁 Affected Files

### Helper Files (High Impact)
- `tests/e2e-playwright/helpers/page-helpers.js` ⚠️ **CRITICAL**
- `tests/e2e-playwright/helpers/test-helpers.js`

### Test Files (Failures)
- `tests/e2e-playwright/logging-workflow.spec.js` (multiple failures)
- `tests/e2e-playwright/product-workflow.spec.js` (multiple failures)
- `tests/e2e-playwright/smoke.spec.js` (modal timing)
- `tests/e2e-playwright/fasting.spec.js` (streak assertion)
- `tests/e2e-playwright/dish-workflow.spec.js` (modal timing)

### Application Files (Investigation Needed)
- `src/fasting_manager.py` (streak calculation)
- Rate limiting configuration in Flask app

---

## 🔬 Diagnostic Artifacts Available

The workflow run generated artifacts for debugging:

1. **Screenshots** - Visual state at failure point
2. **Videos** - Full test execution recordings  
3. **Trace files** (trace.zip) - Detailed Playwright traces
4. **Server logs** - Flask/Demo server output

**Access**: https://github.com/ChervonnyyAnton/nutricount/actions/runs/18804187590/artifacts

---

## 📈 Historical Context

### Phase 1 & 2 Fixes (Completed)
According to project documentation:
- ✅ Phase 1: Modal & timing fixes (Oct 25) - Fixed 23/28 tests
- ✅ Phase 2: Console error handling (Oct 24) - Filtering implemented

### Phase 3 Status (Current)
- ⏳ **IN PROGRESS**: First CI validation run completed
- **Expected**: 96%+ pass rate (115/120 tests)
- **Actual**: 85.4% pass rate (176/206 tests)
- **Gap**: ~10% below target

### Why Tests Are Failing
According to the analysis:
1. **Invalid Playwright API usage** was introduced or not caught in Phase 1
2. **Modal timing issues** persist despite Phase 1 fixes
3. **Test environment differences** (CI vs local) causing timing variations

---

## 🚀 Next Steps

### Immediate Actions
1. ✅ **Document failures** (this document)
2. 🔧 **Fix invalid API usage** in helpers
3. 🔬 **Investigate modal timing** with debug logging
4. 🧪 **Re-run tests** after fixes

### Short-term (This Week)
1. Implement all Priority 1 fixes
2. Implement Priority 2 fixes
3. Re-enable E2E workflow on PRs once 96%+ achieved
4. Monitor for stability over 3-5 runs

### Long-term (Next Sprint)
1. Implement Priority 3 improvements
2. Add more robust error handling
3. Improve test helper functions
4. Document E2E best practices

---

## 📝 Key Takeaways

### What Went Well ✅
- Test infrastructure is working correctly
- Tests execute in CI environment successfully
- 85.4% pass rate shows most tests are stable
- Comprehensive artifacts generated for debugging

### What Needs Improvement ⚠️
- Helper functions using incorrect Playwright API
- Modal timing not yet fully resolved
- Need better handling of CI timing differences
- Console error filtering not applied everywhere

### Critical Path Forward 🎯
1. Fix the invalid `state: 'enabled'` usage (**HIGH PRIORITY**)
2. Resolve modal visibility timeouts (**MEDIUM PRIORITY**)
3. Apply console error filtering everywhere (**LOW PRIORITY**)
4. Validate fixes and achieve 96%+ pass rate

---

## 🔗 Related Documentation

- **Phase 3 Validation Guide**: `E2E_PHASE3_VALIDATION_GUIDE.md`
- **Quick Start Guide**: `QUICK_START_E2E_PHASE3.md`
- **Phase 1 Fixes**: `SESSION_SUMMARY_OCT25_E2E_TEST_FIXES_PHASE1.md`
- **Phase 2 Fixes**: `E2E_TEST_CONSOLE_ERROR_FIXES.md`
- **Issue Tracking**: `ISSUE_E2E_TEST_FIXES.md`

---

**Document Created**: October 25, 2025  
**Analysis Based On**: Workflow run #61 (18804187590)  
**Status**: ❌ Tests Failing - Fixes Required  
**Target**: 96%+ pass rate (115+/120 tests)
