import { test, expect } from '@playwright/test';

test.describe('Account Management (US-001)', () => {
  test('Execute Account Management Flow', async ({ page }) => {
    const username = `test_user_${Date.now()}`;
    await page.goto('http://127.0.0.1:7860/');

    // 1. Successful Account Creation
    await test.step('Successful Account Creation', async () => {
      await page.getByTestId('textbox').fill(username);
      await page.getByRole('button', { name: 'Create Account' }).click();
      
      await expect(page.getByText(`Account created successfully for ${username}`)).toBeVisible();
      
      // Verify Initial State
      await expect(page.getByRole('spinbutton', { name: 'Cash Balance ($)' })).toHaveValue('0');
      await expect(page.getByRole('spinbutton', { name: 'Total Portfolio Value ($)' })).toHaveValue('0');
      await expect(page.getByRole('spinbutton', { name: 'Total Profit/Loss ($)' })).toHaveValue('0');
    });

    // 2. Missing Username Validation
    await test.step('Missing Username Validation', async () => {
      await page.getByTestId('textbox').fill('');
      await page.getByRole('button', { name: 'Create Account' }).click();
      
      await expect(page.getByText('Username cannot be empty')).toBeVisible();
    });

    // 3. Duplicate Username Handling
    await test.step('Duplicate Username Handling', async () => {
      await page.getByTestId('textbox').fill(username);
      await page.getByRole('button', { name: 'Create Account' }).click();
      
      await expect(page.getByText(`Account for '${username}' already exists.`)).toBeVisible();
    });
  });
});
