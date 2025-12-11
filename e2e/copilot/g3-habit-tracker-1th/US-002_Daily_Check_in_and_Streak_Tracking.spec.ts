import { test, expect } from '@playwright/test';

test.describe('Daily Check-in and Streak Tracking', () => {
  test('Successful Daily Check-in and Prevent Duplicate', async ({ page }) => {
    await page.goto('http://0.0.0.0:7860/');

    const habitName = `Meditation Test ${Date.now()}`;

    // 1. Setup: Create a new habit
    await page.getByTestId('textbox').fill(habitName);
    await page.getByRole('spinbutton', { name: 'Daily Target' }).fill('1');
    await page.getByRole('button', { name: 'Create Habit 🚀' }).click();
    await expect(page.getByText(`Habit '${habitName}' created successfully! 🚀`)).toBeVisible();

    // 2. Navigate to the "Daily Tracker" tab.
    await page.getByRole('tab', { name: 'Daily Tracker' }).click();

    // 3. Select a habit from the "Select Habit to Track" dropdown.
    await page.getByRole('listbox', { name: 'Select Habit to Track' }).click();
    await page.getByRole('option', { name: habitName }).click();

    // 4. Verify the "Check In Today" button is enabled.
    const checkInButton = page.getByRole('button', { name: '✅ Check In Today' });
    await expect(checkInButton).toBeEnabled();

    // 5. Click the "✅ Check In Today" button.
    await checkInButton.click();

    // 6. Verify success message.
    await expect(page.getByText(`Great job! Check-in recorded for ${habitName}. 🔥`)).toBeVisible();

    // 7. Verify the "Current Streak" counter increments by 1.
    await expect(page.getByRole('spinbutton', { name: 'Current Streak' })).toHaveValue('1');

    // 8. Verify the "Total Check-ins" counter increments by 1.
    await expect(page.getByRole('spinbutton', { name: 'Total Check-ins' })).toHaveValue('1');

    // 9. Verify the "Check In Today" button becomes disabled or indicates completion.
    const completedButton = page.getByRole('button', { name: '✅ Completed' });
    await expect(completedButton).toBeVisible();
    await expect(completedButton).toBeDisabled();
  });
});
