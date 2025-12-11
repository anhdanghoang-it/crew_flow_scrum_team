"""
Gamified Habit Tracker Backend Module.

This module implements the core business logic, data models, and data persistence
for the Gamified Habit Tracker application. It is designed to integrate seamlessly
with a Gradio frontend.

Usage:
    tracker = HabitTracker()
    
    # Create a habit
    response = tracker.create_habit("Read", 30)
    if response['success']:
        print(response['message'])
        
    # Check in
    response = tracker.check_in("Read")
    
    # Get details for UI
    details = tracker.get_habit_details("Read")
    heatmap_plot = details['data']['heatmap_plot']
"""

import json
import os
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from enum import Enum

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pydantic import BaseModel, Field, field_validator, ValidationError

# --- Constants ---
DATA_FILE = "habits.json"
DATE_FORMAT = "%Y-%m-%d"

# --- Exceptions ---
class BackendError(Exception):
    """Base exception for backend errors."""
    def __init__(self, message: str, code: str = "BACKEND_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)

class ConflictError(BackendError):
    """Raised when a resource already exists."""
    def __init__(self, message: str):
        super().__init__(message, code="CONFLICT_ERROR")

class NotFoundError(BackendError):
    """Raised when a resource is not found."""
    def __init__(self, message: str):
        super().__init__(message, code="NOT_FOUND_ERROR")

class DuplicateActionError(BackendError):
    """Raised when an action is performed twice (e.g. check-in)."""
    def __init__(self, message: str):
        super().__init__(message, code="DUPLICATE_ACTION_ERROR")

# --- Data Models ---

class Habit(BaseModel):
    """
    Represents a single habit to be tracked.
    """
    name: str
    daily_target: int = Field(gt=0, description="Daily target value (e.g. minutes, pages)")
    created_at: str = Field(default_factory=lambda: datetime.now().strftime(DATE_FORMAT))
    check_ins: List[str] = Field(default_factory=list, description="List of dates (YYYY-MM-DD) when checked in")
    earned_badges: List[str] = Field(default_factory=list)

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Habit name cannot be empty')
        return v.strip()

    @property
    def check_in_dates(self) -> List[date]:
        """Returns check-ins as date objects, sorted."""
        return sorted([datetime.strptime(d, DATE_FORMAT).date() for d in set(self.check_ins)])

    @property
    def current_streak(self) -> int:
        """Calculates the current streak of consecutive days."""
        dates = self.check_in_dates
        if not dates:
            return 0

        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # If not checked in today or yesterday, streak is broken
        if dates[-1] < yesterday:
            return 0
            
        streak = 0
        current_check = today
        
        # If last check-in was yesterday, start counting from yesterday
        if dates[-1] == yesterday:
            current_check = yesterday
            
        # Iterate backwards checking for consecutive days
        reversed_dates = sorted(dates, reverse=True)
        for d in reversed_dates:
            if d == current_check:
                streak += 1
                current_check -= timedelta(days=1)
            elif d > current_check:
                # Should not happen if sorted, but safe to ignore duplicates/future
                continue
            else:
                # Gap found
                break
        return streak

    @property
    def longest_streak(self) -> int:
        """Calculates the longest streak ever recorded."""
        dates = self.check_in_dates
        if not dates:
            return 0
            
        max_streak = 0
        current_streak = 0
        last_date = None
        
        for d in dates:
            if last_date is None:
                current_streak = 1
            elif d == last_date + timedelta(days=1):
                current_streak += 1
            elif d == last_date:
                pass # Duplicate, shouldn't happen due to set() but safe
            else:
                current_streak = 1
            
            max_streak = max(max_streak, current_streak)
            last_date = d
            
        return max_streak

    def check_badges(self) -> List[str]:
        """Updates and returns the list of new badges earned based on current streak."""
        streak = self.current_streak
        new_badges = []
        
        badges_map = {
            7: "🥉 Bronze Badge (7 Days)",
            30: "🥈 Silver Badge (30 Days)",
            100: "🥇 Gold Badge (100 Days)"
        }
        
        for threshold, badge_name in badges_map.items():
            if streak >= threshold and badge_name not in self.earned_badges:
                self.earned_badges.append(badge_name)
                new_badges.append(badge_name)
                
        return new_badges

# --- Controller ---

class HabitTracker:
    """
    Controller class for managing habits, persistence, and business logic.
    """
    def __init__(self, data_file: str = DATA_FILE):
        self.data_file = data_file
        self.habits: Dict[str, Habit] = {}
        self._load_data()

    def _load_data(self):
        """Loads habits from the JSON file."""
        if not os.path.exists(self.data_file):
            self.habits = {}
            return

        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                for name, habit_data in data.items():
                    try:
                        self.habits[name] = Habit(**habit_data)
                    except ValidationError as e:
                        print(f"Skipping invalid habit record '{name}': {e}")
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading data file: {e}")
            self.habits = {}

    def _save_data(self):
        """Saves current habits to the JSON file."""
        try:
            data = {name: habit.model_dump() for name, habit in self.habits.items()}
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error saving data file: {e}")

    def _response(self, success: bool, message: str, data: Any = None, code: str = None) -> Dict[str, Any]:
        """Helper to format standard response."""
        return {
            "success": success,
            "message": message,
            "data": data,
            "code": code
        }

    def create_habit(self, name: str, daily_target: Union[int, str]) -> Dict[str, Any]:
        """
        Creates a new habit.
        
        Args:
            name: Name of the habit.
            daily_target: Numeric target.
            
        Returns:
            Standard response dict.
        """
        try:
            # Input Validation
            if not name or not str(name).strip():
                return self._response(False, "Please enter a valid name.", code="VALIDATION_ERROR")
            
            try:
                target_int = int(daily_target)
                if target_int <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                return self._response(False, "Please enter a numeric daily target greater than 0.", code="VALIDATION_ERROR")

            clean_name = name.strip()
            
            # Check for duplicates (case-insensitive)
            for existing_name in self.habits:
                if existing_name.lower() == clean_name.lower():
                    return self._response(
                        False, 
                        f"Habit '{clean_name}' already exists. Please choose a different name.", 
                        code="CONFLICT_ERROR"
                    )

            # Create and Save
            new_habit = Habit(name=clean_name, daily_target=target_int)
            self.habits[clean_name] = new_habit
            self._save_data()
            
            return self._response(True, f"Habit '{clean_name}' created successfully! 🚀", data=new_habit.model_dump())

        except Exception as e:
            return self._response(False, f"Unexpected error: {str(e)}", code="UNEXPECTED_ERROR")

    def check_in(self, habit_name: str) -> Dict[str, Any]:
        """
        Records a check-in for the current day.
        
        Args:
            habit_name: Name of the habit to check in.
            
        Returns:
            Standard response dict with updated stats and any new badges.
        """
        try:
            if habit_name not in self.habits:
                return self._response(False, f"Habit '{habit_name}' not found.", code="NOT_FOUND_ERROR")
            
            habit = self.habits[habit_name]
            today_str = date.today().strftime(DATE_FORMAT)
            
            if today_str in habit.check_ins:
                return self._response(
                    False, 
                    f"You've already checked in for {habit_name} today! Come back tomorrow.", 
                    code="DUPLICATE_ACTION_ERROR"
                )
            
            # Record Check-in
            habit.check_ins.append(today_str)
            
            # Check for new badges
            new_badges = habit.check_badges()
            
            self._save_data()
            
            msg = f"Great job! Check-in recorded for {habit_name}. 🔥"
            if new_badges:
                msg += f"\n\n🎉 You earned: {', '.join(new_badges)}!"
            
            return self._response(True, msg, data={
                "streak": habit.current_streak,
                "total": len(habit.check_ins),
                "badges": habit.earned_badges
            })

        except Exception as e:
            return self._response(False, f"Unexpected error: {str(e)}", code="UNEXPECTED_ERROR")

    def get_all_habits_dataframe(self) -> List[List[Any]]:
        """
        Returns data formatted for Gradio Dataframe.
        Format: [[Name, Target, Created Date], ...]
        """
        data = []
        for h in self.habits.values():
            data.append([h.name, h.daily_target, h.created_at])
        return data

    def get_habit_names(self) -> List[str]:
        """Returns list of habit names for dropdowns."""
        return list(self.habits.keys())

    def get_habit_details(self, habit_name: str) -> Dict[str, Any]:
        """
        Generates detailed stats and plots for a specific habit.
        
        Returns:
            Response dict containing 'data' with keys:
            - streak, total_checkins, badges
            - heatmap_plot (Plotly Figure)
            - progress_plot (Plotly Figure)
        """
        if habit_name not in self.habits:
            return self._response(False, "Habit not found", code="NOT_FOUND_ERROR")
            
        habit = self.habits[habit_name]
        
        # --- Generate Visualizations ---
        
        # 1. Calendar Heatmap (Last 30 Days)
        end_date = date.today()
        start_date = end_date - timedelta(days=29)
        date_range = pd.date_range(start=start_date, end=end_date)
        
        check_in_set = set(habit.check_in_dates)
        
        heatmap_data = []
        for d in date_range:
            status = 1 if d.date() in check_in_set else 0
            heatmap_data.append({"Date": d, "Status": status, "Label": "Completed" if status else "Missed"})
            
        df_heatmap = pd.DataFrame(heatmap_data)
        
        # Create a simple bar-like heatmap or scatter plot
        # Using a scatter plot to simulate a 1D heatmap strip
        fig_heatmap = px.scatter(
            df_heatmap, 
            x="Date", 
            y=[1]*len(df_heatmap), # All on one line
            color="Label",
            color_discrete_map={"Completed": "green", "Missed": "lightgray"},
            title="Last 30 Days Activity",
            height=200
        )
        fig_heatmap.update_yaxes(visible=False, showticklabels=False)
        fig_heatmap.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=True,
            xaxis_title=None
        )
        fig_heatmap.update_traces(marker=dict(size=15, symbol="square"))

        # 2. Progress Chart (Cumulative Check-ins)
        if not habit.check_ins:
            # Empty chart if no data
            fig_progress = go.Figure()
            fig_progress.update_layout(title="No check-ins yet")
        else:
            sorted_dates = sorted(habit.check_in_dates)
            # Create a cumulative count
            df_progress = pd.DataFrame({"Date": sorted_dates})
            df_progress["Count"] = range(1, len(df_progress) + 1)
            
            fig_progress = px.line(
                df_progress, 
                x="Date", 
                y="Count", 
                title="Total Check-ins Over Time",
                markers=True
            )
            fig_progress.update_layout(height=300)

        # Check if checked in today
        today_str = date.today().strftime(DATE_FORMAT)
        checked_in_today = today_str in habit.check_ins

        return self._response(True, "Details retrieved", data={
            "streak": habit.current_streak,
            "total_checkins": len(habit.check_ins),
            "badges": habit.earned_badges,
            "heatmap_plot": fig_heatmap,
            "progress_plot": fig_progress,
            "checked_in_today": checked_in_today
        })

if __name__ == "__main__":
    # Quick verification test
    print("Initializing Habit Tracker...")
    tracker = HabitTracker("test_habits.json")
    
    # Test Creation
    print("\n--- Testing Creation ---")
    res = tracker.create_habit("Test Habit", 10)
    print(f"Create: {res['success']} - {res['message']}")
    
    # Test Duplicate
    res = tracker.create_habit("Test Habit", 10)
    print(f"Duplicate: {not res['success']} - {res['message']}")
    
    # Test Check-in
    print("\n--- Testing Check-in ---")
    res = tracker.check_in("Test Habit")
    print(f"Check-in: {res['success']} - {res['message']}")
    
    # Test Duplicate Check-in
    res = tracker.check_in("Test Habit")
    print(f"Dup Check-in: {not res['success']} - {res['message']}")
    
    # Test Details
    print("\n--- Testing Details ---")
    details = tracker.get_habit_details("Test Habit")
    print(f"Streak: {details['data']['streak']}")
    print(f"Total: {details['data']['total_checkins']}")
    
    # Cleanup
    if os.path.exists("test_habits.json"):
        os.remove("test_habits.json")
    print("\nTest Complete.")
