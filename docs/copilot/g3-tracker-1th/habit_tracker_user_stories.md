# Habit Tracker User Stories

## US-001: Habit Creation and Management

**Story Statement**
As a **User**, I want to **create and view my custom habits**, so that I can **track the specific behaviors I want to build**.

**Business Value**: High. This is the foundational feature for the application. Without habits, there is nothing to track.

**Estimation**: 3 Points

### Acceptance Criteria

**Scenario 1: Successful Habit Creation**
- **Given** the user is on the "Manage Habits" tab
- **When** they enter a valid "Habit Name" (e.g., "Drink Water") and "Daily Target" (e.g., "2 liters")
- **And** click the "Create Habit" button
- **Then** the system should save the new habit
- **And** display a success message: "Habit 'Drink Water' created successfully! 🚀"
- **And** the habit should immediately appear in the "Your Habits" list
- **And** the input fields should be cleared

**Scenario 2: Duplicate Habit Prevention**
- **Given** a habit named "Morning Jog" already exists
- **When** the user tries to create another habit named "Morning Jog" (case-insensitive)
- **Then** the system should **not** create the habit
- **And** display an error message: "Habit 'Morning Jog' already exists. Please choose a different name."

**Scenario 3: Invalid Input Validation**
- **Given** the user is on the creation form
- **When** they leave the "Habit Name" empty OR enter a non-numeric "Daily Target"
- **And** click "Create Habit"
- **Then** the system should display a warning: "Please enter a valid name and a numeric daily target."

### UI/UX Specifications (Gradio)

**Layout Structure:**
- **Tab**: "Manage Habits"
- **Row 1**: Input Section
  - `gr.Textbox(label="Habit Name", placeholder="e.g., Read 30 mins")`
  - `gr.Textbox(label="Daily Target", placeholder="e.g., 30")`
  - `gr.Button(value="Create Habit", variant="primary")`
- **Row 2**: Display Section
  - `gr.Dataframe(label="Your Habits", headers=["Name", "Target", "Created Date"], interactive=False)`

**User Feedback:**
- Use `gr.Info()` for success messages.
- Use `gr.Warning()` for validation errors.

---

## US-002: Daily Check-in and Streak Tracking

**Story Statement**
As a **User**, I want to **check in for my habits daily**, so that I can **maintain my streak and record my consistency**.

**Business Value**: High. This is the core interaction loop of the application.

**Estimation**: 5 Points

### Acceptance Criteria

**Scenario 1: Successful Daily Check-in**
- **Given** the user has selected a habit "Meditation"
- **And** they have not checked in today
- **When** they click the "Check In" button
- **Then** the system should record the completion for the current date
- **And** the "Current Streak" counter should increment by 1
- **And** a success message should appear: "Great job! Check-in recorded for Meditation. 🔥"
- **And** the "Check In" button should become disabled or indicate "Completed"

**Scenario 2: Prevent Duplicate Check-ins**
- **Given** the user has already checked in for "Meditation" today
- **When** they attempt to check in again
- **Then** the system should prevent the action
- **And** display a message: "You've already checked in for Meditation today! Come back tomorrow."

**Scenario 3: Streak Calculation Logic**
- **Given** the user checked in yesterday (Streak: 5)
- **When** they check in today
- **Then** the streak should update to 6
- **Given** the user missed yesterday
- **When** they check in today
- **Then** the streak should reset to 1

### UI/UX Specifications (Gradio)

**Layout Structure:**
- **Tab**: "Daily Tracker"
- **Row 1**: Selection
  - `gr.Dropdown(label="Select Habit to Track", choices=[dynamic list of habits])`
- **Row 2**: Action Area
  - `gr.Markdown` displaying current status (e.g., "Status: ❌ Not checked in today")
  - `gr.Button(value="✅ Check In Today", size="lg")`
- **Row 3**: Real-time Stats (Updates immediately after check-in)
  - `gr.Number(label="Current Streak")`
  - `gr.Number(label="Total Check-ins")`

---

## US-003: Visual Progress and History

**Story Statement**
As a **User**, I want to **see a calendar heatmap and progress chart**, so that I can **visualize my long-term consistency**.

**Business Value**: Medium. Visual feedback reinforces the habit loop.

**Estimation**: 5 Points

### Acceptance Criteria

**Scenario 1: Calendar Heatmap Display**
- **Given** the user selects a habit
- **When** the dashboard loads
- **Then** a calendar heatmap should display the last 30 days
- **And** days with check-ins should be colored Green
- **And** days without check-ins should be colored Gray
- **And** the current day should be clearly visible

**Scenario 2: Completion Rate Chart**
- **Given** the user has check-in history
- **When** they view the progress section
- **Then** a line or bar chart should show the completion rate over time (e.g., weekly or cumulative)

### UI/UX Specifications (Gradio)

**Layout Structure:**
- **Location**: Below the "Action Area" in "Daily Tracker" tab
- **Row 4**: Visualizations
  - `gr.Plot(label="Last 30 Days Activity")` (Use matplotlib/seaborn/plotly for the heatmap)
  - `gr.Plot(label="Completion Progress")`

---

## US-004: Gamification and Badges

**Story Statement**
As a **User**, I want to **earn badges for milestones**, so that I feel **motivated to continue my streaks**.

**Business Value**: Medium. Increases user retention through positive reinforcement.

**Estimation**: 3 Points

### Acceptance Criteria

**Scenario 1: Awarding Bronze Badge**
- **Given** the user's current streak reaches 7 days
- **When** they complete the check-in
- **Then** the system should display a special celebration message: "Congratulations! You've earned the 🥉 Bronze Badge (7 Day Streak)!"
- **And** the badge icon 🥉 should appear in their habit stats

**Scenario 2: Awarding Silver and Gold Badges**
- **Given** the streak reaches 30 days -> Award 🥈 Silver Badge
- **Given** the streak reaches 100 days -> Award 🥇 Gold Badge

**Scenario 3: Badge Display**
- **Given** a user has earned badges
- **When** they view the habit details
- **Then** all earned badges should be visible in a "Trophy Case" or status area

### UI/UX Specifications (Gradio)

**Layout Structure:**
- **Location**: Sidebar or Top of "Daily Tracker" tab
- **Component**: `gr.Markdown` or `gr.HTML`
- **Content**:
  - Display emojis (🥉, 🥈, 🥇) dynamically based on streak count.
  - Use `gr.Info` for the immediate pop-up notification upon earning.

---

## Technical Notes & Definition of Done

### Technical Constraints
- **Framework**: Gradio (Python)
- **Data Persistence**: Simple JSON or SQLite file to store habits and check-in history locally.
- **State Management**: Must use `gr.State` to handle data updates between the "Manage" and "Tracker" tabs without page reloads if possible, or refresh dropdowns on tab switch.

### Definition of Done
- [ ] All acceptance criteria met.
- [ ] UI components implemented using Gradio as specified.
- [ ] "Happy Path" works (Create -> Check-in -> Streak Update -> Badge).
- [ ] Edge cases handled (Duplicate check-ins, empty names).
- [ ] Code is saved in `src/crew_generated/engineering/`.

### Out of Scope
- User authentication/login (Single user system for now).
- Mobile app native features (Push notifications).
- Social sharing features.
