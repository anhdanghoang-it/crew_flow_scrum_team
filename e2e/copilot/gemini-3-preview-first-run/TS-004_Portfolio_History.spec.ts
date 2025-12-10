import { test, expect } from '@playwright/test';

test.describe('TS-004: Portfolio & Reporting', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://127.0.0.1:7860/');
    // Setup: Create account
    await page.getByLabel('Username').fill('trader_portfolio');
    await page.getByLabel('Initial Deposit ($)').fill('10000');
    await page.getByRole('button', { name: 'Create Account' }).click();
    await expect(page.getByRole('tab', { name: 'Portfolio' })).toBeVisible();
  });

  test('4.1 View Holdings', async ({ page }) => {
    // Buy some shares first
    await page.getByRole('tab', { name: 'Trade' }).click();
    await page.getByLabel('Quantity').first().fill('10');
    await page.getByRole('button', { name: 'Buy Shares' }).click();
    await expect(page.getByText('Successfully purchased')).toBeVisible();

    // Go to Portfolio
    await page.getByRole('tab', { name: 'Portfolio' }).click();
    
    // Check table
    await expect(page.getByRole('table')).toBeVisible();
    await expect(page.getByRole('cell', { name: 'AAPL' })).toBeVisible();
    await expect(page.getByRole('cell', { name: '10' })).toBeVisible(); // Quantity
  });

  test('4.2 Empty Portfolio', async ({ page }) => {
    await page.getByRole('tab', { name: 'Portfolio' }).click();
    
    // Should show empty state or empty table
    await expect(page.getByText('Total Capital Invested:')).toBeVisible();
  });

  test('4.3 Refresh Prices', async ({ page }) => {
    await page.getByRole('tab', { name: 'Portfolio' }).click();
    await page.getByRole('button', { name: 'Refresh Prices' }).click();
    
    // Verify button is still visible and clickable
    await expect(page.getByRole('button', { name: 'Refresh Prices' })).toBeVisible();
  });
});
