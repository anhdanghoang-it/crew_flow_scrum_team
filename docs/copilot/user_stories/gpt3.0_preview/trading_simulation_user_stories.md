# Trading Simulation Platform - User Stories

## US-001: Account Fund Management

**Story Statement:**  
As a **Trader**, I want to **deposit and withdraw funds from my account**, so that **I have capital available for trading and can retrieve my earnings.**

**Business Value:**  
High - Fundamental capability required for the system to function. Without funds, no trading can occur.

**Estimation:** 3 Points

### Acceptance Criteria

**Scenario 1: Deposit Funds (Happy Path)**
- **Given** I am on the "Wallet" tab
- **When** I enter a positive amount (e.g., "1000") in the "Amount" field
- **And** I click the "Deposit" button
- **Then** I should see a success message "Successfully deposited $1000.00"
- **And** my "Current Balance" display should increase by 1000

**Scenario 2: Withdraw Funds (Happy Path)**
- **Given** I have a balance of $5000
- **When** I enter "1000" in the "Amount" field
- **And** I click the "Withdraw" button
- **Then** I should see a success message "Successfully withdrawn $1000.00"
- **And** my "Current Balance" display should decrease to $4000

**Scenario 3: Withdraw Insufficient Funds (Error)**
- **Given** I have a balance of $500
- **When** I attempt to withdraw "1000"
- **Then** I should see an error message "Error: Insufficient funds. Available balance: $500.00"
- **And** my balance should remain $500

**Scenario 4: Invalid Input**
- **Given** I am on the "Wallet" tab
- **When** I enter "-100" or "abc" in the "Amount" field
- **And** I click Deposit or Withdraw
- **Then** I should see a warning message "Please enter a valid positive number"

### UI/UX Specifications (Gradio)

- **Layout**: A `gr.Tab("Wallet")` containing:
  - A `gr.Number` display for "Current Balance" (read-only).
  - A `gr.Row` for actions:
    - `gr.Number(label="Amount", precision=2)`
    - `gr.Button("Deposit", variant="primary")`
    - `gr.Button("Withdraw", variant="secondary")`
- **Feedback**:
  - Use `gr.Info` for successful transactions.
  - Use `gr.Error` for insufficient funds.
  - Use `gr.Warning` for invalid inputs.

---

## US-002: Buy Shares

**Story Statement:**  
As a **Trader**, I want to **buy shares of a specific stock**, so that **I can invest my capital in assets.**

**Business Value:**  
High - Core trading functionality.

**Estimation:** 5 Points

### Acceptance Criteria

**Scenario 1: Buy Shares Successfully**
- **Given** I have $2000 balance
- **And** the price of "AAPL" is $150
- **When** I enter "AAPL" as Symbol and "10" as Quantity
- **And** I click "Buy"
- **Then** I should see a success message "Bought 10 shares of AAPL at $150.00. Total cost: $1500.00"
- **And** my balance should update to $500
- **And** my portfolio should reflect 10 AAPL shares

**Scenario 2: Buy with Insufficient Funds**
- **Given** I have $100 balance
- **And** the price of "TSLA" is $200
- **When** I try to buy "1" share of "TSLA"
- **Then** I should see an error message "Insufficient funds. Cost: $200.00, Balance: $100.00"
- **And** the transaction should not proceed

**Scenario 3: Invalid Symbol**
- **Given** the system uses `get_share_price(symbol)`
- **When** I enter an unknown symbol "XYZ"
- **And** I click "Buy"
- **Then** I should see an error message "Error: Symbol 'XYZ' not found or price unavailable"

### UI/UX Specifications (Gradio)

- **Layout**: A `gr.Tab("Trade")` containing:
  - `gr.Markdown("### Execute Trade")`
  - `gr.Row`:
    - `gr.Textbox(label="Stock Symbol", placeholder="e.g., AAPL")`
    - `gr.Number(label="Quantity", precision=0, minimum=1)`
  - `gr.Row`:
    - `gr.Button("Buy", variant="primary")`
    - `gr.Button("Sell", variant="stop")` (See US-003)
  - `gr.Textbox(label="Trade Status", interactive=False)` for immediate feedback log.

---

## US-003: Sell Shares

**Story Statement:**  
As a **Trader**, I want to **sell shares I currently own**, so that **I can liquidate my position and realize profit or loss.**

**Business Value:**  
High - Core trading functionality.

**Estimation:** 5 Points

### Acceptance Criteria

