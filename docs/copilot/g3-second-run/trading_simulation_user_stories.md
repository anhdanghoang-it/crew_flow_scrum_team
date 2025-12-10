# User Stories: Trading Simulation Platform

**Feature**: Trading Simulation Account Management
**Source**: requirements.md
**Status**: Draft

## US-001: User Account Creation

### Story
**As a** new user,
**I want** to create a trading account with a unique username,
**So that** I can start managing my portfolio and trading activities.

### Priority
High

### Estimation
2 Story Points

### Acceptance Criteria
1.  **Scenario: Successful Account Creation**
    *   **Given** the application is loaded
    *   **When** I enter a valid username in the "Username" field
    *   **And** I click the "Create Account" button
    *   **Then** I should see a success message "Account created successfully for [username]"
    *   **And** the dashboard should initialize with 0 balance and empty holdings.

2.  **Scenario: Missing Username**
    *   **Given** the application is loaded
    *   **When** I leave the "Username" field empty
    *   **And** I click "Create Account"
    *   **Then** I should see an error message "Username cannot be empty".

### UI/UX Specifications
*   **Component**: `gr.Textbox` for Username input (label="Enter Username").
*   **Component**: `gr.Button` labeled "Create Account" (variant="primary").
*   **Feedback**: Use `gr.Info` for success and `gr.Warning` for validation errors.
*   **Layout**: Place inside a `gr.Row` at the top of the interface.

---

## US-002: Deposit Funds

### Story
**As a** registered user,
**I want** to deposit funds into my account,
**So that** I have capital to buy shares.

### Priority
High

### Estimation
3 Story Points

### Acceptance Criteria
1.  **Scenario: Successful Deposit**
    *   **Given** I have a valid account
    *   **When** I enter a positive number (e.g., 1000) in the "Amount" field
    *   **And** I click the "Deposit" button
    *   **Then** my "Cash Balance" should increase by 1000
    *   **And** I should see a success message "Deposited $1000.00".

2.  **Scenario: Invalid Amount (Zero or Negative)**
    *   **Given** I am on the deposit screen
    *   **When** I enter 0 or a negative number
    *   **And** I click "Deposit"
    *   **Then** I should see an error message "Deposit amount must be positive".

### UI/UX Specifications
*   **Component**: `gr.Number` for Amount input (label="Amount ($)").
*   **Component**: `gr.Button` labeled "Deposit" (variant="secondary").
*   **Display**: "Cash Balance" displayed via `gr.Number` or `gr.Markdown` (read-only).
*   **Layout**: Group with Withdraw in a "Funds Management" `gr.Tab` or `gr.Group`.

---

## US-003: Withdraw Funds

### Story
**As a** user with funds,
**I want** to withdraw cash from my account,
**So that** I can reduce my available capital.

### Priority
Medium

### Estimation
3 Story Points

### Acceptance Criteria
1.  **Scenario: Successful Withdrawal**
    *   **Given** I have a cash balance of $500
    *   **When** I enter 200 in the "Amount" field
    *   **And** I click "Withdraw"
    *   **Then** my "Cash Balance" should decrease to $300
    *   **And** I should see a success message "Withdrew $200.00".

2.  **Scenario: Insufficient Funds**
    *   **Given** I have a cash balance of $100
    *   **When** I enter 150 in the "Amount" field
    *   **And** I click "Withdraw"
    *   **Then** the transaction should be blocked
    *   **And** I should see an error message "Insufficient funds. Available: $100.00".

### UI/UX Specifications
*   **Component**: `gr.Number` for Amount input (reused or separate from deposit).
*   **Component**: `gr.Button` labeled "Withdraw".
*   **Feedback**: `gr.Error` for insufficient funds.

---

## US-004: Buy Shares

### Story
**As a** trader,
**I want** to buy shares of a specific stock,
**So that** I can invest my capital.

### Priority
High

### Estimation
5 Story Points

### Acceptance Criteria
1.  **Scenario: Successful Purchase**
    *   **Given** I have $1000 cash and AAPL price is $150
    *   **When** I enter "AAPL" as symbol and 2 as quantity
    *   **And** I click "Buy Shares"
    *   **Then** $300 should be deducted from my cash
    *   **And** my portfolio should show 2 AAPL shares
    *   **And** I should see a success message "Bought 2 AAPL @ $150.00".

