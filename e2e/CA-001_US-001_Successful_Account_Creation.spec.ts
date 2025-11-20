// spec: docs/copilot/account_management_trading_simulation_detailed_test_plan.md
// seed: e2e/seed.spec.ts
import { test, expect } from '@playwright/test';

const baseUrl = 'http://127.0.0.1:7860/';

test.describe('US-001 Create Trading Account', () => {
  test('Successful Account Creation', async ({ page }) => {
    // 1. Generate unique username `u_{epoch_ms}` (performed inline)
    // 2. Enter username in Username textbox.
    // 3. Enter display name `Trader {epoch_ms}`.
    // 4. Click `Create Account` button.
    await page.goto(baseUrl);
    const username = `u_${Date.now()}`;
    await page.getByRole('textbox', { name: 'Username' }).fill(username);
    await page.getByRole('textbox', { name: 'Display name' }).fill(`Trader ${Date.now()}`);
    await page.getByRole('button', { name: 'Create Account' }).click();
    await expect(page.getByText('Account created successfully.')).toBeVisible();
    // Final Outcome: Account object created with expected initial state (validated by success message presence)
  });
});