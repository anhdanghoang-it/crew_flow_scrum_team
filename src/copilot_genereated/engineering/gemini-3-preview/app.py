"""
Trading Platform Gradio Application

This application provides a user interface for the Trading Platform, allowing users to:
- Create accounts and login
- Manage funds (Deposit/Withdraw)
- Buy and Sell shares
- View Portfolio and Transaction History

It integrates with the `trading_platform_backend` module.
"""

import gradio as gr
import os
import sys
import inspect

# Add current directory to path to allow importing the backend module
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import the backend module
try:
    import trading_platform_backend
except ImportError as e:
    print(f"Error importing backend: {e}")
    # For robustness in some environments, try importing without package prefix if needed
    # But here we assume standard python path resolution
    raise

# Auto-detect the primary service class
# We look for the class 'TradingService' as defined in the technical design
ServiceClass = None
for name, obj in inspect.getmembers(trading_platform_backend):
    if inspect.isclass(obj) and name == "TradingService":
        ServiceClass = obj
        break

if not ServiceClass:
    raise ValueError("Could not find 'TradingService' class in backend module.")

# Initialize the backend service
backend = ServiceClass()

def handle_create_account(username):
    """Handles account creation."""
    if not username:
        gr.Warning("Username cannot be empty")
        return None, gr.update(visible=False)
    
    response = backend.create_account(username)
    
    if response['success']:
        gr.Info(response['message'])
        return username, gr.update(visible=True)
    else:
        if response.get('code') == "DUPLICATE_USER":
            gr.Error(response['message'])
        else:
            gr.Warning(response['message'])
        return None, gr.update(visible=False)

def handle_login(username):
    """Handles user login by verifying account existence."""
    if not username:
        gr.Warning("Please enter a username")
        return None, gr.update(visible=False)
        
    # We use get_portfolio to check if user exists
    response = backend.get_portfolio(username)
    
    if response['success']:
        gr.Info(f"Welcome back, {username}!")
        return username, gr.update(visible=True)
    else:
        gr.Error(f"User '{username}' not found. Please register.")
        return None, gr.update(visible=False)

def refresh_dashboard(username):
    """Refreshes the dashboard data."""
    if not username:
        return 0.0, 0.0, "$0.00 (+0.00%)", [], gr.update(visible=False)
        
    response = backend.get_portfolio(username)
    
    if response['success']:
        data = response['data']
        return (
            data['total_value'],
            data['cash_balance'],
            data['profit_loss_str'],
            data['holdings_table'],
            gr.update(visible=True)
        )
    else:
        gr.Error(response['message'])
        return 0.0, 0.0, "$0.00", [], gr.update(visible=True)

def handle_deposit(username, amount):
    """Handles fund deposit."""
    if not username:
        gr.Warning("Please login first")
        return
        
    response = backend.deposit(username, amount)
    
    if response['success']:
        gr.Info(response['message'])
    else:
        gr.Error(response['message'])

def handle_withdraw(username, amount):
    """Handles fund withdrawal."""
    if not username:
        gr.Warning("Please login first")
        return
        
    response = backend.withdraw(username, amount)
    
    if response['success']:
        gr.Info(response['message'])
    else:
        gr.Error(response['message'])

def handle_buy(username, symbol, quantity):
    """Handles buying shares."""
    if not username:
        gr.Warning("Please login first")
        return
        
    response = backend.buy_shares(username, symbol, quantity)
    
    if response['success']:
        gr.Info(response['message'])
    else:
        gr.Error(response['message'])

def handle_sell(username, symbol, quantity):
    """Handles selling shares."""
    if not username:
        gr.Warning("Please login first")
        return
        
    response = backend.sell_shares(username, symbol, quantity)
    
    if response['success']:
        gr.Info(response['message'])
    else:
        gr.Error(response['message'])

def refresh_history(username):
    """Refreshes transaction history."""
    if not username:
        return []
        
    response = backend.get_transaction_history(username)
    
    if response['success']:
        return response['data']
    else:
        gr.Error(response['message'])
        return []

# --- UI Layout ---

