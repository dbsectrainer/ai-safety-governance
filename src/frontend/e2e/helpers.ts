import fs from 'node:fs';
import path from 'node:path';
import type { Page } from '@playwright/test';
import { expect } from './fixtures';

export const ADMIN = {
  email: 'e2e-admin@example.com',
  password: 'E2eAdmin123!',
};

export const SCREENSHOT_DIR = path.resolve(process.cwd(), '../../docs/evidence/screenshots');
export const TEST_RESULTS_DIR = path.resolve(process.cwd(), '../../docs/evidence/test-results');

fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
fs.mkdirSync(TEST_RESULTS_DIR, { recursive: true });

export async function capture(page: Page, filename: string, fullPage = true) {
  // Allow MUI transitions and snackbars to settle so screenshots (and layout
  // assertions) reflect the stable page rather than an enter animation.
  await page.waitForTimeout(600);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, filename), fullPage });
}

export async function login(
  page: Page,
  email: string = ADMIN.email,
  password: string = ADMIN.password,
) {
  await page.goto('/login');
  await expect(page.getByRole('heading', { name: 'Sign In', exact: true })).toBeVisible();
  await page.getByLabel('Email Address').fill(email);
  await page.locator('#password').fill(password);
  await page.getByRole('button', { name: 'Sign In', exact: true }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole('heading', { name: 'Dashboard', exact: true })).toBeVisible();
}

export async function logout(page: Page) {
  await page.getByRole('button', { name: 'Open account menu' }).click();
  await page.getByRole('menuitem', { name: 'Sign out' }).click();
  await expect(page).toHaveURL(/\/login$/);
}

export function uniqueSuffix(): string {
  return `${Date.now().toString(36).slice(-5)}${Math.floor(Math.random() * 90 + 10)}`;
}

export async function expectNoHorizontalOverflow(page: Page) {
  await page.waitForTimeout(300);
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth - window.innerWidth,
  );
  expect(overflow, 'page should not overflow horizontally').toBeLessThanOrEqual(1);
}

/**
 * Seed a model version, monitoring samples and a compliance snapshot through
 * the real API so dashboard/monitoring screenshots show meaningful data.
 */
export async function seedPlatformData(page: Page) {
  const token = await page.evaluate(() => localStorage.getItem('token'));
  const headers = { Authorization: `Bearer ${token}` };

  const listing = await page.request.get('/api/v1/models/versions', { headers });
  let versionId: number | undefined;
  if (listing.ok()) {
    const versions = (await listing.json()) as Array<{ id: number; name: string; version: string }>;
    versionId = versions.find((item) => item.name === 'e2e-risk-model' && item.version === '1.0.0')
      ?.id;
  }

  if (!versionId) {
    const created = await page.request.post('/api/v1/models/versions', {
      headers,
      data: {
        name: 'e2e-risk-model',
        version: '1.0.0',
        version_metadata: { framework: 'sklearn', owner: 'e2e' },
        status: 'deployed',
      },
    });
    if (created.status() === 201) {
      versionId = ((await created.json()) as { id: number }).id;
    } else {
      const retry = await page.request.get('/api/v1/models/versions', { headers });
      const versions = (await retry.json()) as Array<{ id: number; name: string; version: string }>;
      versionId = versions.find(
        (item) => item.name === 'e2e-risk-model' && item.version === '1.0.0',
      )?.id;
    }
  }

  if (versionId) {
    const logs = await page.request.get(`/api/v1/models/monitoring/${versionId}`, { headers });
    if (logs.ok() && ((await logs.json()) as unknown[]).length === 0) {
      for (const [metricName, metricValue] of [
        ['accuracy', { value: 0.94 }],
        ['latency', { value: 120 }],
        ['throughput', { value: 540 }],
        ['error_rate', { value: 0.02 }],
      ] as const) {
        await page.request.post('/api/v1/models/monitoring', {
          headers,
          data: { version_id: versionId, metric_name: metricName, metric_value: metricValue },
        });
      }
    }
  }

  await page.request.post('/api/v1/compliance/checks/run', { headers });
}
