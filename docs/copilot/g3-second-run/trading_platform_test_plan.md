# Trading Platform Simulation - Comprehensive Test Plan

## Application Overview

The Trading Platform Simulation is a web-based application built with Gradio that allows users to simulate stock trading activities. The application features:

- **Account Management**: User registration and login functionality.
- **Fund Management**: Deposit and withdrawal of cash funds.
- **Trading Interface**: Buying and selling of supported stocks (AAPL, TSLA, GOOGL).
- **Dashboard**: Real-time view of portfolio holdings, total value, and profit/loss.
- **Transaction History**: Audit log of all financial activities.

## Traceability Matrix

| User Story ID | User Story Title | Test Scenario ID | Test Scenario Title |
| :--- | :--- | :--- | :--- |
| **US-001** | Account Registration | TS-001 | Account Registration & Validation |
| **US-002** | Fund Management | TS-002 | Deposit & Withdrawal Operations |
| **US-003** | Buy Shares | TS-003 | Buy Share Operations |
| **US-004** | Sell Shares | TS-004 | Sell Share Operations |
| **US-005** | Portfolio Dashboard | TS-005 | Dashboard Accuracy & Updates |
| **US-006** | Transaction History | TS-006 | Transaction Logging |

## Test Scenarios

### TS-001: Account Registration & Validation

**Source User Story:** US-001

#### 1.1 Successful Account Creation
**Steps:**
1. Navigate to the application URL.
2. Ensure the "Login / Register" tab is selected.
3. Locate the "New User" section.
4. Enter a unique username (e.g., "TestTrader01") in the "Username" field.
5. Click the "Create Account" button.

**Expected Results:**
- A success message "Account 'TestTrader01' created successfully" is displayed.
- The user is effectively logged in (ready for subsequent actions).
- Navigate to the "Dashboard" tab; "Cash Balance" should display "0".

#### 1.2 Missing Username Validation
**Steps:**
1. Navigate to the application URL.
2. Ensure the "Login / Register" tab is selected.
3. Leave the "Username" field in the "New User" section empty.
4. Click the "Create Account" button.

**Expected Results:**
- An error/warning message "Username cannot be empty" is displayed.
- Account is not created.

#### 1.3 Duplicate Username Validation
**Steps:**
1. Navigate to the application URL.
2. Create an account with username "ExistingUser" (if not already done).
3. Refresh the page or clear fields.
4. Enter "ExistingUser" in the "New User" username field.
5. Click the "Create Account" button.

**Expected Results:**
- An error message "Username 'ExistingUser' already exists" is displayed.

---

### TS-002: Deposit & Withdrawal Operations

**Source User Story:** US-002
**Prerequisites:** User is logged in (e.g., "TestTrader01").

#### 2.1 Successful Deposit
**Steps:**
1. Click on the "Funds" tab.
2. In the "Deposit Funds" section, enter "1000" in the "Amount" field.
3. Click the "Deposit" button.
4. Click on the "Dashboard" tab.
5. Click "Refresh Dashboard" (if auto-refresh is not observed).

**Expected Results:**
- Success message "Deposited $1000.00" is displayed.
- "Cash Balance" in Dashboard shows "1000".

#### 2.2 Successful Withdrawal
**Steps:**
1. Ensure "Cash Balance" is at least 500 (perform deposit if needed).
2. Click on the "Funds" tab.
3. In the "Withdraw Funds" section, enter "200" in the "Amount" field.
4. Click the "Withdraw" button.
5. Click on the "Dashboard" tab and refresh.

**Expected Results:**
- Success message "Withdrawn $200.00" is displayed.
- "Cash Balance" decreases by 200.

#### 2.3 Insufficient Funds for Withdrawal
**Steps:**
1. Check current "Cash Balance" (e.g., 800).
2. Click on the "Funds" tab.
3. In the "Withdraw Funds" section, enter an amount greater than balance (e.g., "1000").
4. Click the "Withdraw" button.

**Expected Results:**
- Error message "Insufficient funds. Available: $..." is displayed.
- "Cash Balance" remains unchanged.

