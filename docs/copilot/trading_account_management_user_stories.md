# Trading Account Management User Stories

## Overview
Feature: Account management for a trading simulation platform — create account, deposit/withdraw funds, record buy/sell transactions, report holdings, portfolio value, and profit/loss over time. Uses `get_share_price(symbol)` with fixed prices for AAPL, TSLA, GOOGL in test implementation.

---

## US-001: Account Creation
- As a new user, I want to create an account so that I can start managing funds and trading.
- Business value: High
- Priority: High
- Estimation guidance: 3-5 story points

### Acceptance Criteria (BDD)
- Given the app is open, when I enter a valid username and click "Create Account", then I see a success message `Account created for <username>.` and an empty dashboard (balance `0.00`, holdings empty, transactions empty).
- Given no username is provided, when I click "Create Account", then I see an error `Username is required.` and the account is not created.
- Given an account already exists, when I attempt to create another account with the same username, then I see an error `Account already exists.` and no changes occur.

### Validation Rules
- Username: non-empty string, trimmed; 1–50 chars; alphanumeric, underscore, hyphen; reject duplicates.

### UI/UX Specifications (Gradio)
- Layout: Blocks → Column
  - `gr.Textbox` id `username_input` label `Username` placeholder `Enter a username`
  - `gr.Button` id `create_account_btn` value `Create Account`
  - `gr.Markdown` id `account_summary_md` shows balance and status after creation
  - Feedback:
    - Success: `gr.Info("Account created for <username>.")`
    - Error: `gr.Error("Username is required.")` or `gr.Error("Account already exists.")`
- Accessibility: Textbox has ARIA label; button focusable; keyboard Enter triggers create.
- Responsive: Components stack vertically; labels wrap.

### Technical Notes
- Create in-memory account object with fields: `username`, `initial_deposit=0`, `balance=0`, `holdings={}`, `transactions=[]`.
- Dependency: None.
- Performance: Instant action (<100ms).

### Definition of Done
- Create account flow works; validations enforced; UI feedback renders consistently; unit tests and e2e cover success and errors.

### Out of Scope
- Multi-user tenancy; persistent storage; authentication.

---

## US-002: Deposit Funds
- As an account holder, I want to deposit funds so that I can trade.
- Business value: High
- Priority: High
- Estimation guidance: 3-5 story points

### Acceptance Criteria (BDD)
- Given an existing account, when I enter a positive numeric amount and click `Deposit`, then my balance increases by that amount and I see `Deposited <amount>. New balance: <balance>.`
- Given zero amount, when I click `Deposit`, then I see `Amount must be greater than 0.` and balance does not change.
- Given negative amount, when I click `Deposit`, then I see `Amount must be greater than 0.`
- Given non-numeric input, when I click `Deposit`, then I see `Amount must be a valid number.`

### Validation Rules
- Amount: number > 0; max 1e9 for test boundary; 2 decimal precision.

### UI/UX Specifications (Gradio)
- Layout: Row under account summary
  - `gr.Number` id `deposit_amount` label `Deposit Amount` precision=2
  - `gr.Button` id `deposit_btn` value `Deposit`
  - Feedback:
    - Success: `gr.Info("Deposited <amount>. New balance: <balance>.")`
    - Error: `gr.Error("Amount must be greater than 0.")`, `gr.Error("Amount must be a valid number.")`
- Accessibility: Number input supports keyboard; button actionable via Enter.

### Technical Notes
- Update `balance += amount`; if `initial_deposit` is 0, optionally set `initial_deposit += amount` to track initial baseline for P/L (see US-006).
- Performance: <100ms.

### Definition of Done
- Validations and balance updates correct; messages clear; tests cover edge cases.

### Out of Scope
- External payment integration.

---

## US-003: Withdraw Funds
- As an account holder, I want to withdraw funds so that I can move money out without creating negative balances.
- Business value: High
- Priority: High
- Estimation guidance: 5-8 story points

### Acceptance Criteria (BDD)
- Given current balance ≥ requested amount, when I withdraw a positive numeric amount, then balance decreases and I see `Withdrew <amount>. New balance: <balance>.`
- Given zero or negative amount, when I withdraw, then I see `Amount must be greater than 0.`
- Given non-numeric input, then I see `Amount must be a valid number.`
- Given requested amount > available balance (consider reserved buying power if applicable), then I see `Insufficient funds. Available balance: <balance>.` and no change.

### Validation Rules
- Amount: number > 0; cannot exceed `balance`.

### UI/UX Specifications (Gradio)
- Layout: Row
  - `gr.Number` id `withdraw_amount` label `Withdraw Amount` precision=2
  - `gr.Button` id `withdraw_btn` value `Withdraw`
  - Feedback:
    - Success: `gr.Info("Withdrew <amount>. New balance: <balance>.")`
    - Error: `gr.Error("Insufficient funds. Available balance: <balance>.")`, `gr.Error("Amount must be greater than 0.")`, `gr.Error("Amount must be a valid number.")`

