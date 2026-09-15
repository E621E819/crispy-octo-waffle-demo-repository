import { defineConfig } from '@playwright/test'
export default defineConfig({
  testDir: './tests',
  timeout: 45000,
  expect: { timeout: 10000 },
  fullyParallel: false,
  use: { baseURL: process.env.TEST_URL || 'http://127.0.0.1:8000', headless: true, viewport: { width: 1440, height: 1000 }, screenshot: 'only-on-failure' },
  reporter: 'list',
})
