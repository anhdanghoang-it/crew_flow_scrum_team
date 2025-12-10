import { test, expect } from '@playwright/test';

test.describe('TS-003: Trading Operations', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://127.0.0.1:7860/');
    // Setup: Create account
    await page.getByLabel('Username').fill('trader_ops');
    await page.getByLabel('Initial Deposit ($)').fill('10000');
    await page.getByRole('button', { name: 'Create Account' }).click();
    await expect(page.getByRole('tab', { name: 'Trade' })).toBeVisible();
  });

  test('3.1 Successful Buy Order', async ({ page }) => {
    await page.getByRole('tab', { name: 'Trade' }).click();
    
    // Select AAPL (assuming it's default or we can select it)
    // Using first quantity input for Buy
    await page.getByLabel('Quantity').first().fill('10');
    await page.getByRole('button', { name: 'Buy Shares' }).click();

    await expect(page.getByText('Successfully purchased 10 shares of AAPL')).toBeVisible();
  });

  test('3.2 Insufficient Funds for Buy', async ({ page }) => {
    await page.getByRole('tab', { name: 'Trade' }).click();
    
    // Try to buy a lot
    await page.getByLabel('Quantity').first().fill('100000');
    await page.getByRole('button', { name: 'Buy Shares' }).click();

    await expect(page.getByText('Insufficient funds')).toBeVisible();
  });

  test('3.3 Successful Sell Order', async ({ page }) => {
    // First buy some shares
    await page.getByRole('tab', { name: 'Trade' }).click();
    await page.getByLabel('Quantity').first().fill('10');
    await page.getByRole('button', { name: 'Buy Shares' }).click();
    await expect(page.getByText('Successfully purchased')).toBeVisible();

    // Now Sell
    // Sell section is below Buy section.
    // Second Quantity input.
    await page.getByLabel('Quantity').nth(1).fill('5');
    await page.getByRole('button', { name: 'Sell Shares' }).click();

    await expect(page.getByText('Successfully sold 5 shares')).toBeVisible();
  });

  test('3.4 Sell More Than Owned', async ({ page }) => {
    await page.getByRole('tab', { name: 'Trade' }).click();
    
    // Try to sell without owning
    await page.getByLabel('Quantity').nth(1).fill('1');
    await page.getByRole('button', { name: 'Sell Shares' }).click();

    await expect(page.getByText('Insufficient shares')).toBeVisible();
  });
});
