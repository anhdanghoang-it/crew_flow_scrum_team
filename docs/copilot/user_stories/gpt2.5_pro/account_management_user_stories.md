# Account Management User Stories

This document outlines the user stories for the Account Management feature of the trading simulation platform.

---

### **Story Header**
- **Story ID**: US-001
- **Title**: Create a New User Account
- **User Story**: As a new user, I want to create an account with an initial deposit, so that I can start using the trading simulation platform.
- **Business Value**: High
- **Priority**: High
- **Story Points Estimation**: 3

### **Acceptance Criteria**
- **Given** a new user is on the account creation page
- **When** they enter a unique username and an initial deposit amount greater than zero
- **Then** a new account is created for them with the specified balance.
- **And** they receive a success message: "Account created successfully for [username]".

- **Given** a new user is on the account creation page
- **When** they enter a username that already exists
- **Then** the system shows an error message: "Username [username] is already taken. Please choose another one."
- **And** the account is not created.

- **Given** a new user is on the account creation page
- **When** they enter an initial deposit of zero or a negative amount
- **Then** the system shows an error message: "Initial deposit must be greater than zero."
- **And** the account is not created.

### **UI/UX Specifications**
- **Interface**: A simple form in a Gradio interface.
- **Components**:
  - `gr.Textbox` for the username, labeled "Username".
  - `gr.Number` for the initial deposit, labeled "Initial Deposit".
  - `gr.Button` to submit, labeled "Create Account".
  - `gr.Textbox` or `gr.Markdown` to display success or error messages.
- **Layout**: Components arranged vertically using `gr.Blocks`.

### **Technical Notes**
- The system must ensure that usernames are unique.
- The initial deposit will be the first transaction recorded for the user.

### **Definition of Done**
- All acceptance criteria are met.
- Unit tests are written for account creation, including edge cases.
- The Gradio interface is functional and meets UI/UX specifications.

### **Out of Scope**
- User authentication (login/logout).
- Password management.

---

### **Story Header**
- **Story ID**: US-002
- **Title**: Deposit Funds
- **User Story**: As a registered user, I want to deposit funds into my account, so that I can increase my trading capital.
- **Business Value**: High
- **Priority**: High
- **Story Points Estimation**: 2

### **Acceptance Criteria**
- **Given** a registered user is on the deposit funds page
- **When** they enter a deposit amount greater than zero
- **Then** their account balance is increased by that amount.
- **And** they receive a success message: "Successfully deposited [amount]. Your new balance is [new_balance]."

- **Given** a registered user is on the deposit funds page
- **When** they enter a deposit amount of zero or a negative number
- **Then** the system shows an error message: "Deposit amount must be greater than zero."
- **And** the balance remains unchanged.

### **UI/UX Specifications**
- **Interface**: A simple form in the Gradio interface.
- **Components**:
  - `gr.Textbox` for the username (or a way to select the current user).
  - `gr.Number` for the deposit amount, labeled "Deposit Amount".
  - `gr.Button` to submit, labeled "Deposit".
  - `gr.Textbox` or `gr.Markdown` for messages.
- **Layout**: Vertical layout using `gr.Blocks`.

### **Technical Notes**
- A transaction record for the deposit should be created.

### **Definition of Done**
- All acceptance criteria are met.
- Unit tests for the deposit functionality are implemented.
- The Gradio interface is functional.

### **Out of Scope**
- Integration with real payment gateways.

---

### **Story Header**
- **Story ID**: US-003
- **Title**: Withdraw Funds
- **User Story**: As a registered user, I want to withdraw funds from my account, so that I can access my money.
- **Business Value**: Medium
- **Priority**: Medium
- **Story Points Estimation**: 3

### **Acceptance Criteria**
- **Given** a registered user with a positive account balance
- **When** they request to withdraw an amount less than or equal to their balance
- **Then** their account balance is decreased by that amount.
- **And** they receive a success message: "Successfully withdrew [amount]. Your new balance is [new_balance]."

- **Given** a registered user
- **When** they request to withdraw an amount greater than their current balance
- **Then** the system shows an error message: "Insufficient funds. Your balance is [balance]."
- **And** the balance remains unchanged.

- **Given** a registered user
- **When** they request to withdraw a zero or negative amount
- **Then** the system shows an error message: "Withdrawal amount must be greater than zero."
- **And** the balance remains unchanged.

