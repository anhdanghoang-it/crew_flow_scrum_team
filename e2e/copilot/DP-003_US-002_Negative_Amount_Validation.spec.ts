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
  test('DP-003 Negative Amount Validation', async ({ page }) => {
    // 1. Create account then open Account Overview.
    await createAccount(page, 'u_deposit_neg');
    await page.getByRole('tab', { name: 'Account Overview' }).click();
    // 2. Enter `-5` and click Deposit.
    await page.getByRole('spinbutton', { name: 'Deposit amount' }).fill('-5');
    await page.getByRole('button', { name: 'Deposit' }).click();
    // Expected: Validation error for negative amount.
    await expect(page.getByText('Value -5 is less than minimum value 0.')).toBeVisible();
  });
});