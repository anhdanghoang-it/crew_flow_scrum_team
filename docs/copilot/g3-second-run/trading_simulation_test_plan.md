# Trading Simulation Platform - Comprehensive Test Plan

## Application Overview

The Trading Simulation Platform is a web-based application that allows users to manage a virtual stock trading portfolio. Users can create accounts, deposit/withdraw funds, buy/sell shares of supported stocks (AAPL, TSLA, GOOGL), and track their performance and transaction history.

**URL**: `http://127.0.0.1:7860/`

## Traceability Matrix

| User Story | Feature | Test Scenarios |
| :--- | :--- | :--- |
| **US-001** | Account Creation | TS-001.1, TS-001.2, TS-001.3 |
| **US-002** | Deposit Funds | TS-002.1, TS-002.3 |
| **US-003** | Withdraw Funds | TS-002.2, TS-002.4, TS-002.5 |
| **US-004** | Buy Shares | TS-003.1, TS-003.3, TS-003.5 |
| **US-005** | Sell Shares | TS-003.2, TS-003.4, TS-003.5 |
| **US-006** | View Portfolio | TS-004.1 |
| **US-007** | View History | TS-004.2 |

## Test Scenarios

### 1. Account Management (US-001)

**Seed:** `e2e/seed.spec.ts`

#### 1.1 Successful Account Creation
**Steps:**
1. Navigate to the application URL.
2. Enter a unique username (e.g., "test_user_1") in the "Username" field.
3. Click "Create Account".

**Expected Results:**
- Success notification "Account created successfully for test_user_1" appears.
- "Cash Balance" shows "0".
- "Total Portfolio Value" shows "0".
- "Total Profit/Loss" shows "0".
- "Holdings" table is empty.

#### 1.2 Missing Username Validation
**Steps:**
1. Refresh the page.
2. Leave "Username" field empty.
3. Click "Create Account".

**Expected Results:**
- Error notification "Username cannot be empty" appears.
- Account is not created.

#### 1.3 Duplicate Username Handling
**Steps:**
1. Create an account with username "existing_user".
2. Refresh the page (or just try again).
3. Enter "existing_user" in "Username".
4. Click "Create Account".

**Expected Results:**
- Error notification "Account for 'existing_user' already exists" appears.

---

### 2. Funds Management (US-002, US-003)

**Prerequisite:** Account "funds_user" created.

#### 2.1 Successful Deposit
**Steps:**
1. Enter "funds_user" in "Username".
2. Click "Login / Refresh".
3. Click "Funds" tab.
4. Enter "1000" in "Amount ($)".
5. Click "Deposit".

**Expected Results:**
- Success notification "Deposited $1000.00" appears.
- "Cash Balance" in Dashboard updates to "1000".

#### 2.2 Successful Withdrawal
**Steps:**
1. Ensure "funds_user" has 1000 balance.
2. Click "Funds" tab.
3. Enter "200" in "Amount ($)".
4. Click "Withdraw".

**Expected Results:**
- Success notification "Withdrew $200.00" appears.
- "Cash Balance" in Dashboard updates to "800".

#### 2.3 Invalid Deposit Amount (Zero/Negative)
**Steps:**
1. Click "Funds" tab.
2. Enter "-100" (or "0") in "Amount ($)".
3. Click "Deposit".

**Expected Results:**
- Error notification "Deposit amount must be positive" appears.
- Balance remains unchanged.

#### 2.4 Invalid Withdrawal Amount (Zero/Negative)
**Steps:**
1. Click "Funds" tab.
2. Enter "-50" in "Amount ($)".
3. Click "Withdraw".

**Expected Results:**
- Error notification "Withdrawal amount must be positive" appears.
- Balance remains unchanged.

#### 2.5 Insufficient Funds for Withdrawal
**Steps:**
1. Ensure "funds_user" has 800 balance.
2. Click "Funds" tab.
3. Enter "1000" in "Amount ($)".
4. Click "Withdraw".

**Expected Results:**
- Error notification "Insufficient funds. Available: $800.00" appears.
- Balance remains unchanged.

---

### 3. Trading Operations (US-004, US-005)

**Prerequisite:** Account "trader_user" created with $2000 deposit.
**Market Data:** AAPL ($150), TSLA ($200), GOOGL ($2800).

#### 3.1 Successful Buy
**Steps:**
1. Login as "trader_user".
2. Click "Trade" tab.
3. Select "AAPL" from "Symbol" dropdown.
4. Enter "2" in "Quantity".
5. Click "Buy Shares".

**Expected Results:**
- Success notification "Bought 2 AAPL @ $150.00" appears.
- Dashboard "Cash Balance" decreases by $300 (2 * 150).
- "Holdings" table shows AAPL, Quantity: 2, Current Price: 150, Total Value: 300.

#### 3.2 Successful Sell
**Steps:**
1. Ensure "trader_user" owns 2 AAPL shares.
2. Click "Trade" tab.
3. Select "AAPL".
4. Enter "1" in "Quantity".
5. Click "Sell Shares".

**Expected Results:**
- Success notification "Sold 1 AAPL @ $150.00" appears.
- Dashboard "Cash Balance" increases by $150.
- "Holdings" table shows AAPL, Quantity: 1.

#### 3.3 Insufficient Funds for Purchase
**Steps:**
1. Ensure "trader_user" has < $2800 cash.
2. Click "Trade" tab.
3. Select "GOOGL" ($2800).
4. Enter "1" in "Quantity".
5. Click "Buy Shares".

**Expected Results:**
- Error notification "Insufficient funds for purchase" appears.
- Transaction fails.

#### 3.4 Selling Unowned/Insufficient Shares
**Steps:**
1. Click "Trade" tab.
2. Select "TSLA" (not owned).
3. Enter "1" in "Quantity".
4. Click "Sell Shares".

**Expected Results:**
- Error notification "Insufficient shares to sell" appears.

#### 3.5 Invalid Quantity (Zero/Negative)
**Steps:**
1. Click "Trade" tab.
2. Select "AAPL".
3. Enter "0" (or "-1") in "Quantity".
4. Click "Buy Shares" (and then "Sell Shares").

**Expected Results:**
- Error notification "Quantity must be positive" appears.

---

### 4. Portfolio & History (US-006, US-007)

**Prerequisite:** Account "audit_user" with mixed history (Deposit, Buy, Sell).

#### 4.1 Portfolio Metrics Accuracy
**Steps:**
1. Login as "audit_user".
2. View "Dashboard" tab.
3. Calculate expected values manually:
    - Cash = Deposits - Withdrawals - Buy Cost + Sell Proceeds.
    - Portfolio Value = Cash + (Shares * Current Price).
    - P/L = Portfolio Value - Net Invested.

**Expected Results:**
- Displayed "Cash Balance", "Total Portfolio Value", and "Total Profit/Loss" match manual calculations.
- "Holdings" table accurately reflects current share counts.

#### 4.2 Transaction History Log
**Steps:**
1. Click "History" tab.
2. Review the table.

**Expected Results:**
- Table lists all performed actions in chronological order.
- Columns (Time, Type, Symbol, Quantity, Price, Total Amount) are correctly populated.
- "Total Amount" is positive for Deposits/Sells and negative for Withdrawals/Buys.
