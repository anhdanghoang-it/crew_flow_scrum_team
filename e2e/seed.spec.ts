import { test, expect } from '@playwright/test';

test.describe('Login script', () => {
  test('seed', async ({ page }) => {
    // generate code here.
    await page.goto('http://127.0.0.1:7860/');
  });
});
