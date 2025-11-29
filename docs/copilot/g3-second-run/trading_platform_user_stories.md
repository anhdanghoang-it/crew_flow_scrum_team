# Trading Platform User Stories

## US-001: Account Registration

### Story Header
**ID**: US-001
**Title**: Account Registration and Initialization
**User Story**: As a new user, I want to create an account with a unique username, so that I can start using the trading platform.
**Business Value**: High - Essential for user onboarding and identifying ownership of funds/portfolios.
**Estimation**: 3 Points

### Acceptance Criteria

**Scenario 1: Successful Account Creation**
- **Given** the user is on the registration screen
- **When** the user enters a valid, unique username (e.g., "TraderJoe")
- **And** clicks the "Create Account" button
- **Then** the system should create a new account
- **And** a success message "Account 'TraderJoe' created successfully" should be displayed via `gr.Info`
- **And** the dashboard view should become accessible/visible
- **And** the initial cash balance should be 0.00

**Scenario 2: Missing Username**
- **Given** the user is on the registration screen
- **When** the user leaves the username field empty
- **And** clicks "Create Account"
- **Then** an error message "Username cannot be empty" should be displayed via `gr.Warning`
- **And** the account should not be created

**Scenario 3: Duplicate Username (If applicable)**
- **Given** an account with username "TraderJoe" already exists
- **When** the user enters "TraderJoe"
- **And** clicks "Create Account"
- **Then** an error message "Username 'TraderJoe' already exists" should be displayed via `gr.Error`

### UI/UX Specifications
- **Layout**: A dedicated "Login/Register" Tab or initial state.
- **Components**:
  - `gr.Textbox(label="Username", placeholder="Enter unique username")`
  - `gr.Button(value="Create Account", variant="primary")`
- **Feedback**:
  - Success: `gr.Info("Account created...")`
  - Error: `gr.Error("...")` or `gr.Warning("...")`

---

## US-002: Fund Management (Deposit & Withdraw)

### Story Header
**ID**: US-002
**Title**: Deposit and Withdraw Funds
**User Story**: As a trader, I want to deposit and withdraw funds from my account, so that I can manage my buying power and cash out my profits.
**Business Value**: High - Core functionality for trading mechanics.
**Estimation**: 5 Points

### Acceptance Criteria

**Scenario 1: Successful Deposit**
- **Given** the user is logged in
- **When** the user enters a positive amount (e.g., 1000) in the "Amount" field
- **And** clicks "Deposit"
- **Then** the user's cash balance should increase by 1000
- **And** a success message "Deposited $1000.00" should be displayed
- **And** the "Cash Balance" display should update immediately

**Scenario 2: Successful Withdrawal**
- **Given** the user has a cash balance of 500
- **When** the user enters 200 in the "Amount" field
- **And** clicks "Withdraw"
- **Then** the user's cash balance should decrease to 300
- **And** a success message "Withdrawn $200.00" should be displayed

**Scenario 3: Insufficient Funds for Withdrawal**
- **Given** the user has a cash balance of 100
- **When** the user attempts to withdraw 150
- **Then** the system should prevent the transaction
- **And** an error message "Insufficient funds. Available: $100.00" should be displayed via `gr.Error`

**Scenario 4: Invalid Amounts**
- **Given** the user is on the funds management screen
- **When** the user enters a negative number or zero
- **And** clicks Deposit or Withdraw
- **Then** an error message "Amount must be positive" should be displayed

### UI/UX Specifications
- **Layout**: A "Funds" Row or Tab.
- **Components**:
  - `gr.Number(label="Amount", precision=2)`
  - `gr.Button(value="Deposit")`
  - `gr.Button(value="Withdraw")`
  - `gr.Markdown` or `gr.Number` display for "Current Cash Balance"
- **Feedback**: Immediate update of balance display.

---

## US-003: Buy Shares

### Story Header
**ID**: US-003
**Title**: Buy Shares
**User Story**: As a trader, I want to buy shares of supported stocks (AAPL, TSLA, GOOGL), so that I can invest my capital.
**Business Value**: High - Core trading functionality.
**Estimation**: 8 Points

### Acceptance Criteria

**Scenario 1: Successful Buy**
- **Given** the user has $1000 cash
- **And** the price of AAPL is $150
- **When** the user selects "AAPL" from the symbol dropdown
- **And** enters quantity 5
- **And** clicks "Buy"
- **Then** the system should deduct $750 (5 * 150) from cash
- **And** add 5 AAPL shares to the user's holdings
- **And** display success message "Bought 5 shares of AAPL at $150.00"

**Scenario 2: Insufficient Funds**
- **Given** the user has $100 cash
- **And** the price of TSLA is $200
- **When** the user attempts to buy 1 TSLA
- **Then** the system should prevent the transaction
- **And** display error "Insufficient funds. Cost: $200.00, Available: $100.00"

**Scenario 3: Invalid Quantity**
- **Given** the user is on the trading screen
- **When** the user enters quantity 0 or -1
- **Then** display error "Quantity must be positive"

