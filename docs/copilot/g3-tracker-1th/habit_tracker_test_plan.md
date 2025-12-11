# Habit Tracker Application - Comprehensive Test Plan

## Application Overview

The Habit Tracker is a gamified application designed to help users build and track positive habits. It features:
- **Habit Management**: Create and view custom habits with daily targets.
- **Daily Tracking**: Check in daily to maintain streaks.
- **Visual Analytics**: View progress through heatmaps and charts.
- **Gamification**: Earn badges for consistent streaks.

## Test Scenarios

### 1. Habit Creation and Management (US-001)

**Source**: `docs/copilot/habit_tracker_user_stories.md` - US-001

#### 1.1 Successful Habit Creation
**Steps:**
1. Navigate to the "Manage Habits" tab.
2. Enter a valid "Habit Name" (e.g., "Drink Water").
3. Enter a valid "Daily Target" (e.g., "2").
4. Click the "Create Habit 🚀" button.

**Expected Results:**
- A success message "Habit 'Drink Water' created successfully! 🚀" is displayed.
- The new habit appears in the "Your Habits" table.
- The input fields are cleared.

#### 1.2 Duplicate Habit Prevention
**Steps:**
1. Navigate to the "Manage Habits" tab.
2. Enter a "Habit Name" that already exists (e.g., "Drink Water").
3. Enter a valid "Daily Target".
4. Click the "Create Habit 🚀" button.

**Expected Results:**
- The habit is **not** added to the table.
- An error message "Habit 'Drink Water' already exists. Please choose a different name." is displayed.

#### 1.3 Invalid Input Validation
**Steps:**
1. Navigate to the "Manage Habits" tab.
2. Leave "Habit Name" empty OR enter a non-numeric "Daily Target".
3. Click the "Create Habit 🚀" button.

**Expected Results:**
- The habit is **not** created.
- A warning message "Please enter a valid name and a numeric daily target." is displayed.

### 2. Daily Check-in and Streak Tracking (US-002)

**Source**: `docs/copilot/habit_tracker_user_stories.md` - US-002

#### 2.1 Successful Daily Check-in
**Steps:**
1. Navigate to the "Daily Tracker" tab.
2. Select a habit from the "Select Habit to Track" dropdown.
3. Verify the "Check In Today" button is enabled.
4. Click the "✅ Check In Today" button.

**Expected Results:**
- A success message "Great job! Check-in recorded for [Habit Name]. 🔥" is displayed.
- The "Current Streak" counter increments by 1.
- The "Total Check-ins" counter increments by 1.
- The "Check In Today" button becomes disabled or indicates completion.

#### 2.2 Prevent Duplicate Check-ins
**Steps:**
1. Navigate to the "Daily Tracker" tab.
2. Select a habit that has already been checked in for the current day.
3. Attempt to click the check-in button (if enabled) or verify it is disabled.

**Expected Results:**
- The system prevents the action.
- If clickable, a message "You've already checked in for [Habit Name] today! Come back tomorrow." is displayed.

### 3. Visual Progress and History (US-003)

**Source**: `docs/copilot/habit_tracker_user_stories.md` - US-003

#### 3.1 Visualizations Display
**Steps:**
1. Navigate to the "Daily Tracker" tab.
2. Select a habit with check-in history.
3. Observe the "Last 30 Days Activity" section.
4. Observe the "Completion Progress" section.

**Expected Results:**
- A heatmap plot is displayed in "Last 30 Days Activity".
- A chart is displayed in "Completion Progress".
- The current day's check-in (if completed) is reflected in the visualizations.

### 4. Gamification and Badges (US-004)

**Source**: `docs/copilot/habit_tracker_user_stories.md` - US-004

#### 4.1 Trophy Case Display
**Steps:**
1. Navigate to the "Daily Tracker" tab.
2. Observe the "Trophy Case 🏆" section.

**Expected Results:**
- The section is present.
- Badges (🥉, 🥈, 🥇) are displayed if the corresponding streak milestones (7, 30, 100 days) are met.

## Traceability Matrix

| User Story | Test Scenario | Description |
| :--- | :--- | :--- |
| US-001 | 1.1 | Successful Habit Creation |
| US-001 | 1.2 | Duplicate Habit Prevention |
| US-001 | 1.3 | Invalid Input Validation |
| US-002 | 2.1 | Successful Daily Check-in |
| US-002 | 2.2 | Prevent Duplicate Check-ins |
| US-003 | 3.1 | Visualizations Display |
| US-004 | 4.1 | Trophy Case Display |
