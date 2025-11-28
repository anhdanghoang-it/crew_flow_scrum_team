// spec: docs/copilot/trading_simulation_test_plan.md
// seed: e2e/seed.spec.ts
import { test, expect } from '@playwright/test';

test.describe('US-001 Initialize Account and View Portfolio Dashboard', () => {
  test('TS-1.1 Successful Account Initialization', async ({ page }) => {
    // 1. Navigate to http://127.0.0.1:7861/
    await page.goto('http://127.0.0.1:7861/');

    // Wait for initial UI to render
    await page.getByText('Trading Simulation Platform').first().waitFor({ state: 'visible' });

    // 2-3. Default Initial Deposit assumed 100000.00
    const startButton = page.getByRole('button', { name: 'Start Simulation' });

    // 4. Click Start Simulation
    await startButton.click();

    // Verify: Info message appears
    await expect(page.getByText('Account initialized with a balance of $100,000.00.')).toBeVisible();

    // Verify: Tabs enabled
    await expect(page.getByRole('tab', { name: 'Trade' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'Cash Management' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'Transaction History' })).toBeVisible();

    // Verify: Cash Balance metric visible (formatted value rendered inside disabled textbox)
    await expect(page.getByRole('textbox', { name: 'Cash Balance' })).toBeVisible();
  });
});
