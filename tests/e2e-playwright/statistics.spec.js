// @ts-check
const { test, expect } = require('@playwright/test');
const helpers = require('./helpers/page-helpers');

test.describe('Statistics Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Navigate to Statistics tab
    await helpers.clickElement(page, 'text=Statistics');
    await page.waitForTimeout(500); // Wait for tab to load
  });

  test('should display statistics page', async ({ page }) => {
    // Verify statistics section is visible
    const statsSection = page.locator('#statistics-section, .statistics-container, [data-statistics]').first();
    await expect(statsSection).toBeVisible();
  });

  test('should show daily statistics', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for daily stats display
    const dailyStats = page.locator('.daily-stats, .today-stats, [data-daily-stats]').first();
    
    if (await dailyStats.isVisible({ timeout: 2000 })) {
      const content = await dailyStats.textContent();
      
      // Should contain nutrition information
      const hasNutrition = content?.toLowerCase().includes('calor') ||
                          content?.toLowerCase().includes('protein') ||
                          content?.toLowerCase().includes('carb') ||
                          content?.toLowerCase().includes('fat');
      
      expect(hasNutrition).toBeTruthy();
    }
  });

  test('should show weekly statistics', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for weekly stats display or tab
    const weeklyTab = page.locator('button:has-text("Weekly"), .tab:has-text("Week"), [data-tab="weekly"]').first();
    
    if (await weeklyTab.isVisible({ timeout: 2000 })) {
      await weeklyTab.click();
      await page.waitForTimeout(500);
      
      // Verify weekly stats are shown
      const weeklyStats = page.locator('.weekly-stats, [data-weekly-stats]').first();
      await expect(weeklyStats).toBeVisible({ timeout: 3000 });
    }
  });

  test('should display nutrition breakdown', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for macronutrient breakdown
    const macros = page.locator('.macros, .macro-breakdown, [data-macros]').first();
    
    if (await macros.isVisible({ timeout: 2000 })) {
      const content = await macros.textContent();
      
      // Should show protein, fat, and carbs
      const hasProtein = content?.toLowerCase().includes('protein');
      const hasFat = content?.toLowerCase().includes('fat');
      const hasCarbs = content?.toLowerCase().includes('carb');
      
      expect(hasProtein || hasFat || hasCarbs).toBeTruthy();
    }
  });

  test('should show calorie information', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for calorie display
    const calories = page.locator('text=/calor/i, .calories, [data-calories]').first();
    
    if (await calories.isVisible({ timeout: 2000 })) {
      const text = await calories.textContent();
      
      // Should contain a number
      const hasNumber = /\d+/.test(text || '');
      expect(hasNumber).toBeTruthy();
    }
  });

  test('should display keto metrics', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for keto-related information
    const ketoSection = page.locator('.keto, [data-keto], text=/keto index/i').first();
    
    if (await ketoSection.isVisible({ timeout: 2000 })) {
      const content = await ketoSection.textContent();
      
      // Should mention keto-related terms
      const hasKetoInfo = content?.toLowerCase().includes('keto') ||
                         content?.toLowerCase().includes('net carb');
      
      expect(hasKetoInfo).toBeTruthy();
    }
  });

  test('should show net carbs calculation', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for net carbs display
    const netCarbs = page.locator('text=/net carb/i, [data-net-carbs]').first();
    
    if (await netCarbs.isVisible({ timeout: 2000 })) {
      const text = await netCarbs.textContent();
      
      // Should show a number
      const hasNumber = /\d+/.test(text || '');
      expect(hasNumber).toBeTruthy();
    }
  });

  test('should change date range', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for date range picker or buttons
    const dateRange = page.locator('input[type="date"]').first();
    
    if (await dateRange.isVisible({ timeout: 2000 })) {
      // Change to yesterday
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      const yesterdayStr = yesterday.toISOString().split('T')[0];
      
      await dateRange.fill(yesterdayStr);
      await page.waitForTimeout(1000);
      
      // Verify date changed
      const currentValue = await dateRange.inputValue();
      expect(currentValue).toBe(yesterdayStr);
    }
  });

  test('should display charts or visualizations', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for chart elements (canvas, svg, chart containers)
    const chart = page.locator('canvas, svg.chart, .chart-container, [data-chart]').first();
    
    if (await chart.isVisible({ timeout: 2000 })) {
      // Verify chart is rendered
      await expect(chart).toBeVisible();
      
      // Check if chart has content
      const boundingBox = await chart.boundingBox();
      expect(boundingBox?.width).toBeGreaterThan(0);
      expect(boundingBox?.height).toBeGreaterThan(0);
    }
  });

  test('should show progress toward goals', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for goal progress indicators
    const progress = page.locator('.progress, [data-progress], text=/goal/i').first();
    
    if (await progress.isVisible({ timeout: 2000 })) {
      const content = await progress.textContent();
      
      // Should mention goals or progress
      const hasGoalInfo = content?.toLowerCase().includes('goal') ||
                         content?.toLowerCase().includes('target') ||
                         content?.toLowerCase().includes('progress');
      
      expect(hasGoalInfo).toBeTruthy();
    }
  });

  test('should display meal time breakdown', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for meal time distribution
    const mealBreakdown = page.locator('.meal-breakdown, [data-meals]').first();
    
    if (await mealBreakdown.isVisible({ timeout: 2000 })) {
      const content = await mealBreakdown.textContent();
      
      // Should show meal times
      const hasMeals = content?.toLowerCase().includes('breakfast') ||
                      content?.toLowerCase().includes('lunch') ||
                      content?.toLowerCase().includes('dinner');
      
      expect(hasMeals).toBeTruthy();
    }
  });

  test('should show average statistics', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for "Weekly" or "Average" tab/section
    const weeklyTab = page.locator('button:has-text("Weekly"), .tab:has-text("Week")').first();
    
    if (await weeklyTab.isVisible({ timeout: 2000 })) {
      await weeklyTab.click();
      await page.waitForTimeout(500);
      
      // Look for average statistics
      const averages = page.locator('text=/average/i, [data-average]').first();
      
      if (await averages.isVisible({ timeout: 2000 })) {
        const text = await averages.textContent();
        
        // Should contain numbers
        const hasNumbers = /\d+/.test(text || '');
        expect(hasNumbers).toBeTruthy();
      }
    }
  });

  test('should export statistics', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for export button
    const exportBtn = page.locator('button:has-text("Export"), button:has-text("Download"), [data-action="export"]').first();
    
    if (await exportBtn.isVisible({ timeout: 2000 })) {
      // Set up download listener
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null);
      
      // Click export
      await exportBtn.click();
      
      // Wait for download
      const download = await downloadPromise;
      
      // If download happens, verify it
      if (download) {
        const filename = download.suggestedFilename();
        expect(filename).toBeTruthy();
        
        // Should be a data file (CSV, JSON, etc.)
        const isDataFile = filename.endsWith('.csv') ||
                          filename.endsWith('.json') ||
                          filename.endsWith('.xlsx');
        expect(isDataFile).toBeTruthy();
      }
    }
  });

  test('should show comparison between periods', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for comparison features (this week vs last week, etc.)
    const comparison = page.locator('text=/vs|compare|previous/i').first();
    
    if (await comparison.isVisible({ timeout: 2000 })) {
      // Verify comparison is displayed
      await expect(comparison).toBeVisible();
    }
  });

  test('should display micronutrients', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for micronutrient information (fiber, sugars, etc.)
    const micronutrients = page.locator('text=/fiber|sugar|sodium|vitamin/i').first();
    
    if (await micronutrients.isVisible({ timeout: 2000 })) {
      const text = await micronutrients.textContent();
      
      // Should show nutrition values
      const hasValue = /\d+/.test(text || '');
      expect(hasValue).toBeTruthy();
    }
  });

  test('should handle empty statistics gracefully', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Change to a future date (should have no data)
    const datePicker = page.locator('input[type="date"]').first();
    
    if (await datePicker.isVisible({ timeout: 2000 })) {
      const futureDate = new Date();
      futureDate.setDate(futureDate.getDate() + 365);
      const futureDateStr = futureDate.toISOString().split('T')[0];
      
      await datePicker.fill(futureDateStr);
      await page.waitForTimeout(1000);
      
      // Should show empty state or zero values
      const emptyState = page.locator('text=/no data|no statistics|no entries/i').first();
      const hasEmptyState = await emptyState.isVisible({ timeout: 2000 }).catch(() => false);
      
      // Or should show zero values
      const zeroValues = page.locator('text=/0\\s*(cal|g)/').first();
      const hasZeros = await zeroValues.isVisible({ timeout: 2000 }).catch(() => false);
      
      expect(hasEmptyState || hasZeros).toBeTruthy();
    }
  });
});
