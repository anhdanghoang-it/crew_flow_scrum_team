### **Filename**: `/docs/crew/trading_simulation_user_stories.md`

---

### **Feature Summary: Account & Portfolio Management**

-   **Epic**: E-01: Core Trading Simulation
-   **Description**: This epic covers the foundational features for a single-user trading simulation application. The goal is to provide a user with the ability to initialize a virtual trading account, manage their cash balance through deposits and withdrawals, execute market orders for a predefined set of stocks, and monitor their portfolio performance and transaction history. The user interface will be built using the Gradio framework for rapid development and a clear, functional layout.
-   **User Persona**: Trader - An individual using the platform to simulate stock trading, learn market dynamics, and test investment strategies without financial risk.

### **Glossary of Terms**

| Term                  | Definition                                                                                              |
| :-------------------- | :------------------------------------------------------------------------------------------------------ |
| **Cash Balance**      | The amount of liquid cash the user has available to trade or withdraw.                                  |
| **Holdings**          | The collection of shares of different stocks owned by the user.                                         |
| **Market Value**      | The current total value of a specific holding (Quantity of Shares \* Current Share Price).              |
| **Total Portfolio Value** | The sum of the user's Cash Balance and the market value of all their holdings.                          |
| **Profit / Loss (P/L)** | The total change in portfolio value relative to the net amount of money invested. Calculated as: `(Current Total Portfolio Value) - (Total Deposits) + (Total Withdrawals)`. |

### **User Flow Diagram**

```mermaid
graph TD
    A[Start Application] --> B{Account Initialized?};
    B -- No --> C[Show Initial Setup UI on Portfolio Tab];
    C --> D[User Enters Initial Deposit & Clicks 'Start Simulation' (US-001)];
    D -- Valid Amount --> E[Initialize Account State & Hide Setup UI];
    D -- Invalid Amount --> F[Show Error Message];
    F --> C;
    B -- Yes --> G[Show Main Dashboard on Portfolio Tab];
    E --> G;
    G --> H[View Portfolio Tab: Metrics & Holdings (US-001)];
    G --> I[Navigate to Trade Tab];
    I --> J{Execute Buy/Sell (US-003)};
    J -- Valid Trade --> K[Update Account State];
    J -- Invalid Trade --> L[Show Error Message];
    K --> G;
    L --> I;
    G --> M[Navigate to Cash Management Tab];
    M --> N{Execute Deposit/Withdraw (US-002)};
    N -- Valid Transaction --> K;
    N -- Invalid Transaction --> O[Show Error Message];
    O --> M;
    G --> P[Navigate to Transaction History Tab];
    P --> Q[View Transaction Log (US-004)];
```

### **High-Level Non-Functional Requirements (NFRs)**

-   **Performance**: UI interactions and state updates must complete in under 200ms. External price fetching calls (`get_share_price`) must not exceed 1 second.
-   **Data Integrity**: All currency values displayed in the UI must be formatted with a dollar sign, thousands separators, and two decimal places (e.g., "$1,234.56").
-   **Accessibility (WCAG)**: All interactive elements must have explicit labels and support keyboard navigation.

### **Requirements Traceability Matrix**

| Raw Requirement                                                                                                                                   | Corresponding User Story(ies) |
| :------------------------------------------------------------------------------------------------------------------------------------------------ | :---------------------------- |
| "A simple account management system for a trading simulation platform."                                                                           | E-01 (Epic)                   |
| "The system should allow users to create an account, deposit funds, and withdraw funds."                                                          | US-001, US-002                |
| "The system should allow users to record that they have bought or sold shares, providing a quantity."                                             | US-003                        |
| "The system should calculate the total value of the user's portfolio, and the profit or loss from the initial deposit."                           | US-001                        |
| "The system should be able to report the holdings of the user at any point in time."                                                              | US-001                        |
| "The system should be able to report the profit or loss of the user at any point in time."                                                        | US-001                        |
| "The system should be able to list the transactions that the user has made over time."                                                            | US-004                        |
| "The system should prevent the user from withdrawing funds..., buying more shares than they can afford, or selling shares that they don't have." | US-002, US-003                |
| "The system has access to a function get_share_price(symbol)..."                                                                                  | US-003 (Technical Notes)      |

---

### **Detailed User Stories**

