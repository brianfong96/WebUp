import { test, expect } from '@playwright/test';

const outDir = 'tests/e2e/screenshots';

test('command center renders and validates', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('WebUp Pipeline')).toBeVisible();
  await expect(page.getByText('JSON Job Config')).toBeVisible();
  await page.screenshot({ path: `${outDir}/command-center.png`, fullPage: true });
});

test('viewer renders log explorer', async ({ page }) => {
  await page.goto('/viewer');
  await expect(page.getByText('Log Explorer')).toBeVisible();
  await expect(page.getByText('Data Inspector')).toBeVisible();
  await page.screenshot({ path: `${outDir}/viewer.png`, fullPage: true });
});
