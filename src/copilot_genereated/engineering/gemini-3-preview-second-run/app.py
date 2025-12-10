"""
Trading Simulation Frontend Application.

This Gradio application provides a user interface for the Trading Simulation Platform.
It connects to the `trading_simulation` backend to allow users to create accounts,
manage funds, trade stocks, and view their portfolio performance.

Run with: python app.py
"""

import gradio as gr
import sys
import os

# Ensure we can import the backend module from the same directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

import trading_simulation
from trading_simulation import TradingEngine

# Initialize the backend engine
engine = TradingEngine()

def get_dashboard_data(username):
    """
    Fetches all data needed to update the dashboard.
    Returns a tuple matching the outputs of the dashboard components.
    """
    try:
        # Check if account exists by trying to get balance
        balance = engine.get_balance(username)
        
        # Get other metrics
        metrics = engine.get_performance_metrics(username)
        holdings = engine.get_portfolio_summary(username)
        history = engine.get_transaction_history(username)
        
        return (
            balance,
            metrics['total_value'],
            metrics['profit_loss'],
            holdings,
            history
        )
    except Exception as e:
        # If account doesn't exist or other error, re-raise to be caught by Gradio
        raise gr.Error(str(e))

def create_account(username):
    try:
        msg = engine.create_account(username)
        gr.Info(msg)
        return get_dashboard_data(username)
    except Exception as e:
        raise gr.Error(str(e))

def login(username):
    try:
        return get_dashboard_data(username)
    except Exception as e:
        raise gr.Error(str(e))

def deposit(username, amount):
    try:
        msg = engine.deposit(username, float(amount))
        gr.Info(msg)
        return get_dashboard_data(username)
    except Exception as e:
        raise gr.Error(str(e))

def withdraw(username, amount):
    try:
        msg = engine.withdraw(username, float(amount))
        gr.Info(msg)
        return get_dashboard_data(username)
    except Exception as e:
        raise gr.Error(str(e))

def buy(username, symbol, quantity):
    try:
        msg = engine.buy_shares(username, symbol, int(quantity))
        gr.Info(msg)
        return get_dashboard_data(username)
    except Exception as e:
        raise gr.Error(str(e))

def sell(username, symbol, quantity):
    try:
        msg = engine.sell_shares(username, symbol, int(quantity))
        gr.Info(msg)
        return get_dashboard_data(username)
    except Exception as e:
        raise gr.Error(str(e))

# --- UI Layout ---

with gr.Blocks(title="Trading Simulation Platform") as app:
    gr.Markdown("# 📈 Trading Simulation Platform")
    gr.Markdown("Manage your portfolio, trade stocks, and track your performance.")

    with gr.Row():
        username_input = gr.Textbox(label="Username", placeholder="Enter your username", scale=2)
        create_btn = gr.Button("Create Account", variant="primary", scale=1)
        login_btn = gr.Button("Login / Refresh", variant="secondary", scale=1)

    # Dashboard Section
    with gr.Tabs():
        with gr.Tab("Dashboard"):
            with gr.Row():
                cash_display = gr.Number(label="Cash Balance ($)", precision=2, interactive=False)
                portfolio_value_display = gr.Number(label="Total Portfolio Value ($)", precision=2, interactive=False)
                pl_display = gr.Number(label="Total Profit/Loss ($)", precision=2, interactive=False)
            
            gr.Markdown("### Current Holdings")
            holdings_table = gr.DataFrame(
                headers=["Symbol", "Quantity", "Current Price", "Total Value"],
                datatype=["str", "number", "number", "number"],
                label="Holdings",
                interactive=False
            )

        with gr.Tab("Trade"):
            with gr.Row():
                symbol_input = gr.Dropdown(
                    choices=["AAPL", "TSLA", "GOOGL"], 
                    label="Symbol", 
                    info="Select a stock to trade"
                )
                quantity_input = gr.Number(label="Quantity", precision=0, minimum=1)
            
            with gr.Row():
                buy_btn = gr.Button("Buy Shares", variant="primary")
                sell_btn = gr.Button("Sell Shares", variant="stop")

        with gr.Tab("Funds"):
            with gr.Row():
                amount_input = gr.Number(label="Amount ($)", precision=2, minimum=0.01)
            with gr.Row():
                deposit_btn = gr.Button("Deposit")
                withdraw_btn = gr.Button("Withdraw")

        with gr.Tab("History"):
            history_table = gr.DataFrame(
                headers=["Time", "Type", "Symbol", "Quantity", "Price", "Total Amount"],
                datatype=["str", "str", "str", "number", "number", "str"],
                label="Transaction History",
                interactive=False
            )

    # --- Event Wiring ---
    
    # Outputs to update on refresh/action
    dashboard_outputs = [
        cash_display, 
        portfolio_value_display, 
        pl_display, 
        holdings_table, 
        history_table
    ]

    create_btn.click(
        fn=create_account,
        inputs=[username_input],
        outputs=dashboard_outputs
    )

    login_btn.click(
        fn=login,
        inputs=[username_input],
        outputs=dashboard_outputs
    )

    deposit_btn.click(
        fn=deposit,
        inputs=[username_input, amount_input],
        outputs=dashboard_outputs
    )

    withdraw_btn.click(
        fn=withdraw,
        inputs=[username_input, amount_input],
        outputs=dashboard_outputs
    )

    buy_btn.click(
        fn=buy,
        inputs=[username_input, symbol_input, quantity_input],
        outputs=dashboard_outputs
    )

    sell_btn.click(
        fn=sell,
        inputs=[username_input, symbol_input, quantity_input],
        outputs=dashboard_outputs
    )

if __name__ == "__main__":
    app.launch()
