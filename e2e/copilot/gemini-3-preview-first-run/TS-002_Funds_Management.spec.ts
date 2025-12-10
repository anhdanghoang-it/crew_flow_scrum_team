import { test, expect } from '@playwright/test';

test.describe('Funds Management (US-002, US-003)', () => {
  test('Execute Funds Management Flow', async ({ page }) => {
    await page.goto('http://127.0.0.1:7860/');

    // 1. Setup: Create Account
    await test.step('Setup: Create Account', async () => {
      // Using a specific username as per interactive session
      await page.getByTestId('textbox').fill('funds_user_new');
      await page.getByRole('button', { name: 'Create Account' }).click();
    });

    // 2. Successful Deposit
    await test.step('Successful Deposit', async () => {
      await page.getByRole('tab', { name: 'Funds' }).click();
      await page.getByRole('spinbutton', { name: 'Amount ($)' }).fill('1000');
      await page.getByRole('button', { name: 'Deposit' }).click();
      
      await expect(page.getByText('Deposited $1000.00')).toBeVisible();
    });

    // 3. Successful Withdrawal
    await test.step('Successful Withdrawal', async () => {
      await page.getByRole('spinbutton', { name: 'Amount ($)' }).fill('200');
      await page.getByRole('button', { name: 'Withdraw' }).click();
      
      await expect(page.getByText('Withdrew $200.00')).toBeVisible();
      
      // Verify Balance
      await page.getByRole('tab', { name: 'Dashboard' }).click();
      await expect(page.getByRole('spinbutton', { name: 'Cash Balance ($)' })).toHaveValue('800');
    });

    // 4. Negative Tests
    await test.step('Negative Tests: Invalid Amounts', async () => {
      await page.getByRole('tab', { name: 'Funds' }).click();
      
      // Negative Deposit
      await page.getByRole('spinbutton', { name: 'Amount ($)' }).fill('-100');
      await page.getByRole('button', { name: 'Deposit' }).click();
      await expect(page.getByText('Value -100 is less than minimum value 0.01.')).toBeVisible();
      
      // Negative Withdrawal
      await page.getByRole('spinbutton', { name: 'Amount ($)' }).fill('-50');
      await page.getByRole('button', { name: 'Withdraw' }).click();
      await expect(page.getByText('Value -50 is less than minimum value 0.01.')).toBeVisible();
    });

    // 5. Insufficient Funds
    await test.step('Negative Test: Insufficient Funds', async () => {
      // Try to withdraw 1000 (Balance 800)
      await page.getByRole('spinbutton', { name: 'Amount ($)' }).fill('1000');
      await page.getByRole('button', { name: 'Withdraw' }).click();
      
      await expect(page.getByText('Insufficient funds. Available: $800.00')).toBeVisible();
    });
  });
});
