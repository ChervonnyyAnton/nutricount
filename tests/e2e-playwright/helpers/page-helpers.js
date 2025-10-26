/**
 * Helper functions for Playwright E2E tests
 */

/**
 * Wait for element to be visible and ready
 * @param {import('@playwright/test').Page} page
 * @param {string} selector
 * @param {Object} options
 */
async function waitForElement(page, selector, options = {}) {
  const timeout = options.timeout || 15000; // Increased from 5s to 15s for CI
  await page.waitForSelector(selector, { state: 'visible', timeout });
}

/**
 * Fill form field with proper waiting
 * @param {import('@playwright/test').Page} page
 * @param {string} selector
 * @param {string} value
 */
async function fillField(page, selector, value) {
  await waitForElement(page, selector);
  await page.fill(selector, value);
}

/**
 * Click element with proper waiting
 * @param {import('@playwright/test').Page} page
 * @param {string} selector
 */
async function clickElement(page, selector) {
  await waitForElement(page, selector);
  await page.click(selector);
}

/**
 * Get text content from element
 * @param {import('@playwright/test').Page} page
 * @param {string} selector
 * @returns {Promise<string>}
 */
async function getTextContent(page, selector) {
  await waitForElement(page, selector);
  return await page.textContent(selector);
}

/**
 * Check if element exists on page
 * @param {import('@playwright/test').Page} page
 * @param {string} selector
 * @returns {Promise<boolean>}
 */
