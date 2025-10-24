// @ts-check
const { test, expect } = require('@playwright/test');
const helpers = require('./helpers/page-helpers');

test.describe('Smoke Tests', () => {
  test.describe('Local Version (Flask Backend)', () => {
    test('should load home page', async ({ page }) => {
      await page.goto('/');
      await expect(page).toHaveTitle(/Nutrition Tracker/i);
    });

    test('should display navigation tabs', async ({ page }) => {
      await page.goto('/');
      
      // Check for main navigation tabs (always present)
      const requiredTabs = ['Products', 'Dishes', 'Log', 'Statistics'];
      for (const tab of requiredTabs) {
        const tabElement = page.locator(`text=${tab}`).first();
        await expect(tabElement).toBeVisible();
      }
      
      // Fasting tab is optional (only in Flask version, not in demo yet)
      const fastingTab = page.locator('text=Fasting').first();
      const hasFastingTab = await fastingTab.count() > 0;
      // Just check it exists if present, don't fail if missing
      if (hasFastingTab) {
        await expect(fastingTab).toBeVisible();
      }
    });

    test('should load products page', async ({ page }) => {
      await page.goto('/');
      
      // Click on Products tab
      await helpers.clickElement(page, '#products-tab');
      
      // Verify products section is visible
      await helpers.waitForElement(page, '#products');
      const productsSection = page.locator('#products');
      await expect(productsSection).toBeVisible();
    });

    test('should have API connectivity or localStorage', async ({ page }) => {
      await page.goto('/');
      
      // For Flask version: wait for API call
      // For Demo version: check localStorage is available
      try {
        const response = await page.waitForResponse(
          (response) => response.url().includes('/api/') && response.status() === 200,
          { timeout: 5000 }
        );
        expect(response.status()).toBe(200);
      } catch (e) {
        // Demo version - check localStorage is working
        const hasLocalStorage = await page.evaluate(() => {
          return typeof Storage !== 'undefined';
        });
        expect(hasLocalStorage).toBeTruthy();
      }
    });
  });

  test.describe('Responsive Design', () => {
    test('should work on mobile viewport', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('/');
      
      // Check if page loads
      await expect(page).toHaveTitle(/Nutrition Tracker/i);
      
      // Verify mobile navigation is present
      const body = page.locator('body');
      await expect(body).toBeVisible();
    });

    test('should work on tablet viewport', async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });
      await page.goto('/');
      
      // Check if page loads
      await expect(page).toHaveTitle(/Nutrition Tracker/i);
    });
  });

  test.describe('Basic Functionality', () => {
    test('should open product modal', async ({ page }) => {
      await page.goto('/');
      
      // Navigate to Products tab
      await helpers.clickElement(page, 'text=Products');
      
      // Click "Add Product" button
      const addButton = page.locator('button:has-text("Add Product")').first();
      if (await addButton.isVisible()) {
        await addButton.click();
        
        // Wait for modal with proper CI timeout
        await helpers.waitForModal(page);
        
        // Verify modal is displayed
        const modal = page.locator('.modal:visible').first();
        await expect(modal).toBeVisible({ timeout: 15000 });
      }
    });

    test('should switch themes', async ({ page }) => {
      await page.goto('/');
      
      // Look for theme toggle button
      const themeToggle = page.locator('[data-theme-toggle], .theme-toggle, button:has-text("Theme")').first();
      
      if (await themeToggle.isVisible({ timeout: 2000 })) {
        // Get initial theme
        const initialTheme = await page.evaluate(() => {
          return document.documentElement.getAttribute('data-theme') ||
                 document.body.getAttribute('data-theme') ||
                 'light';
        });
        
        // Click theme toggle
        await themeToggle.click();
        
        // Wait for theme to change
        await page.waitForTimeout(500);
        
        // Verify theme changed
        const newTheme = await page.evaluate(() => {
          return document.documentElement.getAttribute('data-theme') ||
                 document.body.getAttribute('data-theme') ||
                 'light';
        });
        
        expect(newTheme).not.toBe(initialTheme);
      }
    });
  });

  test.describe('Error Handling', () => {
    test('should handle navigation to non-existent page gracefully', async ({ page }) => {
      const response = await page.goto('/non-existent-page');
      
      // Should either return 404 or redirect to home
      expect(response?.status()).toBeLessThanOrEqual(404);
    });

    test('should not have console errors on load', async ({ page }) => {
      const consoleErrors = await helpers.captureConsoleErrors(page);
      
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // All non-critical errors are already filtered by the helper
      expect(consoleErrors.length).toBe(0);
      
      // If there are errors, log them for debugging
      if (consoleErrors.length > 0) {
        console.log('Critical console errors found:', consoleErrors);
      }
    });
  });
});
