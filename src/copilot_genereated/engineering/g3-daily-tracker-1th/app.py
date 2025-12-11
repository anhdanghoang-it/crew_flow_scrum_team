import gradio as gr
import inspect
import importlib.util
import os
import sys
from typing import Any, Dict, List, Tuple
import pandas as pd
import plotly.graph_objects as go

# --- Backend Auto-detection ---
backend_module_name = "habit_tracker_backend"
try:
    # Add current directory to sys.path to ensure import works
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
        
    module = importlib.import_module(backend_module_name)
    
    # Find the primary class (HabitTracker)
    backend_class = None
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and name == "HabitTracker":
            backend_class = obj
            break
            
    if not backend_class:
        raise ImportError("Could not find HabitTracker class in backend module.")
        
    # Initialize Backend
    tracker = backend_class()
    print(f"Successfully loaded backend: {backend_class.__name__}")

except ImportError as e:
    print(f"Error loading backend: {e}")
    sys.exit(1)

# --- Theme & Styling ---
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

custom_css = """
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

# --- UI Logic Functions ---

def refresh_habit_list():
    """Returns updated dataframe and dropdown choices."""
    df_data = tracker.get_all_habits_dataframe()
    choices = tracker.get_habit_names()
    return df_data, gr.Dropdown(choices=choices)

def handle_create_habit(name: str, target: float):
    """Handles habit creation."""
    # Basic frontend validation
    if not name or not str(name).strip():
        gr.Warning("🎄 Oops! Please enter a valid Habit Name to continue your festive journey!")
        return gr.update(), gr.update(), gr.update(), gr.update()
        
    response = tracker.create_habit(name, target)
    
    if response['success']:
        gr.Info(f"🎉 {response['message']} Your holiday journey continues! 🚀")
        df, dropdown = refresh_habit_list()
        return "", 1, df, dropdown
    else:
        if response.get('code') == 'CONFLICT_ERROR':
             gr.Warning(f"🎅 Ho ho hold on! {response['message']}")
        else:
             gr.Error(f"❄️ {response['message']}")
        return gr.update(), gr.update(), gr.update(), gr.update()

def handle_check_in(habit_name: str):
    """Handles daily check-in."""
    if not habit_name:
        gr.Warning("⚠️ Please select a habit from the list first!")
        return gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update()

    response = tracker.check_in(habit_name)
    
    if response['success']:
        gr.Info(f"🎉 {response['message']}")
        # Refresh details immediately
        return get_habit_details_ui(habit_name)
    else:
        if response.get('code') == 'DUPLICATE_ACTION_ERROR':
             gr.Warning(f"🎅 Ho ho hold on! {response['message']}")
        else:
             gr.Error(f"❄️ {response['message']}")
        # Return current state without changes
        return gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update()

def get_habit_details_ui(habit_name: str):
    """Updates the UI with habit details."""
    if not habit_name:
        return (
            gr.update(value=""), # Status
            gr.update(interactive=False), # Button
            0, # Streak
            0, # Total
            "", # Badges
            None, # Heatmap
            None # Progress
        )
        
    response = tracker.get_habit_details(habit_name)
    
    if not response['success']:
        gr.Error(f"❄️ {response['message']}")
        return gr.update(), gr.update(), 0, 0, "", None, None

    data = response['data']
    
    # Format Status
    if data.get('checked_in_today'):
        status_html = """
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #c8e6c9 0%, #a5d6a7 100%); border-radius: 10px; border-left: 5px solid #4caf50;'>
            <h3 style='margin: 0; color: #2e7d32;'>✅ Checked In Today!</h3>
            <p style='margin: 5px 0 0 0; color: #1b5e20;'>🎉 Great job keeping the magic alive!</p>
        </div>
        """
        btn_interactive = False
        btn_label = "✅ Completed"
    else:
        status_html = """
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #ffcdd2 0%, #ef9a9a 100%); border-radius: 10px; border-left: 5px solid #f44336;'>
            <h3 style='margin: 0; color: #c62828;'>⏰ Action Needed</h3>
            <p style='margin: 5px 0 0 0; color: #b71c1c;'>🎄 Don't break your festive streak!</p>
        </div>
        """
        btn_interactive = True
        btn_label = "🎅 Check In Today"

    # Format Badges
    badges = data.get('badges', [])
    if badges:
        badges_html_content = "".join([
            f"<div style='display: inline-block; margin: 5px; padding: 10px 20px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'><span style='font-size: 1.2em;'>{b}</span></div>" 
            for b in badges
        ])
        badges_display = f"""
        <div style='padding: 20px; background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%); border-radius: 10px; text-align: center;'>
            <h3 style='margin: 0 0 15px 0; color: #f57c00;'>🏆 Your Trophy Case</h3>
            {badges_html_content}
            <p style='margin: 15px 0 0 0; color: #ef6c00; font-weight: 600;'>🎊 Keep going for Gold!</p>
        </div>
        """
    else:
        badges_display = """
        <div style='padding: 20px; background: #f8f9fa; border-radius: 10px; text-align: center; color: #6c757d;'>
            <p>No badges yet. Start your streak to earn rewards! 🏆</p>
        </div>
        """

    return (
        status_html,
        gr.update(value=btn_label, interactive=btn_interactive),
        data['streak'],
        data['total_checkins'],
        badges_display,
        data['heatmap_plot'],
        data['progress_plot']
    )

# --- Layout ---

with gr.Blocks(theme=festive_theme, css=custom_css, title="Noel Habit Tracker") as app:
    
    # Hero Header
    gr.Markdown("""
    <div style='text-align: center; padding: 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin-bottom: 20px;'>
        <h1 style='margin: 0; color: white; font-size: 2.5em;'>🎄 Noel Habit Tracker 🎅</h1>
        <p style='font-size: 1.3em; margin-top: 10px;'>Build habits that last beyond the holidays!</p>
    </div>
    """)

    with gr.Tabs() as tabs:
        
        # --- Tab 1: Manage Habits ---
        with gr.Tab("🎁 Manage Habits"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("""
                    <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); border-radius: 10px; margin-bottom: 15px;'>
                        <h3 style='margin: 0; color: #2e7d32;'>🎅 Create Your Holiday Magic</h3>
                    </div>
                    """)
                    
                    habit_name_input = gr.Textbox(
                        label="🎯 Magic Name", 
                        placeholder="e.g., Morning Reading 📚",
                        lines=1,
                        info="✨ What festive goal will you achieve?"
                    )
                    
                    daily_target_input = gr.Number(
                        label="🎄 Daily Target", 
                        minimum=1,
                        step=1,
                        value=1,
                        info="📊 Your daily goal (e.g., 30 minutes)"
                    )
                    
                    create_btn = gr.Button(
                        "🚀 Create Magic", 
                        variant="primary",
                        size="lg"
                    )
                    
                    gr.Markdown("""
                    <div style='padding: 12px; background: #f0f7ff; border-radius: 8px; margin-top: 15px;'>
                        <p style='margin: 0; color: #1976d2; font-size: 0.95em;'>
                            💡 <strong>Pro Tip:</strong> Start small and watch it grow like a Christmas tree! 🎄
                        </p>
                    </div>
                    """)

                with gr.Column(scale=2):
                    gr.Markdown("### 📜 Your Habit List")
                    habit_list_display = gr.Dataframe(
                        headers=["Name", "Target", "Created Date"],
                        label="Current Habits",
                        interactive=False,
                        value=tracker.get_all_habits_dataframe()
                    )

        # --- Tab 2: Daily Tracker ---
        with gr.Tab("⚡ Daily Tracker"):
            
            with gr.Row():
                habit_select = gr.Dropdown(
                    label="🎯 Select Habit to Track",
                    choices=tracker.get_habit_names(),
                    interactive=True,
                    info="✨ Choose a habit to check in or view stats"
                )
            
            with gr.Row():
                with gr.Column(scale=1):
                    status_display = gr.HTML(label="Status")
                    check_in_btn = gr.Button(
                        "🎅 Check In Today", 
                        variant="primary", 
                        size="lg",
                        interactive=False
                    )
                    
                    gr.Markdown("### 📊 Magic Numbers")
                    with gr.Group():
                        streak_display = gr.Number(label="🔥 Current Streak", value=0, interactive=False)
                        total_display = gr.Number(label="📈 Total Check-ins", value=0, interactive=False)
                
                with gr.Column(scale=2):
                    badges_output = gr.HTML(label="Trophy Case")
            
            with gr.Row():
                with gr.Column():
                    heatmap_plot = gr.Plot(label="📅 Last 30 Days Activity")
                with gr.Column():
                    progress_plot = gr.Plot(label="📈 Completion Progress")

    # --- Event Handlers ---
    
    # Create Habit
    create_btn.click(
        fn=handle_create_habit,
        inputs=[habit_name_input, daily_target_input],
        outputs=[habit_name_input, daily_target_input, habit_list_display, habit_select]
    )
    
    # Select Habit -> Load Details
    habit_select.change(
        fn=get_habit_details_ui,
        inputs=[habit_select],
        outputs=[
            status_display, 
            check_in_btn, 
            streak_display, 
            total_display, 
            badges_output, 
            heatmap_plot, 
            progress_plot
        ]
    )
    
    # Check In
    check_in_btn.click(
        fn=handle_check_in,
        inputs=[habit_select],
        outputs=[
            status_display, 
            check_in_btn, 
            streak_display, 
            total_display, 
            badges_output, 
            heatmap_plot, 
            progress_plot
        ]
    )
    
    # Refresh list on load (optional, but good for persistence check)
    app.load(fn=refresh_habit_list, outputs=[habit_list_display, habit_select])

if __name__ == "__main__":
    app.launch()
