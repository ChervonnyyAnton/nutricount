# ✅ Demo Testing Checklist

After deploying the demo to GitHub Pages, verify all features work correctly.

## Quick Test (2 minutes)

1. **Load Demo**
   - [ ] Visit https://chervonnyyanton.github.io/nutricount/
   - [ ] Page loads without errors
   - [ ] Bootstrap CSS loads (page has styling)
   - [ ] No console errors in browser DevTools

2. **Add Sample Product**
   - [ ] Click "Load Sample Data" button
   - [ ] Verify products appear in Products tab
   - [ ] Check "Chicken Breast" is listed with keto index

3. **Log Food**
   - [ ] Go to Daily Log tab
   - [ ] Select a product from dropdown
   - [ ] Enter quantity (e.g., 150g)
   - [ ] Click "Add to Log"
   - [ ] Verify entry appears in log table

4. **View Statistics**
   - [ ] Go to Statistics tab
   - [ ] Verify daily totals show (calories, protein, etc.)
   - [ ] Numbers should be non-zero if you logged food

5. **Theme Toggle**
   - [ ] Click 🌓 button in header
   - [ ] Theme should switch (dark ↔️ light)
   - [ ] Preference should persist after refresh

## Comprehensive Test (5 minutes)

### Products Tab

**Add Product:**
- [ ] Fill in all fields (name, calories, protein, fat, carbs)
- [ ] Click "Add Product"
- [ ] Product appears in table
- [ ] Keto Index is calculated automatically

**Delete Product:**
- [ ] Click delete (🗑️) button
- [ ] Product is removed from list
- [ ] No errors in console

**Sample Data:**
- [ ] Click "Load Sample Data"
- [ ] 8 products are added
- [ ] Each has correct macro values
- [ ] Keto index calculated for each

### Daily Log Tab

**Add Entry:**
- [ ] Select today's date
- [ ] Choose product from dropdown (should show all products)
- [ ] Enter quantity (100g)
- [ ] Select meal time (breakfast, lunch, dinner, snack)
- [ ] Click "Add to Log"
- [ ] Entry appears in log table with calculated macros

**View Entries:**
- [ ] Table shows: product name, quantity, calories, protein, fat, carbs
- [ ] Macros are calculated based on quantity (not per 100g)
- [ ] Meal time is displayed

**Delete Entry:**
- [ ] Click delete button on an entry
- [ ] Entry is removed
- [ ] Statistics update accordingly

**Date Selection:**
- [ ] Change date
- [ ] Log entries for that date are shown
- [ ] Empty dates show "No entries" message

### Statistics Tab

**Daily View:**
- [ ] Shows total calories for selected date
- [ ] Shows total protein (g)
- [ ] Shows total fat (g)
- [ ] Shows total carbs (g)
- [ ] Shows number of meals/entries
- [ ] Values match sum of log entries

**Date Selection:**
- [ ] Change date
- [ ] Statistics update for new date
- [ ] Dates with no entries show zeros

**Calculations:**
- [ ] Add log entry
- [ ] Go to Statistics
- [ ] Totals should update immediately
- [ ] Values should be accurate (check manually)

### Theme System

**Light Theme:**
- [ ] Background is light/white
- [ ] Text is dark/black
- [ ] Good contrast
- [ ] All elements visible

**Dark Theme:**
- [ ] Background is dark
- [ ] Text is light/white
- [ ] Good contrast
- [ ] All elements visible

**Persistence:**
- [ ] Set theme to dark
- [ ] Refresh page
- [ ] Theme remains dark
- [ ] Same for light theme

### Mobile Responsiveness

**Mobile View (< 768px):**
- [ ] Open browser DevTools (F12)
- [ ] Toggle device toolbar (Ctrl+Shift+M)
- [ ] Select mobile device (iPhone, Android)
- [ ] Layout adapts to narrow screen
- [ ] Buttons are touch-friendly (large enough)
- [ ] Tables scroll horizontally if needed
- [ ] Forms are usable
- [ ] Tab navigation works

**Tablet View (768px - 1024px):**
- [ ] Select tablet device in DevTools
- [ ] Layout uses available space well
- [ ] No awkward gaps or overlaps

**Desktop View (> 1024px):**
- [ ] Full-width layout
- [ ] Content centered
- [ ] Maximum 1200px container width

### Data Persistence

**LocalStorage:**
- [ ] Add products and log entries
- [ ] Close browser tab
- [ ] Open demo again
- [ ] All data should still be there

**Clear Data:**
- [ ] Click "Clear Data" button (if present)
- [ ] All products and entries removed
- [ ] LocalStorage is cleared
- [ ] Can start fresh

### PWA Features

**Manifest:**
- [ ] Check browser console for manifest errors
- [ ] Icons should load (check Network tab)
- [ ] Theme color applied to browser chrome

**Install as App (optional):**
- [ ] Chrome: Look for install icon in address bar
- [ ] Click to install
- [ ] App installs on desktop/home screen
- [ ] Opens in standalone window

### Browser Compatibility

Test in multiple browsers:
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (if Mac/iOS)
- [ ] Chrome Mobile (Android)
- [ ] Safari Mobile (iOS)

### Performance

**Load Time:**
- [ ] First load: < 3 seconds
- [ ] Cached load: < 1 second
- [ ] No significant lag

**Console:**
- [ ] No JavaScript errors
- [ ] No 404 errors (check Network tab)
- [ ] No warnings (except possibly Bootstrap peer dependencies)

**Network:**
- [ ] Bootstrap CDN loads (CSS + JS)
- [ ] index.html loads
- [ ] manifest.json loads
- [ ] Total size: ~120KB

## Automated Testing (Future)

For CI/CD integration, consider:
- Playwright for E2E browser testing
- Lighthouse for performance audits
- axe-core for accessibility testing
- Mobile device testing service

## Issue Reporting

If you find bugs, report with:
- [ ] Browser and version
- [ ] Device (desktop, mobile, tablet)
- [ ] Steps to reproduce
- [ ] Expected vs actual behavior
- [ ] Console errors (F12 → Console)
- [ ] Network errors (F12 → Network)
- [ ] Screenshots if relevant

---

**Status**: ✅ Ready for testing  
**Priority**: Test after first deployment  
**Time Required**: 2-10 minutes depending on depth
