// spec: docs/copilot/trading_simulation_test_plan.md
// seed: e2e/seed.spec.ts
import { test, expect } from '@playwright/test';

test.describe('US-001 Initialize Account and View Portfolio Dashboard', () => {
  test('TS-1.5 Holdings Table Empty State', async ({ page }) => {
    // 1. Navigate to http://127.0.0.1:7861/
    await page.goto('http://127.0.0.1:7861/');
    await page.getByRole('button', { name: 'Start Simulation' }).waitFor({ state: 'visible' });

    // 2. Click Start Simulation to initialize with default deposit
    await page.getByRole('button', { name: 'Start Simulation' }).click();

    // Verify: Success info message appears (US-001 AC #1)
    await expect(page.getByText('Account initialized with a balance of $100,000.00.')).toBeVisible();

    // Verify: Holdings section heading present
    await expect(page.getByText('Current Holdings')).toBeVisible();

    // Scope to first holdings table to avoid duplicate headers from editable layer
    const holdingsTable = page.locator('table').first();
    const headerCells = holdingsTable.locator('tr').first().locator('th, td');
    await expect(headerCells).toHaveCount(4);
    await expect(headerCells.nth(0)).toContainText('Symbol');
    await expect(headerCells.nth(1)).toContainText('Quantity');
    await expect(headerCells.nth(2)).toContainText('Current Price');
    await expect(headerCells.nth(3)).toContainText('Market Value');

    // Empty state: ensure no known symbols appear in any table
    await expect(page.getByText('AAPL')).toHaveCount(0);
    await expect(page.getByText('TSLA')).toHaveCount(0);
    await expect(page.getByText('GOOGL')).toHaveCount(0);
  });
});
