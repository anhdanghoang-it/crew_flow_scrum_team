"""
Trading Simulation Platform - Gradio Frontend

This application provides a user interface for the Trading Simulation Platform,
allowing users to create accounts, manage funds, trade stocks, and view their portfolio.

It integrates with the `trading_simulation_trading_backend` module for all business logic.
"""

import gradio as gr
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import inspect
import importlib.util
import os
import sys

# Add current directory to path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Auto-detect backend module
backend_module_name = "trading_simulation_trading_backend"
try:
    backend = importlib.import_module(backend_module_name)
    # Inspect to find the primary class (TradingAccount)
    classes = [m[0] for m in inspect.getmembers(backend, inspect.isclass) if m[1].__module__ == backend_module_name]
    if "TradingAccount" in classes:
        TradingAccount = getattr(backend, "TradingAccount")
    else:
        raise ImportError("TradingAccount class not found in backend module")
        
    # Import services and constants
    create_account_service = getattr(backend, "create_account_service")
    deposit_service = getattr(backend, "deposit_service")
    withdraw_service = getattr(backend, "withdraw_service")
    buy_stock_service = getattr(backend, "buy_stock_service")
    sell_stock_service = getattr(backend, "sell_stock_service")
    get_share_price = getattr(backend, "get_share_price")
    SUPPORTED_SYMBOLS = getattr(backend, "SUPPORTED_SYMBOLS")
    
except ImportError as e:
    print(f"Error importing backend: {e}")
    sys.exit(1)

# --- Helper Functions ---

def format_currency(value: float) -> str:
    return f"${value:,.2f}"

def format_percentage(value: float) -> str:
    return f"{value:+.2f}%"

def get_holdings_df(account: TradingAccount) -> pd.DataFrame:
    if not account:
        return pd.DataFrame(columns=["Symbol", "Quantity", "Avg Cost", "Current Price", "Total Value", "Gain/Loss", "Gain/Loss %"])
    
    holdings = account.get_holdings()
    data = []
    for h in holdings:
        try:
            current_price = get_share_price(h.symbol)
        except:
            current_price = h.average_cost # Fallback
            
        total_value = h.quantity * current_price
        gain_loss = total_value - h.total_cost
        gain_loss_pct = (gain_loss / h.total_cost * 100) if h.total_cost > 0 else 0
        
        data.append({
            "Symbol": h.symbol,
            "Quantity": h.quantity,
            "Avg Cost": format_currency(h.average_cost),
            "Current Price": format_currency(current_price),
            "Total Value": format_currency(total_value),
            "Gain/Loss": format_currency(gain_loss),
            "Gain/Loss %": format_percentage(gain_loss_pct)
        })
    
    return pd.DataFrame(data)

def get_history_df(account: TradingAccount, type_filter: str, symbol_filter: str) -> pd.DataFrame:
    if not account:
        return pd.DataFrame(columns=["Date/Time", "Type", "Symbol", "Quantity", "Price", "Amount", "Balance"])
    
    transactions = account.get_transaction_history(type_filter, symbol_filter)
    data = []
    for t in transactions:
        data.append({
            "Date/Time": t.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "Type": t.type.value,
            "Symbol": t.symbol if t.symbol else "-",
            "Quantity": t.quantity if t.quantity else "-",
            "Price": format_currency(t.price) if t.price else "-",
            "Amount": format_currency(t.amount),
            "Balance": format_currency(t.balance_after)
        })
    return pd.DataFrame(data)

def get_portfolio_stats_md(account: TradingAccount) -> str:
    if not account:
        return "Please create an account."
    
    # Get current prices for all holdings
    current_prices = {}
    for h in account.holdings.values():
        try:
            current_prices[h.symbol] = get_share_price(h.symbol)
        except:
            pass
            
    summary = account.get_portfolio_summary(current_prices)
    
    color = "green" if summary.total_profit_loss >= 0 else "red"
    arrow = "↑" if summary.total_profit_loss >= 0 else "↓"
    
    return f"""
    ### Overall Performance
    - **Total Capital Invested:** {format_currency(summary.total_invested)}
    - **Current Portfolio Value:** {format_currency(summary.total_portfolio_value)}
    - **Total Cash:** {format_currency(summary.total_cash)}
    - **Profit/Loss:** <span style='color:{color}'>{format_currency(summary.total_profit_loss)} ({format_percentage(summary.total_profit_loss_percentage)}) {arrow}</span>
    """

# --- Event Handlers ---

