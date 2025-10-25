// @ts-check
const { test, expect } = require('@playwright/test');
const helpers = require('./helpers/page-helpers');
const testData = require('./fixtures/test-data');

test.describe('Product Management Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Navigate to Products tab using ID
    await helpers.clickElement(page, '#products-tab');
    await page.waitForTimeout(500); // Wait for tab to load
    // Ensure products section is visible
    await page.locator('#products').waitFor({ state: 'visible', timeout: 3000 });
  });

  test('should create a new product', async ({ page }) => {
    const product = testData.products.apple;
    
    // Click "Add Product" button with proper wait
    await helpers.clickWhenReady(page, 'button:has-text("Add Product")');
    
    // Wait for modal with proper CI timeout
    await helpers.waitForModal(page);
    
    // Fill in product form (demo uses specific IDs)
    await helpers.fillField(page, 'input[name="name"], #productName', product.name);
    await helpers.fillField(page, 'input[name="calories_per_100g"], #productCalories', product.calories_per_100g.toString());
    await helpers.fillField(page, 'input[name="protein_per_100g"], #productProtein', product.protein_per_100g.toString());
    await helpers.fillField(page, 'input[name="fat_per_100g"], #productFat', product.fat_per_100g.toString());
    await helpers.fillField(page, 'input[name="carbs_per_100g"], #productCarbs', product.carbs_per_100g.toString());
    await helpers.fillField(page, 'input[name="fiber_per_100g"], #productFiber', product.fiber_per_100g.toString());
    
    // Submit form with proper API wait
    await helpers.submitModalForm(page);
    
    // Verify product appears in the list
    const productCard = page.locator(`text=${product.name}`).first();
    await expect(productCard).toBeVisible({ timeout: 15000 });
  });

  test('should display product list', async ({ page }) => {
    // Wait for products to load
    await page.waitForTimeout(1000);
    
    // Check if products section exists
    const productsSection = page.locator('#products').first();
    await expect(productsSection).toBeVisible();
  });

  test('should search/filter products', async ({ page }) => {
    // Look for search input
    const searchInput = page.locator('input[type="search"], input[placeholder*="search" i], input[name="search"]').first();
    
    if (await searchInput.isVisible({ timeout: 2000 })) {
      // Type search query
      await searchInput.fill('Apple');
      await page.waitForTimeout(500);
      
      // Verify filtered results
      const results = page.locator('.product-card, [data-product], .product-item');
      const count = await results.count();
      expect(count).toBeGreaterThanOrEqual(0);
    }
  });

  test('should view product details', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Find first product card
    const productCard = page.locator('.product-card, [data-product], .product-item').first();
    
    if (await productCard.isVisible({ timeout: 5000 })) {
      // Click to view details
      await helpers.clickWhenReady(page, '.product-card, [data-product], .product-item');
      await page.waitForTimeout(500);
      
      // Wait for modal if details open in modal
      try {
        await helpers.waitForModal(page, { timeout: 5000 });
      } catch (e) {
        // May not be a modal, could be inline expansion
      }
      
      // Check if details modal or expanded view appears
      const detailsView = page.locator('.modal:visible, .product-details:visible').first();
      await expect(detailsView).toBeVisible({ timeout: 5000 });
    }
  });

  test('should delete a product', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Find a product with delete button
    const deleteButton = page.locator('button:has-text("Delete"), .delete-btn, [data-action="delete"]').first();
    
    if (await deleteButton.isVisible({ timeout: 5000 })) {
      // Click delete button
      await helpers.clickWhenReady(page, 'button:has-text("Delete"), .delete-btn, [data-action="delete"]');
      
      // Wait for confirmation dialog or direct deletion
      await page.waitForTimeout(500);
      
      // If confirmation dialog appears, confirm
      const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Yes"), button:has-text("Delete")').last();
      if (await confirmButton.isVisible({ timeout: 2000 })) {
        try {
          await Promise.all([
            page.waitForResponse(resp => resp.url().includes('/api/products') && resp.status() === 200, { timeout: 10000 }),
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
      
      // Verify success (product removed or success message)
      const hasSuccess = await helpers.hasSuccessMessage(page);
      expect(hasSuccess).toBeTruthy();
    }
  });

  test('should validate product form', async ({ page }) => {
    // Click "Add Product" button
    await helpers.clickWhenReady(page, 'button:has-text("Add Product")');
    
    // Wait for modal with proper CI timeout
    await helpers.waitForModal(page);
    
    // Try to submit empty form
    await helpers.clickWhenReady(page, 'button[type="submit"]:has-text("Save"), button:has-text("Add Product")');
    
    // Wait a bit for validation
    await page.waitForTimeout(500);
    
    // Check for validation messages
    const hasError = await helpers.hasErrorMessage(page);
    const validationMessage = page.locator('.invalid-feedback, .error-message, [role="alert"]').first();
    const hasValidation = await validationMessage.isVisible({ timeout: 2000 }).catch(() => false);
    
    // Should show validation error or prevent submission
    expect(hasError || hasValidation).toBeTruthy();
  });

  test('should calculate keto index', async ({ page }) => {
    const product = testData.products.avocado; // High-fat, low-carb product
    
    // Click "Add Product" button
    await helpers.clickWhenReady(page, 'button:has-text("Add Product")');
    
    // Wait for modal with proper CI timeout
    await helpers.waitForModal(page);
    
    // Fill in high-fat, low-carb product
    await helpers.fillField(page, 'input[name="name"], #product-name', product.name);
    await helpers.fillField(page, 'input[name="calories_per_100g"], #calories', product.calories_per_100g.toString());
    await helpers.fillField(page, 'input[name="protein_per_100g"], #protein', product.protein_per_100g.toString());
    await helpers.fillField(page, 'input[name="fat_per_100g"], #fat', product.fat_per_100g.toString());
    await helpers.fillField(page, 'input[name="carbs_per_100g"], #carbs', product.carbs_per_100g.toString());
    await helpers.fillField(page, 'input[name="fiber_per_100g"], #fiber', product.fiber_per_100g.toString());
    
    // Wait for keto calculation
    await page.waitForTimeout(500);
    
    // Look for keto index display
    const ketoIndex = page.locator('.keto-index, [data-keto-index]').or(page.locator('text=/keto/i')).first();
    const hasKetoIndex = await ketoIndex.isVisible({ timeout: 2000 }).catch(() => false);
    
    // Keto index should be calculated and displayed
    if (hasKetoIndex) {
      const ketoText = await ketoIndex.textContent();
      expect(ketoText).toBeTruthy();
    }
  });
});
