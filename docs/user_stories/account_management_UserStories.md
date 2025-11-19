# User Stories — Account Management System

## Story 1: User Account Creation

**ID:** AM-1  
**Title:** Create a new user account  
**User Story:** As a new user, I want to create an account so that I can participate in trading simulations and manage my portfolio.  
**Business Value:** Enables onboarding and unique user tracking.  
**Priority:** High

### Acceptance Criteria (BDD)
- **Given** I am on the account creation screen, **when** I enter a valid username and click "Create Account", **then** I see a success message: "Account created successfully."
- **Given** I enter a username that already exists, **when** I click "Create Account", **then** I see an error message: "Username already exists. Please choose another."
- **Given** I leave the username field blank, **when** I click "Create Account", **then** I see an error message: "Username is required."

### UI/UX Specs
- Gradio `Textbox` for username input
- Gradio `Button` for account creation
- Success/Error messages displayed in a Gradio `Alert` or `Text` component
- Accessibility: All form fields labeled, keyboard navigation supported

---

## Story 2: Deposit Funds

**ID:** AM-2  
**Title:** Deposit funds into account  
**User Story:** As a user, I want to deposit funds into my account so that I can buy shares.  
**Business Value:** Enables trading activity and portfolio growth.  
**Priority:** High

### Acceptance Criteria (BDD)
- **Given** I am logged in, **when** I enter a positive deposit amount and click "Deposit", **then** I see a success message: "Deposit successful. New balance: $X.XX."
- **Given** I enter a negative or zero amount, **when** I click "Deposit", **then** I see an error message: "Deposit amount must be greater than zero."
- **Given** I leave the amount field blank, **when** I click "Deposit", **then** I see an error message: "Amount is required."

### UI/UX Specs
- Gradio `Number` input for deposit amount
- Gradio `Button` for deposit action
- Success/Error messages displayed in a Gradio `Alert` or `Text` component
- Accessibility: Form fields labeled, error messages announced for screen readers

---

## Story 3: Withdraw Funds

**ID:** AM-3  
**Title:** Withdraw funds from account  
**User Story:** As a user, I want to withdraw funds from my account so that I can access my cash, but withdrawals that would result in a negative balance must be prevented.  
**Business Value:** Supports realistic cash management and prevents overdrafts.  
**Priority:** High

### Acceptance Criteria (BDD)
- **Given** I am logged in, **when** I enter a withdrawal amount less than or equal to my cash balance and click "Withdraw", **then** I see a success message: "Withdrawal successful. New balance: $X.XX."
- **Given** I enter an amount greater than my cash balance, **when** I click "Withdraw", **then** I see an error message: "Insufficient funds. Cannot withdraw more than available balance."
- **Given** I enter a negative or zero amount, **when** I click "Withdraw", **then** I see an error message: "Withdrawal amount must be greater than zero."
- **Given** I leave the amount field blank, **when** I click "Withdraw", **then** I see an error message: "Amount is required."

### UI/UX Specs
- Gradio `Number` input for withdrawal amount
- Gradio `Button` for withdrawal action
- Success/Error messages displayed in a Gradio `Alert` or `Text` component
- Accessibility: Form fields labeled, error messages announced for screen readers

---

## Story 4: Record Buy/Sell Transactions

**ID:** AM-4  
**Title:** Record buy and sell share transactions  
**User Story:** As a user, I want to record buy and sell transactions for shares so that my portfolio and cash balance are updated accordingly.  
**Business Value:** Enables trading simulation and portfolio management.  
**Priority:** High

### Acceptance Criteria (BDD)
- **Given** I am logged in, **when** I enter a valid symbol, quantity, and price for a buy transaction and have sufficient cash, **then** I see a success message: "Buy transaction recorded."
- **Given** I do not have enough cash for a buy transaction, **when** I click "Buy", **then** I see an error message: "Insufficient cash to complete purchase."
- **Given** I enter a valid symbol, quantity, and price for a sell transaction and have enough shares, **then** I see a success message: "Sell transaction recorded."
- **Given** I do not have enough shares for a sell transaction, **when** I click "Sell", **then** I see an error message: "Insufficient shares to complete sale."
- **Given** I leave any field blank, **when** I click "Buy" or "Sell", **then** I see an error message: "All fields are required."