### **UI/UX Specifications**
- **Interface**: A simple form in the Gradio interface.
- **Components**:
  - `gr.Textbox` for the username.
  - `gr.Number` for the withdrawal amount, labeled "Withdrawal Amount".
  - `gr.Button` to submit, labeled "Withdraw".
  - `gr.Textbox` or `gr.Markdown` for messages.
- **Layout**: Vertical layout using `gr.Blocks`.

### **Technical Notes**
- A transaction record for the withdrawal should be created.

### **Definition of Done**
- All acceptance criteria are met.
- Unit tests for the withdrawal functionality, including insufficient funds scenario, are implemented.
- The Gradio interface is functional.

### **Out of Scope**
- Transferring funds to a real bank account.

---

### **Story Header**
- **Story ID**: US-004
- **Title**: Buy Shares
- **User Story**: As a registered user, I want to buy shares of a stock, so that I can build my investment portfolio.
- **Business Value**: High
- **Priority**: High
- **Story Points Estimation**: 5

### **Acceptance Criteria**
- **Given** a registered user with sufficient funds
- **When** they place an order to buy a quantity of shares for a specific symbol
- **Then** the cost of the shares is deducted from their account balance.
- **And** the shares are added to their portfolio.
- **And** they receive a success message: "Successfully bought [quantity] shares of [symbol] for [total_cost]."

- **Given** a registered user
- **When** they place an order to buy shares, but the total cost exceeds their balance
- **Then** the system shows an error message: "Insufficient funds to buy [quantity] shares of [symbol]. Required: [total_cost], Balance: [balance]."
- **And** the transaction is not executed.

- **Given** a registered user
- **When** they try to buy shares of an invalid stock symbol
- **Then** the system shows an error message: "Invalid stock symbol: [symbol]."
- **And** the transaction is not executed.

### **UI/UX Specifications**
- **Interface**: A form in the Gradio interface.
- **Components**:
  - `gr.Textbox` for the username.
  - `gr.Textbox` for the stock symbol (e.g., "AAPL"), labeled "Stock Symbol".
  - `gr.Number` for the quantity, labeled "Quantity".
  - `gr.Button` to submit, labeled "Buy".
  - `gr.Textbox` or `gr.Markdown` for messages.
- **Layout**: Vertical layout.

### **Technical Notes**
- The system needs to call `get_share_price(symbol)` to determine the cost.
- A "buy" transaction must be recorded.

### **Definition of Done**
- All acceptance criteria are met.
- Unit tests for buying shares, including insufficient funds and invalid symbol cases, are implemented.
- The Gradio interface is functional.

### **Out of Scope**
- Real-time stock price updates within the UI.
- Market order vs. limit order types.

---

### **Story Header**
- **Story ID**: US-005
- **Title**: Sell Shares
- **User Story**: As a registered user, I want to sell shares of a stock that I own, so that I can realize profits or cut losses.
- **Business Value**: High
- **Priority**: High
- **Story Points Estimation**: 5

### **Acceptance Criteria**
- **Given** a registered user who owns a sufficient quantity of shares of a stock
- **When** they place an order to sell a quantity of those shares
- **Then** the proceeds from the sale are added to their account balance.
- **And** the shares are removed from their portfolio.
- **And** they receive a success message: "Successfully sold [quantity] shares of [symbol] for [total_proceeds]."

- **Given** a registered user
- **When** they place an order to sell more shares than they own
- **Then** the system shows an error message: "You cannot sell more shares than you own. You have [owned_quantity] shares of [symbol]."
- **And** the transaction is not executed.

- **Given** a registered user
- **When** they try to sell shares of a stock they do not own
- **Then** the system shows an error message: "You do not own any shares of [symbol]."
- **And** the transaction is not executed.

### **UI/UX Specifications**
- **Interface**: A form in the Gradio interface.
- **Components**:
  - `gr.Textbox` for the username.
  - `gr.Textbox` for the stock symbol, labeled "Stock Symbol".
  - `gr.Number` for the quantity, labeled "Quantity".
  - `gr.Button` to submit, labeled "Sell".
  - `gr.Textbox` or `gr.Markdown` for messages.
- **Layout**: Vertical layout.

### **Technical Notes**
- The system needs to call `get_share_price(symbol)` to determine the proceeds.
- A "sell" transaction must be recorded.

### **Definition of Done**
- All acceptance criteria are met.
- Unit tests for selling shares, including insufficient shares cases, are implemented.
- The Gradio interface is functional.

