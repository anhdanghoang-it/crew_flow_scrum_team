import { test, expect } from '@playwright/test';

test.describe('TS-002: Funds Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://127.0.0.1:7860/');
    // Setup: Create account
    await page.getByLabel('Username').fill('trader_funds');
    await page.getByLabel('Initial Deposit ($)').fill('10000');
    await page.getByRole('button', { name: 'Create Account' }).click();
    await expect(page.getByRole('tab', { name: 'Funds' })).toBeVisible();
  });

  test('2.1 Successful Deposit', async ({ page }) => {
    await page.getByRole('tab', { name: 'Funds' }).click();
    await page.getByLabel('Deposit Amount ($)').fill('5000');
    await page.getByRole('button', { name: 'Deposit Funds' }).click();

    await expect(page.getByText('Successfully deposited $5,000.00')).toBeVisible();
    // Use specific locator for balance to avoid ambiguity with toast message
    await expect(page.locator('p').filter({ hasText: 'Current Balance:' })).toContainText('$15,000.00');
  });

  test.fixme('2.2 Invalid Deposit (Negative/Zero)', async ({ page }) => {
    // FIXME: Application displays "Value 0 is less than minimum value 0.01." instead of "Deposit amount must be greater than $0.00"
    await page.getByRole('tab', { name: 'Funds' }).click();
    
    // Zero
    await page.getByLabel('Deposit Amount ($)').fill('0');
    await page.getByRole('button', { name: 'Deposit Funds' }).click();
    await expect(page.getByText('Deposit amount must be greater than $0.00')).toBeVisible();

    // Negative
    await page.getByLabel('Deposit Amount ($)').fill('-500');
    await page.getByRole('button', { name: 'Deposit Funds' }).click();
    await expect(page.getByText('Deposit amount must be greater than $0.00')).toBeVisible();
  });

  test('2.3 Successful Withdrawal', async ({ page }) => {
    await page.getByRole('tab', { name: 'Funds' }).click();
    await page.getByLabel('Withdrawal Amount ($)').fill('2000');
    await page.getByRole('button', { name: 'Withdraw Funds' }).click();

    await expect(page.getByText('Successfully withdrew $2,000.00')).toBeVisible();
    // Use specific locator for balance to avoid ambiguity with toast message
    await expect(page.locator('p').filter({ hasText: 'Current Balance:' })).toContainText('$8,000.00');
  });

  test('2.4 Insufficient Funds Withdrawal', async ({ page }) => {
    await page.getByRole('tab', { name: 'Funds' }).click();
    await page.getByLabel('Withdrawal Amount ($)').fill('100000');
    await page.getByRole('button', { name: 'Withdraw Funds' }).click();

    await expect(page.getByText('Insufficient funds')).toBeVisible();
  });
});
