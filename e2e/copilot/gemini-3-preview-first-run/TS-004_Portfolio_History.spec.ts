import { test, expect } from '@playwright/test';

test.describe('Portfolio & History (US-006, US-007)', () => {
  test('Verify Portfolio Metrics and Transaction History', async ({ page }) => {
    await page.goto('http://127.0.0.1:7860/');

    // 1. Setup: Create Account and Generate History
    await test.step('Setup: Create Account and Generate History', async () => {
      // Create Account
      await page.getByTestId('textbox').fill('audit_user');
      await page.getByRole('button', { name: 'Create Account' }).click();
      
      // Deposit 2000
      await page.getByRole('tab', { name: 'Funds' }).click();
      await page.getByRole('spinbutton', { name: 'Amount ($)' }).fill('2000');
      await page.getByRole('button', { name: 'Deposit' }).click();
      
      // Buy 2 AAPL
      await page.getByRole('tab', { name: 'Trade' }).click();
      // AAPL is default selected
      await page.getByRole('spinbutton', { name: 'Quantity' }).fill('2');
      await page.getByRole('button', { name: 'Buy Shares' }).click();
      
      // Sell 1 AAPL
      await page.getByRole('spinbutton', { name: 'Quantity' }).fill('1');
      await page.getByRole('button', { name: 'Sell Shares' }).click();
    });

    // 2. Verify Portfolio Metrics
    await test.step('Verify Portfolio Metrics', async () => {
      await page.getByRole('tab', { name: 'Dashboard' }).click();
      
      // Cash Balance = 2000 - 300 (Buy) + 150 (Sell) = 1850
      await expect(page.getByRole('spinbutton', { name: 'Cash Balance ($)' })).toHaveValue('1850');
      
      // Portfolio Value = 1850 (Cash) + 150 (1 AAPL * 150) = 2000
      await expect(page.getByRole('spinbutton', { name: 'Total Portfolio Value ($)' })).toHaveValue('2000');
      
      // Profit/Loss = 2000 (Value) - 2000 (Invested) = 0
      await expect(page.getByRole('spinbutton', { name: 'Total Profit/Loss ($)' })).toHaveValue('0');
    });

    // 3. Verify Transaction History
    await test.step('Verify Transaction History', async () => {
      await page.getByRole('tab', { name: 'History' }).click();
      
      // Verify all transaction types are present
      await expect(page.getByText('DEPOSIT')).toBeVisible();
      await expect(page.getByText('BUY')).toBeVisible();
      await expect(page.getByText('SELL')).toBeVisible();
      
      // Verify specific details (optional but good for robustness)
      // We can check if the amounts are visible in the table
      await expect(page.getByText('$2000.00')).toBeVisible(); // Deposit
      await expect(page.getByText('$-300.00')).toBeVisible(); // Buy Cost
      await expect(page.getByText('$150.00')).toBeVisible();  // Sell Proceeds
    });
  });
});