### **Out of Scope**
- Short selling.

---

### **Story Header**
- **Story ID**: US-006
- **Title**: View Portfolio Holdings
- **User Story**: As a registered user, I want to view my current portfolio holdings, so that I can see all the shares I own and their current value.
- **Business Value**: High
- **Priority**: High
- **Story Points Estimation**: 3

### **Acceptance Criteria**
- **Given** a registered user who owns shares in one or more stocks
- **When** they request to see their portfolio
- **Then** the system displays a list of their holdings.
- **For each holding**, the display includes:
  - Stock Symbol
  - Quantity of shares owned
  - Current price per share
  - Total current value of the holding (Quantity * Current Price)
- **And** the system displays the total value of the entire portfolio.

- **Given** a registered user who owns no shares
- **When** they request to see their portfolio
- **Then** the system displays a message: "Your portfolio is empty."

### **UI/UX Specifications**
- **Interface**: A display area in the Gradio interface.
- **Components**:
  - `gr.Textbox` for the username.
  - `gr.Button` labeled "View Portfolio".
  - `gr.DataFrame` or `gr.Markdown` to display the holdings in a tabular format.
  - A `gr.Textbox` or `gr.Markdown` to show the total portfolio value.
- **Layout**: A button to trigger the view, with the results displayed below.

### **Technical Notes**
- Requires calling `get_share_price(symbol)` for each stock in the portfolio to calculate current values.

### **Definition of Done**
- All acceptance criteria are met.
- The Gradio interface correctly displays the portfolio.

### **Out of Scope**
- Historical portfolio value charts.

---

### **Story Header**
- **Story ID**: US-007
- **Title**: View Profit/Loss
- **User Story**: As a registered user, I want to view my overall profit or loss, so that I can track my investment performance.
- **Business Value**: High
- **Priority**: Medium
- **Story Points Estimation**: 4

### **Acceptance Criteria**
- **Given** a registered user has an account
- **When** they request to see their profit or loss
- **Then** the system calculates and displays the total profit or loss.
- **The calculation** is: (Current Portfolio Value + Current Cash Balance) - Total Funds Deposited.

### **UI/UX Specifications**
- **Interface**: A display area in the Gradio interface.
- **Components**:
  - `gr.Textbox` for the username.
  - `gr.Button` labeled "View Profit/Loss".
  - `gr.Textbox` or `gr.Markdown` to display the result, clearly indicating whether it's a profit or a loss (e.g., "Total Profit: $500" or "Total Loss: -$250").
- **Layout**: A button to trigger the calculation, with the result displayed below.

### **Technical Notes**
- This calculation requires knowing the total amount of money the user has ever deposited.
- It also requires calculating the current total portfolio value.

### **Definition of Done**
- All acceptance criteria are met.
- The calculation is accurate.
- The Gradio interface correctly displays the profit/loss.

### **Out of Scope**
- Profit/loss broken down by individual stock.
- Time-weighted returns.

---

### **Story Header**
- **Story ID**: US-008
- **Title**: View Transaction History
- **User Story**: As a registered user, I want to view a list of all my past transactions, so that I can review my trading activity.
- **Business Value**: Medium
- Priority: Medium
- **Story Points Estimation**: 3

### **Acceptance Criteria**
- **Given** a registered user has made one or more transactions
- **When** they request to see their transaction history
- **Then** the system displays a chronological list of all their transactions.
- **For each transaction**, the display includes:
  - Date/Time
  - Transaction Type (e.g., "Deposit", "Withdrawal", "Buy", "Sell")
  - Description (e.g., "Bought 10 shares of AAPL", "Deposited $1000")
  - Amount or Value
  - Account balance after the transaction.

- **Given** a new registered user has made no transactions (other than initial deposit)
- **When** they request to see their transaction history
- **Then** the system displays only the initial deposit transaction.

### **UI/UX Specifications**
- **Interface**: A display area in the Gradio interface.
- **Components**:
  - `gr.Textbox` for the username.
  - `gr.Button` labeled "View Transaction History".
  - `gr.DataFrame` or `gr.Markdown` to display the transaction list in a table.
- **Layout**: A button to trigger the view, with the transaction history displayed below.

### **Technical Notes**
- The system must persist a record of every financial event.

### **Definition of Done**
- All acceptance criteria are met.
- The Gradio interface correctly displays the transaction history.

### **Out of Scope**
- Filtering or searching transaction history.
- Exporting transaction history.
