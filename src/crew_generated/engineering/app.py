import gradio as gr
import pandas as pd
from typing import Tuple, Any, Callable

# Assuming trading_simulation.py is in the same directory
from trading_simulation import TradingSimulation

# Constants
STOCK_CHOICES = ["AAPL", "TSLA", "GOOGL"]
APP_TITLE = "Trading Simulation Platform"
APP_DESCRIPTION = """
Welcome to the Trading Simulation Platform.
1.  **Start** by entering an initial deposit on the 'Portfolio' tab and clicking 'Start Simulation'.
2.  **Manage** your portfolio by buying/selling shares on the 'Trade' tab.
3.  **Adjust** your cash using the 'Cash Management' tab.
4.  **Review** all your actions in the 'Transaction History' tab.
"""

# --- UI Update Helper Functions ---

def _format_metrics_for_display(account: TradingSimulation) -> Tuple[str, str, str]:
    """Formats raw portfolio metrics into display-ready strings."""
    metrics = account.get_portfolio_metrics()
    portfolio_val_str = f"${metrics.total_portfolio_value:,.2f}"
    pnl_str = f"${metrics.profit_loss:,.2f}"
    cash_bal_str = f"${metrics.cash_balance:,.2f}"
    return portfolio_val_str, pnl_str, cash_bal_str

def update_dashboard_views(account: TradingSimulation) -> Tuple[Any, ...]:
    """
    Retrieves all dynamic data from the simulation backend and returns it
    in a tuple formatted for Gradio component updates. This function is the
    single source of truth for refreshing the UI.
    """
    if not account.initialized:
        # If account isn't set up, return no-op updates for all components.
        empty_holdings = pd.DataFrame(columns=["Symbol", "Quantity", "Current Price", "Market Value"])
        empty_transactions = pd.DataFrame(columns=["Timestamp", "Type", "Symbol", "Quantity", "Price/Share", "Total Value"])
        return ("", "", "", empty_holdings, empty_transactions)

    portfolio_val, pnl, cash_bal = _format_metrics_for_display(account)
    holdings_df = account.get_holdings_df()
    transactions_df = account.get_transactions_df()

    return portfolio_val, pnl, cash_bal, holdings_df, transactions_df


# --- Event Handler Functions ---

def handle_initialize(
    account: TradingSimulation, initial_deposit: float
) -> Tuple[Any, ...]:
    """
    Event handler for the 'Start Simulation' button. Initializes the account,
    updates UI visibility and interactivity, and populates the dashboard.
    """
    if not initial_deposit or initial_deposit <= 0:
        gr.Error("Initial deposit must be a positive number.")
        # Return no-op updates for all outputs to prevent UI changes on error
        return (account,) + (gr.update(),) * 10

    response = account.initialize(initial_deposit)

    if response.success:
        gr.Info(response.message)
        # On success, change visibility and interactivity
        visibility_updates = (gr.Group(visible=False), gr.Group(visible=True))
        tab_updates = (
            gr.Tab(interactive=True),
            gr.Tab(interactive=True),
            gr.Tab(interactive=True),
        )
        dashboard_updates = update_dashboard_views(account)
        return (
            account,
            *visibility_updates,
            *tab_updates,
            *dashboard_updates,
        )
    else:
        gr.Error(response.message)
        # On failure, return no-op updates for all UI components
        return (account,) + (gr.update(),) * 10


def create_transaction_handler(
    action_func: Callable[..., Any]
) -> Callable[..., Any]:
    """
    Factory function to create generic event handlers for buy, sell, deposit,
    and withdraw actions. This reduces code duplication.
    """
    def handler(account: TradingSimulation, *args: Any) -> Tuple[Any, ...]:
        # Perform basic UI-side validation for numeric inputs
        numeric_args = [arg for arg in args if isinstance(arg, (int, float))]
        if any(arg is None or arg <= 0 for arg in numeric_args):
            gr.Warning("Please provide a valid, positive amount for the transaction.")
            dashboard_updates = update_dashboard_views(account)
            return (account, *dashboard_updates)

        # Call the specific backend action (e.g., account.buy_shares)
        response = action_func(account, *args)

        # Display the result message from the backend
        if response.success:
            gr.Info(response.message)
        else:
            gr.Error(response.message)

        # Refresh all dashboard components with the latest state
        dashboard_updates = update_dashboard_views(account)
        return (account, *dashboard_updates)

    return handler


# --- Gradio UI Layout ---

