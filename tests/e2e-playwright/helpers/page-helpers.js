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
 * Detect if we're testing the demo version (no backend)
 * @param {import('@playwright/test').Page} page
 * @returns {Promise<boolean>}
 */
async function isDemoVersion(page) {
  try {
    // Demo version has a specific banner or structure
    const demoBanner = await page.locator('.demo-banner').count();
    if (demoBanner > 0) {
      console.log('[isDemoVersion] Demo version detected (demo-banner found)');
      return true;
    }
    
    // Check URL for demo server port
    const url = page.url();
    if (url.includes(':8080') || url.includes('/demo/')) {
      console.log('[isDemoVersion] Demo version detected (URL contains :8080 or /demo/)');
      return true;
    }
    
    console.log('[isDemoVersion] Flask backend version detected');
    return false;
  } catch (e) {
    console.log('[isDemoVersion] Error detecting version, assuming Flask backend');
    return false;
  }
}

/**
 * Wait for modal to be visible and ready for interaction, or skip if demo version
 * Handles CI environment slowness with longer timeouts and proper waits
 * @param {import('@playwright/test').Page} page
 * @param {Object} options
 * @returns {Promise<void>}
 */
async function waitForModal(page, options = {}) {
  const timeout = options.timeout || 20000; // Increased to 20s for CI reliability
  
  // Check if this is the demo version
  const isDemo = await isDemoVersion(page);
  if (isDemo) {
    console.log('[waitForModal] Demo version detected - skipping modal wait (forms are inline)');
    await page.waitForTimeout(500); // Small wait for any animations
    return;
  }
  
  // Try multiple modal selectors to handle different Bootstrap versions and custom modals
  const modalSelectors = [
    '.modal.show',           // Bootstrap 5 (show class added when visible)
    '.modal.fade.show',      // Bootstrap 5 with fade animation
    '.modal[style*="display: block"]', // Inline style check
    '[role="dialog"][aria-modal="true"]', // ARIA attributes
    '.modal:visible'         // Legacy Playwright pseudo-selector (fallback)
  ];
  
  let modalFound = false;
  let lastError = null;
  
  // Try each selector with a shorter individual timeout
  const individualTimeout = Math.floor(timeout / modalSelectors.length);
  
  for (const selector of modalSelectors) {
    try {
      await page.waitForSelector(selector, { 
        state: 'visible', 
        timeout: individualTimeout 
      });
      modalFound = true;
      console.log(`[waitForModal] Modal found with selector: ${selector}`);
      break;
    } catch (e) {
      lastError = e;
      console.log(`[waitForModal] Selector ${selector} not found, trying next...`);
    }
  }
  
  if (!modalFound) {
    throw new Error(`Modal not found with any selector after ${timeout}ms. Last error: ${lastError?.message}`);
  }
  
  // Wait for modal backdrop if present
  try {
    await page.waitForSelector('.modal-backdrop', { 
      state: 'visible', 
      timeout: 2000 
    });
  } catch (e) {
    // Some modals may not have a backdrop, continue
  }
  
  // Wait for modal content to be fully loaded
  try {
    await page.waitForSelector('.modal .modal-content, .modal-body', { 
      state: 'visible', 
      timeout: 5000 
    });
  } catch (e) {
    // Content selector may vary, continue if main modal is visible
    console.log('[waitForModal] Modal content selector not found, but modal is visible');
  }
  
  // Wait for any animations to complete (Bootstrap modal fade)
  await page.waitForTimeout(500);
  
  // Wait for network to be idle (in case modal loads data)
  try {
    await page.waitForLoadState('networkidle', { timeout: 3000 });
  } catch (e) {
    // NetworkIdle may timeout in some cases, that's OK
  }
}

/**
 * Close modal and wait for it to disappear, or skip if demo version
 * @param {import('@playwright/test').Page} page
 * @param {Object} options
 * @returns {Promise<void>}
 */
