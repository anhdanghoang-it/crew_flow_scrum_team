import { test, expect } from '@playwright/test';

test.describe('TS-1.1_US-001_SuccessfulAccountInitializationandDashboardDisplay', () => {
  test('Successful Account Initialization and Dashboard Display (Happy Path)', async ({ page }) => {
    // Step 1: Navigate to the application URL and verify initial state.
    // Expected: 'Initial Setup' group is visible and 'Portfolio Overview' is hidden.
    await page.goto('http://127.0.0.1:7860/');
    await expect(page.getByRole('heading', { name: '1. Start Your Simulation' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Key Metrics' })).toBeHidden();

    // Step 2: Enter '100000.00' into the 'Initial Deposit' input field.
    await page.getByRole('spinbutton', { name: 'Initial Deposit' }).fill('100000.00');

    // Step 3: Click the 'Start Simulation' button.
    await page.getByRole('button', { name: 'Start Simulation' }).click();

    // Step 4: Verify the 'Initial Setup' group is now hidden and the 'Portfolio Overview' group is visible.
    await expect(page.getByRole('heading', { name: '1. Start Your Simulation' })).toBeHidden();
    await expect(page.getByRole('heading', { name: 'Key Metrics' })).toBeVisible();

    // Step 5: Verify a success information message is displayed: 'Account initialized with a balance of $100,000.00.'.
    await expect(page.getByText('Account initialized with a balance of $100,000.00.')).toBeVisible();

    // Step 6: Verify the 'Cash Balance' metric displays '$100,000.00'.
    await expect(page.getByRole('textbox', { name: 'Cash Balance' })).toHaveValue('$100,000.00');

    // Step 7: Verify all main tabs ('Trade', 'Cash Management', 'Transaction History') are enabled.
    await expect(page.getByRole('tab', { name: 'Trade' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'Cash Management' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'Transaction History' })).toBeVisible();
  });
});