### UI/UX Specifications
- **Layout**: "Trade" section.
- **Components**:
  - `gr.Dropdown(choices=["AAPL", "TSLA", "GOOGL"], label="Symbol")`
  - `gr.Number(label="Quantity", precision=0)`
  - `gr.Markdown` displaying "Current Price: $..." (updates when symbol selected)
  - `gr.Button(value="Buy", variant="primary")`
- **Technical Note**: Use `get_share_price(symbol)` to fetch real-time price for calculation.

---

## US-004: Sell Shares

### Story Header
**ID**: US-004
**Title**: Sell Shares
**User Story**: As a trader, I want to sell shares I currently own, so that I can liquidate my position.
**Business Value**: High - Core trading functionality.
**Estimation**: 5 Points

### Acceptance Criteria

**Scenario 1: Successful Sell**
- **Given** the user owns 10 shares of GOOGL
- **And** the price of GOOGL is $100
- **When** the user selects "GOOGL"
- **And** enters quantity 5
- **And** clicks "Sell"
- **Then** the system should add $500 to cash
- **And** reduce GOOGL holdings to 5
- **And** display success message "Sold 5 shares of GOOGL at $100.00"

**Scenario 2: Selling Not Owned/Insufficient Shares**
- **Given** the user owns 2 shares of AAPL
- **When** the user attempts to sell 5 AAPL
- **Then** the system should prevent the transaction
- **And** display error "Insufficient shares. Owned: 2"

**Scenario 3: Selling Unowned Symbol**
- **Given** the user owns 0 shares of TSLA
- **When** the user attempts to sell TSLA
- **Then** display error "You do not own any shares of TSLA"

### UI/UX Specifications
- **Layout**: "Trade" section (can be same as Buy, or separate tab).
- **Components**:
  - Reuse Symbol Dropdown and Quantity input.
  - `gr.Button(value="Sell", variant="secondary")`

---

## US-005: Portfolio Dashboard

### Story Header
**ID**: US-005
**Title**: Portfolio Dashboard and P/L Reporting
**User Story**: As a trader, I want to view my current holdings, total portfolio value, and profit/loss, so that I can track my financial performance.
**Business Value**: High - Provides visibility into investment status.
**Estimation**: 5 Points

### Acceptance Criteria

**Scenario 1: View Holdings**
- **Given** the user owns shares in AAPL and TSLA
- **When** the user views the dashboard
- **Then** a table should display rows for AAPL and TSLA
- **And** columns should include: Symbol, Quantity, Current Price, Total Value (Qty * Price)

**Scenario 2: Total Value Calculation**
- **Given** the user has $500 cash
- **And** owns $1000 worth of shares
- **When** the dashboard refreshes
- **Then** the "Total Portfolio Value" should display $1500

**Scenario 3: Profit/Loss Calculation**
- **Given** the user has deposited a net total of $1000 (Deposits - Withdrawals)
- **And** the current Total Portfolio Value is $1500
- **When** the dashboard refreshes
- **Then** the "Profit/Loss" should display +$500 (or +50%)
- **And** if P/L is negative, it should be indicated (e.g., -$200)

### UI/UX Specifications
- **Layout**: Main Dashboard area.
- **Components**:
  - `gr.DataFrame(headers=["Symbol", "Quantity", "Current Price", "Value"], label="Current Holdings")`
  - `gr.Number(label="Total Portfolio Value", interactive=False)`
  - `gr.Number(label="Total Profit/Loss", interactive=False)`
  - `gr.Button(value="Refresh Prices")` (Optional, if auto-refresh isn't implemented)

---

## US-006: Transaction History

### Story Header
**ID**: US-006
**Title**: Transaction History
**User Story**: As a trader, I want to see a list of all my past transactions, so that I can audit my trading activity.
**Business Value**: Medium - Auditability and user trust.
**Estimation**: 3 Points

### Acceptance Criteria

**Scenario 1: List Transactions**
- **Given** the user has performed deposits, buys, and sells
- **When** the user views the "History" tab
- **Then** a table should display all transactions in reverse chronological order (newest first)
- **And** columns should include: Timestamp, Type (Buy/Sell/Deposit/Withdraw), Symbol (if applicable), Quantity, Price, Total Amount

### UI/UX Specifications
- **Layout**: "History" Tab.
- **Components**:
  - `gr.DataFrame(headers=["Time", "Type", "Symbol", "Quantity", "Price", "Amount"], label="Transaction History")`

---

## Definition of Done
- [ ] Code implemented in Python.
- [ ] UI implemented using Gradio.
- [ ] All acceptance criteria met and verified via manual or automated tests.
- [ ] Error messages are clearly visible to the user.
- [ ] Code passes linting standards.

## Out of Scope
- Real-time streaming stock prices (simulated fixed prices or simple fetch is sufficient).
- User authentication/password management (simple username entry is sufficient).
- Persistent database storage (in-memory or simple file storage is acceptable for this iteration).
- Multiple portfolios per user.
- Margin trading or short selling.