### Technical Notes
- Update `balance -= amount` only if `amount <= balance`.

### Definition of Done
- Cannot go negative; clear messages; tests cover boundary.

### Out of Scope
- Fees, overdrafts, holds.

---

## US-004: Record Buy Transactions
- As an account holder, I want to buy shares by recording symbol and quantity so that holdings reflect my purchases and cash decreases accordingly.
- Business value: High
- Priority: High
- Estimation guidance: 8-13 story points

### Acceptance Criteria (BDD)
- Given a valid `symbol` and `quantity > 0`, when I click `Buy`, then the system calls `get_share_price(symbol)`, calculates `cost = price * quantity`, ensures sufficient `balance >= cost`, decreases `balance` by `cost`, updates holdings `{symbol: prev_qty + quantity, avg_cost updated}`, logs transaction, and shows `Bought <quantity> <symbol> at <price>. Cost: <cost>. New balance: <balance>.`
- Given insufficient balance, when I click `Buy`, then I see `Insufficient funds to buy <quantity> <symbol>. Required: <cost>, Available: <balance>.`
- Given non-numeric or non-positive quantity, I see `Quantity must be a positive number.`
- Given unsupported symbol, I see `Unknown symbol: <symbol>.`

### Validation Rules
- `symbol` in {AAPL, TSLA, GOOGL} for test; case-insensitive mapping.
- `quantity`: number > 0; up to 1e6.

### UI/UX Specifications (Gradio)
- Layout: Row
  - `gr.Dropdown` id `buy_symbol` label `Buy Symbol` choices `["AAPL", "TSLA", "GOOGL"]`
  - `gr.Number` id `buy_quantity` label `Quantity` precision=0
  - `gr.Button` id `buy_btn` value `Buy`
  - Feedback:
    - Success: `gr.Info("Bought <quantity> <symbol> at <price>. Cost: <cost>. New balance: <balance>.")`
    - Error: `gr.Error("Insufficient funds to buy <quantity> <symbol>. Required: <cost>, Available: <balance>.")`, `gr.Error("Quantity must be a positive number.")`, `gr.Error("Unknown symbol: <symbol>.")`

### Technical Notes
- Use `get_share_price(symbol)`; maintain `holdings[symbol] = {quantity, avg_cost}`. For avg cost: `new_avg = (old_avg*old_qty + price*qty)/(old_qty+qty)`.
- Log transaction: `{type: "BUY", symbol, quantity, price, timestamp}`.

### Definition of Done
- Balance decreases correctly; holdings update; transaction recorded; messages accurate.

### Out of Scope
- Order types, fees, partial fills, market slippage.

---

## US-005: Record Sell Transactions
- As an account holder, I want to sell shares so that I can realize cash proceeds and update holdings accordingly, preventing short sales.
- Business value: High
- Priority: High
- Estimation guidance: 8-13 story points

### Acceptance Criteria (BDD)
- Given `quantity > 0` and `holdings[symbol] >= quantity`, when I click `Sell`, then `price = get_share_price(symbol)`, `proceeds = price*quantity`, `balance += proceeds`, `holdings[symbol] -= quantity` (if 0, remove), log transaction, and show `Sold <quantity> <symbol> at <price>. Proceeds: <proceeds>. New balance: <balance>.`
- Given attempting to sell more than held, I see `Insufficient shares to sell. Held: <held_qty>, Requested: <quantity>.`
- Given non-numeric or non-positive quantity, I see `Quantity must be a positive number.`
- Given unknown symbol, I see `Unknown symbol: <symbol>.`

### Validation Rules
- `symbol` in {AAPL, TSLA, GOOGL}; `quantity > 0`; must not exceed holdings.

### UI/UX Specifications (Gradio)
- Layout: Row
  - `gr.Dropdown` id `sell_symbol` label `Sell Symbol` choices from current holdings; fallback to global list
  - `gr.Number` id `sell_quantity` label `Quantity` precision=0
  - `gr.Button` id `sell_btn` value `Sell`
  - Feedback:
    - Success: `gr.Info("Sold <quantity> <symbol> at <price>. Proceeds: <proceeds>. New balance: <balance>.")`
    - Error: `gr.Error("Insufficient shares to sell. Held: <held_qty>, Requested: <quantity>.")`, `gr.Error("Quantity must be a positive number.")`, `gr.Error("Unknown symbol: <symbol>.")`

### Technical Notes
- Update holdings; avg cost typically unchanged on sell; P/L tracked in US-006.
- Log transaction: `{type: "SELL", symbol, quantity, price, timestamp}`.

### Definition of Done
- Prevent selling non-owned shares; cash proceeds correct; transactions recorded; feedback clear.

### Out of Scope
- Tax lots, specific cost basis selection.

---

