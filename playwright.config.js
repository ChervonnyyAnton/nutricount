// @ts-check
const { defineConfig, devices } = require('@playwright/test');

/**
 * Read environment variables from file.
 * https://github.com/motdotla/dotenv
 */
// require('dotenv').config();

/**
 * @see https://playwright.dev/docs/test-configuration
 */
module.exports = defineConfig({
  testDir: './tests/e2e-playwright',
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  /* Global timeout for each test - increased for CI */
  timeout: 60 * 1000, // 60 seconds per test
  /* Expect timeout for assertions */
  expect: {
    timeout: 10 * 1000, // 10 seconds for assertions
  },
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list']
  ],
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: process.env.BASE_URL || 'http://localhost:5000',
    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',
    /* Screenshot on failure */
    screenshot: 'only-on-failure',
    /* Video on failure */
    video: 'retain-on-failure',
    /* Navigation timeout - increased for CI */
    navigationTimeout: 30 * 1000, // 30 seconds
    /* Action timeout - increased for CI */
    actionTimeout: 15 * 1000, // 15 seconds for clicks, fills, etc.
    // If you need to ignore HTTPS errors for specific resources, set ignoreHTTPSErrors: true in those test contexts only.
    // ignoreHTTPSErrors: true,
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    // Uncomment for more browser coverage
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },

    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },

    /* Test against mobile viewports. */
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    // {
    //   name: 'Mobile Safari',
    //   use: { ...devices['iPhone 12'] },
    // },
  ],

  /* Run your local dev server before starting the tests */
  /* Only auto-start server in local development (not in CI) */
  /* In CI, the workflow starts the server manually to have better control */
  webServer: process.env.CI 
    ? undefined 
    : (process.env.BASE_URL && process.env.BASE_URL !== 'http://localhost:5000' 
      ? undefined 
      : {
          command: 'python3 app.py',
          url: 'http://localhost:5000',
          reuseExistingServer: false, // Always start fresh server in local development
          timeout: 120 * 1000,
          env: {
            FLASK_ENV: 'test',
            PYTHONPATH: process.cwd(),
          },
        }),
});