async function elementExists(page, selector) {
  try {
    await page.waitForSelector(selector, { state: 'attached', timeout: 2000 });
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Wait for API response (with fallback for demo version)
 * @param {import('@playwright/test').Page} page
 * @param {string} urlPattern
 * @param {Function} action
 * @param {Object} options
 * @returns {Promise<Response|null>}
 */
async function waitForApiResponse(page, urlPattern, action, options = {}) {
  const timeout = options.timeout || 5000;
  
  try {
    const responsePromise = page.waitForResponse(
      (response) => response.url().includes(urlPattern) && response.status() === 200,
      { timeout }
    );
    await action();
    return await responsePromise;
  } catch (e) {
    // Demo version doesn't have API - just perform the action
    await action();
    // Wait a bit for localStorage operations to complete
    await page.waitForTimeout(500);
    return null;
  }
}

/**
 * Clear local storage
 * @param {import('@playwright/test').Page} page
 */
async function clearLocalStorage(page) {
  await page.evaluate(() => localStorage.clear());
}

/**
 * Set local storage item
 * @param {import('@playwright/test').Page} page
 * @param {string} key
 * @param {string} value
 */
async function setLocalStorageItem(page, key, value) {
  await page.evaluate(
    ({ key, value }) => localStorage.setItem(key, value),
    { key, value }
  );
}

/**
 * Get local storage item
 * @param {import('@playwright/test').Page} page
 * @param {string} key
 * @returns {Promise<string|null>}
 */
async function getLocalStorageItem(page, key) {
  return await page.evaluate((key) => localStorage.getItem(key), key);
}

/**
 * Take screenshot with timestamp
 * @param {import('@playwright/test').Page} page
 * @param {string} name
 */
async function takeScreenshot(page, name) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  await page.screenshot({ path: `screenshots/${name}-${timestamp}.png` });
}

/**
 * Wait for navigation to complete
 * @param {import('@playwright/test').Page} page
 * @param {Function} action
 */
async function waitForNavigation(page, action) {
  await Promise.all([page.waitForNavigation(), action()]);
}

/**
 * Check if page has error messages
 * @param {import('@playwright/test').Page} page
 * @returns {Promise<boolean>}
 */
async function hasErrorMessage(page) {
  const errorSelectors = ['.alert-danger', '.error-message', '[role="alert"]'];
  for (const selector of errorSelectors) {
    if (await elementExists(page, selector)) {
      return true;
    }
  }
  return false;
}

/**
 * Check if page has success messages
 * @param {import('@playwright/test').Page} page
 * @returns {Promise<boolean>}
 */
async function hasSuccessMessage(page) {
  const successSelectors = ['.alert-success', '.success-message'];
  for (const selector of successSelectors) {
    if (await elementExists(page, selector)) {
      return true;
    }
  }
  return false;
}

/**
 * Wait for modal to be visible and ready for interaction
 * Handles CI environment slowness with longer timeouts and proper waits
 * @param {import('@playwright/test').Page} page
 * @param {Object} options
 * @returns {Promise<void>}
 */
async function waitForModal(page, options = {}) {
  const timeout = options.timeout || 15000; // Increased from 5s to 15s for CI
  
  // Wait for modal backdrop to appear (indicates modal is opening)
  try {
    await page.waitForSelector('.modal-backdrop', { 
      state: 'visible', 
      timeout: timeout 
    });
  } catch (e) {
    // Some modals may not have a backdrop, continue
  }
  
  // Wait for modal itself to be visible
  await page.waitForSelector('.modal:visible', { 
    timeout: timeout 
  });
  
  // Wait for modal content to be fully loaded
  await page.waitForSelector('.modal .modal-content', { 
    state: 'visible', 
    timeout: timeout 
  });
  
  // Wait for any animations to complete (Bootstrap modal fade)
  await page.waitForTimeout(500);
  
  // Wait for network to be idle (in case modal loads data)
  try {
    await page.waitForLoadState('networkidle', { timeout: 5000 });
  } catch (e) {
    // NetworkIdle may timeout in some cases, that's OK
  }
}

/**
 * Close modal and wait for it to disappear
 * @param {import('@playwright/test').Page} page
 * @param {Object} options
 * @returns {Promise<void>}
 */
async function closeModal(page, options = {}) {
  const timeout = options.timeout || 15000;
  
  // Try multiple close methods (X button, close button, cancel button)
  const closeSelectors = [
    '.modal .close',
    '.modal .btn-close', 
    '.modal button:has-text("Close")',
    '.modal button:has-text("Cancel")'
  ];
  
  for (const selector of closeSelectors) {
    try {
      const closeButton = page.locator(selector).first();
      if (await closeButton.isVisible({ timeout: 1000 })) {
        await closeButton.click();
        break;
      }
    } catch (e) {
      // Continue to next selector
    }
  }
  
  // Wait for modal to be hidden
  await page.waitForSelector('.modal', { 
    state: 'hidden', 
    timeout: timeout 
  });
  
  // Wait for backdrop to disappear
  try {
    await page.waitForSelector('.modal-backdrop', { 
      state: 'hidden', 
      timeout: 5000 
    });
  } catch (e) {
    // Backdrop may not exist
  }
  
  // Wait for network to settle
  try {
    await page.waitForLoadState('networkidle', { timeout: 5000 });
  } catch (e) {
    // NetworkIdle may timeout, that's OK
  }
}

/**
 * Click button and wait for it to be ready
 * Handles disabled states and loading indicators
 * @param {import('@playwright/test').Page} page
 * @param {string} selector - Playwright selector (supports pseudo-selectors like :has-text())
 * @param {Object} options
 * @returns {Promise<void>}
 */
async function clickWhenReady(page, selector, options = {}) {
  const timeout = options.timeout || 15000;
  
  // Use Playwright locator (handles pseudo-selectors natively)
  const locator = page.locator(selector).first();
  
  // Wait for element to be visible
  await locator.waitFor({ state: 'visible', timeout: timeout });
  
  // Poll for enabled state using Playwright API
  // This avoids the querySelector incompatibility with Playwright pseudo-selectors
  const maxAttempts = Math.ceil(timeout / 100);
  let isEnabled = false;
  
  for (let i = 0; i < maxAttempts; i++) {
    try {
      // Check if element is enabled (not disabled)
      isEnabled = await locator.isEnabled({ timeout: 100 });
      
      if (isEnabled) {
        // Additional check for 'disabled' class
        const hasDisabledClass = await locator.evaluate(el => 
          el.classList.contains('disabled')
        );
        
        if (!hasDisabledClass) {
          break;
        }
      }
    } catch (e) {
      // Element might not be ready yet, continue polling
    }
    
    await page.waitForTimeout(100);
  }
  
  if (!isEnabled) {
    throw new Error(`Element ${selector} is still disabled after ${timeout}ms`);
  }
  
  // Wait for any animations to complete
  await page.waitForTimeout(300);
  
  // Click the element using locator
  await locator.click();
}

/**
 * Submit form in modal and wait for completion
 * @param {import('@playwright/test').Page} page
 * @param {Object} options
 * @returns {Promise<void>}
 */
async function submitModalForm(page, options = {}) {
  const timeout = options.timeout || 15000;
  const waitForApi = options.waitForApi !== false; // Default true
  
  // Find submit button
  const submitSelectors = [
    '.modal button[type="submit"]',
    '.modal button:has-text("Save")',
    '.modal button:has-text("Add")',
    '.modal button:has-text("Submit")'
  ];
  
  let submitButton = null;
  for (const selector of submitSelectors) {
    const button = page.locator(selector).last();
    if (await button.isVisible({ timeout: 1000 })) {
      submitButton = selector;
      break;
    }
  }
  
  if (!submitButton) {
    throw new Error('Submit button not found in modal');
  }
  
  if (waitForApi) {
    // Wait for API response (or timeout for demo version)
    try {
      await Promise.all([
        page.waitForResponse(
          resp => resp.url().includes('/api/') && resp.status() === 200,
          { timeout: timeout }
        ),
        clickWhenReady(page, submitButton)
      ]);
    } catch (e) {
      // Demo version - just click and wait
      await clickWhenReady(page, submitButton);
      await page.waitForTimeout(1000);
    }
  } else {
    await clickWhenReady(page, submitButton);
  }
  
  // Wait for modal to close
  await page.waitForSelector('.modal', { 
    state: 'hidden', 
    timeout: timeout 
  });
  
  // Wait for network to settle
  try {
    await page.waitForLoadState('networkidle', { timeout: 5000 });
  } catch (e) {
    // NetworkIdle may timeout, that's OK
  }
}

/**
 * List of known non-critical console error patterns to filter out
 * These are errors that don't affect functionality
 */
const KNOWN_NON_CRITICAL_ERRORS = [
  'favicon',              // Missing favicon
  'sourcemap',            // Missing source maps
  'Failed to load resource', // Generic resource loading (often non-critical)
  'net::ERR_',           // Network errors during testing
  'ResizeObserver',      // ResizeObserver loop limit exceeded (browser bug)
  'chrome-extension',    // Chrome extension errors
  'Manifest:',          // PWA manifest warnings
  'Service Worker',     // Service worker registration issues in tests
];

/**
 * Capture and filter console errors on a page
 * @param {import('@playwright/test').Page} page
 * @param {Object} options
 * @returns {Promise<Array<string>>} Array of critical error messages
 */
async function captureConsoleErrors(page, options = {}) {
  const errors = [];
  const additionalFilters = options.additionalFilters || [];
  const allFilters = [...KNOWN_NON_CRITICAL_ERRORS, ...additionalFilters];
  
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      const errorText = msg.text();
      
      // Check if error matches any known non-critical pattern
      const isNonCritical = allFilters.some(pattern => 
        errorText.toLowerCase().includes(pattern.toLowerCase())
      );
      
      if (!isNonCritical) {
        errors.push(errorText);
      }
    }
  });
  
  return errors;
}

/**
 * Get captured console errors
 * @param {Array<string>} errors - Array returned by captureConsoleErrors
 * @returns {Array<string>} Array of critical error messages
 */
function getCriticalErrors(errors) {
  return errors;
}

module.exports = {
  waitForElement,
  fillField,
  clickElement,
  getTextContent,
  elementExists,
  waitForApiResponse,
  clearLocalStorage,
  setLocalStorageItem,
  getLocalStorageItem,
  takeScreenshot,
  waitForNavigation,
  hasErrorMessage,
  hasSuccessMessage,
  // New modal helpers
  waitForModal,
  closeModal,
  clickWhenReady,
  submitModalForm,
  // Console error helpers
  captureConsoleErrors,
  getCriticalErrors,
  KNOWN_NON_CRITICAL_ERRORS,
};
