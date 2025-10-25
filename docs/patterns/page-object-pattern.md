# Page Object Pattern for E2E Tests

**Pattern Type**: Structural (Testing)  
**Complexity**: Medium  
**Use Case**: Organizing and maintaining Playwright E2E tests  
**Status**: 📋 Design Document (Recommended for Implementation)

---

## 🎯 Overview

The Page Object Pattern is a design pattern that creates an object-oriented class representation of a web page or component. Instead of writing selectors and actions directly in test files, you encapsulate them in page objects, making tests more maintainable and readable.

### Benefits for Nutricount E2E Tests

- **Maintainability**: Change selectors in one place
- **Readability**: Tests read like user stories
- **Reusability**: Share page logic across tests
- **Type Safety**: Better IDE support and autocomplete
- **Reduced Duplication**: DRY principle for test code

---

## 📋 Problems Solved

### Without Page Objects (Current State)

```javascript
// ❌ Hard to maintain, repetitive, coupled to implementation
test('should add food to log', async ({ page }) => {
  await page.goto('/');
  await page.click('text=Daily Log');
  await page.click('button:has-text("Add Food")');
  await page.waitForSelector('.modal:visible', { timeout: 15000 });
  await page.selectOption('#item-type', 'product');
  await page.selectOption('#item-id', '1');
  await page.fill('#quantity', '100');
  await page.selectOption('#meal-time', 'breakfast');
  await page.click('button:has-text("Save")');
  await page.waitForSelector('.modal', { state: 'hidden' });
  
  const logEntry = await page.locator('.log-entry').first();
  expect(await logEntry.textContent()).toContain('Test Product');
});

// ❌ If modal selector changes, must update ALL tests
test('should edit food entry', async ({ page }) => {
  // ... same selectors repeated ...
  await page.waitForSelector('.modal:visible', { timeout: 15000 });
  // ... more duplication ...
});
```

### With Page Objects (Proposed)

```javascript
// ✅ Clean, maintainable, readable
test('should add food to log', async ({ page }) => {
  const dailyLogPage = new DailyLogPage(page);
  
  await dailyLogPage.navigate();
  await dailyLogPage.addFoodEntry({
    type: 'product',
    id: 1,
    quantity: 100,
    mealTime: 'breakfast'
  });
  
  await expect(dailyLogPage.logEntries.first()).toContainText('Test Product');
});

// ✅ Same selectors, different tests - no duplication
test('should edit food entry', async ({ page }) => {
  const dailyLogPage = new DailyLogPage(page);
  
  await dailyLogPage.navigate();
  await dailyLogPage.editFirstEntry({ quantity: 150 });
  
  await expect(dailyLogPage.firstEntry.quantity).toHaveText('150g');
});
```

---

## 🏗️ Page Object Structure

### Base Page Class

```javascript
// tests/e2e-playwright/pages/BasePage.js
class BasePage {
  constructor(page) {
    this.page = page;
    this.baseURL = process.env.BASE_URL || 'http://localhost:5000';
  }
  
  async navigate(path = '/') {
    await this.page.goto(`${this.baseURL}${path}`);
    await this.page.waitForLoadState('networkidle');
  }
  
  async waitForModal() {
    await this.page.waitForSelector('.modal:visible', { 
      timeout: 15000 
    });
    await this.page.waitForLoadState('domcontentloaded');
  }
  
  async closeModal() {
    await this.page.waitForSelector('.modal', { 
      state: 'hidden',
      timeout: 15000 
    });
  }
  
  async clickWhenReady(selector) {
    const element = this.page.locator(selector);
    await element.waitFor({ state: 'visible', timeout: 10000 });
    await element.click();
  }
  
  async fillForm(data) {
    for (const [selector, value] of Object.entries(data)) {
      await this.page.fill(selector, value);
    }
  }
  
  async screenshot(name) {
    await this.page.screenshot({ 
      path: `test-results/screenshots/${name}.png` 
    });
  }
}

module.exports = BasePage;
```

### Navigation Component

