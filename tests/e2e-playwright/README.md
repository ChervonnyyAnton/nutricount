# E2E Testing with Playwright

End-to-end tests for the Nutricount application using Playwright.

## 📋 Overview

This directory contains E2E tests that verify complete user workflows across the application. Tests run against the real application with a Flask backend server.

## 🗂️ Structure

```
tests/e2e-playwright/
├── README.md                  # This file
├── smoke.spec.js              # Basic smoke tests
├── product-workflow.spec.js   # Product management tests
├── fixtures/
│   └── test-data.js          # Test data fixtures
└── helpers/
    └── page-helpers.js       # Reusable helper functions
```

## 🚀 Running Tests

### Prerequisites

```bash
# Install dependencies
npm install

# Install Playwright browsers (first time only)
npx playwright install chromium
```

### Run Tests

```bash
# Run all E2E tests
npm run test:e2e

# Run with visible browser (headed mode)
npm run test:e2e:headed

# Run with Playwright UI (interactive mode)
npm run test:e2e:ui

# Run specific test suite
npm run test:e2e:smoke           # Smoke tests only
npm run test:e2e:products        # Product workflow tests only

# Debug tests
npm run test:e2e:debug

# View test report
npm run test:e2e:report
```

### Run with Custom Base URL

```bash
# Test against a different environment
BASE_URL=http://localhost:8080 npm run test:e2e
```

## 📝 Test Suites

### Smoke Tests (`smoke.spec.js`)
Basic tests to verify the application is functional:
- ✅ Home page loads
- ✅ Navigation tabs are visible
- ✅ API connectivity works
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Basic functionality (modals, theme switching)
- ✅ Error handling

### Product Workflow Tests (`product-workflow.spec.js`)
Complete product management workflow:
- ✅ Create new product
- ✅ Display product list
- ✅ Search/filter products
- ✅ View product details
- ✅ Delete product
- ✅ Form validation
- ✅ Keto index calculation

### Future Test Suites (Planned)
- `logging-workflow.spec.js` - Daily food logging
- `dishes-workflow.spec.js` - Dish management
- `statistics.spec.js` - Statistics and analytics
- `fasting.spec.js` - Intermittent fasting tracking
- `authentication.spec.js` - User authentication (if implemented)

## 🛠️ Writing Tests

### Test Structure

```javascript
const { test, expect } = require('@playwright/test');
const helpers = require('./helpers/page-helpers');
const testData = require('./fixtures/test-data');

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup before each test
    await page.goto('/');
  });

  test('should do something', async ({ page }) => {
    // Arrange
    const data = testData.products.apple;
    
    // Act
    await helpers.clickElement(page, 'button:has-text("Add")');
    await helpers.fillField(page, '#name', data.name);
    
    // Assert
    await expect(page.locator('#name')).toHaveValue(data.name);
  });
});
```

### Best Practices

1. **Use Helper Functions**: Use page-helpers.js for common operations
2. **Use Test Data**: Use fixtures/test-data.js for consistent test data
3. **Descriptive Names**: Test names should clearly describe what they test
4. **AAA Pattern**: Arrange, Act, Assert structure
5. **Wait Properly**: Use waitForElement, waitForApiResponse for reliability
6. **Clean State**: Each test should start with a clean state
7. **Independent Tests**: Tests should not depend on each other

### Helper Functions

Available in `helpers/page-helpers.js`:

```javascript
// Element interactions
await helpers.waitForElement(page, selector);
await helpers.clickElement(page, selector);
await helpers.fillField(page, selector, value);
await helpers.getTextContent(page, selector);
await helpers.elementExists(page, selector);

// API interactions
await helpers.waitForApiResponse(page, urlPattern, action);

// Local storage
await helpers.clearLocalStorage(page);
await helpers.setLocalStorageItem(page, key, value);
await helpers.getLocalStorageItem(page, key);

// Navigation
await helpers.waitForNavigation(page, action);

// Error checking
const hasError = await helpers.hasErrorMessage(page);
const hasSuccess = await helpers.hasSuccessMessage(page);

// Screenshots
await helpers.takeScreenshot(page, name);
```

## 🔧 Configuration

Configuration is in `playwright.config.js` at the project root:

```javascript
module.exports = {
  testDir: './tests/e2e-playwright',
  baseURL: 'http://localhost:5000',
  
  // Projects for different browsers
  projects: [
    { name: 'chromium' },
    { name: 'Mobile Chrome' },
  ],
  
  // Web server configuration
  webServer: {
    command: 'python3 app.py',
    url: 'http://localhost:5000',
    reuseExistingServer: !process.env.CI,
  },
};
```

## 📊 Reports

### HTML Report

After running tests, view the HTML report:

```bash
npm run test:e2e:report
```

Report includes:
- Test results (pass/fail)
- Screenshots on failure
- Video recordings on failure
- Test execution time
- Detailed logs

### CI/CD Integration

Tests automatically run in CI/CD pipeline:
- Headless browser mode
- Automatic retries on failure
- Screenshot/video capture on failure
- Test results uploaded as artifacts

## 🐛 Debugging

### Debug Mode

```bash
# Step through tests with browser DevTools
npm run test:e2e:debug
```

### Playwright Inspector

The debug command opens Playwright Inspector where you can:
- Step through tests line by line
- Inspect DOM elements
- See network requests
- View console logs
- Take screenshots

### Verbose Logging

```bash
# Run with detailed logs
DEBUG=pw:api npm run test:e2e
```

## 📈 Coverage

E2E tests cover critical user journeys:

- ✅ Product management (create, read, update, delete)
- 🚧 Daily logging workflow (planned)
- 🚧 Dish management (planned)
- 🚧 Statistics viewing (planned)
- 🚧 Fasting tracking (planned)

Target: 80%+ coverage of critical user paths

## 🚦 CI/CD Integration

E2E tests run automatically on:
- Pull requests to main branch
- Commits to main branch
- Manual workflow dispatch

### GitHub Actions Workflow

```yaml
- name: Install Playwright
  run: npx playwright install chromium --with-deps

- name: Run E2E Tests
  run: npm run test:e2e
  env:
    BASE_URL: http://localhost:5000

- name: Upload Test Report
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
```

## 🤝 Contributing

When adding new E2E tests:

1. Create a new `.spec.js` file in this directory
2. Use descriptive test names
3. Use existing helpers and fixtures
4. Follow the AAA pattern
5. Add test documentation to this README
6. Ensure tests pass locally before committing
7. Update test count in this README

## 📚 Resources

- [Playwright Documentation](https://playwright.dev/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Playwright API Reference](https://playwright.dev/docs/api/class-playwright)
- [Project Testing Guide](../../docs/qa/testing-strategy.md)

## 🆘 Troubleshooting

### Tests timing out

- Increase timeout in test: `test.setTimeout(60000)`
- Check if Flask server is running
- Verify BASE_URL is correct

### Browser not installed

```bash
npx playwright install chromium
```

### Flaky tests

- Add proper waits: `await page.waitForSelector()`
- Use retry logic: `retries: 2` in config
- Avoid hard-coded timeouts: `await page.waitForTimeout()`

### CI/CD failures

- Check CI logs for specific errors
- Verify environment variables are set
- Ensure dependencies are installed
- Check browser installation on CI

## 📝 Test Statistics

- **Total Tests**: 15+
- **Test Suites**: 2
- **Coverage**: ~30% of critical paths
- **Execution Time**: ~2-5 minutes
- **Success Rate**: 90%+ (target)

---

**Last Updated**: October 22, 2025  
**Maintainer**: ChervonnyyAnton  
**Status**: ✅ Active Development
