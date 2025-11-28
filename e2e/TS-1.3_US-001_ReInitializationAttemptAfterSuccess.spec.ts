// spec: docs/copilot/trading_simulation_test_plan.md
// seed: e2e/seed.spec.ts
import { test, expect } from '@playwright/test';

test.describe('US-001 Initialize Account and View Portfolio Dashboard', () => {
  test('TS-1.3 Re-Initialization Attempt After Success', async ({ page }) => {
    // 1. Navigate to http://127.0.0.1:7861/
    await page.goto('http://127.0.0.1:7861/');

    // Wait for Start Simulation button to appear
    await page.getByRole('button', { name: 'Start Simulation' }).waitFor({ state: 'visible' });

    // 2. Click Start Simulation to initialize
    const startButton = page.getByRole('button', { name: 'Start Simulation' });
    await startButton.click();

    // Verify: Initialization info message visible
    await expect(page.getByText('Account initialized with a balance of $100,000.00.')).toBeVisible();

    // Verify: Start Simulation button no longer present (hidden after init)
    await expect(page.getByRole('button', { name: 'Start Simulation' })).toHaveCount(0);
  });
});