def on_create_account(username, deposit):
    res = create_account_service(username, deposit)
    if res["success"]:
        account = res["data"]
        gr.Info(res["message"])
        # Return: 
        # 1. Account State
        # 2. Creation Group (visible=False)
        # 3. Dashboard Tabs (visible=True)
        # 4. Balance Display (Funds Tab)
        # 5. Available Cash (Trade Tab)
        # 6. Holdings Table
        # 7. Portfolio Stats
        # 8. History Table
        return (
            account,
            gr.Group(visible=False),
            gr.Tabs(visible=True),
            f"**Current Balance:** {format_currency(account.cash)}",
            f"**Available Cash:** {format_currency(account.cash)}",
            get_holdings_df(account),
            get_portfolio_stats_md(account),
            get_history_df(account, "All", "All")
        )
    else:
        raise gr.Error(res["message"])

def on_deposit(account, amount):
    res = deposit_service(account, amount)
    if res["success"]:
        gr.Info(res["message"])
        # Update balance displays and history
        return (
            account, # State update
            f"**Current Balance:** {format_currency(account.cash)}",
            f"**Available Cash:** {format_currency(account.cash)}",
            get_portfolio_stats_md(account),
            get_history_df(account, "All", "All")
        )
    else:
        raise gr.Error(res["message"])

def on_withdraw(account, amount):
    res = withdraw_service(account, amount)
    if res["success"]:
        gr.Info(res["message"])
        return (
            account,
            f"**Current Balance:** {format_currency(account.cash)}",
            f"**Available Cash:** {format_currency(account.cash)}",
            get_portfolio_stats_md(account),
            get_history_df(account, "All", "All")
        )
    else:
        raise gr.Error(res["message"])

def on_buy(account, symbol, qty):
    res = buy_stock_service(account, symbol, qty)
    if res["success"]:
        gr.Info(res["message"])
        return (
            account,
            f"**Current Balance:** {format_currency(account.cash)}",
            f"**Available Cash:** {format_currency(account.cash)}",
            get_holdings_df(account),
            get_portfolio_stats_md(account),
            get_history_df(account, "All", "All")
        )
    else:
        raise gr.Error(res["message"])

def on_sell(account, symbol, qty):
    res = sell_stock_service(account, symbol, qty)
    if res["success"]:
        gr.Info(res["message"])
        return (
            account,
            f"**Current Balance:** {format_currency(account.cash)}",
            f"**Available Cash:** {format_currency(account.cash)}",
            get_holdings_df(account),
            get_portfolio_stats_md(account),
            get_history_df(account, "All", "All")
        )
    else:
        raise gr.Error(res["message"])

def update_trade_totals(symbol, quantity):
    if not symbol:
        return "**Current Price:** Select a symbol", "**Total Cost:** $0.00"
    try:
        price = get_share_price(symbol)
        total = price * (quantity if quantity else 0)
        return f"**Current Price:** {format_currency(price)}/share", f"**Total Cost:** {format_currency(total)}"
    except:
        return "**Current Price:** N/A", "**Total Cost:** N/A"

def update_sell_totals(symbol, quantity):
    if not symbol:
        return "**Current Price:** Select a symbol", "**Sale Proceeds:** $0.00"
    try:
        price = get_share_price(symbol)
        total = price * (quantity if quantity else 0)
        return f"**Current Price:** {format_currency(price)}/share", f"**Sale Proceeds:** {format_currency(total)}"
    except:
        return "**Current Price:** N/A", "**Sale Proceeds:** N/A"

def refresh_portfolio(account):
    return get_holdings_df(account), get_portfolio_stats_md(account)

def refresh_history(account, type_filter, symbol_filter):
    return get_history_df(account, type_filter, symbol_filter)

def update_sell_choices(account):
    if not account:
        return gr.Dropdown(choices=[])
    choices = [f"{h.symbol}" for h in account.holdings.values()]
    return gr.Dropdown(choices=choices)

# --- UI Layout ---