```javascript
// tests/e2e-playwright/components/NavigationComponent.js
class NavigationComponent {
  constructor(page) {
    this.page = page;
    
    // Selectors
    this.navBar = page.locator('nav.navbar');
    this.tabs = {
      dailyLog: page.locator('a[href="#daily-log"]'),
      products: page.locator('a[href="#products"]'),
      dishes: page.locator('a[href="#dishes"]'),
      fasting: page.locator('a[href="#fasting"]'),
      statistics: page.locator('a[href="#statistics"]')
    };
  }
  
  async goToTab(tabName) {
    const tab = this.tabs[tabName];
    if (!tab) throw new Error(`Unknown tab: ${tabName}`);
    
    await tab.click();
    await this.page.waitForLoadState('domcontentloaded');
  }
  
  async isTabActive(tabName) {
    const tab = this.tabs[tabName];
    return await tab.getAttribute('class').then(c => c.includes('active'));
  }
}

module.exports = NavigationComponent;
```

### Modal Component

```javascript
// tests/e2e-playwright/components/ModalComponent.js
class ModalComponent {
  constructor(page, modalSelector = '.modal') {
    this.page = page;
    this.modalSelector = modalSelector;
    
    // Selectors
    this.modal = page.locator(modalSelector);
    this.title = this.modal.locator('.modal-title');
    this.closeButton = this.modal.locator('button.btn-close');
    this.saveButton = this.modal.locator('button:has-text("Save")');
    this.cancelButton = this.modal.locator('button:has-text("Cancel")');
  }
  
  async waitForVisible() {
    await this.page.waitForSelector(`${this.modalSelector}:visible`, {
      timeout: 15000
    });
    await this.page.waitForLoadState('domcontentloaded');
  }
  
  async waitForHidden() {
    await this.page.waitForSelector(this.modalSelector, {
      state: 'hidden',
      timeout: 15000
    });
  }
  
  async getTitle() {
    return await this.title.textContent();
  }
  
  async save() {
    await this.saveButton.click();
    await this.waitForHidden();
  }
  
  async cancel() {
    await this.cancelButton.click();
    await this.waitForHidden();
  }
  
  async close() {
    await this.closeButton.click();
    await this.waitForHidden();
  }
  
  async fillField(selector, value) {
    const field = this.modal.locator(selector);
    await field.fill(value);
  }
  
  async selectOption(selector, value) {
    const field = this.modal.locator(selector);
    await field.selectOption(value);
  }
}

module.exports = ModalComponent;
```

---

## 📄 Page Object Examples

### Daily Log Page

```javascript
// tests/e2e-playwright/pages/DailyLogPage.js
const BasePage = require('./BasePage');
const NavigationComponent = require('../components/NavigationComponent');
const ModalComponent = require('../components/ModalComponent');

class DailyLogPage extends BasePage {
  constructor(page) {
    super(page);
    this.navigation = new NavigationComponent(page);
    
    // Selectors
    this.addFoodButton = page.locator('button:has-text("Add Food")');
    this.logEntries = page.locator('.log-entry');
    this.totalCalories = page.locator('#total-calories');
    this.totalProtein = page.locator('#total-protein');
    this.emptyMessage = page.locator('.empty-log-message');
    
    // Date picker
    this.dateInput = page.locator('input[type="date"]');
    this.prevDayButton = page.locator('button[data-action="prev-day"]');
    this.nextDayButton = page.locator('button[data-action="next-day"]');
  }
  
  async navigate() {
    await super.navigate('/');
    await this.navigation.goToTab('dailyLog');
  }
  
  async addFoodEntry({ type, id, quantity, mealTime = 'breakfast', notes = '' }) {
    // Click add button
    await this.addFoodButton.click();
    
    // Wait for modal
    const modal = new ModalComponent(this.page, '#add-food-modal');
    await modal.waitForVisible();
    
    // Fill form
    await modal.selectOption('#item-type', type);
    await modal.selectOption('#item-id', String(id));
    await modal.fillField('#quantity', String(quantity));
    await modal.selectOption('#meal-time', mealTime);
    if (notes) {
      await modal.fillField('#notes', notes);
    }
    
    // Save
    await modal.save();
  }
  
  async editFirstEntry(updates) {
    const editButton = this.logEntries.first().locator('button.edit-entry');
    await editButton.click();
    
    const modal = new ModalComponent(this.page, '#edit-food-modal');
    await modal.waitForVisible();
    
    if (updates.quantity) {
      await modal.fillField('#quantity', String(updates.quantity));
    }
    if (updates.mealTime) {
      await modal.selectOption('#meal-time', updates.mealTime);
    }
    if (updates.notes !== undefined) {
      await modal.fillField('#notes', updates.notes);
    }
    
    await modal.save();
  }
  
  async deleteFirstEntry() {
    const deleteButton = this.logEntries.first().locator('button.delete-entry');
    await deleteButton.click();
    
    // Confirm deletion
    await this.page.locator('button:has-text("Confirm")').click();
  }
  
  async getEntryCount() {
    return await this.logEntries.count();
  }
  
  async getTotalCalories() {
    const text = await this.totalCalories.textContent();
    return parseFloat(text);
  }
  
  async getTotalProtein() {
    const text = await this.totalProtein.textContent();
    return parseFloat(text);
  }
  
  async selectDate(date) {
    await this.dateInput.fill(date);
    await this.page.waitForLoadState('networkidle');
  }
  
  async goToPreviousDay() {
    await this.prevDayButton.click();
    await this.page.waitForLoadState('networkidle');
  }
  
  async goToNextDay() {
    await this.nextDayButton.click();
    await this.page.waitForLoadState('networkidle');
  }
  
  async clearLog() {
    await this.page.locator('button:has-text("Clear Log")').click();
    await this.page.locator('button:has-text("Confirm")').click();
  }
  
  async isLogEmpty() {
    return await this.emptyMessage.isVisible();
  }
}

module.exports = DailyLogPage;
```

