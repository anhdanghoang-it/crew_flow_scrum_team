import { test, expect } from '@playwright/test';

test.describe('Habit Creation and Management (US-001)', () => {
  test('Invalid Input Validation', async ({ page }) => {
    // 1. Navigate to the "Manage Habits" tab.
    await page.goto('http://127.0.0.1:7860/');

    // Case 1: Empty Habit Name
    // 2. Leave "Habit Name" empty.
    await page.getByTestId('textbox').fill('');
    
    // Enter a valid "Daily Target" to isolate the empty name error.
    await page.getByRole('spinbutton', { name: 'Daily Target' }).fill('5');

    // 3. Click the "Create Habit 🚀" button.
    await page.getByRole('button', { name: 'Create Habit 🚀' }).click();

    // Expected Results:
    // - A warning message is displayed.
    await expect(page.getByText('Please enter a valid name.')).toBeVisible();

    // Case 2: Invalid Daily Target (Empty/Non-numeric)
    // Note: The input type="number" prevents typing non-numeric characters like "abc".
    // We test with empty input which is invalid.
    
    // Enter a valid "Habit Name".
    await page.getByTestId('textbox').fill('Valid Name');

    // Clear "Daily Target".
    await page.getByRole('spinbutton', { name: 'Daily Target' }).fill('');

    // Click the "Create Habit 🚀" button.
    await page.getByRole('button', { name: 'Create Habit 🚀' }).click();

    // Expected Results:
    // - A warning message is displayed.
    await expect(page.getByText('Please enter a numeric daily target.')).toBeVisible();
  });
});
