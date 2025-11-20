// spec: docs/copilot/account_management_trading_simulation_detailed_test_plan.md
// seed: e2e/seed.spec.ts
import { test, expect } from '@playwright/test';

const baseUrl = 'http://127.0.0.1:7860/';

test.describe('US-001 Create Trading Account', () => {
  test('Missing Username Validation', async ({ page }) => {
    // 1. Leave Username empty.
    // 2. (Optional) Provide display name.
    // 3. Click Create Account.
    await page.goto(baseUrl);
    await page.getByRole('button', { name: 'Create Account' }).click();
    await expect(page.getByText('Username is required.')).toBeVisible();
    // Final Outcome: No account created (active account remains none selected)
  });
});