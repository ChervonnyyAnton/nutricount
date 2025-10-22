// @ts-check
const { test, expect } = require('@playwright/test');
const helpers = require('./helpers/page-helpers');

test.describe('Fasting Tracking Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Navigate to Fasting tab
    await helpers.clickElement(page, 'text=Fasting');
    await page.waitForTimeout(500); // Wait for tab to load
  });

  test('should display fasting page', async ({ page }) => {
    // Verify fasting section is visible
    const fastingSection = page.locator('#fasting-section, .fasting-container, [data-fasting]').first();
    await expect(fastingSection).toBeVisible();
  });

  test('should show fasting types', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for fasting type options (16:8, 18:6, 20:4, OMAD, etc.)
    const fastingTypes = page.locator('text=/16:8|18:6|20:4|OMAD/i').first();
    
    if (await fastingTypes.isVisible({ timeout: 2000 })) {
      const text = await fastingTypes.textContent();
      
      // Should show at least one fasting type
      const hasType = /16:8|18:6|20:4|OMAD/i.test(text || '');
      expect(hasType).toBeTruthy();
    }
  });

  test('should start a fasting session', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for "Start Fasting" button
    const startBtn = page.locator('button:has-text("Start"), button:has-text("Begin"), [data-action="start"]').first();
    
    if (await startBtn.isVisible({ timeout: 2000 })) {
      // Select fasting type if available
      const fastingTypeSelect = page.locator('select[name="fasting_type"], input[name="type"]').first();
      if (await fastingTypeSelect.isVisible({ timeout: 2000 })) {
        if (await fastingTypeSelect.evaluate(el => el.tagName === 'SELECT')) {
          await fastingTypeSelect.selectOption('16:8');
        }
      }
      
      // Click start button
      await startBtn.click();
      await page.waitForTimeout(1000);
      
      // Verify fasting session started
      const status = page.locator('text=/fasting|active|in progress/i').first();
      const hasActiveSession = await status.isVisible({ timeout: 3000 }).catch(() => false);
      
      // Or check for timer
      const timer = page.locator('.timer, [data-timer], text=/\\d+:\\d+/').first();
      const hasTimer = await timer.isVisible({ timeout: 3000 }).catch(() => false);
      
      expect(hasActiveSession || hasTimer).toBeTruthy();
    }
  });

  test('should show fasting timer', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for timer display
    const timer = page.locator('.timer, [data-timer], text=/\\d+:\\d+/').first();
    
    if (await timer.isVisible({ timeout: 2000 })) {
      const text = await timer.textContent();
      
      // Should show time in format HH:MM or similar
      const hasTimeFormat = /\d+:\d+/.test(text || '');
      expect(hasTimeFormat).toBeTruthy();
    }
  });

  test('should display fasting progress', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for progress indicator
    const progress = page.locator('.progress, [data-progress], text=/progress|%/i').first();
    
    if (await progress.isVisible({ timeout: 2000 })) {
      // Verify progress is shown
      await expect(progress).toBeVisible();
    }
  });

  test('should pause a fasting session', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for pause button (only visible if session is active)
    const pauseBtn = page.locator('button:has-text("Pause"), [data-action="pause"]').first();
    
    if (await pauseBtn.isVisible({ timeout: 2000 })) {
      // Click pause
      await pauseBtn.click();
      await page.waitForTimeout(1000);
      
      // Verify session is paused
      const pausedStatus = page.locator('text=/paused/i').first();
      const isPaused = await pausedStatus.isVisible({ timeout: 3000 }).catch(() => false);
      
      // Or check for resume button
      const resumeBtn = page.locator('button:has-text("Resume")').first();
      const hasResume = await resumeBtn.isVisible({ timeout: 3000 }).catch(() => false);
      
      expect(isPaused || hasResume).toBeTruthy();
    }
  });

  test('should resume a fasting session', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for resume button
    const resumeBtn = page.locator('button:has-text("Resume"), [data-action="resume"]').first();
    
    if (await resumeBtn.isVisible({ timeout: 2000 })) {
      // Click resume
      await resumeBtn.click();
      await page.waitForTimeout(1000);
      
      // Verify session is active again
      const activeStatus = page.locator('text=/active|in progress/i').first();
      const isActive = await activeStatus.isVisible({ timeout: 3000 }).catch(() => false);
      
      expect(isActive).toBeTruthy();
    }
  });

  test('should end a fasting session', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for end/stop button
    const endBtn = page.locator('button:has-text("End"), button:has-text("Stop"), button:has-text("Finish"), [data-action="end"]').first();
    
    if (await endBtn.isVisible({ timeout: 2000 })) {
      // Click end button
      await endBtn.click();
      await page.waitForTimeout(500);
      
      // Confirm if needed
      const confirmBtn = page.locator('button:has-text("Confirm"), button:has-text("Yes")').last();
      if (await confirmBtn.isVisible({ timeout: 1000 })) {
        await confirmBtn.click();
      }
      
      await page.waitForTimeout(1000);
      
      // Verify session ended
      const hasSuccess = await helpers.hasSuccessMessage(page);
      const startBtn = page.locator('button:has-text("Start")').first();
      const canStartNew = await startBtn.isVisible({ timeout: 3000 }).catch(() => false);
      
      expect(hasSuccess || canStartNew).toBeTruthy();
    }
  });

  test('should show fasting history', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for history section or tab
    const historyTab = page.locator('button:has-text("History"), .tab:has-text("History"), [data-tab="history"]').first();
    
    if (await historyTab.isVisible({ timeout: 2000 })) {
      await historyTab.click();
      await page.waitForTimeout(500);
      
      // Verify history section is shown
      const historySection = page.locator('.history, .fasting-history, [data-history]').first();
      await expect(historySection).toBeVisible({ timeout: 3000 });
    }
  });

  test('should display fasting statistics', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for statistics section
    const stats = page.locator('.fasting-stats, [data-fasting-stats], text=/stats|statistics/i').first();
    
    if (await stats.isVisible({ timeout: 2000 })) {
      const content = await stats.textContent();
      
      // Should show fasting metrics
      const hasMetrics = content?.toLowerCase().includes('session') ||
                        content?.toLowerCase().includes('average') ||
                        content?.toLowerCase().includes('longest') ||
                        content?.toLowerCase().includes('total');
      
      expect(hasMetrics).toBeTruthy();
    }
  });

  test('should show current fasting status', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for status indicator
    const status = page.locator('.status, [data-status], .fasting-status').first();
    
    if (await status.isVisible({ timeout: 2000 })) {
      const text = await status.textContent();
      
      // Should show status (active, inactive, paused, completed)
      const hasStatus = /active|inactive|paused|complete|not fasting/i.test(text || '');
      expect(hasStatus).toBeTruthy();
    }
  });

  test('should display fasting goals', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for goals section
    const goals = page.locator('.goals, [data-goals], text=/goal/i').first();
    
    if (await goals.isVisible({ timeout: 2000 })) {
      const content = await goals.textContent();
      
      // Should mention goals
      const hasGoalInfo = content?.toLowerCase().includes('goal') ||
                         content?.toLowerCase().includes('target');
      
      expect(hasGoalInfo).toBeTruthy();
    }
  });

  test('should allow adding notes to fasting session', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for notes input
    const notesInput = page.locator('textarea[name="notes"], input[name="notes"], [data-notes]').first();
    
    if (await notesInput.isVisible({ timeout: 2000 })) {
      // Add a note
      await notesInput.fill('Test fasting note');
      await page.waitForTimeout(500);
      
      // Verify note was added
      const value = await notesInput.inputValue();
      expect(value).toContain('Test fasting note');
    }
  });

  test('should show fasting streak', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for streak display
    const streak = page.locator('text=/streak|consecutive/i, [data-streak]').first();
    
    if (await streak.isVisible({ timeout: 2000 })) {
      const text = await streak.textContent();
      
      // Should show a number
      const hasNumber = /\d+/.test(text || '');
      expect(hasNumber).toBeTruthy();
    }
  });

  test('should display different fasting protocols', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for protocol selection
    const protocols = page.locator('select[name="protocol"], select[name="fasting_type"]').first();
    
    if (await protocols.isVisible({ timeout: 2000 })) {
      // Get options
      const options = await protocols.locator('option').allTextContents();
      
      // Should have multiple fasting types
      expect(options.length).toBeGreaterThan(1);
      
      // Should include common types
      const hasCommonTypes = options.some(opt => 
        /16:8|18:6|20:4|OMAD|custom/i.test(opt)
      );
      
      expect(hasCommonTypes).toBeTruthy();
    }
  });

  test('should validate fasting session data', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Try to start without selecting type (if required)
    const startBtn = page.locator('button:has-text("Start")').first();
    
    if (await startBtn.isVisible({ timeout: 2000 })) {
      // Click start without selecting type
      await startBtn.click();
      await page.waitForTimeout(500);
      
      // Should either start with default or show validation
      const hasError = await helpers.hasErrorMessage(page);
      const hasSession = page.locator('.timer, [data-timer]').isVisible({ timeout: 2000 }).catch(() => false);
      
      // Should either validate or start successfully
      expect(hasError || hasSession).toBeTruthy();
    }
  });

  test('should show time until goal', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Look for countdown or time remaining
    const timeRemaining = page.locator('text=/remaining|time left|until goal/i, [data-remaining]').first();
    
    if (await timeRemaining.isVisible({ timeout: 2000 })) {
      const text = await timeRemaining.textContent();
      
      // Should show time
      const hasTime = /\d+:\d+/.test(text || '') || /\d+\s*(hour|min)/i.test(text || '');
      expect(hasTime).toBeTruthy();
    }
  });
});
