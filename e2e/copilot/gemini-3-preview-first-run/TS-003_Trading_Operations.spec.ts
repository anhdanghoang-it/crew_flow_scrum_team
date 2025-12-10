import { test, expect } from '@playwright/test';

test.describe('Trading Operations (US-004, US-005)', () => {
  test('Execute Trading Operations Flow', async ({ page }) => {
    await page.goto('http://127.0.0.1:7860/');

    // 1. Setup: Create Account and Deposit Funds
    await test.step('Setup: Create Account and Deposit Funds', async () => {
      await page.getByTestId('textbox').fill('trader_user');
      await page.getByRole('button', { name: 'Create Account' }).click();
      
      await page.getByRole('tab', { name: 'Funds' }).click();
      await page.getByRole('spinbutton', { name: 'Amount ($)' }).fill('2000');
      await page.getByRole('button', { name: 'Deposit' }).click();
    });

    // 2. Successful Buy
    await test.step('Successful Buy: Buy 2 AAPL shares', async () => {
      await page.getByRole('tab', { name: 'Trade' }).click();
      
      // Select AAPL
      await page.getByRole('listbox', { name: 'Symbol' }).fill('AAPL');
      await page.getByRole('listbox', { name: 'Symbol' }).press('Enter');
      
      // Enter Quantity 2
      await page.getByRole('spinbutton', { name: 'Quantity' }).fill('2');
      
      // Buy
      await page.getByRole('button', { name: 'Buy Shares' }).click();
      
      // Verify Success Message
      await expect(page.getByText('Bought 2 AAPL @ $150.00')).toBeVisible();
      
      // Verify Dashboard Updates
      await page.getByRole('tab', { name: 'Dashboard' }).click();
      await expect(page.getByRole('spinbutton', { name: 'Cash Balance ($)' })).toHaveValue('1700');
      await expect(page.getByRole('button', { name: 'AAPL' })).toBeVisible();
    });

    // 3. Successful Sell
    await test.step('Successful Sell: Sell 1 AAPL share', async () => {
      await page.getByRole('tab', { name: 'Trade' }).click();
      
      // Enter Quantity 1 (Symbol AAPL is already selected)
      await page.getByRole('spinbutton', { name: 'Quantity' }).fill('1');
      
      // Sell
      await page.getByRole('button', { name: 'Sell Shares' }).click();
      
      // Verify Success Message
      await expect(page.getByText('Sold 1 AAPL @ $150.00')).toBeVisible();
      
      // Verify Dashboard Updates
      await page.getByRole('tab', { name: 'Dashboard' }).click();
      // Refresh to ensure data is up to date
      await page.getByRole('button', { name: 'Login / Refresh' }).click();
      
      await expect(page.getByRole('spinbutton', { name: 'Cash Balance ($)' })).toHaveValue('1850');
      await expect(page.getByText('AAPL')).toBeVisible();
    });

    // 4. Negative Test: Insufficient Funds
    await test.step('Negative Test: Insufficient Funds for Purchase', async () => {
      await page.getByRole('tab', { name: 'Trade' }).click();
      
      // Try to buy 100 AAPL (Cost 15000 > Balance 1850)
      await page.getByRole('spinbutton', { name: 'Quantity' }).fill('100');
      await page.getByRole('button', { name: 'Buy Shares' }).click();
      
      await expect(page.getByText('Insufficient funds for purchase')).toBeVisible();
    });

    // 5. Negative Test: Insufficient Shares
    await test.step('Negative Test: Insufficient Shares to Sell', async () => {
      // Try to sell 100 AAPL (Owned 1)
      // Quantity is already 100 from previous step
      await page.getByRole('button', { name: 'Sell Shares' }).click();
      
      await expect(page.getByText('Insufficient shares to sell')).toBeVisible();
    });
  });
});