with gr.Blocks(title="Trading Platform") as app:
    # Global State
    current_user = gr.State(value=None)
    
    gr.Markdown("# 📈 Trading Platform Simulation")
    gr.Markdown("Manage your portfolio, trade stocks, and track your performance.")
    
    with gr.Tabs():
        
        # --- Tab 1: Login / Register ---
        with gr.Tab("Login / Register"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### New User")
                    reg_username = gr.Textbox(label="Username", placeholder="Choose a unique username")
                    reg_btn = gr.Button("Create Account", variant="primary")
                
                with gr.Column():
                    gr.Markdown("### Returning User")
                    login_username = gr.Textbox(label="Username", placeholder="Enter your username")
                    login_btn = gr.Button("Login")
            
            login_status = gr.Markdown(visible=False)

        # --- Tab 2: Dashboard ---
        with gr.Tab("Dashboard"):
            with gr.Row():
                dash_total_value = gr.Number(label="Total Portfolio Value", precision=2, interactive=False)
                dash_cash = gr.Number(label="Cash Balance", precision=2, interactive=False)
                dash_pl = gr.Textbox(label="Total Profit/Loss", interactive=False)
            
            gr.Markdown("### Current Holdings")
            dash_holdings = gr.Dataframe(
                headers=["Symbol", "Quantity", "Current Price", "Total Value"],
                datatype=["str", "number", "str", "str"],
                interactive=False,
                label="Holdings"
            )
            
            dash_refresh_btn = gr.Button("Refresh Dashboard")

        # --- Tab 3: Trade ---
        with gr.Tab("Trade"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Buy Shares")
                    buy_symbol = gr.Dropdown(choices=["AAPL", "TSLA", "GOOGL"], label="Symbol")
                    buy_qty = gr.Number(label="Quantity", precision=0, minimum=1)
                    buy_btn = gr.Button("Buy", variant="primary")
                
                with gr.Column():
                    gr.Markdown("### Sell Shares")
                    sell_symbol = gr.Dropdown(choices=["AAPL", "TSLA", "GOOGL"], label="Symbol")
                    sell_qty = gr.Number(label="Quantity", precision=0, minimum=1)
                    sell_btn = gr.Button("Sell", variant="secondary")

        # --- Tab 4: Funds ---
        with gr.Tab("Funds"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Deposit Funds")
                    dep_amount = gr.Number(label="Amount", precision=2, minimum=0.01)
                    dep_btn = gr.Button("Deposit")
                
                with gr.Column():
                    gr.Markdown("### Withdraw Funds")
                    with_amount = gr.Number(label="Amount", precision=2, minimum=0.01)
                    with_btn = gr.Button("Withdraw")

        # --- Tab 5: History ---
        with gr.Tab("History"):
            hist_refresh_btn = gr.Button("Refresh History")
            hist_table = gr.Dataframe(
                headers=["Time", "Type", "Symbol", "Quantity", "Price", "Amount"],
                interactive=False,
                label="Transaction History"
            )

    # --- Event Wiring ---
    
    # Login / Register Events
    reg_btn.click(
        fn=handle_create_account,
        inputs=[reg_username],
        outputs=[current_user, login_status]
    ).success(
        fn=refresh_dashboard,
        inputs=[current_user],
        outputs=[dash_total_value, dash_cash, dash_pl, dash_holdings, login_status]
    )
    
    login_btn.click(
        fn=handle_login,
        inputs=[login_username],
        outputs=[current_user, login_status]
    ).success(
        fn=refresh_dashboard,
        inputs=[current_user],
        outputs=[dash_total_value, dash_cash, dash_pl, dash_holdings, login_status]
    )

    # Dashboard Events
    dash_refresh_btn.click(
        fn=refresh_dashboard,
        inputs=[current_user],
        outputs=[dash_total_value, dash_cash, dash_pl, dash_holdings, login_status]
    )

    # Trade Events
    buy_btn.click(
        fn=handle_buy,
        inputs=[current_user, buy_symbol, buy_qty],
        outputs=None
    ).success(
        fn=refresh_dashboard,
        inputs=[current_user],
        outputs=[dash_total_value, dash_cash, dash_pl, dash_holdings, login_status]
    )

    sell_btn.click(
        fn=handle_sell,
        inputs=[current_user, sell_symbol, sell_qty],
        outputs=None
    ).success(
        fn=refresh_dashboard,
        inputs=[current_user],
        outputs=[dash_total_value, dash_cash, dash_pl, dash_holdings, login_status]
    )

    # Funds Events
    dep_btn.click(
        fn=handle_deposit,
        inputs=[current_user, dep_amount],
        outputs=None
    ).success(
        fn=refresh_dashboard,
        inputs=[current_user],
        outputs=[dash_total_value, dash_cash, dash_pl, dash_holdings, login_status]
    )

    with_btn.click(
        fn=handle_withdraw,
        inputs=[current_user, with_amount],
        outputs=None
    ).success(
        fn=refresh_dashboard,
        inputs=[current_user],
        outputs=[dash_total_value, dash_cash, dash_pl, dash_holdings, login_status]
    )

    # History Events
    hist_refresh_btn.click(
        fn=refresh_history,
        inputs=[current_user],
        outputs=[hist_table]
    )
    
    # Auto-refresh history when tab is selected (optional, but good UX)
    # Note: Gradio doesn't have a direct 'on tab select' event easily accessible in Blocks without JS
    # So we rely on the button.

if __name__ == "__main__":
    app.launch()
