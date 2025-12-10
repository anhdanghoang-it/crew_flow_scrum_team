# Trading Simulation Platform - Comprehensive Test Plan

## Executive Summary

This test plan covers the functional testing of the Trading Simulation Platform. The platform allows users to create accounts, manage funds (deposit/withdraw), trade stocks (buy/sell), and view portfolio performance. The testing focuses on validating user stories, ensuring data integrity, and verifying UI/UX requirements.

## Traceability Matrix

| User Story ID | User Story Title | Test Scenario ID | Test Scenario Title |
| :--- | :--- | :--- | :--- |
| **US-001** | Initialize Trading Account | **TS-001** | Account Creation & Validation |
| **US-002** | Deposit Funds | **TS-002** | Funds Deposit Operations |
| **US-003** | Withdraw Funds | **TS-002** | Funds Withdrawal Operations |
| **US-004** | Buy Shares | **TS-003** | Buy Stock Operations |
| **US-005** | Sell Shares | **TS-003** | Sell Stock Operations |
| **US-006** | View Current Holdings | **TS-004** | Portfolio & Holdings Display |

---

## Test Scenarios

### TS-001: Account Creation & Validation

**Objective:** Verify that users can successfully create an account and that invalid inputs are handled correctly.
**Prerequisites:** Application is loaded at `http://127.0.0.1:7860/`.

#### 1.1 Successful Account Creation
**Steps:**
1. Navigate to the application URL.
2. Enter a valid username (e.g., "trader_01").
3. Enter a valid initial deposit (e.g., "10000").
4. Click "Create Account".

**Expected Results:**
- Success message displayed: "Account 'trader_01' created successfully...".
- Dashboard tabs (Funds, Trade, Portfolio, History) become visible.
- "Funds" tab is selected by default.
- Current Balance shows "$10,000.00".

#### 1.2 Missing Username Validation
**Steps:**
1. Refresh page to reset.
2. Leave "Username" field empty.
3. Enter valid deposit amount.
4. Click "Create Account".

**Expected Results:**
- Error message displayed: "Username is required...".
- Account is not created.

#### 1.3 Invalid Username Format
**Steps:**
1. Refresh page.
2. Enter invalid username (e.g., "user@123").
3. Click "Create Account".

**Expected Results:**
- Error message displayed: "Username must contain only letters, numbers, and underscores...".

#### 1.4 Invalid Deposit Amount (Zero/Negative)
**Steps:**
1. Refresh page.
2. Enter valid username.
3. Enter deposit amount "0" or "-100".
4. Click "Create Account".

**Expected Results:**
- Error message displayed: "Initial deposit must be greater than $0.00".

---

### TS-002: Funds Management

**Objective:** Verify deposit and withdrawal functionality, including balance updates and validation.
**Prerequisites:** Account created with $10,000 balance.

#### 2.1 Successful Deposit
**Steps:**
1. Navigate to "Funds" tab.
2. In "Deposit" section, enter "5000".
3. Click "Deposit Funds".

**Expected Results:**
- Success message displayed.
- Current Balance updates to "$15,000.00".

#### 2.2 Invalid Deposit (Negative/Zero)
**Steps:**
1. In "Deposit" section, enter "-500" or "0".
2. Click "Deposit Funds".

**Expected Results:**
- Error message displayed.
- Balance remains unchanged.

#### 2.3 Successful Withdrawal
**Steps:**
1. In "Withdraw" section, enter "2000".
2. Click "Withdraw Funds".

**Expected Results:**
- Success message displayed.
- Current Balance decreases by $2,000.

#### 2.4 Insufficient Funds Withdrawal
**Steps:**
1. In "Withdraw" section, enter amount greater than current balance (e.g., "100000").
2. Click "Withdraw Funds".

**Expected Results:**
- Error message displayed: "Insufficient funds...".
- Balance remains unchanged.

---

### TS-003: Trading Operations

**Objective:** Verify buying and selling of stocks, including cost calculations and holdings updates.
**Prerequisites:** Account created with funds.

#### 3.1 Successful Buy Order
**Steps:**
1. Navigate to "Trade" tab.
2. Select Symbol "AAPL".
3. Enter Quantity "10".
4. Verify "Total Cost" is calculated correctly (Price * 10).
5. Click "Buy Shares".

**Expected Results:**
- Success message displayed.
- Available Cash decreases by Total Cost.
- Transaction is recorded.

#### 3.2 Insufficient Funds for Buy
**Steps:**
1. Select Symbol "GOOGL".
2. Enter a large Quantity that exceeds available cash.
3. Click "Buy Shares".

**Expected Results:**
- Error message displayed: "Insufficient funds...".
- No shares purchased.

#### 3.3 Successful Sell Order
**Steps:**
1. Ensure user owns AAPL shares (from 3.1).
2. In "Sell Shares" section, select "AAPL".
3. Enter Quantity "5".
4. Verify "Sale Proceeds" is calculated.
5. Click "Sell Shares".

**Expected Results:**
- Success message displayed.
- Available Cash increases by Sale Proceeds.
- Holdings updated (reduced by 5).

#### 3.4 Sell More Than Owned
**Steps:**
1. Select "AAPL".
2. Enter Quantity greater than currently owned.
3. Click "Sell Shares".

**Expected Results:**
- Error message displayed: "Insufficient shares...".
- No sale occurs.

---

### TS-004: Portfolio & Reporting

**Objective:** Verify portfolio display, real-time updates, and profit/loss calculations.
**Prerequisites:** Account created, some trades executed.

#### 4.1 View Holdings
**Steps:**
1. Navigate to "Portfolio" tab.
2. Observe "Current Holdings" table.

**Expected Results:**
- Table displays owned stocks (Symbol, Quantity, Current Price, Total Value, Gain/Loss).
- "Overall Performance" section shows correct Total Invested, Current Value, and Profit/Loss.

#### 4.2 Empty Portfolio
**Steps:**
1. Create a new account (or sell all shares).
2. Navigate to "Portfolio" tab.

**Expected Results:**
- Message displayed: "No holdings..." or empty table.
- "Total Capital Invested" should be $0 (or initial deposit if considered capital, but typically invested means in stocks).

#### 4.3 Refresh Prices
**Steps:**
1. On "Portfolio" tab, click "Refresh Prices".

**Expected Results:**
- Prices update (if market data changes/simulated).
- "Last updated" timestamp refreshes.
