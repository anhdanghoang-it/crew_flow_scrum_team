// spec: docs/copilot/account_management_trading_simulation_detailed_test_plan.md
// seed: e2e/seed.spec.ts
import { test, expect } from '@playwright/test';

const baseUrl = 'http://127.0.0.1:7860/';

async function createAccount(page) {
  await page.goto(baseUrl);
  const username = `u_deposit_${Date.now()}`;
  await page.getByRole('textbox', { name: 'Username' }).fill(username);
  await page.getByRole('button', { name: 'Create Account' }).click();
  await expect(page.getByText('Account created successfully.')).toBeVisible();
  return username;
}

test.describe('US-002 Deposit Funds', () => {
  test('DP-002 Non-Positive Amount Validation (Zero)', async ({ page }) => {
    // Preconditions: Active account.
    await createAccount(page);
    await page.getByRole('tab', { name: 'Account Overview' }).click();
    // 1. Enter `0`.
    // 2. Click Deposit.
    await page.getByRole('spinbutton', { name: 'Deposit amount' }).fill('0');
    await page.getByRole('button', { name: 'Deposit' }).click();
    // Expected: Error message; balance unchanged.
    await expect(page.getByText('Deposit amount must be greater than 0.')).toBeVisible();
  });
});