**Scenario 1: Sell Shares Successfully**
- **Given** I own 20 shares of "GOOGL"
- **And** the current price is $100
- **When** I enter "GOOGL" and Quantity "5"
- **And** I click "Sell"
- **Then** I should see a success message "Sold 5 shares of GOOGL at $100.00. Total received: $500.00"
- **And** my share count for GOOGL should decrease to 15
- **And** my cash balance should increase by $500

**Scenario 2: Sell More Than Owned**
- **Given** I own 10 shares of "AAPL"
- **When** I try to sell "15" shares of "AAPL"
- **Then** I should see an error message "Error: Insufficient shares. You own 10 AAPL."

**Scenario 3: Sell Unowned Stock**
- **Given** I own 0 shares of "TSLA"
- **When** I try to sell "1" share of "TSLA"
- **Then** I should see an error message "Error: You do not own any shares of TSLA."

### UI/UX Specifications (Gradio)

- **Layout**: Shares the "Trade" tab with Buying (US-002).
- **Interaction**: Clicking "Sell" triggers the sell logic.
- **Feedback**: Updates the "Trade Status" textbox and shows `gr.Info` or `gr.Error`.

---

## US-004: Portfolio Dashboard & P/L Reporting

**Story Statement:**  
As a **Trader**, I want to **view my current holdings, total portfolio value, and profit/loss**, so that **I can assess my financial performance.**

**Business Value:**  
Medium - Provides visibility into the user's status.

**Estimation:** 5 Points

### Acceptance Criteria

**Scenario 1: View Holdings**
- **Given** I own 10 AAPL ($150) and 5 TSLA ($200)
- **And** I have $500 cash
- **When** I view the "Dashboard" tab
- **Then** I should see a table listing:
  - AAPL | 10 | $150.00 | $1500.00
  - TSLA | 5 | $200.00 | $1000.00
- **And** I should see "Cash Balance: $500.00"
- **And** I should see "Total Portfolio Value: $3000.00" (1500 + 1000 + 500)

**Scenario 2: Profit/Loss Calculation**
- **Given** I initially deposited $2000
- **And** my current Total Portfolio Value is $3000
- **When** I view the "Dashboard" tab
- **Then** I should see "Total Profit/Loss: +$1000.00 (+50.0%)" (Green color for profit)

**Scenario 3: Loss Indication**
- **Given** Initial deposit $2000, Current Value $1500
- **Then** I should see "Total Profit/Loss: -$500.00 (-25.0%)" (Red color for loss)

### UI/UX Specifications (Gradio)

- **Layout**: A `gr.Tab("Dashboard")` containing:
  - `gr.Row`:
    - `gr.Number(label="Total Portfolio Value")`
    - `gr.Number(label="Total Profit/Loss")`
  - `gr.DataFrame(headers=["Symbol", "Quantity", "Current Price", "Total Value"], label="Current Holdings")`
  - `gr.Button("Refresh Dashboard")` to update prices and values.

---

## US-005: Transaction History

**Story Statement:**  
As a **Trader**, I want to **see a list of all my past transactions**, so that **I can track my trading activity over time.**

**Business Value:**  
Low - Auditability and record-keeping.

**Estimation:** 2 Points

### Acceptance Criteria

**Scenario 1: List Transactions**
- **Given** I have made a deposit, a buy, and a sell
- **When** I view the "History" tab
- **Then** I should see a table with rows for each action:
  - Date/Time | DEPOSIT | - | - | - | $1000
  - Date/Time | BUY | AAPL | 10 | $150 | -$1500
  - Date/Time | SELL | AAPL | 5 | $160 | +$800

### UI/UX Specifications (Gradio)

- **Layout**: A `gr.Tab("History")` containing:
  - `gr.DataFrame(headers=["Timestamp", "Type", "Symbol", "Quantity", "Price", "Amount"], label="Transaction Log")`

---

## Technical Notes

- **Pricing Source**: Use the provided `get_share_price(symbol)` function.
  - Mock values: AAPL, TSLA, GOOGL.
- **State Management**: User state (balance, holdings, transaction log) must be persisted during the session.
- **Concurrency**: Ensure balance checks and updates are atomic to prevent race conditions (though for a simple simulation, basic variable updates are sufficient).

## Definition of Done

- [ ] Code implemented for all scenarios.
- [ ] Unit tests written and passing for Account, Portfolio, and Transaction logic.
- [ ] UI implemented in Gradio and fully functional.
- [ ] Error messages displayed as specified.
- [ ] "Out of Scope" items respected.

## Out of Scope

- Real-time stock market data integration (use mocks).
- User authentication/login (single user session assumed for simplicity).
- Persistent database storage (in-memory or simple file storage is fine).
- Advanced order types (Limit, Stop-loss).
