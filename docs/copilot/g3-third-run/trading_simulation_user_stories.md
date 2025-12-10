# Trading Simulation Platform - User Stories

**Document Version:** 1.0  
**Date:** December 10, 2025  
**Project:** Trading Simulation Platform - Account Management System

---

## Table of Contents
1. [Overview](#overview)
2. [User Personas](#user-personas)
3. [User Stories](#user-stories)
   - [Epic 1: Account Management](#epic-1-account-management)
   - [Epic 2: Funds Management](#epic-2-funds-management)
   - [Epic 3: Trading Operations](#epic-3-trading-operations)
   - [Epic 4: Portfolio & Reporting](#epic-4-portfolio--reporting)
4. [Story Dependencies](#story-dependencies)

---

## Overview

This document contains user stories for a trading simulation platform that enables users to manage accounts, handle funds, execute trades, and track portfolio performance. All stories follow INVEST principles and include comprehensive UI/UX specifications using the Gradio framework.

---

## User Personas

**Primary Persona: Trading Simulator User**
- Individual learning stock trading concepts
- Needs to practice trading without financial risk
- Wants clear feedback on portfolio performance
- Requires intuitive interface for quick transactions

---

## User Stories

### Epic 1: Account Management

#### **US-001: Account Creation and Initialization**

**Story ID:** US-001  
**Title:** Initialize Trading Account with Starting Balance  
**Priority:** High  
**Story Points Guidance:** 3

**User Story:**  
As a trading simulator user, I want to create a new account with an initial deposit, so that I can start practicing trading with virtual funds.

**Business Value:**  
Enables users to begin using the platform immediately. This is the foundational feature required for all other functionality.

---

**Acceptance Criteria:**

**AC1: Successful Account Creation**
- **Given** I am on the account creation interface
- **When** I enter a valid username (3-50 characters, alphanumeric and underscores only) and an initial deposit amount greater than zero
- **And** I click the "Create Account" button
- **Then** the system creates my account with the specified initial balance
- **And** displays a success message: "Account '[username]' created successfully with initial balance of $[amount]"
- **And** the account dashboard becomes visible showing my username, current balance, and empty holdings table

**AC2: Missing Username Validation**
- **Given** I am on the account creation interface
- **When** I leave the username field empty or enter only whitespace
- **And** I click the "Create Account" button
- **Then** the system displays an error message: "Username is required and cannot be empty"
- **And** the account is not created
- **And** the username field is highlighted with red border

**AC3: Invalid Username Format**
- **Given** I am on the account creation interface
- **When** I enter a username with special characters (e.g., "user@123", "user name", "user#1")
- **And** I click the "Create Account" button
- **Then** the system displays an error message: "Username must contain only letters, numbers, and underscores (3-50 characters)"
- **And** the account is not created

**AC4: Zero or Negative Initial Deposit**
- **Given** I am on the account creation interface
- **When** I enter a valid username and an initial deposit of zero or negative value
- **And** I click the "Create Account" button
- **Then** the system displays an error message: "Initial deposit must be greater than $0.00"
- **And** the account is not created
- **And** the deposit amount field is highlighted with red border

**AC5: Non-Numeric Initial Deposit**
- **Given** I am on the account creation interface
- **When** I enter a valid username and a non-numeric value in the deposit field (e.g., "abc", "1.2.3")
- **And** I click the "Create Account" button
- **Then** the system displays an error message: "Please enter a valid numeric amount"
- **And** the account is not created

**AC6: Duplicate Username Handling**
- **Given** an account with username "trader123" already exists
- **When** I attempt to create another account with username "trader123"
- **And** I click the "Create Account" button
- **Then** the system displays an error message: "Username 'trader123' already exists. Please choose a different username"
- **And** the new account is not created

---

**UI/UX Specifications:**

**Gradio Components:**
```python
with gr.Blocks() as account_creation:
    gr.Markdown("## Create Trading Account")
    
    with gr.Row():
        with gr.Column():
            username_input = gr.Textbox(
                label="Username",
                placeholder="Enter username (3-50 characters)",
                max_lines=1,
                info="Only letters, numbers, and underscores allowed"
            )
            initial_deposit_input = gr.Number(
                label="Initial Deposit ($)",
                minimum=0.01,
                value=10000.00,
                precision=2,
                info="Minimum deposit: $0.01"
            )
            create_btn = gr.Button("Create Account", variant="primary")
            
        with gr.Column():
            status_output = gr.Markdown(visible=False)
```

**Component Behaviors:**
- Username field: Auto-trim whitespace, convert to lowercase for consistency
- Initial deposit field: Format to 2 decimal places, show $ prefix
- Create button: Disable during account creation (show loading state)
- Success/Error messages: Display using `gr.Info()` for success, `gr.Error()` for errors

**Accessibility:**
- All form fields must have descriptive labels
- Error messages announced to screen readers via ARIA live regions
- Keyboard navigation: Tab through fields, Enter to submit
- Focus management: On error, move focus to first invalid field

**Responsive Design:**
- Two-column layout on desktop (≥768px width)
- Single-column stack on mobile (<768px width)
- Buttons full-width on mobile

---

**Technical Notes:**
- Backend must validate username uniqueness before account creation
- Store initial deposit as the baseline for profit/loss calculations
- Initialize account with empty holdings list and transaction history
- Timestamp account creation for audit trail

**Dependencies:**
- None (foundational story)

**Definition of Done:**
- [ ] All acceptance criteria implemented and verified
- [ ] Unit tests for validation logic (username format, deposit amount)
- [ ] Integration test for successful account creation flow
- [ ] Error handling tests for all validation scenarios
- [ ] UI matches specifications with proper Gradio components
- [ ] Accessibility requirements met (ARIA labels, keyboard navigation)
- [ ] Code reviewed and merged
- [ ] Documentation updated

**Out of Scope:**
- Email verification or authentication
- Password protection
- Multi-currency support
- Account deletion or modification
- Profile pictures or additional user metadata

---

### Epic 2: Funds Management

#### **US-002: Deposit Funds**

**Story ID:** US-002  
**Title:** Add Funds to Trading Account  
**Priority:** High  
**Story Points Guidance:** 2

**User Story:**  
As a trading simulator user, I want to deposit additional funds into my account, so that I can increase my trading capital and continue practicing with more virtual money.

**Business Value:**  
Allows users to replenish their account balance, enabling continued platform engagement without creating new accounts.

---

**Acceptance Criteria:**

**AC1: Successful Deposit**
- **Given** I have an active account with current balance $5,000
- **When** I enter a deposit amount of $2,000 and click "Deposit Funds"
- **Then** my account balance increases to $7,000
- **And** the system displays: "Successfully deposited $2,000.00. New balance: $7,000.00"
- **And** the balance display updates immediately
- **And** a deposit transaction is recorded with timestamp

**AC2: Zero Amount Validation**
- **Given** I am on the deposit interface
- **When** I enter $0.00 and click "Deposit Funds"
- **Then** the system displays an error: "Deposit amount must be greater than $0.00"
- **And** my balance remains unchanged

**AC3: Negative Amount Validation**
- **Given** I am on the deposit interface
- **When** I enter a negative amount (e.g., -$100) and click "Deposit Funds"
- **Then** the system displays an error: "Deposit amount must be greater than $0.00"
- **And** my balance remains unchanged

**AC4: Non-Numeric Input**
- **Given** I am on the deposit interface
- **When** I enter a non-numeric value (e.g., "five hundred", "abc") and click "Deposit Funds"
- **Then** the system displays an error: "Please enter a valid numeric amount"
- **And** my balance remains unchanged

**AC5: Large Deposit Boundary**
- **Given** I am on the deposit interface
- **When** I enter a very large amount (e.g., $999,999,999.99)
- **And** click "Deposit Funds"
- **Then** the deposit succeeds
- **And** the system displays: "Successfully deposited $999,999,999.99. New balance: $[new_balance]"
- **And** balance displays with proper comma formatting

**AC6: Decimal Precision**
- **Given** I am on the deposit interface
- **When** I enter an amount with more than 2 decimal places (e.g., $100.567)
- **And** click "Deposit Funds"
- **Then** the system rounds to 2 decimal places ($100.57)
- **And** displays: "Successfully deposited $100.57. New balance: $[new_balance]"

---

**UI/UX Specifications:**

**Gradio Components:**
```python
with gr.Blocks() as funds_management:
    gr.Markdown("## Funds Management")
    
    current_balance_display = gr.Markdown("**Current Balance:** $0.00")
    
    with gr.Tab("Deposit"):
        deposit_amount = gr.Number(
            label="Deposit Amount ($)",
            minimum=0.01,
            precision=2,
            value=1000.00,
            info="Enter amount to add to your account"
        )
        deposit_btn = gr.Button("Deposit Funds", variant="primary")
        
    deposit_btn.click(
        fn=process_deposit,
        inputs=[username_state, deposit_amount],
        outputs=[current_balance_display, status_message]
    )
```

**Component Behaviors:**
- Amount input: Auto-format with $ and commas (e.g., $1,000.00)
- Deposit button: Show loading spinner during processing
- Balance display: Animate number change on successful deposit
- Quick deposit buttons: Optional shortcuts for $500, $1000, $5000

**User Feedback:**
- Success: Green checkmark icon + message via `gr.Info()`
- Error: Red X icon + message via `gr.Error()`
- Processing: "Processing deposit..." loading state

**Accessibility:**
- Amount field labeled with ARIA description of minimum value
- Success/error announcements via ARIA live regions
- Balance updates announced to screen readers

---

**Technical Notes:**
- Record deposit transaction with type="DEPOSIT", amount, timestamp
- Update account balance atomically to prevent race conditions
- Log all deposit attempts (success and failure) for audit

**Dependencies:**
- US-001 (Account Creation) must be completed

**Definition of Done:**
- [ ] All acceptance criteria pass
- [ ] Unit tests for deposit validation and balance updates
- [ ] Integration tests for successful and failed deposits
- [ ] Transaction history correctly records deposits
- [ ] UI implements all specified components
- [ ] Accessibility tests pass
- [ ] Code reviewed and merged

**Out of Scope:**
- Payment gateway integration
- Deposit limits or daily caps
- Deposit bonuses or promotions
- Scheduled/recurring deposits

---

#### **US-003: Withdraw Funds**

**Story ID:** US-003  
**Title:** Withdraw Funds from Trading Account  
**Priority:** High  
**Story Points Guidance:** 3

**User Story:**  
As a trading simulator user, I want to withdraw funds from my account, so that I can practice portfolio liquidation and test my trading strategy outcomes.

**Business Value:**  
Provides realistic simulation of fund withdrawals, helping users understand liquidity management.

---

**Acceptance Criteria:**

**AC1: Successful Withdrawal**
- **Given** my account has a balance of $10,000 and no open positions
- **When** I enter a withdrawal amount of $3,000 and click "Withdraw Funds"
- **Then** my balance decreases to $7,000
- **And** the system displays: "Successfully withdrew $3,000.00. New balance: $7,000.00"
- **And** a withdrawal transaction is recorded with timestamp

**AC2: Insufficient Funds - Would Create Negative Balance**
- **Given** my account has a balance of $1,000
- **When** I attempt to withdraw $1,500
- **Then** the system displays an error: "Insufficient funds. Available balance: $1,000.00"
- **And** my balance remains $1,000
- **And** no transaction is recorded

**AC3: Exact Balance Withdrawal**
- **Given** my account has a balance of $5,000
- **When** I withdraw exactly $5,000
- **Then** my balance becomes $0.00
- **And** the system displays: "Successfully withdrew $5,000.00. New balance: $0.00"

**AC4: Zero or Negative Amount**
- **Given** I am on the withdrawal interface
- **When** I enter $0.00 or a negative amount and click "Withdraw Funds"
- **Then** the system displays an error: "Withdrawal amount must be greater than $0.00"
- **And** my balance remains unchanged

**AC5: Non-Numeric Input**
- **Given** I am on the withdrawal interface
- **When** I enter non-numeric text and click "Withdraw Funds"
- **Then** the system displays an error: "Please enter a valid numeric amount"

**AC6: Withdrawal with Locked Funds (Holdings)**
- **Given** my account balance is $10,000 with $6,000 invested in stocks
- **When** I attempt to withdraw $8,000
- **Then** the system displays an error: "Insufficient available cash. Available: $4,000.00 (Total balance: $10,000.00, Invested: $6,000.00)"
- **And** the withdrawal is rejected

---

**UI/UX Specifications:**

**Gradio Components:**
```python
with gr.Tab("Withdraw"):
    with gr.Row():
        available_cash_display = gr.Markdown("**Available Cash:** $0.00")
        invested_funds_display = gr.Markdown("**Invested:** $0.00")
    
    withdraw_amount = gr.Number(
        label="Withdrawal Amount ($)",
        minimum=0.01,
        precision=2,
        info="Maximum: Available cash balance"
    )
    
    max_withdraw_btn = gr.Button("Withdraw Max", size="sm")
    withdraw_btn = gr.Button("Withdraw Funds", variant="secondary")
```

**Component Behaviors:**
- "Withdraw Max" button: Auto-fills available cash amount
- Withdrawal button: Disabled if balance is $0
- Real-time validation: Show warning if amount exceeds available cash
- Confirmation for large withdrawals: Modal for amounts >50% of balance

**User Feedback:**
- Success: `gr.Info()` with green checkmark
- Error: `gr.Error()` with specific reason
- Warning: `gr.Warning()` for amounts approaching total balance

**Accessibility:**
- Clear distinction between total balance and available cash
- Error messages specify exact available amount
- Keyboard shortcut for "Withdraw Max" (Alt+M)

---

**Technical Notes:**
- Calculate available cash as: total_balance - total_invested_value
- Validate withdrawal amount against available cash, not total balance
- Record transaction with type="WITHDRAWAL"
- Consider implementing withdrawal fee in future iterations

**Dependencies:**
- US-001 (Account Creation)
- US-002 (Deposit Funds)
- US-004 (Buy Shares) - for locked funds calculation

**Definition of Done:**
- [ ] All acceptance criteria validated
- [ ] Unit tests for withdrawal logic and validation
- [ ] Integration tests including insufficient funds scenarios
- [ ] Transaction history records withdrawals correctly
- [ ] UI displays available vs. invested funds clearly
- [ ] Accessibility compliance verified
- [ ] Code reviewed and merged

**Out of Scope:**
- Withdrawal processing time simulation
- Withdrawal fees or penalties
- Withdrawal limits per transaction
- Bank account integration

---

### Epic 3: Trading Operations

#### **US-004: Buy Shares**

**Story ID:** US-004  
**Title:** Purchase Shares of Stock  
**Priority:** High  
**Story Points Guidance:** 5

**User Story:**  
As a trading simulator user, I want to buy shares of stocks, so that I can build a portfolio and practice investment strategies.

**Business Value:**  
Core trading functionality enabling users to execute buy orders and build portfolios.

---

**Acceptance Criteria:**

**AC1: Successful Share Purchase**
- **Given** I have $10,000 available cash and AAPL trades at $150 per share
- **When** I enter symbol "AAPL", quantity 10, and click "Buy Shares"
- **Then** the system purchases 10 shares for $1,500 total
- **And** my available cash decreases by $1,500 to $8,500
- **And** displays: "Successfully purchased 10 shares of AAPL at $150.00/share. Total: $1,500.00"
- **And** my holdings show 10 shares of AAPL with current value
- **And** a BUY transaction is recorded

**AC2: Insufficient Funds**
- **Given** I have $1,000 available cash and TSLA trades at $800 per share
- **When** I attempt to buy 2 shares of TSLA (total $1,600)
- **Then** the system displays an error: "Insufficient funds. Required: $1,600.00, Available: $1,000.00"
- **And** no shares are purchased
- **And** my balance remains unchanged

**AC3: Invalid Stock Symbol**
- **Given** I am on the buy shares interface
- **When** I enter an unsupported symbol (e.g., "XYZ") and click "Buy Shares"
- **Then** the system displays an error: "Invalid or unsupported stock symbol: XYZ. Supported symbols: AAPL, TSLA, GOOGL"
- **And** no transaction occurs

**AC4: Zero or Negative Quantity**
- **Given** I am on the buy shares interface
- **When** I enter a quantity of 0 or negative number
- **Then** the system displays an error: "Quantity must be a positive whole number"
- **And** the buy button remains disabled until valid input

**AC5: Non-Integer Quantity**
- **Given** I am on the buy shares interface
- **When** I enter a fractional quantity (e.g., 2.5 shares)
- **Then** the system displays an error: "Quantity must be a whole number (no fractional shares)"

**AC6: Accumulating Shares of Same Symbol**
- **Given** I already own 5 shares of AAPL
- **When** I purchase 3 more shares of AAPL
- **Then** my holdings show 8 total shares of AAPL
- **And** both transactions are recorded separately in transaction history
- **And** average cost basis is calculated correctly

**AC7: Real-Time Price Display**
- **Given** I am on the buy shares interface
- **When** I select a stock symbol (e.g., "GOOGL")
- **Then** the current price is displayed: "Current price: $2,800.00/share"
- **And** the total cost updates in real-time as I change quantity
- **And** shows: "Total cost: $[quantity × price]"

**AC8: Empty or Missing Symbol**
- **Given** I am on the buy shares interface
- **When** I leave the symbol field empty and click "Buy Shares"
- **Then** the system displays an error: "Stock symbol is required"

---

**UI/UX Specifications:**

**Gradio Components:**
```python
with gr.Blocks() as trading:
    gr.Markdown("## Trading Operations")
    
    with gr.Tab("Buy Shares"):
        with gr.Row():
            symbol_input = gr.Dropdown(
                label="Stock Symbol",
                choices=["AAPL", "TSLA", "GOOGL"],
                value=None,
                info="Select a stock to trade"
            )
            quantity_input = gr.Number(
                label="Quantity",
                minimum=1,
                precision=0,
                value=1,
                info="Number of shares to buy"
            )
        
        current_price_display = gr.Markdown("**Current Price:** Select a symbol")
        total_cost_display = gr.Markdown("**Total Cost:** $0.00")
        available_cash_display = gr.Markdown("**Available Cash:** $0.00")
        
        buy_btn = gr.Button("Buy Shares", variant="primary")
        
        # Real-time calculation
        def update_totals(symbol, quantity):
            price = get_share_price(symbol) if symbol else 0
            total = price * (quantity or 0)
            return (
                f"**Current Price:** ${price:.2f}/share",
                f"**Total Cost:** ${total:,.2f}"
            )
        
        symbol_input.change(update_totals, [symbol_input, quantity_input], 
                           [current_price_display, total_cost_display])
        quantity_input.change(update_totals, [symbol_input, quantity_input],
                             [current_price_display, total_cost_display])
```

**Component Behaviors:**
- Symbol dropdown: Show company names alongside symbols (e.g., "AAPL - Apple Inc.")
- Quantity stepper: Increment/decrement buttons for ease
- Buy button: Disabled until valid symbol and quantity entered
- Price display: Update immediately when symbol changes
- Confirmation modal: For purchases >10% of portfolio value

**User Feedback:**
- Success: `gr.Info()` with transaction summary
- Error: `gr.Error()` with specific reason and available amount
- Warning: `gr.Warning()` for large purchases relative to portfolio

**Accessibility:**
- Symbol dropdown navigable via keyboard
- Price updates announced to screen readers
- Clear error messages for insufficient funds

---

**Technical Notes:**
- Call `get_share_price(symbol)` to retrieve current price
- Validate symbol is in supported list: ["AAPL", "TSLA", "GOOGL"]
- Calculate total cost = quantity × current_price
- Check: available_cash >= total_cost before execution
- Update holdings: add to existing position or create new
- Record transaction with type="BUY", symbol, quantity, price, total_cost, timestamp
- Update available cash atomically

**Dependencies:**
- US-001 (Account Creation)
- US-002 (Deposit Funds)
- External: `get_share_price(symbol)` function

**Definition of Done:**
- [ ] All acceptance criteria pass
- [ ] Unit tests for buy logic, validation, insufficient funds
- [ ] Integration tests with mock price data
- [ ] Holdings correctly updated for new and existing positions
- [ ] Transaction history records all details
- [ ] UI implements real-time calculations
- [ ] Accessibility verified
- [ ] Code reviewed and merged

**Out of Scope:**
- Market orders vs. limit orders
- Pre-market or after-hours trading
- Short selling
- Options or derivatives
- Real-time stock price APIs
- Trading fees or commissions

---

#### **US-005: Sell Shares**

**Story ID:** US-005  
**Title:** Sell Shares from Portfolio  
**Priority:** High  
**Story Points Guidance:** 5

**User Story:**  
As a trading simulator user, I want to sell shares from my portfolio, so that I can realize gains/losses and rebalance my investments.

**Business Value:**  
Enables users to complete the trading cycle, realize profits/losses, and free up cash for reinvestment.

---

**Acceptance Criteria:**

**AC1: Successful Share Sale**
- **Given** I own 10 shares of AAPL and the current price is $160/share
- **When** I enter symbol "AAPL", quantity 5, and click "Sell Shares"
- **Then** the system sells 5 shares for $800 total ($160 × 5)
- **And** my available cash increases by $800
- **And** my holdings show 5 remaining shares of AAPL
- **And** displays: "Successfully sold 5 shares of AAPL at $160.00/share. Total: $800.00"
- **And** a SELL transaction is recorded

**AC2: Selling Entire Position**
- **Given** I own exactly 15 shares of GOOGL
- **When** I sell all 15 shares
- **Then** my holdings no longer show GOOGL (position closed)
- **And** cash increases by sale proceeds
- **And** displays: "Successfully sold 15 shares of GOOGL at $[price]/share. Total: $[total]. Position closed."

**AC3: Insufficient Shares**
- **Given** I own 3 shares of TSLA
- **When** I attempt to sell 5 shares of TSLA
- **Then** the system displays an error: "Insufficient shares. You own 3 shares of TSLA"
- **And** no sale occurs
- **And** my holdings remain unchanged

**AC4: Selling Shares Not Owned**
- **Given** I do not own any shares of AAPL
- **When** I attempt to sell AAPL shares
- **Then** the system displays an error: "You do not own any shares of AAPL"
- **And** no transaction occurs

**AC5: Zero or Negative Quantity**
- **Given** I am on the sell shares interface
- **When** I enter a quantity of 0 or negative
- **Then** the system displays an error: "Quantity must be a positive whole number"

**AC6: Non-Integer Quantity**
- **Given** I am on the sell shares interface
- **When** I enter fractional shares (e.g., 1.5)
- **Then** the system displays an error: "Quantity must be a whole number (no fractional shares)"

**AC7: Portfolio Display Integration**
- **Given** I own multiple stocks
- **When** I view the sell interface
- **Then** the symbol dropdown shows only symbols I currently own
- **And** displays my current holdings quantity next to each symbol
- **And** shows: "AAPL (10 shares owned)"

**AC8: Real-Time Sale Proceeds Display**
- **Given** I select a symbol I own
- **When** I enter a quantity
- **Then** the system displays current price and calculates: "Sale proceeds: $[quantity × current_price]"
- **And** updates in real-time as I change quantity

---

**UI/UX Specifications:**

**Gradio Components:**
```python
with gr.Tab("Sell Shares"):
    with gr.Row():
        sell_symbol_input = gr.Dropdown(
            label="Stock Symbol",
            choices=[],  # Populated dynamically with owned symbols
            value=None,
            info="Select from your holdings"
        )
        sell_quantity_input = gr.Number(
            label="Quantity",
            minimum=1,
            precision=0,
            value=1,
            info="Number of shares to sell"
        )
    
    owned_shares_display = gr.Markdown("**You own:** 0 shares")
    current_sell_price_display = gr.Markdown("**Current Price:** Select a symbol")
    sale_proceeds_display = gr.Markdown("**Sale Proceeds:** $0.00")
    
    sell_max_btn = gr.Button("Sell All", size="sm")
    sell_btn = gr.Button("Sell Shares", variant="secondary")
```

**Component Behaviors:**
- Symbol dropdown: Only show owned stocks with quantity in label
- "Sell All" button: Auto-fills quantity with total shares owned
- Sell button: Disabled if quantity exceeds owned shares
- Real-time validation: Show warning if selling entire position
- Confirmation modal: "Are you sure you want to sell [qty] shares of [symbol]?"

**User Feedback:**
- Success: `gr.Info()` showing realized gain/loss if applicable
- Error: `gr.Error()` with specific holdings information
- Warning: `gr.Warning()` when selling >50% of position

**Accessibility:**
- Dropdown shows holdings clearly for screen readers
- Sale proceeds announced on quantity change
- Error messages include specific owned quantity

---

**Technical Notes:**
- Retrieve holdings to populate symbol dropdown
- Validate: owned_shares >= sell_quantity
- Call `get_share_price(symbol)` for current price
- Calculate proceeds = quantity × current_price
- Update holdings: reduce quantity or remove if position closed
- Record transaction: type="SELL", symbol, quantity, price, total_proceeds, timestamp
- Update available cash atomically
- Optional: Calculate realized gain/loss (proceeds - cost_basis)

**Dependencies:**
- US-001 (Account Creation)
- US-004 (Buy Shares) - must have holdings to sell

**Definition of Done:**
- [ ] All acceptance criteria validated
- [ ] Unit tests for sell logic and validation
- [ ] Integration tests for insufficient shares scenarios
- [ ] Holdings updated correctly (reduction and position closure)
- [ ] Transaction history records sell transactions
- [ ] UI dynamically populates with owned symbols
- [ ] Real-time proceeds calculation working
- [ ] Accessibility verified
- [ ] Code reviewed and merged

**Out of Scope:**
- Tax loss harvesting
- Wash sale rules
- Stop-loss orders
- Limit orders
- Short selling or margin trading
- Trading fees or commissions

---

### Epic 4: Portfolio & Reporting

#### **US-006: View Current Holdings**

**Story ID:** US-006  
**Title:** Display Current Portfolio Holdings  
**Priority:** High  
**Story Points Guidance:** 3

**User Story:**  
As a trading simulator user, I want to view my current stock holdings at any time, so that I can understand my portfolio composition and make informed trading decisions.

**Business Value:**  
Provides essential visibility into portfolio state, enabling users to track investments and plan next moves.

---

**Acceptance Criteria:**

**AC1: Holdings Table Display**
- **Given** I own 10 shares of AAPL (at $150), 5 shares of TSLA (at $800), and 20 shares of GOOGL (at $2,800)
- **When** I view the holdings section
- **Then** the system displays a table with columns: Symbol, Quantity, Current Price, Total Value, Gain/Loss
- **And** shows:
  - AAPL: 10 shares, $150.00, $1,500.00, [gain/loss from cost basis]
  - TSLA: 5 shares, $800.00, $4,000.00, [gain/loss from cost basis]
  - GOOGL: 20 shares, $2,800.00, $56,000.00, [gain/loss from cost basis]
- **And** a total portfolio value row at bottom: $61,500.00

**AC2: Empty Holdings Display**
- **Given** I have not purchased any shares
- **When** I view the holdings section
- **Then** the system displays: "No holdings. Start trading to build your portfolio!"
- **And** shows an empty table with column headers

**AC3: Real-Time Price Updates**
- **Given** I am viewing my holdings
- **When** stock prices change (simulated or refreshed)
- **Then** the Current Price and Total Value columns update automatically
- **And** the Gain/Loss column recalculates
- **And** displays refresh timestamp: "Last updated: [timestamp]"

**AC4: Gain/Loss Calculation**
- **Given** I bought 10 AAPL shares at average cost $140/share and current price is $150
- **When** I view holdings
- **Then** the Gain/Loss column shows: "+$100.00 (+7.14%)" in green
- **And** if the current price were $130, shows: "-$100.00 (-7.14%)" in red

**AC5: Multiple Purchases Cost Basis**
- **Given** I bought 5 AAPL shares at $140, then 5 more at $160 (average: $150)
- **When** I view holdings with current price $155
- **Then** Gain/Loss is calculated against average cost basis of $150
- **And** shows: "+$50.00 (+3.33%)"

**AC6: Sortable Columns**
- **Given** I have multiple holdings
- **When** I click on a column header (e.g., "Total Value")
- **Then** the table sorts by that column (descending then ascending on repeated clicks)
- **And** shows sort indicator (↑/↓) next to column name

**AC7: Holdings Summary Statistics**
- **Given** I have a diversified portfolio
- **When** I view the holdings section
- **Then** the system displays summary cards showing:
  - Total Portfolio Value: $[sum of all holdings + cash]
  - Total Invested: $[sum of all purchase costs]
  - Total Cash: $[available cash balance]
  - Overall Gain/Loss: $[portfolio value - total invested] ([percentage])

---

**UI/UX Specifications:**

**Gradio Components:**
```python
with gr.Blocks() as portfolio_view:
    gr.Markdown("## Portfolio Holdings")
    
    with gr.Row():
        gr.Markdown("**Total Portfolio Value:** $0.00")
        gr.Markdown("**Total Cash:** $0.00")
        gr.Markdown("**Overall Gain/Loss:** $0.00 (0.00%)")
    
    holdings_table = gr.DataFrame(
        headers=["Symbol", "Quantity", "Avg Cost", "Current Price", "Total Value", "Gain/Loss", "Gain/Loss %"],
        datatype=["str", "number", "number", "number", "number", "str", "str"],
        label="Current Holdings",
        interactive=False,
        wrap=True
    )
    
    refresh_btn = gr.Button("Refresh Prices", size="sm")
    last_updated = gr.Markdown("*Last updated: [timestamp]*")
```

**Component Behaviors:**
- Table: Auto-scrollable on mobile, fixed headers on desktop
- Gain/Loss cells: Green background for positive, red for negative
- Refresh button: Fetches latest prices, shows loading spinner
- Empty state: Display call-to-action button "Start Trading"

**Visual Design:**
- Positive gains: Green text (#10b981)
- Losses: Red text (#ef4444)
- Neutral: Gray text (#6b7280)
- Currency formatting: $1,234.56 with commas
- Percentage formatting: +7.14% or -3.25%

**Accessibility:**
- Table headers clearly labeled
- Color-blind friendly: Use +/- symbols in addition to colors
- Screen reader descriptions for gain/loss percentages
- Keyboard navigation through table rows

---

**Technical Notes:**
- Calculate average cost basis: sum(purchase_price × quantity) / total_quantity
- Retrieve current prices via `get_share_price(symbol)`
- Gain/Loss = (current_price - avg_cost) × quantity
- Gain/Loss % = ((current_price - avg_cost) / avg_cost) × 100
- Update holdings in real-time or on-demand via refresh
- Cache prices for 30 seconds to reduce API calls

**Dependencies:**
- US-004 (Buy Shares) - to have holdings
- US-005 (Sell Shares) - affects holdings display

**Definition of Done:**
- [ ] All acceptance criteria met
- [ ] Unit tests for gain/loss calculations
- [ ] Integration tests with multiple buy/sell scenarios
- [ ] UI displays all columns correctly formatted
- [ ] Sorting functionality works
- [ ] Empty state displays properly
- [ ] Accessibility verified
- [ ] Code reviewed and merged

**Out of Scope:**
- Charts or graphs of holdings distribution
- Export to CSV/PDF
- Historical holdings snapshots
- Watchlist functionality
- Price alerts

---

#### **US-007: View Profit/Loss Report**

**Story ID:** US-007  
**Title:** Calculate and Display Overall Profit/Loss  
**Priority:** Medium  
**Story Points Guidance:** 3

**User Story:**  
As a trading simulator user, I want to see my overall profit or loss from my initial deposit, so that I can evaluate my trading performance.

**Business Value:**  
Provides key performance metric helping users assess trading strategy effectiveness.

---

**Acceptance Criteria:**

**AC1: Profit Calculation**
- **Given** I started with $10,000 initial deposit
- **And** I have $12,500 current portfolio value (cash + holdings)
- **When** I view the profit/loss report
- **Then** the system displays: "Total Profit: +$2,500.00 (+25.00%)" in green
- **And** shows breakdown: Initial Investment: $10,000.00, Current Value: $12,500.00

**AC2: Loss Calculation**
- **Given** I started with $10,000 and current portfolio value is $8,000
- **When** I view the profit/loss report
- **Then** the system displays: "Total Loss: -$2,000.00 (-20.00%)" in red
- **And** shows motivational message: "Keep learning! Every trader faces losses."

**AC3: Break-Even State**
- **Given** my current portfolio value equals my initial deposit
- **When** I view the report
- **Then** the system displays: "Break Even: $0.00 (0.00%)" in gray

**AC4: Including Additional Deposits**
- **Given** I started with $10,000, deposited $5,000 more (total capital: $15,000)
- **And** current portfolio value is $17,000
- **When** I view the profit/loss report
- **Then** the system calculates profit against total capital: "+$2,000.00 (+13.33%)"
- **And** shows: Total Capital Invested: $15,000.00

**AC5: After Withdrawals**
- **Given** I started with $10,000, withdrew $3,000 (net capital: $7,000)
- **And** current portfolio value is $9,000
- **When** I view the report
- **Then** profit is calculated as: $9,000 - $7,000 = +$2,000.00 (+28.57%)
- **And** shows: Net Capital Invested: $7,000.00, Withdrawn: $3,000.00

**AC6: Performance Metrics**
- **Given** I have an active trading history
- **When** I view the profit/loss report
- **Then** additional metrics are displayed:
  - Total Trades Executed: [count]
  - Winning Trades: [count] ([percentage])
  - Losing Trades: [count] ([percentage])
  - Largest Gain: $[amount] on [symbol]
  - Largest Loss: $[amount] on [symbol]

---

**UI/UX Specifications:**

**Gradio Components:**
```python
with gr.Blocks() as profit_loss_report:
    gr.Markdown("## Profit/Loss Report")
    
    with gr.Row():
        gr.Column():
            gr.Markdown("### Overall Performance")
            total_capital_display = gr.Markdown("**Total Capital Invested:** $0.00")
            current_value_display = gr.Markdown("**Current Portfolio Value:** $0.00")
            profit_loss_display = gr.Markdown("**Profit/Loss:** $0.00 (0.00%)")
        
        gr.Column():
            gr.Markdown("### Trading Statistics")
            total_trades = gr.Markdown("**Total Trades:** 0")
            win_rate = gr.Markdown("**Win Rate:** 0.00%")
            best_trade = gr.Markdown("**Best Trade:** N/A")
            worst_trade = gr.Markdown("**Worst Trade:** N/A")
    
    gr.Plot()  # Optional: Visual chart of performance over time
```

**Component Behaviors:**
- Profit/Loss display: Large, prominent font with color coding
- Performance chart: Line graph showing portfolio value over time
- Refresh button: Updates calculations with latest prices
- "Reset Simulation" button: Clears all data (with confirmation)

**Visual Design:**
- Profit: Green with upward arrow ↑
- Loss: Red with downward arrow ↓
- Break-even: Gray with horizontal line →
- Percentage in parentheses next to dollar amount

**Accessibility:**
- Clear labels for all metrics
- Color-coded values also have symbols (+/-)
- Chart includes alt text description of trend

---

**Technical Notes:**
- Total capital = initial_deposit + sum(deposits) - sum(withdrawals)
- Current value = available_cash + sum(holdings_current_value)
- Profit/Loss = current_value - total_capital
- Percentage = (profit_loss / total_capital) × 100
- Track individual trade outcomes for win/loss statistics
- Consider realized vs. unrealized gains in advanced version

**Dependencies:**
- US-001 (Account Creation) - for initial deposit
- US-002 (Deposit Funds) - affects capital calculation
- US-003 (Withdraw Funds) - affects capital calculation
- US-004 (Buy Shares) - affects portfolio value
- US-005 (Sell Shares) - affects portfolio value
- US-006 (View Holdings) - for current value calculation

**Definition of Done:**
- [ ] All acceptance criteria validated
- [ ] Unit tests for profit/loss calculations
- [ ] Integration tests with various deposit/withdrawal scenarios
- [ ] UI displays all metrics correctly
- [ ] Color coding and formatting correct
- [ ] Accessibility verified
- [ ] Code reviewed and merged

**Out of Scope:**
- Time-weighted returns
- Benchmark comparisons (e.g., vs. S&P 500)
- Tax implications
- Dividend tracking
- Historical performance charts

---

#### **US-008: View Transaction History**

**Story ID:** US-008  
**Title:** Display Complete Transaction History  
**Priority:** Medium  
**Story Points Guidance:** 3

**User Story:**  
As a trading simulator user, I want to view a complete history of all my transactions over time, so that I can review my trading decisions and learn from past actions.

**Business Value:**  
Provides transparency and audit trail, enabling users to analyze trading patterns and improve strategies.

---

**Acceptance Criteria:**

**AC1: Complete Transaction List**
- **Given** I have performed multiple transactions (deposits, withdrawals, buys, sells)
- **When** I view the transaction history
- **Then** the system displays all transactions in reverse chronological order (newest first)
- **And** each entry shows: Date/Time, Type, Symbol (if applicable), Quantity, Price, Amount, Balance After

**AC2: Transaction Type Filtering**
- **Given** I am viewing transaction history
- **When** I select a filter (e.g., "Buy Trades Only")
- **Then** the system displays only BUY transactions
- **And** filter options include: All, Deposits, Withdrawals, Buys, Sells

**AC3: Date Range Filtering**
- **Given** I have a long transaction history
- **When** I select a date range (e.g., "Last 30 Days")
- **Then** the system displays only transactions within that period
- **And** shows transaction count: "Showing 15 transactions from [start_date] to [end_date]"

**AC4: Symbol-Specific History**
- **Given** I select "AAPL" from a symbol filter
- **When** viewing transaction history
- **Then** the system shows only transactions involving AAPL
- **And** displays statistics: Total AAPL bought: 50 shares, Total sold: 20 shares, Net position: 30 shares

**AC5: Empty History Display**
- **Given** I have a new account with no transactions
- **When** I view transaction history
- **Then** the system displays: "No transactions yet. Start trading to see your history here!"

**AC6: Transaction Details Expansion**
- **Given** I am viewing the transaction list
- **When** I click on a transaction row
- **Then** an expanded panel shows additional details:
  - Transaction ID
  - Exact timestamp (with seconds)
  - Current value of holding (for trades)
  - Realized gain/loss (for sells)
  - Running balance after transaction

**AC7: Export Functionality**
- **Given** I am viewing transaction history
- **When** I click "Export CSV"
- **Then** the system downloads a CSV file with all visible transactions
- **And** includes all columns in a formatted spreadsheet

**AC8: Pagination**
- **Given** I have more than 50 transactions
- **When** I view transaction history
- **Then** transactions are paginated with 50 per page
- **And** navigation controls allow moving between pages
- **And** shows: "Page 1 of 3 (150 total transactions)"

---

**UI/UX Specifications:**

**Gradio Components:**
```python
with gr.Blocks() as transaction_history:
    gr.Markdown("## Transaction History")
    
    with gr.Row():
        type_filter = gr.Dropdown(
            label="Transaction Type",
            choices=["All", "Deposits", "Withdrawals", "Buys", "Sells"],
            value="All"
        )
        symbol_filter = gr.Dropdown(
            label="Symbol",
            choices=["All", "AAPL", "TSLA", "GOOGL"],
            value="All"
        )
        date_range = gr.Dropdown(
            label="Date Range",
            choices=["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"],
            value="All Time"
        )
    
    export_btn = gr.Button("Export CSV", size="sm")
    
    transactions_table = gr.DataFrame(
        headers=["Date/Time", "Type", "Symbol", "Quantity", "Price", "Amount", "Balance"],
        datatype=["str", "str", "str", "number", "number", "number", "number"],
        label="Transactions",
        interactive=False,
        max_rows=50
    )
    
    transaction_count = gr.Markdown("*Showing 0 transactions*")
```

**Component Behaviors:**
- Filters: Apply immediately on selection
- Table rows: Clickable to expand details
- Export button: Downloads CSV with current filter applied
- Type column: Color-coded badges (green for deposits/sells, red for withdrawals/buys)
- Responsive: Horizontal scroll on mobile

**Visual Design:**
- Transaction types with icons:
  - Deposit: 💰 (green)
  - Withdrawal: 💸 (red)
  - Buy: 📈 (blue)
  - Sell: 📉 (orange)
- Alternating row colors for readability
- Hover effect on rows

**Accessibility:**
- Table navigable via keyboard
- Screen reader announces transaction type and amount
- Filters labeled clearly
- Export CSV includes headers

---

**Technical Notes:**
- Store all transactions with fields: id, timestamp, type, symbol, quantity, price, amount, balance_after
- Index transactions by type, symbol, and date for efficient filtering
- Pagination on backend to avoid loading all transactions at once
- CSV export uses standard format compatible with Excel/Google Sheets
- Consider archiving old transactions after 1 year (keep in DB, hide from UI by default)

**Dependencies:**
- US-001 (Account Creation)
- US-002 (Deposit Funds)
- US-003 (Withdraw Funds)
- US-004 (Buy Shares)
- US-005 (Sell Shares)

**Definition of Done:**
- [ ] All acceptance criteria met
- [ ] Unit tests for filtering logic
- [ ] Integration tests with various transaction types
- [ ] UI displays transactions correctly formatted
- [ ] Filters work correctly individually and combined
- [ ] Export CSV functionality tested
- [ ] Pagination works correctly
- [ ] Accessibility verified
- [ ] Code reviewed and merged

**Out of Scope:**
- Search by amount or keyword
- Transaction editing or deletion
- Recurring transactions
- Transaction categories or tags
- Import from CSV
- Multi-account consolidation

---

## Story Dependencies

### Critical Path (Must implement in order):
1. **US-001** (Account Creation) → Foundation
2. **US-002** (Deposit Funds) → Enables initial capital
3. **US-004** (Buy Shares) → Core trading functionality
4. **US-005** (Sell Shares) → Complete trading cycle
5. **US-006** (View Holdings) → Portfolio visibility

### Parallel Development Opportunities:
- **US-003** (Withdraw Funds) can be developed alongside US-002
- **US-007** (Profit/Loss Report) and **US-008** (Transaction History) can be built in parallel after core trading features (US-004, US-005)

### Dependency Graph:
```
US-001 (Account Creation)
  ├── US-002 (Deposit Funds)
  ├── US-003 (Withdraw Funds) [depends on US-002]
  ├── US-004 (Buy Shares) [depends on US-002]
  │     ├── US-005 (Sell Shares) [depends on US-004]
  │     └── US-006 (View Holdings) [depends on US-004]
  ├── US-007 (Profit/Loss) [depends on US-002, US-003, US-004, US-005, US-006]
  └── US-008 (Transaction History) [depends on all above]
```

---

## Non-Functional Requirements

### Performance
- All operations complete within 2 seconds
- UI updates in real-time (<500ms)
- Support up to 1,000 transactions without performance degradation

### Security
- Input validation on all user-entered data
- Prevent SQL injection and XSS attacks
- Sanitize all outputs displayed to users

### Accessibility (WCAG 2.1 Level AA)
- Keyboard navigation for all features
- Screen reader compatible
- Color contrast ratio ≥4.5:1
- ARIA labels on all interactive elements

### Browser Compatibility
- Gradio-supported browsers (Chrome, Firefox, Safari, Edge)
- Responsive design for mobile (≥375px width) and desktop (≥1024px)

### Data Integrity
- Atomic transactions (all-or-nothing updates)
- Balance calculations always accurate to 2 decimal places
- No orphaned holdings or transactions

---

**Document End**