### Products Page

```javascript
// tests/e2e-playwright/pages/ProductsPage.js
const BasePage = require('./BasePage');
const NavigationComponent = require('../components/NavigationComponent');
const ModalComponent = require('../components/ModalComponent');

class ProductsPage extends BasePage {
  constructor(page) {
    super(page);
    this.navigation = new NavigationComponent(page);
    
    // Selectors
    this.addProductButton = page.locator('button:has-text("Add Product")');
    this.searchInput = page.locator('input[placeholder*="Search"]');
    this.productCards = page.locator('.product-card');
    this.categoryFilter = page.locator('select#category-filter');
  }
  
  async navigate() {
    await super.navigate('/');
    await this.navigation.goToTab('products');
  }
  
  async createProduct({ name, brand, category, calories, protein, fat, carbs }) {
    await this.addProductButton.click();
    
    const modal = new ModalComponent(this.page, '#product-modal');
    await modal.waitForVisible();
    
    await modal.fillField('#product-name', name);
    if (brand) await modal.fillField('#brand', brand);
    if (category) await modal.selectOption('#category', category);
    await modal.fillField('#calories', String(calories));
    await modal.fillField('#protein', String(protein));
    await modal.fillField('#fat', String(fat));
    await modal.fillField('#carbs', String(carbs));
    
    await modal.save();
  }
  
  async searchProduct(query) {
    await this.searchInput.fill(query);
    await this.page.waitForLoadState('networkidle');
  }
  
  async filterByCategory(category) {
    await this.categoryFilter.selectOption(category);
    await this.page.waitForLoadState('networkidle');
  }
  
  async getProductCard(productName) {
    return this.productCards.filter({ hasText: productName }).first();
  }
  
  async editProduct(productName, updates) {
    const card = await this.getProductCard(productName);
    await card.locator('button.edit-product').click();
    
    const modal = new ModalComponent(this.page, '#product-modal');
    await modal.waitForVisible();
    
    if (updates.name) await modal.fillField('#product-name', updates.name);
    if (updates.calories) await modal.fillField('#calories', String(updates.calories));
    if (updates.protein) await modal.fillField('#protein', String(updates.protein));
    
    await modal.save();
  }
  
  async deleteProduct(productName) {
    const card = await this.getProductCard(productName);
    await card.locator('button.delete-product').click();
    await this.page.locator('button:has-text("Confirm")').click();
  }
  
  async getProductCount() {
    return await this.productCards.count();
  }
}

module.exports = ProductsPage;
```

### Fasting Page