2.  **Scenario: Insufficient Funds for Purchase**
    *   **Given** I have $100 cash and TSLA price is $200
    *   **When** I attempt to buy 1 TSLA
    *   **Then** the trade should fail
    *   **And** I should see an error message "Insufficient funds for purchase".

### UI/UX Specifications
*   **Component**: `gr.Textbox` or `gr.Dropdown` for Symbol (e.g., ["AAPL", "TSLA", "GOOGL"]).
*   **Component**: `gr.Number` for Quantity (precision=0).
*   **Component**: `gr.Button` labeled "Buy" (variant="primary").
*   **Technical Note**: Use `get_share_price(symbol)` to fetch current price.

---

## US-005: Sell Shares

### Story
**As a** trader,
**I want** to sell shares I own,
**So that** I can realize profits or cut losses.

### Priority
High

### Estimation
5 Story Points

### Acceptance Criteria
1.  **Scenario: Successful Sale**
    *   **Given** I own 5 shares of GOOGL
    *   **When** I enter "GOOGL" and quantity 2
    *   **And** I click "Sell Shares"
    *   **Then** my cash balance should increase by (2 * current_price)
    *   **And** my portfolio should show 3 GOOGL shares remaining.

2.  **Scenario: Selling Unowned Shares**
    *   **Given** I do not own any TSLA shares
    *   **When** I attempt to sell 1 TSLA
    *   **Then** the trade should fail
    *   **And** I should see an error message "Insufficient shares to sell".

### UI/UX Specifications
*   **Component**: Same inputs as Buy (Symbol, Quantity).
*   **Component**: `gr.Button` labeled "Sell" (variant="stop").

---

## US-006: View Portfolio & Performance

### Story
**As a** user,
**I want** to view my current holdings, total portfolio value, and profit/loss,
**So that** I can track my investment performance.

### Priority
High

### Estimation
5 Story Points

### Acceptance Criteria
1.  **Scenario: View Holdings**
    *   **Given** I own shares in AAPL and TSLA
    *   **When** I view the dashboard
    *   **Then** I should see a table listing Symbol, Quantity, Current Price, and Total Value for each holding.

2.  **Scenario: View Performance Metrics**
    *   **Given** I have made deposits and trades
    *   **When** I view the dashboard
    *   **Then** I should see "Total Portfolio Value" (Cash + Share Value)
    *   **And** I should see "Total Profit/Loss" (Total Value - Total Deposits).

### UI/UX Specifications
*   **Component**: `gr.DataFrame` for Holdings Table (Columns: Symbol, Quantity, Current Price, Value).
*   **Component**: `gr.Number` or `gr.Markdown` for "Total Value" and "P/L".
*   **Layout**: Prominent display, auto-refreshing after trades.

---

## US-007: View Transaction History

### Story
**As a** user,
**I want** to see a log of all my deposits, withdrawals, and trades,
**So that** I can audit my account activity.

### Priority
Low

### Estimation
3 Story Points

### Acceptance Criteria
1.  **Scenario: Transaction Log**
    *   **Given** I have performed multiple actions
    *   **When** I look at the "History" section
    *   **Then** I should see a chronological list of transactions including Type (Buy/Sell/Deposit/Withdraw), Symbol (if applicable), Quantity, Price, and Total Amount.

### UI/UX Specifications
*   **Component**: `gr.DataFrame` for Transaction History.
*   **Layout**: Can be in a separate `gr.Tab` named "History".

---

## Definition of Done
*   [ ] Code implemented in `src/crew_generated/engineering/`
*   [ ] Unit tests passing
*   [ ] UI components rendered correctly in Gradio
*   [ ] All acceptance criteria met
*   [ ] Error messages verified

## Out of Scope
*   Real-time stock price streaming (uses fixed `get_share_price` mock).
*   User authentication/login (simple username entry only).
*   Persistent database storage (in-memory or simple file storage is sufficient).
*   Multiple portfolios per user.
