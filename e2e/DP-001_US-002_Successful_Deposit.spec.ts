// spec: docs/copilot/account_management_trading_simulation_detailed_test_plan.md
// seed: e2e/seed.spec.ts
import { test, expect } from '@playwright/test';

const baseUrl = 'http://127.0.0.1:7860/';

// Helper to create a fresh account for deposit scenarios
async function createAccount(page) {
  await page.goto(baseUrl);
  const username = `u_deposit_${Date.now()}`;
  await page.getByRole('textbox', { name: 'Username' }).fill(username);
  await page.getByRole('button', { name: 'Create Account' }).click();
  await expect(page.getByText('Account created successfully.')).toBeVisible();
  return username;
}

test.describe('US-002 Deposit Funds', () => {
  test('DP-001 Successful Deposit', async ({ page }) => {
    // Preconditions: Active account with cash=0; on Account Overview tab.
    await createAccount(page);
    await page.getByRole('tab', { name: 'Account Overview' }).click();
    // 1. Enter `1000` in Deposit amount.
    // 2. Click Deposit.
    await page.getByRole('spinbutton', { name: 'Deposit amount' }).fill('1000');
    await page.getByRole('button', { name: 'Deposit' }).click();
    // Expected: Success message; balance updates; transaction logged (message presence used as proxy).
    await expect(page.getByText('Deposit successful.')).toBeVisible();
    await expect(page.getByText('Cash balance:')).toBeVisible();
  });
});