// spec: docs/copilot/account_management_trading_simulation_detailed_test_plan.md
// seed: e2e/seed.spec.ts
import { test, expect } from '@playwright/test';

const baseUrl = 'http://127.0.0.1:7860/';

async function createAccount(page, label: string) {
  await page.goto(baseUrl);
  const username = `${label}_${Date.now()}`;
  await page.getByRole('textbox', { name: 'Username' }).fill(username);
  await page.getByRole('button', { name: 'Create Account' }).click();
  await expect(page.getByText('Account created successfully.')).toBeVisible();
  return username;
}

test.describe('US-002 Deposit Funds', () => {
  test('DP-005 Large Deposit Boundary', async ({ page }) => {
    // Preconditions: Active account.
    await createAccount(page, 'u_deposit_large');
    await page.getByRole('tab', { name: 'Account Overview' }).click();
    // 1. Enter `100000`.
    // 2. Click Deposit.
    await page.getByRole('spinbutton', { name: 'Deposit amount' }).fill('100000');
    await page.getByRole('button', { name: 'Deposit' }).click();
    // Expected: Success message and updated cash balance formatting.
    await expect(page.getByText('Deposit successful.')).toBeVisible();
    await expect(page.getByText('Cash balance:')).toBeVisible();
  });
});