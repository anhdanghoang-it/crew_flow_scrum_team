import gradio as gr
import inspect
import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_SYMBOLS = ["AAPL", "TSLA", "GOOGL"]


def _locate_backend_file() -> Path:
    current_dir = Path(__file__).parent
    candidates = [
        path for path in current_dir.glob("*.py")
        if path.name not in {"app.py", "__init__.py"}
    ]
    if not candidates:
        raise ImportError("No backend module found alongside app.py.")
    prioritized = sorted(candidates, key=lambda p: (0 if "backend" in p.stem.lower() else 1, p.name))
    return prioritized[0]


def _detect_backend_class(module: Any) -> type:
    classes: List[Tuple[str, type]] = []
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ != module.__name__:
            continue
        if name.startswith("_"):
            continue
        if issubclass(obj, Exception):
            continue
        bases = {base.__name__ for base in inspect.getmro(obj)}
        if "BaseModel" in bases:
            continue
        classes.append((name, obj))
    if not classes:
        raise ImportError("No usable backend class detected in module.")
    backend_named = [cls for name, cls in classes if name.lower().endswith("backend")]
    if backend_named:
        return backend_named[0]
    return classes[0][1]


def _load_backend() -> Any:
    backend_path = _locate_backend_file()
    module_name = backend_path.stem
    spec = importlib.util.spec_from_file_location(module_name, backend_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load backend module from {backend_path}.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    backend_class = _detect_backend_class(module)
    return backend_class()


def _resolve_symbols(candidate: Any) -> List[str]:
    if callable(candidate):
        try:
            resolved = list(candidate())
            return sorted({symbol.upper() for symbol in resolved if isinstance(symbol, str)}) or DEFAULT_SYMBOLS
        except Exception:
            return DEFAULT_SYMBOLS
    return DEFAULT_SYMBOLS


backend = _load_backend()
SYMBOL_CHOICES = _resolve_symbols(getattr(backend, "supported_symbols", None))


def _account_status_text(account_id: str) -> str:
    if not account_id:
        return "**Active account:** _none selected_. Use the Create tab to get started."
    return f"**Active account ID:** `{account_id}`"


def _need_account(account_id: str) -> Optional[str]:
    if account_id:
        return None
    gr.Warning("Please create or select an account first.")
    return "Please create or select an account first."


def _render_portfolio(resp: Any, headline: Optional[str] = None) -> Tuple[Any, Any, Any, Any, Any]:
    if resp is None:
        return (
            "Unable to load portfolio.",
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
        )
    if not getattr(resp, "success", False):
        gr.Error(resp.message)
        return (
            resp.message,
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
        )
    data: Dict[str, Any] = resp.data or {}
    rows = data.get("holdings_table", [])
    cash = data.get("cash_balance", 0.0)
    holdings_value = data.get("total_holdings_value", 0.0)
    total_value = data.get("total_portfolio_value", cash + holdings_value)
    warning_text = data.get("warning", "")
    message = headline or resp.message
    warning = gr.update(value=f"⚠️ {warning_text}" if warning_text else "", visible=bool(warning_text))
    return (
        message,
        rows,
        f"**Cash balance:** ${cash:,.2f}",
        f"**Holdings value:** ${holdings_value:,.2f} | **Portfolio value:** ${total_value:,.2f}",
        warning,
    )


def _render_profit_loss(resp: Any) -> Any:
    if resp is None:
        return gr.update()
    if not getattr(resp, "success", False):
        gr.Error(resp.message)
        return resp.message
    data: Dict[str, Any] = resp.data or {}
    status = data.get("status", "Status unavailable")
    color_map = {
        "Profit": "#16a34a",
        "Loss": "#dc2626",
        "Break-even": "#2563eb",
        "NO_BASELINE": "#475569",
    }
    color = color_map.get(status, "#2563eb")
    display_value = data.get("display")
    profit_loss = data.get("profit_loss")
    if display_value is None and profit_loss is not None:
        display_value = f"${profit_loss:,.2f}"
    if display_value is None:
        display_value = "N/A"
    baseline = data.get("baseline")
    baseline_text = "N/A" if baseline is None else f"${baseline:,.2f}"
    total_value = data.get("total_portfolio_value")
    total_text = "N/A" if total_value is None else f"${total_value:,.2f}"
    return (
        f"**Status:** {status}\n\n"
        f"**Profit / Loss:** <span style='color:{color}; font-weight:600;'>{display_value}</span>\n\n"
        f"**Initial deposits:** {baseline_text}\n\n"
        f"**Total portfolio value:** {total_text}"
    )


def _portfolio_no_change(message: str) -> Tuple[Any, Any, Any, Any, Any]:
    return (
        message,
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
    )


def _portfolio_and_pl(account_id: str, headline: Optional[str] = None) -> Tuple[Any, Any, Any, Any, Any, Any]:
    missing = _need_account(account_id)
    if missing:
        return (
            missing,
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
        )
    portfolio_resp = backend.portfolio(account_id)
    portfolio_outputs = _render_portfolio(portfolio_resp, headline)
    pl_resp = backend.profit_loss(account_id)
    pl_output = _render_profit_loss(pl_resp)
    return (*portfolio_outputs, pl_output)


def handle_create_account(username: str, display_name: str) -> Tuple[Any, Any, str, str, Any, Any, Any, Any, Any, Any]:
    resp = backend.create_account(username or "", display_name or "")
    data = resp.data or {}
    account = data.get("account", {})
    account_id = account.get("account_id", "")
    if resp.success and account_id:
        gr.Info(resp.message)
        portfolio_resp = backend.portfolio(account_id)
        portfolio_outputs = _render_portfolio(portfolio_resp, resp.message)
        pl_output = _render_profit_loss(backend.profit_loss(account_id))
        return (
            resp.message,
            account,
            account_id,
            _account_status_text(account_id),
            *portfolio_outputs,
            pl_output,
        )
    gr.Error(resp.message)
    return (
        resp.message,
        account,
        account_id,
        _account_status_text(account_id),
        *_portfolio_no_change(resp.message),
        gr.update(),
    )


def handle_deposit(account_id: str, amount: float) -> Tuple[Any, Any, Any, Any, Any, Any]:
    missing = _need_account(account_id)
    if missing:
        return (
            missing,
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
        )
    resp = backend.deposit(account_id, amount)
    if resp.success:
        gr.Info(resp.message)
        return _portfolio_and_pl(account_id, resp.message)
    gr.Error(resp.message)
    return (
        resp.message,
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
    )


def handle_withdraw(account_id: str, amount: float) -> Tuple[Any, Any, Any, Any, Any, Any]:
    missing = _need_account(account_id)
    if missing:
        return (
            missing,
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
        )
    resp = backend.withdraw(account_id, amount)
    if resp.success:
        gr.Info(resp.message)
        return _portfolio_and_pl(account_id, resp.message)
    gr.Error(resp.message)
    return (
        resp.message,
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
    )


def handle_refresh_portfolio(account_id: str) -> Tuple[Any, Any, Any, Any, Any, Any]:
    return _portfolio_and_pl(account_id)


def handle_refresh_pl(account_id: str) -> Any:
    missing = _need_account(account_id)
    if missing:
        return gr.update()
    return _render_profit_loss(backend.profit_loss(account_id))


def _holdings_text(account_id: str, symbol: str) -> str:
    if not account_id:
        return "Account selection required to view holdings."
    resp = backend.portfolio(account_id)
    if not getattr(resp, "success", False):
        return "Unable to load holdings." if not resp.success else resp.message
    rows = resp.data.get("holdings_table", []) if resp.data else []
    for row in rows:
        if str(row.get("Symbol", "")).upper() == symbol.upper():
            qty = row.get("Quantity", 0)
            return f"You currently hold {qty} shares of {symbol}."
    return f"You do not hold any shares of {symbol} yet."


def handle_price_preview(account_id: str, symbol: str, quantity: float) -> Tuple[str, str, str]:
    clean_symbol = (symbol or "").upper().strip()
    if not clean_symbol:
        gr.Warning("Symbol is required for price lookup.")
        return ("Enter a symbol to preview pricing.", "Estimated total cost will appear here.", "")
    resp = backend.share_price(clean_symbol)
    if not getattr(resp, "success", False):
        gr.Error(resp.message)
        return (resp.message, "Estimated total cost unavailable.", "")
    price = resp.data.get("price", 0.0) if resp.data else 0.0
    qty = int(quantity) if quantity and quantity > 0 else None
    estimate = price * qty if qty else 0.0
    estimate_text = (
        f"Estimated total for {qty} {clean_symbol}: ${estimate:,.2f}"
        if qty
        else "Enter a positive quantity to see estimated total."
    )
    holdings_text = _holdings_text(account_id, clean_symbol) if account_id else "Select an account to view holdings context."
    return (f"Current price for {clean_symbol}: ${price:,.2f}", estimate_text, holdings_text)


def _handle_trade(account_id: str, symbol: str, quantity: float, action: str) -> Tuple[Any, Any, Any, Any, Any, Any, Any, Any]:
    clean_symbol = (symbol or "").upper().strip()
    missing = _need_account(account_id)
    if missing:
        return (
            missing,
            None,
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
        )
    if not clean_symbol:
        gr.Warning("Symbol is required.")
        return (
            "Symbol is required.",
            None,
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
        )
    method = getattr(backend, action)
    resp = method(account_id, clean_symbol, quantity)
    if resp.success:
        gr.Info(resp.message)
        portfolio_outputs = _portfolio_and_pl(account_id, resp.message)
        return (
            resp.message,
            resp.data,
            *portfolio_outputs,
        )
    gr.Error(resp.message)
    return (
        resp.message,
        resp.data,
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
    )


def handle_buy(account_id: str, symbol: str, quantity: float) -> Tuple[Any, Any, Any, Any, Any, Any, Any, Any]:
    return _handle_trade(account_id, symbol, quantity, "buy")


def handle_sell(account_id: str, symbol: str, quantity: float) -> Tuple[Any, Any, Any, Any, Any, Any, Any, Any]:
    return _handle_trade(account_id, symbol, quantity, "sell")


def handle_snapshot_options(account_id: str) -> Tuple[Any, str]:
    missing = _need_account(account_id)
    if missing:
        return gr.update(), missing
    resp = backend.snapshot_options(account_id)
    if not getattr(resp, "success", False):
        gr.Error(resp.message)
        return gr.update(), resp.message
    timestamps = resp.data.get("timestamps", []) if resp.data else []
    choices = [item.get("value") for item in timestamps if item.get("value")]
    dropdown_value = choices[0] if choices else None
    return gr.update(choices=choices, value=dropdown_value), (resp.message if choices else "No transactions available for snapshots yet.")


def handle_snapshot_view(account_id: str, timestamp_value: str) -> Tuple[Any, str, str, Any]:
    missing = _need_account(account_id)
    if missing:
        return gr.update(), missing, missing, gr.update()
    if not timestamp_value:
        gr.Warning("Select a timestamp before viewing a snapshot.")
        return gr.update(), "Select a timestamp before viewing a snapshot.", "", gr.update()
    resp = backend.snapshot(account_id, timestamp_value)
    if not getattr(resp, "success", False):
        gr.Error(resp.message)
        return gr.update(), resp.message, resp.message, gr.update()
    data = resp.data or {}
    cash = data.get("cash_balance", 0.0)
    holdings_value = data.get("total_holdings_value", 0.0)
    total_value = data.get("total_portfolio_value", cash + holdings_value)
    baseline = data.get("baseline")
    profit_loss = data.get("profit_loss")
    status = data.get("status", "Status")
    warning = data.get("warning", "")
    summary = (
        f"**Timestamp:** {data.get('timestamp', timestamp_value)}\n\n"
        f"**Cash balance:** ${cash:,.2f}\n\n"
        f"**Holdings value:** ${holdings_value:,.2f}\n\n"
        f"**Total portfolio value:** ${total_value:,.2f}\n\n"
        f"**Baseline deposits:** {('N/A' if baseline is None else f'${baseline:,.2f}')}\n\n"
        f"**Profit/Loss:** {('N/A' if profit_loss is None else f'${profit_loss:,.2f}')} ({status})"
    )
    warning_update = gr.update(value=f"⚠️ {warning}" if warning else "", visible=bool(warning))
    return (data.get("holdings_table", []), summary, resp.message, warning_update)


def handle_transactions(account_id: str, tx_type: str, symbol: str) -> Tuple[Any, str]:
    missing = _need_account(account_id)
    if missing:
        return gr.update(), missing
    resp = backend.transactions(account_id, tx_type, symbol)
    if not getattr(resp, "success", False):
        gr.Error(resp.message)
        return gr.update(), resp.message
    rows = resp.data.get("transactions", []) if resp.data else []
    return rows, resp.message


with gr.Blocks(title="Trading Simulation Control Center", theme=gr.themes.Soft()) as app:
    account_state = gr.State("")
    gr.Markdown("# Trading Simulation Control Center")
    gr.Markdown(
        "Manage account creation, cash movements, trades, and history from a single interface. "
        "Each action validates inputs before touching the backend so you always see clear feedback."
    )
    account_status_md = gr.Markdown(_account_status_text(""))

    with gr.Tabs():
        with gr.Tab("Create Account"):
            gr.Markdown("Provide a unique username and optional display name to start trading.")
            username_tb = gr.Textbox(label="Username", placeholder="Enter a unique username", lines=1)
            display_tb = gr.Textbox(label="Display name", placeholder="Enter a display name (optional)", lines=1)
            create_btn = gr.Button("Create Account", variant="primary")
            create_msg = gr.Markdown("Status updates will appear here.")
            account_json = gr.JSON(label="New account details", value={})
            gr.Examples(
                examples=[["alex_trader", "Alex"], ["quantum_lee", "Lee"]],
                inputs=[username_tb, display_tb],
                label="Example usernames",
            )

        with gr.Tab("Account Overview"):
            gr.Markdown("Track balances, holdings, and performance. Deposit or withdraw cash as needed.")
            with gr.Row():
                with gr.Column():
                    deposit_amount = gr.Number(
                        label="Deposit amount",
                        minimum=0,
                        value=0,
                        info="Enter amount to deposit",
                    )
                    deposit_btn = gr.Button("Deposit", variant="primary")
                    gr.Examples(examples=[[500], [2500]], inputs=[deposit_amount], label="Deposit examples")
                with gr.Column():
                    withdraw_amount = gr.Number(
                        label="Withdrawal amount",
                        minimum=0,
                        value=0,
                        info="Enter amount to withdraw",
                    )
                    withdraw_btn = gr.Button("Withdraw", variant="secondary")
                    gr.Examples(examples=[[100], [750]], inputs=[withdraw_amount], label="Withdrawal examples")
            refresh_portfolio_btn = gr.Button("Refresh Portfolio", variant="secondary")
            refresh_pl_btn = gr.Button("Refresh Profit / Loss", variant="secondary")
            portfolio_msg = gr.Markdown("Portfolio insights will appear here once you load an account.")
            holdings_df = gr.Dataframe(
                headers=["Symbol", "Quantity", "Current price", "Market value"],
                datatype=["str", "number", "str", "str"],
                row_count=(0, "dynamic"),
                label="Current holdings",
                value=[],
                interactive=False,
            )
            cash_md = gr.Markdown("**Cash balance:** $0.00")
            totals_md = gr.Markdown("**Holdings value:** $0.00 | **Portfolio value:** $0.00")
            portfolio_warning_md = gr.Markdown("", visible=False)
            pl_md = gr.Markdown("Profit / loss will appear here once you deposit funds.")

        with gr.Tab("Trade"):
            gr.Markdown("Buy or sell supported symbols with affordability and holdings checks built-in.")
            trade_symbol = gr.Dropdown(
                choices=SYMBOL_CHOICES,
                value=SYMBOL_CHOICES[0] if SYMBOL_CHOICES else None,
                label="Symbol",
                info="Select or type a supported ticker",
                allow_custom_value=True,
            )
            trade_quantity = gr.Number(
                label="Quantity",
                value=1,
                minimum=1,
                precision=0,
                info="Enter number of shares",
            )
            preview_btn = gr.Button("Check Price & Estimate", variant="secondary")
            with gr.Row():
                buy_btn = gr.Button("Buy", variant="primary")
                sell_btn = gr.Button("Sell", variant="secondary")
            price_md = gr.Markdown("Price preview will show here.")
            estimate_md = gr.Markdown("Estimated total appears here.")
            holding_md = gr.Markdown("Holdings context appears here.")
            trade_msg = gr.Markdown("Trade confirmations will appear here.")
            trade_json = gr.JSON(label="Most recent trade payload", value={})
            gr.Examples(
                examples=[["AAPL", 5], ["TSLA", 2]],
                inputs=[trade_symbol, trade_quantity],
                label="Trade examples",
            )

        with gr.Tab("History Snapshot"):
            gr.Markdown("Reconstruct portfolio state at any recorded timestamp.")
            snapshot_refresh_btn = gr.Button("Load Snapshot Timestamps")
            snapshot_dropdown = gr.Dropdown(
                choices=[],
                label="Select timestamp",
                info="Timestamps populate from your transaction history",
            )
            snapshot_view_btn = gr.Button("View Snapshot", variant="primary")
            snapshot_message_md = gr.Markdown("Load timestamps to begin.")
            snapshot_table = gr.Dataframe(
                headers=["Symbol", "Quantity", "Current price", "Market value"],
                datatype=["str", "number", "str", "str"],
                row_count=(0, "dynamic"),
                label="Snapshot holdings",
                value=[],
                interactive=False,
            )
            snapshot_summary_md = gr.Markdown("Snapshot summary will appear here.")
            snapshot_warning_md = gr.Markdown("", visible=False)

        with gr.Tab("Transactions"):
            gr.Markdown("Filter and review the complete transaction log.")
            tx_type_filter = gr.Dropdown(
                choices=["ALL", "DEPOSIT", "WITHDRAWAL", "BUY", "SELL"],
                value="ALL",
                label="Type filter",
            )
            symbol_filter = gr.Dropdown(
                choices=["ALL"] + SYMBOL_CHOICES,
                value="ALL",
                label="Symbol filter",
                allow_custom_value=True,
            )
            transactions_btn = gr.Button("Apply Filters", variant="primary")
            tx_message_md = gr.Markdown("Filtered transactions will appear here.")
            transactions_df = gr.Dataframe(
                headers=["Timestamp", "Type", "Symbol", "Quantity", "Amount", "Resulting cash balance"],
                datatype=["str", "str", "str", "str", "number", "number"],
                row_count=(0, "dynamic"),
                label="Transactions",
                value=[],
                interactive=False,
            )

    with gr.Accordion("Quick Demo", open=False):
        gr.Markdown(
            "1. Create a new account with the first tab.\n"
            "2. Deposit sample funds, then refresh the portfolio.\n"
            "3. Use the Trade tab to buy or sell supported symbols.\n"
            "4. Explore snapshots and transaction history to audit activity."
        )

    create_btn.click(
        handle_create_account,
        inputs=[username_tb, display_tb],
        outputs=[
            create_msg,
            account_json,
            account_state,
            account_status_md,
            portfolio_msg,
            holdings_df,
            cash_md,
            totals_md,
            portfolio_warning_md,
            pl_md,
        ],
    )
    deposit_btn.click(
        handle_deposit,
        inputs=[account_state, deposit_amount],
        outputs=[portfolio_msg, holdings_df, cash_md, totals_md, portfolio_warning_md, pl_md],
    )
    withdraw_btn.click(
        handle_withdraw,
        inputs=[account_state, withdraw_amount],
        outputs=[portfolio_msg, holdings_df, cash_md, totals_md, portfolio_warning_md, pl_md],
    )
    refresh_portfolio_btn.click(
        handle_refresh_portfolio,
        inputs=[account_state],
        outputs=[portfolio_msg, holdings_df, cash_md, totals_md, portfolio_warning_md, pl_md],
    )
    refresh_pl_btn.click(
        handle_refresh_pl,
        inputs=[account_state],
        outputs=[pl_md],
    )
    preview_btn.click(
        handle_price_preview,
        inputs=[account_state, trade_symbol, trade_quantity],
        outputs=[price_md, estimate_md, holding_md],
    )
    buy_btn.click(
        handle_buy,
        inputs=[account_state, trade_symbol, trade_quantity],
        outputs=[
            trade_msg,
            trade_json,
            portfolio_msg,
            holdings_df,
            cash_md,
            totals_md,
            portfolio_warning_md,
            pl_md,
        ],
    )
    sell_btn.click(
        handle_sell,
        inputs=[account_state, trade_symbol, trade_quantity],
        outputs=[
            trade_msg,
            trade_json,
            portfolio_msg,
            holdings_df,
            cash_md,
            totals_md,
            portfolio_warning_md,
            pl_md,
        ],
    )
    snapshot_refresh_btn.click(
        handle_snapshot_options,
        inputs=[account_state],
        outputs=[snapshot_dropdown, snapshot_message_md],
    )
    snapshot_view_btn.click(
        handle_snapshot_view,
        inputs=[account_state, snapshot_dropdown],
        outputs=[snapshot_table, snapshot_summary_md, snapshot_message_md, snapshot_warning_md],
    )
    transactions_btn.click(
        handle_transactions,
        inputs=[account_state, tx_type_filter, symbol_filter],
        outputs=[transactions_df, tx_message_md],
    )


if __name__ == "__main__":
    app.launch()
