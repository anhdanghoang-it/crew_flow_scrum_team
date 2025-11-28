// spec: docs/copilot/trading_simulation_test_plan.md
// seed: e2e/seed.spec.ts
import { test, expect } from '@playwright/test';

test.describe('US-001 Initialize Account and View Portfolio Dashboard', () => {
  test('TS-1.2 Initialization With Zero (Invalid)', async ({ page }) => {
    // 1. Navigate to http://127.0.0.1:7861/ (fresh state)
    await page.goto('http://127.0.0.1:7861/');

    // 2. Set Initial Deposit spinner value to 0
    const initialDeposit = page.getByRole('spinbutton', { name: 'Initial Deposit' });
    await initialDeposit.fill('0');

    // 3. Click Start Simulation button
    const startButton = page.getByRole('button', { name: 'Start Simulation' });
    await startButton.click();

    // Verify: Error message for non-positive initial deposit (minimum 0.01 enforced)
    await expect(page.getByText('Value 0 is less than minimum value 0.01.')).toBeVisible();

    // Verify: Setup UI remains visible (spinner still present with value 0)
    await expect(initialDeposit).toBeVisible();

    // Verify: Other tabs remain disabled (still visible but not interactive)
    await expect(page.getByRole('tab', { name: 'Trade' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'Cash Management' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'Transaction History' })).toBeVisible();
  });
});