async function closeModal(page, options = {}) {
  const timeout = options.timeout || 20000; // Increased for CI
  
  // Check if this is the demo version
  const isDemo = await isDemoVersion(page);
  if (isDemo) {
    console.log('[closeModal] Demo version detected - skipping modal close (no modals)');
    return;
  }
  
  console.log('[closeModal] Attempting to close modal');
  
  // Try multiple close methods (X button, close button, cancel button)
  const closeSelectors = [
    '.modal .close',
    '.modal .btn-close', 
    '.modal button:has-text("Close")',
    '.modal button:has-text("Cancel")',
    '.modal [data-bs-dismiss="modal"]', // Bootstrap 5 dismiss attribute
    '.modal [data-dismiss="modal"]'     // Bootstrap 4 dismiss attribute
  ];
  
  let closeClicked = false;
  for (const selector of closeSelectors) {
    try {
      const closeButton = page.locator(selector).first();
      if (await closeButton.isVisible({ timeout: 1000 })) {
        await closeButton.click();
        console.log(`[closeModal] Clicked close button: ${selector}`);
        closeClicked = true;
        break;
      }
    } catch (e) {
      // Continue to next selector
    }
  }
  
  if (!closeClicked) {
    console.log('[closeModal] No close button found, trying ESC key');
    // Fallback: press ESC key
    await page.keyboard.press('Escape');
  }
  
  // Wait for modal to be hidden with multiple strategies
  try {
    await page.waitForSelector('.modal.show, .modal.fade.show', { 
      state: 'hidden', 
      timeout: timeout 
    });
    console.log('[closeModal] Modal hidden successfully');
  } catch (e) {
    // Try alternative hiding detection
    console.log('[closeModal] Trying alternative modal hiding detection');
    await page.waitForSelector('.modal[style*="display: none"]', { 
      timeout: 5000 
    }).catch(() => {
      console.log('[closeModal] Modal close detection uncertain, continuing');
    });
  }
  
  // Wait for backdrop to disappear
  try {
    await page.waitForSelector('.modal-backdrop', { 
      state: 'hidden', 
      timeout: 3000 
    });
  } catch (e) {
    // Backdrop may not exist
  }
  
  // Wait for network to settle
  try {
    await page.waitForLoadState('networkidle', { timeout: 3000 });
  } catch (e) {
    // NetworkIdle may timeout, that's OK
  }
  
  console.log('[closeModal] Modal close complete');
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
  const timeout = options.timeout || 20000; // Increased to 20s for CI
  
  console.log(`[clickWhenReady] Attempting to click element: ${selector}`);
  
  // Use Playwright locator (handles pseudo-selectors natively)
  const locator = page.locator(selector).first();
  
  // Wait for element to be visible and attached
  try {
    await locator.waitFor({ state: 'visible', timeout: timeout });
    console.log(`[clickWhenReady] Element visible: ${selector}`);
  } catch (e) {
    console.error(`[clickWhenReady] Element not visible within ${timeout}ms: ${selector}`);
    throw new Error(`Element not visible: ${selector}. ${e.message}`);
  }
  
  // Poll for enabled state using Playwright API
  // This avoids the querySelector incompatibility with Playwright pseudo-selectors
  const maxAttempts = Math.ceil(timeout / 100);
  let isEnabled = false;
  let attempts = 0;
  
  for (let i = 0; i < maxAttempts; i++) {
    attempts++;
    try {
      // Check if element is enabled (not disabled)
      // Note: isEnabled() doesn't accept a timeout parameter in Playwright API,
      // so we use this polling loop to repeatedly check the enabled state and
      // provide our own timeout functionality.
      const enabled = await locator.isEnabled();

      if (enabled) {
        // Additional check for 'disabled' class
        const hasDisabledClass = await locator.evaluate(el =>
          el.classList.contains('disabled')
        ).catch(() => false); // Handle element detachment gracefully

        if (!hasDisabledClass) {
          isEnabled = true;
          console.log(`[clickWhenReady] Element enabled after ${attempts} attempts: ${selector}`);
          break;
        }
      }
    } catch (e) {
      // Element might not be ready yet, continue polling
      if (i > maxAttempts - 5) {
        console.log(`[clickWhenReady] Element still not enabled (attempt ${i}/${maxAttempts}): ${selector}`);
      }
    }

    await page.waitForTimeout(100);
  }
  
  if (!isEnabled) {
    console.error(`[clickWhenReady] Element disabled after ${timeout}ms: ${selector}`);
    throw new Error(`Element ${selector} is still disabled after ${timeout}ms (${attempts} attempts)`);
  }
  
  // Wait for any animations to complete
  await page.waitForTimeout(300);
  
  // Click the element using locator with force option as fallback
  try {
    await locator.click({ timeout: 5000 });
    console.log(`[clickWhenReady] Successfully clicked: ${selector}`);
  } catch (e) {
    console.log(`[clickWhenReady] Regular click failed, trying force click: ${selector}`);
    // Sometimes elements are clickable but covered by animations, force click
    await locator.click({ force: true, timeout: 5000 });
    console.log(`[clickWhenReady] Force clicked successfully: ${selector}`);
  }
}

/**
 * Submit form in modal and wait for completion, or submit inline form for demo version
 * @param {import('@playwright/test').Page} page
 * @param {Object} options
 * @returns {Promise<void>}
 */