---

#### **US-001: Initialize Account and View Portfolio Dashboard**

-   **Story ID**: US-001
-   **Title**: Initialize Account and View Portfolio Dashboard
-   **User Story**: As a Trader, I want to set an initial account balance and view a dashboard of my key portfolio metrics, so that I have a starting point for my simulation and can track my performance at a glance.
-   **Business Value**: High
-   **Priority**: High
-   **Story Points Estimation Guidance**: Medium (3 points).

##### **Acceptance Criteria**

1.  **Scenario: Initializing the account successfully (Happy Path)**
    -   **Given** I am a new user launching the application.
    -   **When** I provide an initial deposit amount of "100000.00" and click "Start Simulation".
    -   **Then** the "Initial Setup" group (`initial_setup_group`) should become hidden (`visible=False`).
    -   **And** the "Portfolio Overview" group (`portfolio_overview_group`) should become visible (`visible=True`).
    -   **And** my "Cash Balance" metric should display "$100,000.00".
    -   **And** I should see an information message: `gr.Info("Account initialized with a balance of $100,000.00.")`
    -   **And** all other main tabs (Trade, Cash Management, History) should become enabled.

2.  **Scenario: Attempting to initialize with invalid input (Non-positive amount)**
    -   **Given** I am a new user launching the application.
    -   **When** I enter "0" into the initial deposit field and click "Start Simulation".
    -   **Then** the account state should not change, and the "Initial Setup" UI remains visible.
    -   **And** I should see an error message: `gr.Error("Initial deposit must be a positive number.")`

3.  **Scenario: Dynamic Portfolio Metric Calculation**
    -   **Given** Cash Balance is $5,000, Total Deposits are $100,000, Total Withdrawals are $0, and Holdings Market Value is $15,000.
    -   **When** I view the "Portfolio" tab.
    -   **Then** the "Total Portfolio Value" must display "$20,000.00".
    -   **And** the "Profit / Loss" must display "-$80,000.00" (Calculated as $20,000 - $100,000 + $0).
    -   **And** the "Current Holdings" table (`holdings_df`) must accurately reflect all owned assets, including symbol, quantity, current price, and market value.

##### **UI/UX Specifications**

-   **Layout Structure**: The Portfolio tab uses a main `gr.Blocks` structure. The initialization UI is contained within a `gr.Group` that is conditionally hidden after setup. The dashboard uses a `gr.Row` for key metrics (`gr.Number` components) followed by a `gr.DataFrame` for holdings.
-   **Gradio Components**:
    -   `gr.Group(visible=True, elem_id="initial_setup_group")`
    -   `gr.Number(label="Initial Deposit", minimum=0.01, elem_id="initial_deposit_input")`
    -   `gr.Button("Start Simulation", variant="primary", elem_id="start_sim_button")`
    -   `gr.DataFrame(headers=["Symbol", "Quantity", "Current Price", "Market Value"], interactive=False, elem_id="holdings_df")`
-   **User Feedback Messages**:
    -   Success: `gr.Info("Account initialized with a balance of ${amount}.")`
    -   Error: `gr.Error("Initial deposit must be a positive number.")`
-   **Accessibility**: All metric `gr.Number` components must have explicit labels for screen reader clarity.

##### **Technical Notes**

-   **State Management**: Initialization must populate the central `gr.State` object with the initial cash balance and set the `total_deposits` field.

##### **Definition of Done**

-   [ ] All Acceptance Criteria are met.
-   [ ] UI visibility toggles correctly between setup and dashboard.
-   [ ] Portfolio metrics calculate and display correctly with currency formatting.

##### **Out of Scope**

-   Saving the initial deposit amount as a configurable setting.

---

#### **US-002: Manage Cash Balance**

-   **Story ID**: US-002
-   **Title**: Manage Cash Balance by Depositing and Withdrawing Funds
-   **User Story**: As a Trader, I want to deposit additional funds and withdraw existing funds, so that I can manage my cash balance in the simulation.
-   **Business Value**: High
-   **Priority**: High
-   **Story Points Estimation Guidance**: Small (2 points).

##### **Acceptance Criteria**

