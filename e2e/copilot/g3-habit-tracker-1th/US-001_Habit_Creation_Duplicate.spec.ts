import { test, expect } from '@playwright/test';

test.describe('Habit Creation and Management (US-001)', () => {
  test('Duplicate Habit Prevention', async ({ page }) => {
    // 1. Navigate to the "Manage Habits" tab.
    await page.goto('http://127.0.0.1:7860/');

    // Pre-condition: Create a habit
    const habitName = 'Duplicate Habit';
    await page.getByTestId('textbox').fill(habitName);
    await page.getByRole('spinbutton', { name: 'Daily Target' }).fill('2');
    await page.getByRole('button', { name: 'Create Habit 🚀' }).click();
    await expect(page.getByText(`Habit '${habitName}' created successfully! 🚀`)).toBeVisible();

    // 2. Enter a "Habit Name" that already exists.
    await page.getByTestId('textbox').fill(habitName);

    // 3. Enter a valid "Daily Target".
    await page.getByRole('spinbutton', { name: 'Daily Target' }).fill('2');

    // 4. Click the "Create Habit 🚀" button.
    await page.getByRole('button', { name: 'Create Habit 🚀' }).click();

    // Expected Results:
    // - An error message is displayed.
    await expect(page.getByText(`Habit '${habitName}' already exists. Please choose a different name.`)).toBeVisible();
  });
});