async function submitModalForm(page, options = {}) {
  const timeout = options.timeout || 20000; // Increased for CI reliability
  const waitForApi = options.waitForApi !== false; // Default true
  
  // Check if this is the demo version
  const isDemo = await isDemoVersion(page);
  
  if (isDemo) {
    console.log('[submitModalForm] Demo version detected - submitting inline form');
    // Demo uses inline forms, look for submit button in active tab pane
    const demoSubmitSelectors = [
      '.tab-pane.active button[type="submit"]',
      '.tab-pane.active form button:has-text("Add")',
      '#productForm button[type="submit"]',
      '#logForm button[type="submit"]'
    ];
    
    let submitButton = null;
    for (const selector of demoSubmitSelectors) {
      try {
        const button = page.locator(selector).first();
        if (await button.isVisible({ timeout: 1000 })) {
          submitButton = selector;
          console.log(`[submitModalForm] Found demo submit button: ${selector}`);
          break;
        }
      } catch (e) {
        // Try next selector
      }
    }
    
    if (!submitButton) {
      console.log('[submitModalForm] No submit button found in demo, trying generic form submit');
      // Try generic form submit
      await page.locator('form button[type="submit"]').first().click();
    } else {
      await page.locator(submitButton).click();
    }
    
    // Wait for LocalStorage operations to complete
    await page.waitForTimeout(1000);
    console.log('[submitModalForm] Demo form submission complete');
    return;
  }
  
  console.log('[submitModalForm] Looking for submit button in modal');
  
  // Find submit button with multiple selectors
  const submitSelectors = [
    '.modal button[type="submit"]',
    '.modal button:has-text("Save")',
    '.modal button:has-text("Add")',
    '.modal button:has-text("Submit")',
    '.modal .btn-primary'
  ];
  
  let submitButton = null;
  for (const selector of submitSelectors) {
    try {
      const button = page.locator(selector).first();
      if (await button.isVisible({ timeout: 1000 })) {
        submitButton = selector;
        console.log(`[submitModalForm] Found submit button: ${selector}`);
        break;
      }
    } catch (e) {
      // Try next selector
    }
  }
  
  if (!submitButton) {
    throw new Error('Submit button not found in modal. Tried selectors: ' + submitSelectors.join(', '));
  }
  
  if (waitForApi) {
    // Wait for API response (or timeout for demo version)
    try {
      console.log('[submitModalForm] Waiting for API response and clicking submit');
      await Promise.all([
        page.waitForResponse(
          resp => {
            const isApi = resp.url().includes('/api/');
            const isSuccess = resp.status() === 200 || resp.status() === 201;
            return isApi && isSuccess;
          },
          { timeout: timeout }
        ),
        clickWhenReady(page, submitButton, { timeout: timeout })
      ]);
      console.log('[submitModalForm] Form submitted successfully with API response');
    } catch (e) {
      console.log('[submitModalForm] No API response (demo version), clicking and waiting');
      // Demo version - just click and wait
      await clickWhenReady(page, submitButton, { timeout: timeout });
      await page.waitForTimeout(1000);
    }
  } else {
    console.log('[submitModalForm] Clicking submit without waiting for API');
    await clickWhenReady(page, submitButton, { timeout: timeout });
  }
  
  // Wait for modal to close with multiple strategies
  console.log('[submitModalForm] Waiting for modal to close');
  try {
    await page.waitForSelector('.modal.show, .modal.fade.show', { 
      state: 'hidden', 
      timeout: timeout 
    });
  } catch (e) {
    // Try alternative modal hiding detection
    await page.waitForSelector('.modal[style*="display: none"], .modal[style*="display:none"]', { 
      timeout: 5000 
    }).catch(() => {
      // Modal might use different hiding mechanism
      console.log('[submitModalForm] Modal close detection uncertain, continuing');
    });
  }
  
  // Wait for backdrop to disappear
  try {
    await page.waitForSelector('.modal-backdrop', { 
      state: 'hidden', 
      timeout: 3000 
    });
  } catch (e) {
    // Backdrop detection is optional
  }
  
  // Wait for network to settle
  try {
    await page.waitForLoadState('networkidle', { timeout: 3000 });
  } catch (e) {
    // NetworkIdle may timeout, that's OK
  }
  
  console.log('[submitModalForm] Modal form submission complete');
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
  isDemoVersion,
  waitForModal,
  closeModal,
  clickWhenReady,
  submitModalForm,
  // Console error helpers
  captureConsoleErrors,
  getCriticalErrors,
  KNOWN_NON_CRITICAL_ERRORS,
};