```javascript
// tests/e2e-playwright/pages/FastingPage.js
const BasePage = require('./BasePage');
const NavigationComponent = require('../components/NavigationComponent');

class FastingPage extends BasePage {
  constructor(page) {
    super(page);
    this.navigation = new NavigationComponent(page);
    
    // Selectors
    this.fastingTypeSelect = page.locator('select#fasting-type');
    this.startButton = page.locator('button:has-text("Start Fasting")');
    this.endButton = page.locator('button:has-text("End Fasting")');
    this.pauseButton = page.locator('button:has-text("Pause")');
    this.resumeButton = page.locator('button:has-text("Resume")');
    
    this.timerDisplay = page.locator('.fasting-timer');
    this.progressBar = page.locator('.progress-bar');
    this.statsContainer = page.locator('.fasting-stats');
  }
  
  async navigate() {
    await super.navigate('/');
    await this.navigation.goToTab('fasting');
  }
  
  async startFastingSession(type = '16:8', notes = '') {
    await this.fastingTypeSelect.selectOption(type);
    
    if (notes) {
      await this.page.locator('#fasting-notes').fill(notes);
    }
    
    await this.startButton.click();
    await this.page.waitForLoadState('networkidle');
  }
  
  async endFastingSession() {
    await this.endButton.click();
    await this.page.waitForLoadState('networkidle');
  }
  
  async pauseFastingSession() {
    await this.pauseButton.click();
  }
  
  async resumeFastingSession() {
    await this.resumeButton.click();
  }
  
  async getTimerValue() {
    const text = await this.timerDisplay.textContent();
    return text.trim();
  }
  
  async getProgress() {
    const width = await this.progressBar.getAttribute('style');
    const match = width.match(/width:\s*(\d+)%/);
    return match ? parseInt(match[1]) : 0;
  }
  
  async getStats() {
    const totalSessions = await this.statsContainer
      .locator('.stat-total-sessions')
      .textContent();
    const avgDuration = await this.statsContainer
      .locator('.stat-avg-duration')
      .textContent();
    
    return {
      totalSessions: parseInt(totalSessions),
      avgDuration: parseFloat(avgDuration)
    };
  }
  
  async isSessionActive() {
    return await this.endButton.isVisible();
  }
}

module.exports = FastingPage;
```

---

## 💡 Usage in Tests

### Basic Test

```javascript
const { test, expect } = require('@playwright/test');
const DailyLogPage = require('./pages/DailyLogPage');

test.describe('Daily Log', () => {
  test('should add and display food entry', async ({ page }) => {
    const dailyLog = new DailyLogPage(page);
    
    await dailyLog.navigate();
    
    await dailyLog.addFoodEntry({
      type: 'product',
      id: 1,
      quantity: 100,
      mealTime: 'breakfast'
    });
    
    expect(await dailyLog.getEntryCount()).toBe(1);
    expect(await dailyLog.getTotalCalories()).toBeGreaterThan(0);
  });
});
```

### Complex Workflow

```javascript
test('complete daily log workflow', async ({ page }) => {
  const dailyLog = new DailyLogPage(page);
  const products = new ProductsPage(page);
  
  // Create a product
  await products.navigate();
  await products.createProduct({
    name: 'Test Protein',
    calories: 120,
    protein: 25,
    fat: 2,
    carbs: 1
  });
  
  // Add to daily log
  await dailyLog.navigate();
  await dailyLog.addFoodEntry({
    type: 'product',
    id: 1,
    quantity: 150,
    mealTime: 'breakfast'
  });
  
  // Verify
  const calories = await dailyLog.getTotalCalories();
  expect(calories).toBeCloseTo(180, 0); // 120 * 1.5
});
```

### Data-Driven Tests

```javascript
const testCases = [
  { mealTime: 'breakfast', quantity: 100 },
  { mealTime: 'lunch', quantity: 150 },
  { mealTime: 'dinner', quantity: 200 }
];

test.describe('Meal time variations', () => {
  testCases.forEach(({ mealTime, quantity }) => {
    test(`should add ${mealTime} with ${quantity}g`, async ({ page }) => {
      const dailyLog = new DailyLogPage(page);
      
      await dailyLog.navigate();
      await dailyLog.addFoodEntry({
        type: 'product',
        id: 1,
        quantity,
        mealTime
      });
      
      expect(await dailyLog.getEntryCount()).toBe(1);
    });
  });
});
```

---

## 🔧 Implementation Checklist

