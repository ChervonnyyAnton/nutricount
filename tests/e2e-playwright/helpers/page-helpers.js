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
  const timeout = options.timeout || 5000;
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
 * Wait for API response
 * @param {import('@playwright/test').Page} page
 * @param {string} urlPattern
 * @param {Function} action
 * @returns {Promise<Response>}
 */
async function waitForApiResponse(page, urlPattern, action) {
  const responsePromise = page.waitForResponse(
    (response) => response.url().includes(urlPattern) && response.status() === 200
  );
  await action();
  return await responsePromise;
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
};
