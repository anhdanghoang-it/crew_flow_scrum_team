# Habit Tracker Technical Design

## 1. Overview & Architecture

### High-Level Architecture
The application follows a monolithic architecture with a clear separation between the presentation layer (Gradio) and the business logic layer (Python).

*   **Frontend**: Gradio interface for user interaction, visualization, and feedback.
*   **Backend**: Python class-based controller managing business logic, state, and data persistence.
*   **Data Store**: Local JSON file storage for simplicity and portability.

### Technology Stack
*   **Language**: Python 3.10+
*   **Frontend Framework**: Gradio 4.x+
*   **Data Validation**: Pydantic 2.x
*   **Visualization**: Plotly or Matplotlib (for heatmaps and charts)
*   **Persistence**: Standard `json` library

### Module Organization
```
src/crew_generated/engineering/
├── app.py                 # Main entry point and Gradio UI definition
├── habit_tracker.py       # Core business logic and data persistence
└── models.py              # Pydantic data models
```

---

## 2. Python Backend Design

### Data Models (`models.py`)

We will use Pydantic for robust data validation and serialization.

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date, datetime

class CheckIn(BaseModel):
    date: date
    timestamp: datetime = Field(default_factory=datetime.now)

class Habit(BaseModel):
    name: str
    daily_target: int = Field(gt=0, description="Target value for the habit (e.g., minutes, count)")
    created_at: datetime = Field(default_factory=datetime.now)
    check_ins: List[date] = Field(default_factory=list)
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Habit name cannot be empty')
        return v.strip()

    @property
    def current_streak(self) -> int:
        # Logic to calculate current streak based on check_ins
        pass

    @property
    def longest_streak(self) -> int:
        # Logic to calculate longest streak
        pass
        
    @property
    def badges(self) -> List[str]:
        # Logic to return earned badges based on streaks
        pass
```

### Core Logic (`habit_tracker.py`)

The `HabitTracker` class will act as the controller.

```python
import json
from typing import List, Dict, Any, Tuple
from datetime import date
from .models import Habit

class HabitTracker:
    def __init__(self, data_file: str = "habits.json"):
        self.data_file = data_file
        self.habits: Dict[str, Habit] = {}
        self._load_data()

    def _load_data(self) -> None:
        """Loads habits from the JSON file."""
        pass

    def _save_data(self) -> None:
        """Saves current state to the JSON file."""
        pass

    def create_habit(self, name: str, target: int) -> Tuple[bool, str]:
        """
        Creates a new habit.
        Returns: (success: bool, message: str)
        """
        pass

    def get_all_habits_dataframe(self) -> List[List[Any]]:
        """Returns data formatted for Gradio Dataframe."""
        pass
        
    def get_habit_names(self) -> List[str]:
        """Returns a list of habit names for dropdowns."""
        pass

    def check_in(self, habit_name: str) -> Tuple[bool, str]:
        """
        Records a check-in for today.
        Returns: (success: bool, message: str)
        """
        pass

    def get_habit_details(self, habit_name: str) -> Dict[str, Any]:
        """
        Returns detailed stats for a specific habit.
        Keys: streak, total_checkins, badges, history_plot, progress_plot
        """
        pass