1.  **Scenario: Successfully depositing funds (Happy Path)**
    -   **Given** my current cash balance is $10,000.00.
    -   **When** I enter "5000.00" in the deposit field and click "Deposit".
    -   **Then** my cash balance updates to $15,000.00.
    -   **And** I see a success message: `gr.Info("Successfully deposited $5,000.00.")`
    -   **And** a "DEPOSIT" transaction is logged (US-004).

2.  **Scenario: Edge Case: Attempting to withdraw more funds than available (Validation)**
    -   **Given** my current cash balance is $10,000.00.
    -   **When** I enter "10001.00" in the withdrawal field and click "Withdraw".
    -   **Then** my cash balance remains $10,000.00.
    -   **And** I see an error message: `gr.Error("Withdrawal failed. Insufficient funds. Available: $10,000.00.")`

3.  **Scenario: Invalid input (Non-positive amount)**
    -   **Given** I have an active account.
    -   **When** I enter "-50" into the deposit field and click "Deposit".
    -   **Then** my cash balance does not change.
    -   **And** I see an error message: `gr.Error("Amount must be a positive number.")`

##### **UI/UX Specifications**

-   **Layout Structure**: The Cash Management tab uses a `gr.Row` divided into two `gr.Column` sections, one for Deposit and one for Withdrawal, to clearly separate the actions.
-   **Gradio Components**:
    -   `gr.Tab(label="Cash Management", elem_id="cash_management_tab")`.
    -   `gr.Number(label="Deposit Amount", minimum=0.01, elem_id="deposit_input")`.
    -   `gr.Button("Deposit", variant="primary")`.
    -   `gr.Number(label="Withdrawal Amount", minimum=0.01, elem_id="withdrawal_input")`.
    -   `gr.Button("Withdraw", variant="stop")`.
-   **User Feedback Messages**:
    -   Success (Deposit): `gr.Info("Successfully deposited $5,000.00.")`
    -   Error (Withdrawal): `gr.Error("Withdrawal failed. Insufficient funds. Available: ${balance}.")`

##### **Technical Notes**

-   **State Update**: Both actions must update the main `cash_balance` and the respective `total_deposits` or `total_withdrawals` fields in the `gr.State`.

##### **Definition of Done**

-   [ ] All Acceptance Criteria are met and tested.
-   [ ] Cash Balance updates are correctly reflected in the Portfolio Dashboard (US-001).
-   [ ] Transactions are logged for history (US-004).

---

#### **US-003: Buy and Sell Shares**

-   **Story ID**: US-003
-   **Title**: Execute Trades by Buying and Selling Shares
-   **User Story**: As a Trader, I want to buy and sell shares of specific stocks, so that I can build and manage my investment portfolio.
-   **Business Value**: High
-   **Priority**: High
-   **Story Points Estimation Guidance**: Medium (3 points).

##### **Acceptance Criteria**

1.  **Scenario: Successfully buying shares (Happy Path)**
    -   **Given** I have $50,000.00 cash and the price of "AAPL" is $150.00.
    -   **When** I select symbol "AAPL", enter quantity "10", and click "Buy".
    -   **Then** my cash balance should decrease by $1,500.00.
    -   **And** my holdings for "AAPL" should increase by 10 shares.
    -   **And** I should see a success message: `gr.Info("Successfully purchased 10 shares of AAPL for $1,500.00.")`

2.  **Scenario: Validation: Insufficient cash for Buy Order**
    -   **Given** I have $1,000.00 cash and the required cost for the trade is $1,500.00.
    -   **When** I attempt to execute the Buy order.
    -   **Then** the transaction is rejected.
    -   **And** I should see an error message: `gr.Error("Buy order failed. Insufficient funds. Required: $1,500.00, Available: $1,000.00.")`

3.  **Scenario: Validation: Selling more shares than owned**
    -   **Given** I own 50 shares of "TSLA".
    -   **When** I select "TSLA", enter quantity "60", and click "Sell".
    -   **Then** the transaction is rejected.
    -   **And** I should see an error message: `gr.Error("Sell order failed. You cannot sell 60 shares of TSLA. You only own 50.")`

4.  **Scenario: Edge Case: Price fetching service fails**
    -   **Given** I have an active account.
    -   **And** the call to `get_share_price("GOOGL")` returns an API error.
    -   **When** I attempt to trade "GOOGL".
    -   **Then** the trade should be aborted without changing account state.
    -   **And** I should see an error message: `gr.Error("Could not fetch price for GOOGL. Please try again later.")`