## US-006: Portfolio Value and Profit/Loss
- As an account holder, I want to see my portfolio’s total value and profit/loss compared to my initial deposit baseline.
- Business value: Medium-High
- Priority: High
- Estimation guidance: 5-8 story points

### Acceptance Criteria (BDD)
- Given holdings and balance, when I click `Calculate Portfolio`, then the system sums `cash balance + Σ(quantity * current_price)` for each symbol using `get_share_price`, and shows `Portfolio Value: <value>`.
- Given an initial deposit baseline, when I view `Profit/Loss`, then `P/L = Portfolio Value - Initial Deposit Baseline` and shows `Profit/Loss: <pl>` with positive/negative formatting.
- Given no holdings, `Portfolio Value = balance`.

### Validation Rules
- Prices fetched synchronously; handle unknown symbol with error: `Unknown symbol in holdings: <symbol>.`

### UI/UX Specifications (Gradio)
- Layout: Column
  - `gr.Button` id `calc_portfolio_btn` value `Calculate Portfolio`
  - `gr.Markdown` id `portfolio_value_md`
  - `gr.Markdown` id `profit_loss_md`
  - Feedback: Info messages on calculation; Error on unknown symbols.
- Accessibility: Buttons focusable; screen reader announces values.

### Technical Notes
- Baseline: Sum of all deposits minus withdrawals at time-of-creation or first successful deposit marked as baseline (choose consistent rule: baseline = first successful deposit amount). Store `initial_deposit_baseline`.
- Performance: Fetch prices for at most 3 symbols; <200ms.

### Definition of Done
- Correct math; deterministic with fixed price function; tests cover empty holdings and mixed positions.

### Out of Scope
- Real-time streaming updates; historical price curve.

---

## US-007: Holdings Report
- As an account holder, I want to view my holdings at any point in time.
- Business value: Medium
- Priority: Medium
- Estimation guidance: 3-5 story points

### Acceptance Criteria (BDD)
- Given current holdings, when I view Holdings, then I see a table with columns: `Symbol`, `Quantity`, `Avg Cost`, `Market Price`, `Market Value`.
- Given empty holdings, then I see `No holdings yet.`

### UI/UX Specifications (Gradio)
- Layout: Column
  - `gr.Dataframe` id `holdings_df` interactive=false with specified columns
  - Feedback: Info `No holdings yet.`
- Accessibility: Table has headers, keyboard navigable.

### Technical Notes
- Market price sourced via `get_share_price(symbol)`; market value `qty*price`.

### Definition of Done
- Accurate holdings grid; empty state message; test cases for both states.

### Out of Scope
- CSV export.

---

## US-008: Transaction History
- As an account holder, I want to list my transactions over time.
- Business value: Medium
- Priority: Medium
- Estimation guidance: 3-5 story points

### Acceptance Criteria (BDD)
- Given transactions exist, when I view History, then I see a table columns: `Timestamp`, `Type`, `Symbol`, `Quantity`, `Price`, `Amount` (cost or proceeds), `Balance After`.
- Given no transactions, then I see `No transactions yet.`

### UI/UX Specifications (Gradio)
- Layout: Column
  - `gr.Dataframe` id `transactions_df` interactive=false
  - Feedback: Info `No transactions yet.`

### Technical Notes
- Log after each action; timestamps in ISO 8601; balance snapshot after each transaction.

### Definition of Done
- Complete, chronological list; empty state; e2e tests.

### Out of Scope
- Filters, search.

---

## Global UI/UX and Layout
- Gradio Blocks structure:
  - Header: `gr.Markdown` title "Trading Simulation"
  - Account Section: Username + Create
  - Summary Section: Balance, Portfolio Value, Profit/Loss (markdown labels)
  - Actions Section: Deposit/Withdraw rows
  - Trading Section: Buy/Sell rows
  - Reports Section: Holdings table, Transactions table
- Messages: Use `gr.Info`, `gr.Error` consistently with exact strings above.
- Accessibility: ARIA labels for inputs; keyboard navigation; color contrast for positive/negative P/L.
- Responsive: Single-column stacking; tables scroll horizontally on small screens.

## Non-Functional Requirements
- Performance targets: Typical interactions <200ms.
- Security: No external APIs; trust-only price function.
- Cross-browser: Chromium baseline per Playwright e2e.
- Reliability: Deterministic test prices.

## Dependencies
- `get_share_price(symbol)` utility with fixed prices for AAPL, TSLA, GOOGL.
- Stories dependencies: US-001 precedes all; US-002 precedes trading; US-006 relies on price function and deposits.

## Definition of Done (Global)
- Implemented Gradio UI per specs
- Validations enforced across flows
- Unit tests and Playwright e2e for all ACs
- Documentation updated

## Out of Scope (Global)
- Real money movement, authentication, multi-user tenancy, advanced trading features, fees, tax handling, historical charts.