```

### Error Handling Strategy

*   **Custom Exceptions**:
    *   `HabitAlreadyExistsError`: Raised when creating a duplicate habit.
    *   `HabitNotFoundError`: Raised when operating on a non-existent habit.
    *   `DuplicateCheckInError`: Raised when checking in twice on the same day.
*   **Response Format**: Public methods return a tuple `(success: bool, message: str)` or raise exceptions that the UI layer catches and converts to `gr.Warning` or `gr.Error`.

---

## 3. Gradio Frontend Design

### UI Layout & Workflow

The UI will use `gr.Blocks` with a tabbed interface.

#### Tab 1: Manage Habits
*   **Input Group**:
    *   `habit_name_input` (Textbox)
    *   `daily_target_input` (Number)
    *   `create_btn` (Button, variant="primary")
*   **Display**:
    *   `habits_list` (Dataframe)

#### Tab 2: Daily Tracker
*   **Selection**:
    *   `habit_dropdown` (Dropdown)
*   **Action Area**:
    *   `status_markdown` (Markdown: "Status: ❌ Not checked in")
    *   `check_in_btn` (Button, size="lg")
*   **Stats Row**:
    *   `current_streak_display` (Number)
    *   `total_checkins_display` (Number)
    *   `badges_display` (HTML/Markdown)
*   **Visualizations**:
    *   `heatmap_plot` (Plot)
    *   `progress_plot` (Plot)

### Component Mapping

| Backend Method | Gradio Component | Event | User Feedback |
| :--- | :--- | :--- | :--- |
| `create_habit` | `create_btn` | `click` | `gr.Info` (Success), `gr.Warning` (Error) |
| `get_all_habits_dataframe` | `habits_list` | `load`, `create_habit` | Table update |
| `check_in` | `check_in_btn` | `click` | `gr.Info` (Success), `gr.Warning` (Duplicate) |
| `get_habit_details` | `habit_dropdown` | `change` | Updates all stats & plots |

### User-Facing Messages

*   **Success**: "Habit '{name}' created successfully! 🚀"
*   **Check-in Success**: "Great job! Check-in recorded for {name}. 🔥"
*   **Duplicate Error**: "Habit '{name}' already exists."
*   **Duplicate Check-in**: "You've already checked in for {name} today!"
*   **Badges**: "Congratulations! You've earned the {badge_name}!"

---

## 4. Integration Points

### Data Flow: Habit Creation
1.  User enters Name and Target -> Click "Create".
2.  UI calls `create_habit(name, target)`.
3.  Backend validates input -> Checks duplicates -> Saves to JSON.
4.  Backend returns `(True, "Success message")`.
5.  UI shows `gr.Info`, clears inputs, and refreshes `habits_list` and `habit_dropdown`.

### Data Flow: Check-in
1.  User selects Habit -> Click "Check In".
2.  UI calls `check_in(habit_name)`.
3.  Backend adds today's date to `check_ins` list -> Saves JSON.
4.  Backend recalculates streak.
5.  UI updates Streak, Total, Heatmap, and Badges immediately.

### Visualization Integration
*   **Heatmap**: The backend `get_habit_details` will generate a Plotly figure object representing the calendar heatmap and return it. Gradio's `gr.Plot` will render this object directly.
*   **Badges**: The backend returns an HTML string containing badge icons (🥉, 🥈, 🥇) which is rendered by `gr.HTML`.

---

## 5. Implementation Examples

### Backend: Streak Calculation Logic
```python
def calculate_streak(dates: List[date]) -> int:
    if not dates:
        return 0
    
    sorted_dates = sorted(set(dates), reverse=True)
    today = date.today()
    streak = 0
    
    # Check if the streak is active (checked in today or yesterday)
    if sorted_dates[0] < today - timedelta(days=1):
        return 0
        
    current = today
    # If not checked in today, start checking from yesterday
    if sorted_dates[0] != today:
        current = today - timedelta(days=1)
        
    for d in sorted_dates:
        if d == current:
            streak += 1
            current -= timedelta(days=1)
        else:
            break
    return streak
```

### Frontend: Gradio App Skeleton
```python
import gradio as gr
from habit_tracker import HabitTracker

tracker = HabitTracker()

with gr.Blocks() as app:
    gr.Markdown("# 📅 Gamified Habit Tracker")
    
    with gr.Tabs():
        with gr.Tab("Manage Habits"):
            name = gr.Textbox(label="Habit Name")
            target = gr.Number(label="Daily Target")
            create_btn = gr.Button("Create Habit")
            habit_list = gr.Dataframe(headers=["Name", "Target", "Created"])
            
            def add_habit(n, t):
                success, msg = tracker.create_habit(n, t)
                if success:
                    gr.Info(msg)
                    return gr.update(value=""), gr.update(value=None), tracker.get_all_habits_dataframe()
                else:
                    raise gr.Warning(msg)

            create_btn.click(add_habit, [name, target], [name, target, habit_list])

        with gr.Tab("Daily Tracker"):
            # ... Implementation for tracker tab
            pass

if __name__ == "__main__":
    app.launch()
```

---

## 6. Testing & QA Guidelines

### Backend Unit Tests (`tests/test_backend.py`)
*   **Test Creation**: Verify habit is saved and appears in list.
*   **Test Duplicate**: Verify `HabitAlreadyExistsError` or False return.
*   **Test Streak**:
    *   Mock dates: [Today, Yesterday, Day Before] -> Streak 3.
    *   Mock dates: [Today, Day Before] -> Streak 1 (Gap).
*   **Test Persistence**: Verify data persists after reloading `HabitTracker`.

### Integration Tests
*   **End-to-End Flow**:
    1.  Start App.
    2.  Create "Read Book".
    3.  Switch to Tracker Tab.
    4.  Select "Read Book".
    5.  Click "Check In".
    6.  Verify Streak = 1.
    7.  Verify Heatmap updates.

---

## 7. Dependencies & Setup

### `requirements.txt`
```text
gradio>=4.0.0
pydantic>=2.0.0
pandas>=2.0.0
plotly>=5.0.0
matplotlib>=3.7.0
```

### Setup
1.  Install dependencies: `pip install -r requirements.txt`
2.  Run application: `python src/crew_generated/engineering/app.py`

---

## 8. Definition of Done

*   [ ] `models.py` implemented with Pydantic validation.
*   [ ] `habit_tracker.py` implements all CRUD and logic methods.
*   [ ] `app.py` implements the full Gradio UI with 2 tabs.
*   [ ] Streak calculation logic covers edge cases (missed days, today vs yesterday).
*   [ ] Heatmap visualization renders correctly.
*   [ ] Badges appear when milestones (7, 30, 100) are hit.
*   [ ] Code is fully type-hinted.
*   [ ] Docstrings provided for all public methods.