##### **UI/UX Specifications**

-   **Gradio Components**:
    -   `gr.Tab(label="Trade", elem_id="trade_tab")`.
    -   `gr.Dropdown(label="Symbol", choices=["AAPL", "TSLA", "GOOGL"], elem_id="symbol_dropdown")`.
    -   `gr.Number(label="Quantity", minimum=1, step=1, precision=0, elem_id="quantity_input")`.
    -   `gr.Row()` for buttons: `gr.Button("Buy", variant="primary")` and `gr.Button("Sell", variant="stop")`.
-   **User Feedback Messages**: Must clearly state the reason for failure (e.g., "Insufficient funds" vs. "Insufficient shares").

##### **Technical Notes**

-   **API Dependency**: Must call `get_share_price(symbol)` for every trade execution.
-   **Data Handling**: When selling, if the resulting quantity is zero, the symbol must be removed from the `holdings` state dictionary.

##### **Definition of Done**

-   [ ] All trade validations are implemented and tested.
-   [ ] Cash and Holdings states update atomically upon successful trade.
-   [ ] Error handling for external price fetching is robust.

---

#### **US-004: View Transaction History**

-   **Story ID**: US-004
-   **Title**: View a Chronological List of All Transactions
-   **User Story**: As a Trader, I want to view a history of all my transactions, so that I can review my past trading activity and analyze my decisions.
-   **Business Value**: Medium
-   **Priority**: Medium
-   **Story Points Estimation Guidance**: Small (1 point).
-   **Dependencies**: US-001, US-002, US-003 (Requires transaction data creation).

##### **Acceptance Criteria**

1.  **Scenario: Viewing a populated transaction history**
    -   **Given** I have executed multiple transaction types (Deposit, Buy, Withdraw, Sell).
    -   **When** I navigate to the "Transaction History" tab.
    -   **Then** I should see a `gr.DataFrame` populated with all transactions.
    -   **And** the transactions must be displayed in reverse chronological order (newest first).
    -   **And** the table must include columns: "Timestamp", "Type", "Symbol", "Quantity", "Price/Share", and "Total Value".
    -   **And** the "Total Value" column must reflect cash outflow as negative (Buy, Withdraw) and cash inflow as positive (Sell, Deposit).

2.  **Scenario: Displaying non-trade transactions correctly**
    -   **Given** The history contains a "DEPOSIT" transaction.
    -   **When** The history is displayed.
    -   **Then** the "Symbol", "Quantity", and "Price/Share" columns for that row must display "N/A" or be empty strings.

##### **UI/UX Specifications**

-   **Gradio Components**:
    -   `gr.Tab(label="Transaction History", elem_id="history_tab")`.
    -   `gr.DataFrame(headers=["Timestamp", "Type", "Symbol", "Quantity", "Price/Share", "Total Value"], interactive=False, elem_id="history_df")`.
-   **Data Presentation**: The "Timestamp" must include date and time. Currency columns must be formatted with the dollar sign.

##### **Technical Notes**

-   The data source for the `gr.DataFrame` must be the `transactions` list from the `gr.State`, sorted descending by timestamp.
-   A mapping logic must be applied to format the raw transaction data into the required table columns (e.g., converting cash changes to positive/negative values for the "Total Value" column).

##### **Definition of Done**

-   [ ] All Acceptance Criteria are met and tested.
-   [ ] Data formatting and sorting are consistent and correct.
-   [ ] The history table updates automatically when a new transaction is recorded in any other tab.

---

### **Overall Out of Scope Items**

The following items are explicitly excluded from the scope of this development effort:
1.  **Multi-User Support**: The application is strictly single-user simulation.
2.  **Persistence**: Account data will not be saved between application sessions (data is volatile upon closing the Gradio application).
3.  **Real-Time Data Feeds**: Stock prices are fetched only upon trade execution via the `get_share_price(symbol)` function; no continuous real-time streaming or automatic price updates are supported.
4.  **Advanced Trading**: Margin trading, short selling, limit orders, or stop-loss orders.
5.  **Market Mechanics**: Simulation of transaction fees, slippage, or market spread.
6.  **Reporting**: Advanced charting or export functionality for performance data.