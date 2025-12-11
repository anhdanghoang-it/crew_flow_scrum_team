import { test, expect } from '@playwright/test';

test.describe('Habit Creation and Management (US-001)', () => {
  test('Successful Habit Creation', async ({ page }) => {
    // 1. Navigate to the "Manage Habits" tab.
    await page.goto('http://127.0.0.1:7860/');

    const habitName = `Drink Water ${Date.now()}`;

    // 2. Enter a valid "Habit Name" (e.g., "Drink Water").
    await page.getByRole('textbox', { name: /Magic Name/ }).fill(habitName);

    // 3. Enter a valid "Daily Target" (e.g., "2").
    await page.getByRole('spinbutton', { name: /Daily Target/ }).fill('2');

    // 4. Click the "Create Habit 🚀" button.
    await page.getByRole('button', { name: /Create Magic/ }).click();

    // Expected Results:
    // - A success message "Habit 'Drink Water' created successfully! 🚀" is displayed.
    await expect(page.getByText(`Habit '${habitName}' created successfully! 🚀`)).toBeVisible();

    // - The new habit appears in the "Your Habits" table.
    await expect(page.getByRole('cell', { name: habitName })).toBeVisible();

    // - The input fields are cleared.
    await expect(page.getByRole('textbox', { name: /Magic Name/ })).toHaveValue('');
    await expect(page.getByRole('spinbutton', { name: /Daily Target/ })).toHaveValue('1');
  });
});
