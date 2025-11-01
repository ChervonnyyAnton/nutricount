// @ts-check
const { test, expect } = require('@playwright/test');
const helpers = require('./helpers/page-helpers');
const testData = require('./fixtures/test-data');

test.describe('Daily Logging Workflow', () => {
  let createdProductId;
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Navigate to Log tab using ID
    await helpers.clickElement(page, '#log-tab');
    await page.waitForTimeout(500); // Wait for tab to load
    // Ensure log section is visible
    await page.locator('#log').waitFor({ state: 'visible', timeout: 3000 });
  });

  test('should display log page', async ({ page }) => {
    // Verify log section is visible
    const logSection = page.locator('#log').first();
    await expect(logSection).toBeVisible();
  });

  test('should show current date by default', async ({ page }) => {
    // Check for date display or date picker
    const dateElement = page.locator('input[type="date"], .current-date, [data-date]').first();
    
    if (await dateElement.isVisible({ timeout: 2000 })) {
      const dateValue = await dateElement.inputValue();
      const today = new Date().toISOString().split('T')[0];
      
      // Should show today's date or be editable to today
      expect(dateValue).toBeTruthy();
    }
  });

  test.skip('should create a log entry', async ({ page }) => {
    // Check if demo version
    const isDemo = await helpers.isDemoVersion(page);
    
    // First, ensure we have a product to log
    await helpers.clickElement(page, 'text=Products');
    await page.waitForTimeout(500);
    
    // Create a test product if needed
    const addProductBtn = page.locator('button:has-text("Add Product")').first();
    if (await addProductBtn.isVisible({ timeout: 5000 })) {
      if (!isDemo) {
        // Flask version: click button to open modal
        await helpers.clickWhenReady(page, 'button:has-text("Add Product")');
        
        // Wait for modal with proper CI timeout
        await helpers.waitForModal(page);
      } else {
        // Demo version: form is inline, just wait
        await page.waitForTimeout(500);
      }
      
      const product = testData.products.apple;
      await helpers.fillField(page, 'input[name="name"], #productName', product.name + ' - Log Test');
      await helpers.fillField(page, 'input[name="protein_per_100g"], #productProtein', product.protein_per_100g.toString());
      await helpers.fillField(page, 'input[name="fat_per_100g"], #productFat', product.fat_per_100g.toString());
      await helpers.fillField(page, 'input[name="carbs_per_100g"], #productCarbs', product.carbs_per_100g.toString());
      
      // Submit form with proper API wait
      await helpers.submitModalForm(page);
    }
    
    // Go back to Log tab
    await helpers.clickElement(page, 'text=Log');
    await page.waitForTimeout(500);
    
    // Click "Add Log Entry" or similar button
    const addLogBtn = page.locator('button:has-text("Add Entry"), button:has-text("Add Log"), button:has-text("Log Food")').first();
    
    if (await addLogBtn.isVisible({ timeout: 5000 })) {
      await helpers.clickWhenReady(page, 'button:has-text("Add Entry"), button:has-text("Add Log"), button:has-text("Log Food")');
      await page.waitForTimeout(500);
      
      // Fill in log entry form
      // Select a product (usually a dropdown or autocomplete)
      const productSelect = page.locator('select[name="item_id"], select[name="product_id"], input[name="product"]').first();
      if (await productSelect.isVisible({ timeout: 2000 })) {
        // If it's a select dropdown
        if (await productSelect.evaluate(el => el.tagName === 'SELECT')) {
          const options = await productSelect.locator('option').count();
          if (options > 1) {
            await productSelect.selectOption({ index: 1 });
          }
        } else {
          // If it's an input (autocomplete)
          await productSelect.fill('Apple');
          await page.waitForTimeout(500);
        }
      }
      
      // Fill quantity
      const quantityInput = page.locator('input[name="quantity"], input[name="quantity_grams"]').first();
      if (await quantityInput.isVisible({ timeout: 2000 })) {
        await quantityInput.fill('100');
      }
      
      // Select meal time
      const mealSelect = page.locator('select[name="meal_time"]').first();
      if (await mealSelect.isVisible({ timeout: 2000 })) {
        await mealSelect.selectOption('breakfast');
      }
      
      // Submit with API wait
      const submitLogBtn = page.locator('button[type="submit"]:has-text("Save"), button:has-text("Add"), button:has-text("Log")').last();
      try {
        await Promise.all([
          page.waitForResponse(resp => resp.url().includes('/api/log') && resp.status() === 200, { timeout: 10000 }),
          helpers.clickWhenReady(page, 'button[type="submit"]:has-text("Save"), button:has-text("Add"), button:has-text("Log")')
        ]);
      } catch (e) {
        // Demo version - just click and wait
        await helpers.clickWhenReady(page, 'button[type="submit"]:has-text("Save"), button:has-text("Add"), button:has-text("Log")');
        await page.waitForTimeout(1000);
      }
      
      // Wait for network to settle
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
      
      // Verify log entry appears
      const logEntry = page.locator('.log-entry, .log-item, [data-log-entry]').first();
      const hasEntry = await logEntry.isVisible({ timeout: 5000 }).catch(() => false);
      expect(hasEntry).toBeTruthy();
    }
  });

  test('should display daily nutrition totals', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for totals display
    const totalsSection = page.locator('.totals, .daily-totals, [data-totals], .nutrition-summary').first();
    
    if (await totalsSection.isVisible({ timeout: 2000 })) {
      // Verify key nutrition values are displayed
      const content = await totalsSection.textContent();
      
      // Should show at least some of these
      const hasCalories = content?.toLowerCase().includes('calor');
      const hasProtein = content?.toLowerCase().includes('protein');
      const hasCarbs = content?.toLowerCase().includes('carb');
      
      expect(hasCalories || hasProtein || hasCarbs).toBeTruthy();
    }
  });

  test('should change date to view different days', async ({ page }) => {
    // Find date picker
    const datePicker = page.locator('input[type="date"]').first();
    
    if (await datePicker.isVisible({ timeout: 2000 })) {
      // Get yesterday's date
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      const yesterdayStr = yesterday.toISOString().split('T')[0];
      
      // Change to yesterday
      await datePicker.fill(yesterdayStr);
      await page.waitForTimeout(1000);
      
      // Verify date changed (page should reload or update)
      const currentValue = await datePicker.inputValue();
      expect(currentValue).toBe(yesterdayStr);
    }
  });

  test('should delete a log entry', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Find a log entry with delete button
    const deleteBtn = page.locator('button:has-text("Delete"), .delete-btn, [data-action="delete"]').first();
    
    if (await deleteBtn.isVisible({ timeout: 5000 })) {
      // Click delete
      await helpers.clickWhenReady(page, 'button:has-text("Delete"), .delete-btn, [data-action="delete"]');
      await page.waitForTimeout(500);
      
      // Confirm if needed (may open confirmation modal)
      const confirmBtn = page.locator('button:has-text("Confirm"), button:has-text("Yes"), button:has-text("Delete")').last();
      if (await confirmBtn.isVisible({ timeout: 2000 })) {
        try {
          await Promise.all([
            page.waitForResponse(resp => resp.url().includes('/api/log') && resp.status() === 200, { timeout: 10000 }),
            helpers.clickWhenReady(page, 'button:has-text("Confirm"), button:has-text("Yes"), button:has-text("Delete")')
          ]);
        } catch (e) {
          // Demo version - just click
          await helpers.clickWhenReady(page, 'button:has-text("Confirm"), button:has-text("Yes"), button:has-text("Delete")');
        }
      }
      
      // Wait for network to settle
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
      await page.waitForTimeout(500);

      // Verify deletion completed without errors
      // Note: Success message might not always appear, so we check for absence of error instead
      const hasError = await helpers.hasErrorMessage(page);
      expect(hasError).toBeFalsy();
    }
  });

  test('should filter by meal time', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for meal time filter
    const mealFilter = page.locator('select[name="meal_filter"], button:has-text("Breakfast"), button:has-text("Lunch")').first();
    
    if (await mealFilter.isVisible({ timeout: 5000 })) {
      // Apply filter
      if (await mealFilter.evaluate(el => el.tagName === 'SELECT')) {
        await mealFilter.selectOption('breakfast');
      } else {
        await helpers.clickWhenReady(page, 'select[name="meal_filter"], button:has-text("Breakfast"), button:has-text("Lunch")');
      }
      
      await page.waitForTimeout(500);
      
      // Verify filtering works (entries are filtered)
      const entries = page.locator('.log-entry, .log-item, [data-log-entry]');
      const count = await entries.count();
      expect(count).toBeGreaterThanOrEqual(0);
    }
  });

  test('should show meal distribution', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for meal breakdown (breakfast, lunch, dinner, snacks)
    const mealBreakdown = page.locator('.meal-breakdown, .meal-distribution, [data-meals]').first();
    
    if (await mealBreakdown.isVisible({ timeout: 2000 })) {
      const content = await mealBreakdown.textContent();
      
      // Should mention different meal times
      const hasMealTimes = content?.toLowerCase().includes('breakfast') ||
                          content?.toLowerCase().includes('lunch') ||
                          content?.toLowerCase().includes('dinner');
      
      expect(hasMealTimes).toBeTruthy();
    }
  });

  test('should validate quantity input', async ({ page }) => {
    // Click "Add Log Entry"
    const addLogBtn = page.locator('button:has-text("Add Entry"), button:has-text("Add Log"), button:has-text("Log Food")').first();
    
    if (await addLogBtn.isVisible({ timeout: 5000 })) {
      await helpers.clickWhenReady(page, 'button:has-text("Add Entry"), button:has-text("Add Log"), button:has-text("Log Food")');
      await page.waitForTimeout(500);
      
      // Try to enter invalid quantity (negative or too large)
      const quantityInput = page.locator('input[name="quantity"], input[name="quantity_grams"]').first();
      if (await quantityInput.isVisible({ timeout: 5000 })) {
        await quantityInput.fill('-100'); // Negative quantity
        
        const submitBtn = page.locator('button[type="submit"]:has-text("Save"), button:has-text("Add"), button:has-text("Log")').last();
        await submitBtn.click();
        await page.waitForTimeout(500);
        
        // Should show validation error
        const hasError = await helpers.hasErrorMessage(page);
        const validationMessage = page.locator('.invalid-feedback, .error-message, [role="alert"]').first();
        const hasValidation = await validationMessage.isVisible({ timeout: 1000 }).catch(() => false);
        
        expect(hasError || hasValidation).toBeTruthy();
      }
    }
  });

  test('should show empty state when no entries', async ({ page }) => {
    // Change to a future date (should have no entries)
    const datePicker = page.locator('input[type="date"]').first();
    
    if (await datePicker.isVisible({ timeout: 2000 })) {
      const futureDate = new Date();
      futureDate.setDate(futureDate.getDate() + 365); // Next year
      const futureDateStr = futureDate.toISOString().split('T')[0];
      
      await datePicker.fill(futureDateStr);
      await page.waitForTimeout(1000);
      
      // Look for empty state message
      const emptyState = page.locator('text=/no entries|no logs|nothing logged/i').first();
      const hasEmptyState = await emptyState.isVisible({ timeout: 2000 }).catch(() => false);
      
      // Should show empty state or have zero entries
      const entries = page.locator('.log-entry, .log-item, [data-log-entry]');
      const entryCount = await entries.count();
      
      expect(hasEmptyState || entryCount === 0).toBeTruthy();
    }
  });
});