### Phase 1: Foundation (4 hours)
- [ ] Create `tests/e2e-playwright/pages/` directory
- [ ] Create `tests/e2e-playwright/components/` directory
- [ ] Implement `BasePage` class
- [ ] Implement `NavigationComponent`
- [ ] Implement `ModalComponent`
- [ ] Add documentation and examples

### Phase 2: Page Objects (4 hours)
- [ ] Implement `DailyLogPage`
- [ ] Implement `ProductsPage`
- [ ] Implement `DishesPage`
- [ ] Implement `FastingPage`
- [ ] Implement `StatisticsPage`

### Phase 3: Migration (4 hours)
- [ ] Migrate `logging-workflow.spec.js` (highest priority)
- [ ] Migrate `product-workflow.spec.js`
- [ ] Migrate `fasting.spec.js`
- [ ] Migrate `statistics.spec.js`
- [ ] Keep `smoke.spec.js` as-is (simple enough)

### Phase 4: Polish (2 hours)
- [ ] Add JSDoc comments
- [ ] Create helper utilities
- [ ] Performance optimization
- [ ] Code review

**Total Estimated Time**: 14 hours

---

## 🎓 Best Practices

### 1. One Page Object Per Page/Component

```javascript
// ✅ Good: Separate page objects
class DailyLogPage extends BasePage { }
class ProductsPage extends BasePage { }

// ❌ Bad: Mixed responsibilities
class AllPagesInOne extends BasePage {
  async addProduct() { }
  async addLogEntry() { }
}
```

### 2. Return Page Objects for Chaining

```javascript
// ✅ Good: Chainable
class DailyLogPage {
  async navigate() {
    await this.page.goto('/');
    return this;  // Enable chaining
  }
  
  async addFood() {
    // ...
    return this;  // Enable chaining
  }
}

// Usage
await dailyLog.navigate().addFood();
```

### 3. Use Getters for Selectors

```javascript
// ✅ Good: Lazy evaluation
class Page {
  get addButton() {
    return this.page.locator('button.add');
  }
}

// ❌ Bad: Eager evaluation (may fail before page loads)
class Page {
  constructor(page) {
    this.addButton = page.locator('button.add'); // Too early!
  }
}
```

### 4. Wait in Page Objects, Assert in Tests

```javascript
// ✅ Good: Page objects handle waits
class DailyLogPage {
  async addFood() {
    await this.addButton.waitFor({ state: 'visible' });
    await this.addButton.click();
    await this.modal.waitFor({ state: 'hidden' });
  }
}

// Test does assertions
test('should add food', async ({ page }) => {
  const dailyLog = new DailyLogPage(page);
  await dailyLog.addFood();
  
  expect(await dailyLog.getCount()).toBe(1); // Assert in test
});

// ❌ Bad: Assertions in page objects
class DailyLogPage {
  async addFood() {
    await this.addButton.click();
    expect(await this.getCount()).toBe(1); // Wrong place!
  }
}
```

### 5. Abstract Implementation Details

```javascript
// ✅ Good: Hide implementation
class Page {
  async selectDate(date) {
    await this.dateInput.fill(date);
    await this.page.waitForLoadState('networkidle');
  }
}

// Test doesn't care about implementation
await page.selectDate('2025-10-25');

// ❌ Bad: Expose implementation
await page.page.locator('input[type="date"]').fill('2025-10-25');
await page.page.waitForLoadState('networkidle');
```

---

## 📖 Additional Resources

### Pattern References
- [Playwright Page Objects](https://playwright.dev/docs/pom) - Official guide
- [Selenium Page Objects](https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/)
- [Martin Fowler: Page Object](https://martinfowler.com/bliki/PageObject.html)

### Related Patterns
- **Screen Play Pattern**: Actor-based testing (alternative to Page Objects)
- **Component Objects**: For reusable UI components
- **Facade Pattern**: Simplified interface to complex subsystems

### Tools
- [Playwright](https://playwright.dev/) - E2E testing framework
- [Playwright Test](https://playwright.dev/docs/test-intro) - Test runner
- [CodeceptJS](https://codecept.io/) - BDD-style E2E testing

---

**Status**: 📋 Design Document (Recommended for Implementation)  
**Next Steps**: Implementation Phase 1 (Foundation)  
**Priority**: High (E2E test maintainability)  
**Dependencies**: Playwright E2E tests already exist  
**Estimated ROI**: Very High (critical for test maintenance)