with gr.Blocks(title="Trading Simulator") as app:
    account_state = gr.State(None)
    
    gr.Markdown("# 📈 Trading Simulation Platform")
    
    # Account Creation
    with gr.Group(visible=True) as account_creation_group:
        gr.Markdown("## Create Trading Account")
        with gr.Row():
            with gr.Column():
                username_input = gr.Textbox(label="Username", placeholder="Enter username (3-50 characters)")
                initial_deposit_input = gr.Number(label="Initial Deposit ($)", value=10000.00, minimum=0.01)
                create_btn = gr.Button("Create Account", variant="primary")
    
    # Dashboard
    with gr.Tabs(visible=False) as dashboard_tabs:
        
        # Funds Tab
        with gr.Tab("Funds"):
            gr.Markdown("## Funds Management")
            current_balance_display = gr.Markdown("**Current Balance:** $0.00")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Deposit")
                    deposit_amount = gr.Number(label="Deposit Amount ($)", minimum=0.01)
                    deposit_btn = gr.Button("Deposit Funds", variant="primary")
                
                with gr.Column():
                    gr.Markdown("### Withdraw")
                    withdraw_amount = gr.Number(label="Withdrawal Amount ($)", minimum=0.01)
                    withdraw_btn = gr.Button("Withdraw Funds", variant="secondary")

        # Trade Tab
        with gr.Tab("Trade"):
            gr.Markdown("## Trading Operations")
            available_cash_display = gr.Markdown("**Available Cash:** $0.00")
            
            with gr.Row():
                # Buy Column
                with gr.Column():
                    gr.Markdown("### Buy Shares")
                    buy_symbol = gr.Dropdown(label="Symbol", choices=SUPPORTED_SYMBOLS)
                    buy_qty = gr.Number(label="Quantity", minimum=1, precision=0)
                    buy_price_display = gr.Markdown("**Current Price:** Select a symbol")
                    buy_total_display = gr.Markdown("**Total Cost:** $0.00")
                    buy_btn = gr.Button("Buy Shares", variant="primary")
                
                # Sell Column
                with gr.Column():
                    gr.Markdown("### Sell Shares")
                    sell_symbol = gr.Dropdown(label="Symbol", choices=[]) # Populated dynamically
                    sell_qty = gr.Number(label="Quantity", minimum=1, precision=0)
                    sell_price_display = gr.Markdown("**Current Price:** Select a symbol")
                    sell_total_display = gr.Markdown("**Sale Proceeds:** $0.00")
                    sell_btn = gr.Button("Sell Shares", variant="secondary")

        # Portfolio Tab
        with gr.Tab("Portfolio"):
            gr.Markdown("## Portfolio Holdings")
            portfolio_stats = gr.Markdown("Loading...")
            refresh_holdings_btn = gr.Button("Refresh Prices", size="sm")
            holdings_table = gr.DataFrame(label="Current Holdings", interactive=False)
            
        # History Tab
        with gr.Tab("History"):
            gr.Markdown("## Transaction History")
            with gr.Row():
                type_filter = gr.Dropdown(label="Type", choices=["All", "Deposits", "Withdrawals", "Buys", "Sells"], value="All")
                symbol_filter = gr.Dropdown(label="Symbol", choices=["All"] + SUPPORTED_SYMBOLS, value="All")
            
            history_table = gr.DataFrame(label="Transactions", interactive=False)

    # --- Wiring ---
    
    # Create Account
    create_btn.click(
        on_create_account,
        inputs=[username_input, initial_deposit_input],
        outputs=[
            account_state, 
            account_creation_group, 
            dashboard_tabs, 
            current_balance_display,
            available_cash_display,
            holdings_table,
            portfolio_stats,
            history_table
        ]
    )
    
    # Deposit
    deposit_btn.click(
        on_deposit,
        inputs=[account_state, deposit_amount],
        outputs=[account_state, current_balance_display, available_cash_display, portfolio_stats, history_table]
    )
    
    # Withdraw
    withdraw_btn.click(
        on_withdraw,
        inputs=[account_state, withdraw_amount],
        outputs=[account_state, current_balance_display, available_cash_display, portfolio_stats, history_table]
    )
    
    # Buy Real-time updates
    buy_symbol.change(update_trade_totals, [buy_symbol, buy_qty], [buy_price_display, buy_total_display])
    buy_qty.change(update_trade_totals, [buy_symbol, buy_qty], [buy_price_display, buy_total_display])
    
    # Buy Action
    buy_btn.click(
        on_buy,
        inputs=[account_state, buy_symbol, buy_qty],
        outputs=[account_state, current_balance_display, available_cash_display, holdings_table, portfolio_stats, history_table]
    ).then(
        update_sell_choices, inputs=[account_state], outputs=[sell_symbol]
    )
    
    # Sell Real-time updates
    sell_symbol.change(update_sell_totals, [sell_symbol, sell_qty], [sell_price_display, sell_total_display])
    sell_qty.change(update_sell_totals, [sell_symbol, sell_qty], [sell_price_display, sell_total_display])
    
    # Sell Action
    sell_btn.click(
        on_sell,
        inputs=[account_state, sell_symbol, sell_qty],
        outputs=[account_state, current_balance_display, available_cash_display, holdings_table, portfolio_stats, history_table]
    ).then(
        update_sell_choices, inputs=[account_state], outputs=[sell_symbol]
    )
    
    # Refresh Portfolio
    refresh_holdings_btn.click(
        refresh_portfolio,
        inputs=[account_state],
        outputs=[holdings_table, portfolio_stats]
    )
    
    # Refresh History (on filter change)
    type_filter.change(refresh_history, [account_state, type_filter, symbol_filter], [history_table])
    symbol_filter.change(refresh_history, [account_state, type_filter, symbol_filter], [history_table])

if __name__ == "__main__":
    app.launch()
