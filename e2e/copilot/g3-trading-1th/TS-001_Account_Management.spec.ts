import { test, expect } from '@playwright/test';

test.describe('TS-001: Account Creation & Validation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://127.0.0.1:7860/');
  });

  test('1.1 Successful Account Creation', async ({ page }) => {
    const username = 'trader_01';
    const initialDeposit = '10000';

    await page.getByLabel('Username').fill(username);
    await page.getByLabel('Initial Deposit ($)').fill(initialDeposit);
    await page.getByRole('button', { name: 'Create Account' }).click();

    // Verify success message
    await expect(page.getByText(`Account '${username}' created successfully`)).toBeVisible();

    // Verify dashboard tabs are visible
    await expect(page.getByRole('tab', { name: 'Funds' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'Trade' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'Portfolio' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'History' })).toBeVisible();

    // Verify Funds tab is selected by default and balance is correct
    await expect(page.getByRole('tab', { name: 'Funds' })).toHaveAttribute('aria-selected', 'true');
    await expect(page.getByText('$10,000.00')).toBeVisible();
  });

  test('1.2 Missing Username Validation', async ({ page }) => {
    await page.getByLabel('Initial Deposit ($)').fill('10000');
    await page.getByRole('button', { name: 'Create Account' }).click();

    // Verify error message
    await expect(page.getByText('Username is required')).toBeVisible();
  });

  test('1.3 Invalid Username Format', async ({ page }) => {
    await page.getByLabel('Username').fill('user@123');
    await page.getByLabel('Initial Deposit ($)').fill('10000');
    await page.getByRole('button', { name: 'Create Account' }).click();

    // Verify error message
    await expect(page.getByText('Username must contain only letters, numbers, and underscores')).toBeVisible();
  });

  test('1.4 Invalid Deposit Amount (Zero/Negative)', async ({ page }) => {
    const username = 'trader_invalid_deposit';
    
    // Test Zero
    await page.getByLabel('Username').fill(username);
    await page.getByLabel('Initial Deposit ($)').fill('0');
    await page.getByRole('button', { name: 'Create Account' }).click();
    await expect(page.getByText('Initial deposit must be greater than $0.00')).toBeVisible();

    // Test Negative
    await page.getByLabel('Initial Deposit ($)').fill('-100');
    await page.getByRole('button', { name: 'Create Account' }).click();
    await expect(page.getByText('Initial deposit must be greater than $0.00')).toBeVisible();
  });
});
