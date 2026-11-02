/**
 * Smoke-test a `vite preview` build against a running backend.
 *
 * Usage:
 *   npm run build
 *   npm run preview -- --host 127.0.0.1 --port 4173
 *   node scripts/smoke-production.mjs
 *
 * The preview server proxies /api to VITE_API_PROXY_TARGET (default
 * http://127.0.0.1:8000). The backend must have an admin seeded.
 */
import { chromium } from 'playwright';
import path from 'node:path';

const baseUrl =
  process.env.SMOKE_URL || process.env.PREVIEW_URL || 'http://127.0.0.1:4173';
const screenshotPrefix = process.env.SMOKE_SCREENSHOT_PREFIX || 'production';
const email = process.env.SMOKE_ADMIN_EMAIL || 'admin@example.com';
const password = process.env.SMOKE_ADMIN_PASSWORD || 'AdminPass123!';
const screenshots = path.resolve(process.cwd(), '../../docs/evidence/screenshots');

const consoleErrors = [];
const apiFailures = [];
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
page.on('console', (msg) => {
  if (msg.type() === 'error') consoleErrors.push(msg.text());
});
page.on('pageerror', (err) => consoleErrors.push(`pageerror: ${err.message}`));
page.on('response', (res) => {
  if (res.url().includes('/api/') && res.status() >= 400) {
    apiFailures.push(`${res.status()} ${res.url()}`);
  }
});

await page.goto(`${baseUrl}/`);
await page.waitForSelector('h1');
await page.waitForLoadState('networkidle');
// Allow the landing page's Fade/Slide transitions and lazy image to settle.
await page.waitForTimeout(1600);
const title = await page.title();
const heading = await page.locator('h1').first().innerText();
await page.screenshot({
  path: path.join(screenshots, `homepage-${screenshotPrefix}.png`),
  fullPage: true,
});

await page.goto(`${baseUrl}/login`);
await page.locator('#email').fill(email);
await page.locator('#password').fill(password);
await page.getByRole('button', { name: 'Sign In', exact: true }).click();
await page.waitForURL(/\/dashboard$/);
await page.waitForSelector('text=Platform Growth (last 24 hours)');
// Let the login snackbar auto-hide so the evidence screenshot is unobstructed.
await page.waitForTimeout(3200);
const dashboardHeading = await page.locator('h1').first().innerText();
await page.screenshot({
  path: path.join(screenshots, `dashboard-${screenshotPrefix}.png`),
  fullPage: true,
});

console.log(
  JSON.stringify(
    {
      title,
      heading,
      dashboardHeading,
      url: page.url(),
      consoleErrors,
      apiFailures,
    },
    null,
    2,
  ),
);
await browser.close();
