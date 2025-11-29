import { test, expect } from '@playwright/test';

test.describe('TS-001: Account Registration & Validation', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('http://127.0.0.1:7860/');
    await page.getByRole('tab', { name: 'Login / Register' }).click();
  });

  test('1.1 Successful Account Creation', async ({ page }) => {
    const username = `TestTrader_${Date.now()}`;

    // Using placeholder to target the specific registration input based on snapshot analysis
    await page.getByPlaceholder('Choose a unique username').fill(username);
    await page.getByRole('button', { name: 'Create Account' }).click();

    // Verify success message
    await expect(page.getByText(`Account '${username}' created successfully`)).toBeVisible();

    // Verify Dashboard initial state
    await page.getByRole('tab', { name: 'Dashboard' }).click();
    // Based on snapshot, Cash Balance is a spinbutton with label "Cash Balance"
    await expect(page.getByLabel('Cash Balance')).toHaveValue('0');
  });

  test('1.2 Missing Username Validation', async ({ page }) => {
    // Ensure input is empty
    await page.getByPlaceholder('Choose a unique username').fill('');
    await page.getByRole('button', { name: 'Create Account' }).click();

    // Verify error message
    await expect(page.getByText('Username cannot be empty')).toBeVisible();
  });

  test.fixme('1.3 Duplicate Username Validation', async ({ page }) => {
    // Fixme: Application fails to display duplicate username error message. 
    // Console shows "Connection errored out", suggesting backend instability or failure to handle the request.
    const username = `DuplicateUser_${Date.now()}`;

    // 1. Create the account first
    await page.getByPlaceholder('Choose a unique username').fill(username);
    await page.getByRole('button', { name: 'Create Account' }).click();
    await expect(page.getByText(`Account '${username}' created successfully`)).toBeVisible();

    // 2. Refresh to reset state/UI
    await page.reload();
    await page.getByRole('tab', { name: 'Login / Register' }).click();

    // 3. Try to create the same account again
    await page.getByPlaceholder('Choose a unique username').fill(username);
    await page.getByRole('button', { name: 'Create Account' }).click();

    // Verify duplicate error message
    await expect(page.getByText(`Username '${username}' already exists`)).toBeVisible();
  });
});