### UI/UX Specs
- Gradio `Dropdown` for symbol selection (AAPL, TSLA, GOOGL)
- Gradio `Number` input for quantity and price
- Gradio `Button` for Buy/Sell actions
- Success/Error messages displayed in a Gradio `Alert` or `Text` component
- Accessibility: All controls labeled, error messages announced for screen readers

---

## Story 5: View Portfolio Value

**ID:** AM-5  
**Title:** View total portfolio value  
**User Story:** As a user, I want to view the total value of my portfolio using current share prices so that I can track my net worth.  
**Business Value:** Provides real-time feedback on investment performance.  
**Priority:** Medium

### Acceptance Criteria (BDD)
- **Given** I am logged in, **when** I click "View Portfolio Value", **then** I see my total portfolio value displayed: "Portfolio value: $X.XX."
- **Given** I have no holdings, **when** I click "View Portfolio Value", **then** I see: "Portfolio value: $0.00."

### UI/UX Specs
- Gradio `Button` for viewing portfolio value
- Gradio `Text` component for displaying value
- Accessibility: Value announced for screen readers

---

## Story 6: View Profit/Loss

**ID:** AM-6  
**Title:** View current profit or loss  
**User Story:** As a user, I want to view my current profit or loss relative to my initial deposit so that I can assess my trading performance.  
**Business Value:** Enables users to track performance and make informed decisions.  
**Priority:** Medium

### Acceptance Criteria (BDD)
- **Given** I am logged in, **when** I click "View Profit/Loss", **then** I see: "Current profit/loss: $X.XX."
- **Given** I have no transactions, **when** I click "View Profit/Loss", **then** I see: "Current profit/loss: $0.00."

### UI/UX Specs
- Gradio `Button` for viewing profit/loss
- Gradio `Text` component for displaying result
- Accessibility: Value announced for screen readers

---

## Story 7: View Holdings

**ID:** AM-7  
**Title:** View current share holdings  
**User Story:** As a user, I want to view my current share holdings so that I know which symbols and quantities I own.  
**Business Value:** Improves transparency and user control.  
**Priority:** Medium

### Acceptance Criteria (BDD)
- **Given** I am logged in, **when** I click "View Holdings", **then** I see a list of symbols and quantities: "Holdings: AAPL: 10, TSLA: 5, GOOGL: 0."
- **Given** I have no holdings, **when** I click "View Holdings", **then** I see: "No holdings."

### UI/UX Specs
- Gradio `Button` for viewing holdings
- Gradio `Text` or `Dataframe` for displaying holdings
- Accessibility: Holdings announced for screen readers

---

## Story 8: View Transaction History

**ID:** AM-8  
**Title:** View transaction history  
**User Story:** As a user, I want to view my transaction history in chronological order so that I can review my trading activity.  
**Business Value:** Enables auditability and learning from past trades.  
**Priority:** Medium

### Acceptance Criteria (BDD)
- **Given** I am logged in, **when** I click "View Transactions", **then** I see a list of transactions ordered by timestamp.
- **Given** I have no transactions, **when** I click "View Transactions", **then** I see: "No transactions recorded."

### UI/UX Specs
- Gradio `Button` for viewing transactions
- Gradio `Dataframe` or `Text` for displaying transaction list
- Accessibility: Transaction list announced for screen readers

---

## Non-Functional Requirements
- All user-facing messages must be visible in the Gradio UI and testable by QA.
- Accessibility: All controls labeled, error messages and values announced for screen readers.
- Performance: All actions should complete within 2 seconds under normal load.
- Security: No sensitive data exposed in UI; only show relevant account info to logged-in user.
- Out of Scope: Currency precision (cents), concurrency, external brokerage integration.