#### 2.4 Invalid Amount Validation
**Steps:**
1. Click on the "Funds" tab.
2. Enter "-100" or "0" in the "Deposit Funds" amount field.
3. Click "Deposit".
4. Repeat for "Withdraw Funds".

**Expected Results:**
- Error message "Amount must be positive" is displayed for both actions.

---

### TS-003: Buy Share Operations

**Source User Story:** US-003
**Prerequisites:** User is logged in and has sufficient funds (e.g., $2000).

#### 3.1 Successful Buy Transaction
**Steps:**
1. Click on the "Trade" tab.
2. In the "Buy Shares" section, select "AAPL" from the "Symbol" dropdown.
3. Enter "5" in the "Quantity" field.
4. Click the "Buy" button.
5. Click on the "Dashboard" tab and refresh.

**Expected Results:**
- Success message "Bought 5 shares of AAPL at $..." is displayed.
- "Cash Balance" decreases by (5 * Price of AAPL).
- "Current Holdings" table displays a row for AAPL with Quantity 5.

#### 3.2 Insufficient Funds for Buy
**Steps:**
1. Determine current cash balance (e.g., $100).
2. Click on the "Trade" tab.
3. Select "TSLA" (assuming price > $100).
4. Enter "10" in the "Quantity" field.
5. Click the "Buy" button.

**Expected Results:**
- Error message "Insufficient funds..." is displayed.
- No new shares are added to holdings.

#### 3.3 Invalid Quantity Validation
**Steps:**
1. Click on the "Trade" tab.
2. Enter "0" or "-5" in the "Quantity" field for Buying.
3. Click "Buy".

**Expected Results:**
- Error message "Quantity must be positive" is displayed.

---

### TS-004: Sell Share Operations

**Source User Story:** US-004
**Prerequisites:** User is logged in and owns shares (e.g., 5 AAPL).

#### 4.1 Successful Sell Transaction
**Steps:**
1. Click on the "Trade" tab.
2. In the "Sell Shares" section, select "AAPL".
3. Enter "2" in the "Quantity" field.
4. Click the "Sell" button.
5. Click on the "Dashboard" tab and refresh.

**Expected Results:**
- Success message "Sold 2 shares of AAPL at $..." is displayed.
- "Cash Balance" increases by (2 * Price of AAPL).
- "Current Holdings" table updates AAPL quantity to 3.

#### 4.2 Insufficient Shares for Sell
**Steps:**
1. Click on the "Trade" tab.
2. Select "AAPL".
3. Enter a quantity greater than owned (e.g., "10").
4. Click the "Sell" button.

**Expected Results:**
- Error message "Insufficient shares. Owned: 3" is displayed.
- Transaction is blocked.

#### 4.3 Selling Unowned Symbol
**Steps:**
1. Click on the "Trade" tab.
2. Select a symbol not owned (e.g., "GOOGL").
3. Enter "1" in "Quantity".
4. Click "Sell".

**Expected Results:**
- Error message "You do not own any shares of GOOGL" is displayed.

---

### TS-005: Dashboard Accuracy & Updates

**Source User Story:** US-005
**Prerequisites:** User has performed trades.

#### 5.1 Verify Portfolio Dashboard Updates
**Steps:**
1. Click on the "Dashboard" tab.
2. Click "Refresh Dashboard".
3. Verify "Current Holdings" table contains all owned stocks.
4. Verify "Total Portfolio Value" equals (Cash + Sum of (Qty * Price) for all holdings).
5. Verify "Total Profit/Loss" reflects (Total Value - Net Deposits).

**Expected Results:**
- All calculations are accurate based on current simulated prices.
- Table displays correct columns: Symbol, Quantity, Current Price, Total Value.

---

### TS-006: Transaction Logging

**Source User Story:** US-006
**Prerequisites:** User has performed multiple actions (Deposit, Buy, Sell, Withdraw).

#### 6.1 Verify Transaction History
**Steps:**
1. Click on the "History" tab.
2. Click "Refresh History".
3. Review the "Transaction History" table.

**Expected Results:**
- Table lists all performed actions in reverse chronological order.
- Columns include: Time, Type, Symbol, Quantity, Price, Amount.
- Data matches the actions performed in previous steps.
