"""
Gamified Habit Tracker Frontend Application.

This Gradio application provides a user interface for the Habit Tracker system,
allowing users to create habits, track daily progress, view statistics, and earn badges.
It integrates with the backend logic defined in `habit_tracker_backend.py`.
"""

import gradio as gr
import os
import sys
import inspect
import importlib.util
from typing import Any, Tuple, List

# --- Backend Auto-detection and Import ---

def import_backend():
    """
    Auto-detects and imports the backend module and the HabitTracker class.
    Searches in the current directory and immediate subdirectories.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_file_name = "habit_tracker_backend.py"
    backend_path = None

    # Search for the backend file
    for root, dirs, files in os.walk(current_dir):
        if backend_file_name in files:
            backend_path = os.path.join(root, backend_file_name)
            break
    
    if not backend_path:
        # Fallback: check if it's in the same directory as this script (if not found by walk)
        possible_path = os.path.join(current_dir, backend_file_name)
        if os.path.exists(possible_path):
            backend_path = possible_path

    if not backend_path:
        raise FileNotFoundError(f"Could not find backend module '{backend_file_name}'")

    print(f"Loading backend from: {backend_path}")

    # Import the module dynamically
    spec = importlib.util.spec_from_file_location("habit_tracker_backend", backend_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["habit_tracker_backend"] = module
    spec.loader.exec_module(module)

    # Find the HabitTracker class
    tracker_class = None
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and name == "HabitTracker":
            tracker_class = obj
            break
    
    if not tracker_class:
        raise ImportError("Could not find 'HabitTracker' class in backend module.")

    return tracker_class

# Initialize Backend
try:
    HabitTracker = import_backend()
    tracker = HabitTracker()
except Exception as e:
    print(f"Critical Error: Failed to initialize backend. {e}")
    sys.exit(1)


# --- Event Handlers ---

def create_habit_handler(name: str, target: float) -> Tuple[Any, Any, Any, Any]:
    """
    Handles habit creation.
    Returns: (Name Input update, Target Input update, Dataframe update, Dropdown update)
    """
    # Basic client-side validation
    if not name or not str(name).strip():
        gr.Warning("🎅 Ho ho hold on! Please enter a festive habit name to begin your journey!")
        return gr.update(), gr.update(), gr.update(), gr.update()
    
    try:
        # Ensure target is treated as int/float
        target_val = int(target)
    except (ValueError, TypeError):
        gr.Warning("🎄 Oops! Please enter a magical numeric daily target!")
        return gr.update(), gr.update(), gr.update(), gr.update()

    response = tracker.create_habit(name, target_val)
    
    if response['success']:
        gr.Info(f"🎉 {response['message']} Your holiday habit journey begins now! 🚀")
        # Refresh the list and dropdown
        new_df = tracker.get_all_habits_dataframe()
        new_choices = tracker.get_habit_names()
        return gr.update(value=""), gr.update(value=None), new_df, gr.update(choices=new_choices)
    else:
        if response.get('code') == 'CONFLICT_ERROR':
            gr.Warning(response['message'])
        else:
            gr.Error(response['message'])
        return gr.update(), gr.update(), gr.update(), gr.update()


def refresh_habit_list() -> List[List[Any]]:
    """Refreshes the dataframe of habits."""
    return tracker.get_all_habits_dataframe()


def update_habit_details(habit_name: str):
    """
    Updates the Daily Tracker tab when a habit is selected.
    Returns updates for: Status, Check-in Btn, Streak, Total, Badges, Heatmap, Progress
    """
    if not habit_name:
        return (
            gr.update(value="Please select a habit."), # Status
            gr.update(interactive=False),              # Button
            0,                                         # Streak
            0,                                         # Total
            "",                                        # Badges
            None,                                      # Heatmap
            None                                       # Progress
        )

    response = tracker.get_habit_details(habit_name)
    
    if not response['success']:
        gr.Error(response['message'])
        return (
            gr.update(value="Error loading habit."), 
            gr.update(interactive=False), 
            0, 0, "", None, None
        )

    data = response['data']
    
    # Format Status and Button with festive styling
    if data['checked_in_today']:
        status_md = """
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #c8e6c9 0%, #a5d6a7 100%); border-radius: 10px; border-left: 5px solid #4caf50;'>
            <h3 style='margin: 0; color: #2e7d32;'>✅ Fantastic! You've checked in today!</h3>
            <p style='margin: 5px 0 0 0; color: #1b5e20;'>🎉 Keep this festive momentum going!</p>
        </div>
        """
        btn_update = gr.update(value="🎁 Completed Today!", interactive=False)
    else:
        status_md = """
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #ffcdd2 0%, #ef9a9a 100%); border-radius: 10px; border-left: 5px solid #f44336;'>
            <h3 style='margin: 0; color: #c62828;'>⏰ Time to Build Your Streak!</h3>
            <p style='margin: 5px 0 0 0; color: #b71c1c;'>🎄 Click below to check in and keep the magic alive!</p>
        </div>
        """
        btn_update = gr.update(value="🎅 Check In Now!", interactive=True)

    # Format Badges with festive styling
    badges_list = data['badges']
    if badges_list:
        badges_html = "<div style='padding: 20px; background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%); border-radius: 10px; text-align: center;'>"
        badges_html += "<h3 style='margin: 0 0 15px 0; color: #f57c00;'>🏆 Your Trophy Case</h3>"
        for badge in badges_list:
            badges_html += f"<div style='display: inline-block; margin: 5px; padding: 10px 20px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'><span style='font-size: 1.2em;'>{badge}</span></div>"
        badges_html += "<p style='margin: 15px 0 0 0; color: #ef6c00; font-weight: 600;'>🎊 Amazing work! Keep collecting!</p></div>"
        badges_md = badges_html
    else:
        badges_md = """
        <div style='padding: 20px; background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%); border-radius: 10px; text-align: center;'>
            <h3 style='margin: 0 0 10px 0; color: #f57c00;'>🏆 Your Trophy Case</h3>
            <p style='margin: 0; color: #666;'><em>No badges yet - but you're on your way! 🌟</em></p>
            <p style='margin: 10px 0 0 0; color: #ef6c00; font-size: 0.95em;'>💪 Keep checking in to earn: 🥉 Bronze (7 days), 🥈 Silver (30 days), 🥇 Gold (100 days)</p>
        </div>
        """

    return (
        status_md,
        btn_update,
        data['streak'],
        data['total_checkins'],
        badges_md,
        data['heatmap_plot'],
        data['progress_plot']
    )


def check_in_handler(habit_name: str):
    """
    Handles the check-in action.
    """
    if not habit_name:
        gr.Warning("🎄 Please select a festive habit first to check in!")
        return update_habit_details(None)

    response = tracker.check_in(habit_name)
    
    if response['success']:
        gr.Info(f"🎊 {response['message']} Keep the holiday magic alive! ✨")
    else:
        if response.get('code') == 'DUPLICATE_ACTION_ERROR':
            gr.Warning(f"🎅 {response['message']}")
        else:
            gr.Error(f"❄️ {response['message']}")
            
    # Refresh details regardless of success to ensure UI is in sync
    return update_habit_details(habit_name)


# --- UI Layout ---

# Create festive holiday theme
festive_theme = gr.themes.Soft(
    primary_hue="red",
    secondary_hue="green",
    neutral_hue="slate",
    font=gr.themes.GoogleFont("Poppins")
).set(
    button_primary_background_fill="*primary_500",
    button_primary_background_fill_hover="*primary_600",
    button_primary_text_color="white",
)

with gr.Blocks(
    title="🎄 Holiday Habit Wonderland 🎅", 
    theme=festive_theme,
    css="""
        .gradio-container {
            background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        }
        .gr-button-primary {
            background: linear-gradient(135deg, #d32f2f 0%, #c62828 100%) !important;
            box-shadow: 0 4px 15px rgba(211, 47, 47, 0.3);
            border: none !important;
            transition: all 0.3s ease;
        }
        .gr-button-primary:hover {
            box-shadow: 0 6px 20px rgba(211, 47, 47, 0.4);
            transform: translateY(-2px);
        }
        .gr-button {
            border-radius: 8px;
        }
        h1, h2, h3 {
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .gr-panel {
            border-radius: 12px;
        }
    """
) as app:
    gr.Markdown("""
    <div style='text-align: center; padding: 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin-bottom: 20px;'>
        <h1 style='margin: 0; color: white; font-size: 2.5em;'>🎄 Holiday Habit Wonderland 🎅</h1>
        <p style='font-size: 1.3em; margin-top: 10px;'>Transform your life one festive habit at a time!</p>
    </div>
    """)
    gr.Markdown("""
    <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #ff9800;'>
        <p style='margin: 0; color: #e65100; font-size: 1.1em; font-weight: 600;'>
            ✨ Build holiday magic through daily habits! Track streaks, earn badges, and celebrate your journey! 🎁
        </p>
    </div>
    """)

    with gr.Tabs():
        # --- Tab 1: Manage Habits ---
        with gr.Tab("🎁 Manage Habits"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("""
                    <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); border-radius: 10px; margin-bottom: 15px;'>
                        <h3 style='margin: 0; color: #2e7d32;'>🎅 Create Your Holiday Habit</h3>
                    </div>
                    """)
                    habit_name_input = gr.Textbox(
                        label="🎯 Habit Name", 
                        placeholder="e.g., Read 30 mins, Meditate, Exercise 🏃‍♂️",
                        lines=1,
                        info="✨ What festive habit will you build?"
                    )
                    daily_target_input = gr.Number(
                        label="🎄 Daily Target", 
                        minimum=1,
                        step=1,
                        info="📊 Your daily goal (e.g., 30 minutes, 10 pages)"
                    )
                    create_btn = gr.Button(
                        "🚀 Create Magic Habit", 
                        variant="primary",
                        size="lg"
                    )
                    gr.Markdown("""
                    <div style='padding: 12px; background: #f0f7ff; border-radius: 8px; margin-top: 15px;'>
                        <p style='margin: 0; color: #1976d2; font-size: 0.95em;'>
                            💡 <strong>Pro Tip:</strong> Start with small, achievable habits and watch them grow like a Christmas tree! 🎄
                        </p>
                    </div>
                    """)
                
                with gr.Column(scale=2):
                    gr.Markdown("""
                    <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); border-radius: 10px; margin-bottom: 15px;'>
                        <h3 style='margin: 0; color: #1565c0;'>🎄 Your Holiday Habit Collection</h3>
                    </div>
                    """)
                    habits_list = gr.Dataframe(
                        headers=["Name", "Target", "Created Date"],
                        value=refresh_habit_list,
                        interactive=False,
                        label="🎁 Active Habits",
                        wrap=True
                    )

        # --- Tab 2: Daily Tracker ---
        with gr.Tab("⚡ Daily Tracker"):
            gr.Markdown("""
            <div style='padding: 15px; background: linear-gradient(135deg, #fce4ec 0%, #f8bbd0 100%); border-radius: 10px; margin-bottom: 20px;'>
                <p style='margin: 0; color: #c2185b; font-size: 1.1em; font-weight: 600; text-align: center;'>
                    🔥 Daily consistency is the secret to holiday magic! Let's check in and build your streak! 🎯
                </p>
            </div>
            """)
            with gr.Row():
                habit_dropdown = gr.Dropdown(
                    label="🎯 Select Your Habit to Track",
                    choices=tracker.get_habit_names(),
                    interactive=True,
                    info="✨ Choose the habit you want to focus on today"
                )
            
            with gr.Row():
                with gr.Column():
                    status_markdown = gr.Markdown("""
                    <div style='text-align: center; padding: 20px; background: #f5f5f5; border-radius: 10px;'>
                        <h3 style='color: #666;'>🎄 Select a habit to begin your journey</h3>
                    </div>
                    """)
                    check_in_btn = gr.Button(
                        "✅ Check In Today!", 
                        size="lg", 
                        interactive=False,
                        variant="primary"
                    )
                
                with gr.Column():
                    gr.Markdown("<p style='text-align: center; font-weight: 600; color: #666; margin-bottom: 10px;'>🌟 Your Holiday Stats</p>")
                    with gr.Row():
                        current_streak_display = gr.Number(
                            label="🔥 Current Streak", 
                            value=0, 
                            interactive=False,
                            container=True
                        )
                        total_checkins_display = gr.Number(
                            label="🎁 Total Check-ins", 
                            value=0, 
                            interactive=False,
                            container=True
                        )
            
            with gr.Row():
                badges_display = gr.Markdown("""
                <div style='padding: 20px; background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%); border-radius: 10px; text-align: center;'>
                    <h3 style='margin: 0 0 10px 0; color: #f57c00;'>🏆 Your Trophy Case</h3>
                    <p style='margin: 0; color: #666;'><em>Select a habit to view your earned badges</em></p>
                </div>
                """)

            gr.Markdown("<h3 style='text-align: center; margin-top: 30px; color: #666;'>📊 Your Holiday Progress Journey</h3>")
            with gr.Row():
                with gr.Column():
                    heatmap_plot = gr.Plot(label="📅 Last 30 Days Calendar")
                with gr.Column():
                    progress_plot = gr.Plot(label="📈 Completion Trend")
            
            gr.Markdown("""
            <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%); border-radius: 10px; margin-top: 20px;'>
                <p style='margin: 0; color: #3f51b5; font-weight: 600;'>
                    💪 Remember: Every check-in is a gift to your future self! Keep the festive spirit alive! 🎄✨
                </p>
            </div>
            """)

    # --- Event Wiring ---
    
    # Create Habit
    create_btn.click(
        fn=create_habit_handler,
        inputs=[habit_name_input, daily_target_input],
        outputs=[habit_name_input, daily_target_input, habits_list, habit_dropdown]
    )

    # Select Habit (Update Details)
    habit_dropdown.change(
        fn=update_habit_details,
        inputs=[habit_dropdown],
        outputs=[
            status_markdown, 
            check_in_btn, 
            current_streak_display, 
            total_checkins_display, 
            badges_display, 
            heatmap_plot, 
            progress_plot
        ]
    )

    # Check In
    check_in_btn.click(
        fn=check_in_handler,
        inputs=[habit_dropdown],
        outputs=[
            status_markdown, 
            check_in_btn, 
            current_streak_display, 
            total_checkins_display, 
            badges_display, 
            heatmap_plot, 
            progress_plot
        ]
    )
    
    # Refresh dropdown on tab select (optional, but good for UX if habits added)
    # Note: Gradio doesn't have a direct 'tab select' event easily exposed without some workarounds,
    # but the create_habit_handler already updates the dropdown.

if __name__ == "__main__":
    app.launch()