def create_ui() -> gr.Blocks:
    """Builds and returns the Gradio UI application."""
    with gr.Blocks(title=APP_TITLE, theme=gr.themes.Soft(primary_hue="blue")) as demo:
        # The gr.State component holds the single source of truth: the TradingSimulation instance.
        account_state = gr.State(value=TradingSimulation())

        gr.Markdown(f"# {APP_TITLE}")
        gr.Markdown(APP_DESCRIPTION)

        with gr.Tabs() as tabs:
            with gr.Tab("Portfolio", id=0):
                # US-001: Initial Setup UI (visible by default)
                with gr.Group(visible=True) as initial_setup_group:
                    gr.Markdown("## 1. Start Your Simulation")
                    with gr.Row():
                        initial_deposit_input = gr.Number(
                            label="Initial Deposit", value=100000.00, minimum=0.01,
                            info="Enter the amount of cash to start with."
                        )
                        start_sim_button = gr.Button(
                            "Start Simulation", variant="primary", scale=0
                        )

                # US-001: Portfolio Overview UI (hidden by default)
                with gr.Group(visible=False) as portfolio_overview_group:
                    gr.Markdown("### Key Metrics")
                    with gr.Row():
                        portfolio_val_txt = gr.Textbox(label="Total Portfolio Value", interactive=False)
                        pnl_txt = gr.Textbox(label="Profit / Loss", interactive=False)
                        cash_bal_txt = gr.Textbox(label="Cash Balance", interactive=False)
                    gr.Markdown("### Current Holdings")
                    holdings_df = gr.DataFrame(
                        headers=["Symbol", "Quantity", "Current Price", "Market Value"],
                        interactive=False,
                        row_count=(5, "dynamic"),
                        col_count=(4, "fixed")
                    )

            with gr.Tab("Trade", id=1, interactive=False) as trade_tab:
                # US-003: Trade Execution UI
                gr.Markdown("## Execute a Trade")
                with gr.Row():
                    with gr.Column(scale=2):
                        trade_symbol_dd = gr.Dropdown(
                            STOCK_CHOICES, label="Symbol", value="AAPL"
                        )
                        trade_qty_num = gr.Number(
                            label="Quantity", minimum=1, step=1, precision=0, value=1
                        )
                    with gr.Column(scale=1, min_width=200):
                        gr.Markdown("&nbsp;") # For alignment
                        buy_button = gr.Button("Buy", variant="primary")
                        sell_button = gr.Button("Sell", variant="stop")


            with gr.Tab("Cash Management", id=2, interactive=False) as cash_management_tab:
                # US-002: Cash Management UI
                gr.Markdown("## Manage Your Cash Balance")
                with gr.Row(equal_height=True):
                    with gr.Column():
                        gr.Markdown("### Deposit Funds")
                        deposit_amount_num = gr.Number(label="Deposit Amount", minimum=0.01)
                        deposit_button = gr.Button("Deposit", variant="primary")
                    with gr.Column():
                        gr.Markdown("### Withdraw Funds")
                        withdraw_amount_num = gr.Number(label="Withdrawal Amount", minimum=0.01)
                        withdraw_button = gr.Button("Withdraw", variant="stop")

            with gr.Tab("Transaction History", id=3, interactive=False) as history_tab:
                # US-004: Transaction History UI
                gr.Markdown("## Transaction History")
                transactions_df = gr.DataFrame(
                    headers=["Timestamp", "Type", "Symbol", "Quantity", "Price/Share", "Total Value"],
                    interactive=False,
                    row_count=(10, "dynamic"),
                    col_count=(6, "fixed")
                )

        # --- Event Handling Wiring ---

        # Define the list of outputs that are updated by most transactions
        dashboard_outputs = [
            portfolio_val_txt,
            pnl_txt,
            cash_bal_txt,
            holdings_df,
            transactions_df,
        ]

        # 1. Initialization Event
        start_sim_button.click(
            fn=handle_initialize,
            inputs=[account_state, initial_deposit_input],
            outputs=[
                account_state,
                initial_setup_group,
                portfolio_overview_group,
                trade_tab,
                cash_management_tab,
                history_tab,
                *dashboard_outputs,
            ],
        )

        # 2. Trading Events (Buy/Sell)
        buy_button.click(
            fn=create_transaction_handler(lambda acc, sym, qty: acc.buy_shares(sym, qty)),
            inputs=[account_state, trade_symbol_dd, trade_qty_num],
            outputs=[account_state, *dashboard_outputs],
        )
        sell_button.click(
            fn=create_transaction_handler(lambda acc, sym, qty: acc.sell_shares(sym, qty)),
            inputs=[account_state, trade_symbol_dd, trade_qty_num],
            outputs=[account_state, *dashboard_outputs],
        )

        # 3. Cash Management Events (Deposit/Withdraw)
        deposit_button.click(
            fn=create_transaction_handler(lambda acc, amt: acc.deposit(amt)),
            inputs=[account_state, deposit_amount_num],
            outputs=[account_state, *dashboard_outputs],
        )
        withdraw_button.click(
            fn=create_transaction_handler(lambda acc, amt: acc.withdraw(amt)),
            inputs=[account_state, withdraw_amount_num],
            outputs=[account_state, *dashboard_outputs],
        )

    return demo


if __name__ == "__main__":
    app = create_ui()
    app.launch()