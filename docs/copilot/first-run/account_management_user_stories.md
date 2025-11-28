# Account Management & Trading Simulation – User Stories

## US-001 – Create Trading Account

**User Story**  
As a new platform user, I want to create a trading account, so that I can participate in the trading simulation and track my portfolio and cash balance.

**Business Value / Priority**  
- Value: High – foundation for all other features  
- Priority: High  
- Estimation guidance: 3–5 story points (backend + basic UI)

**Acceptance Criteria (BDD)**
- **AC1 – Successful account creation**  
  - Given I am on the "Create Account" screen  
    And I have entered a unique username and an optional display name  
  - When I click the `Create Account` button  
  - Then a new account is created with:  
    - Cash balance = 0  
    - No holdings  
    - No transactions  
    And I see a success message: `Account created successfully.`  
    And I am shown the account overview screen for this new account.

- **AC2 – Required field validation**  
  - Given I am on the "Create Account" screen  
  - When I click `Create Account` without providing a username  
  - Then the system does not create an account  
    And I see a validation error under the username field: `Username is required.`

- **AC3 – Duplicate username handling**  
  - Given an account already exists with username `alex`  
    And I am on the "Create Account" screen  
  - When I enter `alex` as the username and click `Create Account`  
  - Then the account is not created  
    And I see an error message: `Username already exists. Please choose another.`

- **AC4 – Technical errors**  
  - Given I have filled out all required fields correctly  
  - When an unexpected server error occurs during account creation  
  - Then the account is not created  
    And I see an error notification: `Unable to create account at the moment. Please try again later.`

**UI/UX Specifications**
- `Create Account` view implemented using Gradio `Blocks`:
  - `gr.Textbox` for `Username` (required, single line).  
    - Placeholder: `Enter a unique username`  
    - Label: `Username`  
  - `gr.Textbox` for `Display name` (optional).  
    - Placeholder: `Enter a display name (optional)`  
    - Label: `Display name`  
  - `gr.Button` labeled `Create Account`  
  - Feedback:
    - Use `gr.Info` for `Account created successfully.`  
    - Use `gr.Error` for validation or server errors.
- Layout:  
  - Single column form, centered in the main content area using `with gr.Row():` and `with gr.Column(scale=1):` pattern.  
- Accessibility:  
  - Labels associated with textboxes using Gradio’s built-in labeling.  
  - All actions reachable via keyboard (Tab to navigate, Enter/Space to activate `Create Account`).

**Technical Notes**
- Minimal account object fields: `account_id`, `username`, `display_name`, `cash_balance`, `holdings`, `transactions`, `created_at`.
- No external API dependencies.

**Definition of Done**
- User can create an account via UI and see the account overview.  
- Validation and error messages behave as described.  
- New accounts start with zero cash and no holdings/transactions.  
- Unit tests cover account creation logic and duplicate username validation.  
- Basic UI snapshot/interaction test exists for the create account flow.

**Out of Scope**
- Authentication/login or password management.  
- Profile editing (changing username or display name).  
- Multi-currency support.

---

## US-002 – Deposit Funds into Account

**User Story**  
As an account holder, I want to deposit funds into my trading account, so that I can use the deposited cash to buy shares in the simulation.

**Business Value / Priority**  
- Value: High – required for trading  
- Priority: High  
- Estimation guidance: 3–5 story points

**Acceptance Criteria (BDD)**
- **AC1 – Successful deposit**  
  - Given I am viewing my account overview  
  - When I enter a positive deposit amount (e.g., `1000`) and click `Deposit`  
  - Then my cash balance increases by that amount  
    And a deposit transaction is recorded with type `DEPOSIT`, amount, timestamp, and resulting balance  
    And I see a success message: `Deposit successful.`

- **AC2 – Amount validation (non-positive)**  
  - Given I am on the account overview  
  - When I enter `0` or a negative number as the deposit amount  
  - Then the deposit is not processed  
    And I see a validation error: `Deposit amount must be greater than 0.`

- **AC3 – Amount validation (non-numeric)**  
  - Given I am on the account overview  
  - When I enter non-numeric characters (e.g., `abc`)  
  - Then the deposit is not processed  
    And I see a validation error: `Enter a valid numeric amount.`

- **AC4 – Technical errors**  
  - Given I have entered a valid positive numeric amount  
  - When a server error occurs while saving the transaction  
  - Then the cash balance does not change  
    And I see an error: `Unable to process deposit at the moment. Please try again later.`

**UI/UX Specifications**
- On the `Account Overview` screen:
  - `gr.Number` or `gr.Textbox` for `Deposit amount`.  
    - Label: `Deposit amount`  
    - Placeholder: `Enter amount to deposit`  
  - `gr.Button` labeled `Deposit`  
  - Feedback:  
    - `gr.Info` for `Deposit successful.`  
    - `gr.Error` for validation and server errors.
- Show updated cash balance immediately after successful deposit.
- Accessibility: fields and button should be keyboard-accessible and screen reader friendly.

**Technical Notes**
- Balance update should be atomic to avoid race conditions in concurrent use (in memory or via DB transaction model as applicable).

**Definition of Done**
- Deposits correctly increase cash balance and create a transaction record.  
- Invalid inputs are rejected with clear messages.  
- Tests cover deposit logic, including boundary values and error handling.

**Out of Scope**
- Integration with real payment providers.  
- Multi-currency deposits.

---

## US-003 – Withdraw Funds with Non-Negative Balance Enforcement

**User Story**  
As an account holder, I want to withdraw funds from my trading account, so that I can simulate taking cash out, but the system must prevent my cash balance from going negative.

**Business Value / Priority**  
- Value: High – core money management  
- Priority: High  
- Estimation guidance: 3–5 story points

**Acceptance Criteria (BDD)**
- **AC1 – Successful withdrawal**  
  - Given my current cash balance is `1000`  
    And I am on the account overview screen  
  - When I enter `200` and click `Withdraw`  
  - Then my cash balance decreases to `800`  
    And a withdrawal transaction is recorded with type `WITHDRAWAL`, amount, timestamp, and resulting balance  
    And I see a success message: `Withdrawal successful.`

- **AC2 – Prevent negative balance**  
  - Given my current cash balance is `300`  
  - When I attempt to withdraw `400`  
  - Then the withdrawal is rejected  
    And my cash balance remains `300`  
    And I see an error message: `Insufficient funds. Withdrawal would result in a negative balance.`

- **AC3 – Amount validation**  
  - Given I am on the account overview screen  
  - When I enter `0`, a negative amount, or non-numeric input  
  - Then the withdrawal is not processed  
    And I see the appropriate validation message:  
      - `Withdrawal amount must be greater than 0.` for `0` or negative values  
      - `Enter a valid numeric amount.` for non-numeric values.

- **AC4 – Technical errors**  
  - Given I have entered a valid amount not exceeding my balance  
  - When a server error occurs while saving the withdrawal  
  - Then the cash balance does not change  
    And I see an error: `Unable to process withdrawal at the moment. Please try again later.`

**UI/UX Specifications**
- On the `Account Overview` screen:
  - `gr.Number` or `gr.Textbox` for `Withdrawal amount`.  
    - Label: `Withdrawal amount`  
    - Placeholder: `Enter amount to withdraw`  
  - `gr.Button` labeled `Withdraw`  
  - Feedback:  
    - `gr.Info` for `Withdrawal successful.`  
    - `gr.Error` for validation and insufficient funds errors.

**Technical Notes**
- Withdrawal must check available cash balance before processing.  
- Balance update and transaction record creation must be atomic.

**Definition of Done**
- Withdrawals never result in a negative cash balance.  
- All validation and error scenarios are handled with clear messages.  
- Automated tests cover both successful and rejected withdrawals.

**Out of Scope**
- Fees or charges on withdrawals.  
- Partial approvals or queued withdrawals.

---

## US-004 – Record Buy Share Transaction with Affordability Check

**User Story**  
As an account holder, I want to record the purchase of shares for a specific symbol and quantity, so that my cash balance and holdings accurately reflect the simulated trade, and I cannot buy more than I can afford.

**Business Value / Priority**  
- Value: High – core trading simulation  
- Priority: High  
- Estimation guidance: 5–8 story points (including integration with `get_share_price`)

**Acceptance Criteria (BDD)**
- **AC1 – Successful buy transaction**  
  - Given I am on the `Trade` screen for my account  
  - When I select or enter symbol `AAPL`  
    And I enter quantity `10`  
    And the function `get_share_price("AAPL")` returns `150`  
  - Then the system calculates the total cost as `1500`  
    And if my available cash balance is at least `1500`, then:  
      - My cash balance decreases by `1500`  
      - My holdings for `AAPL` increase by `10` shares  
      - A transaction is recorded with type `BUY`, symbol, quantity, price per share, total cost, timestamp, and resulting cash balance and holdings  
      - I see a success message: `Buy order recorded successfully.`

- **AC2 – Prevent buy exceeding available cash**  
  - Given my cash balance is `1000`  
    And `get_share_price("AAPL")` returns `150`  
  - When I attempt to buy quantity `10` (total cost `1500`)  
  - Then the buy transaction is rejected  
    And my cash balance and holdings do not change  
    And I see an error message: `Insufficient funds. You cannot afford this purchase.`

- **AC3 – Validation of quantity and symbol**  
  - Given I am on the `Trade` screen  
  - When I do any of the following:  
    - Leave symbol empty  
    - Enter a quantity that is `0` or negative  
    - Enter a non-numeric quantity  
  - Then the buy is not processed  
    And I see one of the following validation messages as applicable:  
      - `Symbol is required.`  
      - `Quantity must be greater than 0.`  
      - `Enter a valid numeric quantity.`

- **AC4 – Share price retrieval failure**  
  - Given I have entered a valid symbol and quantity  
  - When `get_share_price(symbol)` fails or returns an error (e.g., unknown symbol not in test list)  
  - Then the buy transaction is not processed  
    And I see an error message: `Unable to retrieve share price for the selected symbol.`

- **AC5 – Technical errors**  
  - Given I have entered valid symbol and quantity  
    And `get_share_price` has returned a valid price  
  - When a server error occurs while updating balance or holdings  
  - Then no changes are committed to my balance or holdings  
    And I see an error: `Unable to record buy transaction at the moment. Please try again later.`

**UI/UX Specifications**
- `Trade` screen (Buy/Sell combined, see US-005):
  - `gr.Dropdown` or `gr.Textbox` for `Symbol`  
    - Pre-populate with `AAPL`, `TSLA`, `GOOGL` options at minimum  
  - `gr.Number` or `gr.Textbox` for `Quantity`  
    - Label: `Quantity`  
    - Placeholder: `Enter number of shares`  
  - `gr.Button` labeled `Buy`  
  - Display of `Current share price` (read-only `gr.Textbox` or `gr.Markdown`) after selecting symbol using `get_share_price(symbol)`.  
  - Display of `Estimated total cost` as price × quantity before confirming, if feasible.
- Feedback / Messages:  
  - `gr.Info` for `Buy order recorded successfully.`  
  - `gr.Error` for validation, insufficient funds, or price retrieval issues.

**Technical Notes**
- Use the provided `get_share_price(symbol)` function.  
- Support at least the test symbols `AAPL`, `TSLA`, `GOOGL` with fixed prices in test implementation.  
- Ensure atomic update of: cash balance, holdings map (e.g., `{symbol: quantity}`), and transaction log.

**Definition of Done**
- Users can record buy trades without ever overspending their available cash.  
- All amounts and holdings are updated consistently and logged as transactions.  
- Tests cover affordability checks, price integration, and error scenarios.

**Out of Scope**
- Partial fills, order book, or market simulation.  
- Support for complex order types (limit, stop-loss, etc.).

---

## US-005 – Record Sell Share Transaction with Holdings Check

**User Story**  
As an account holder, I want to record the sale of shares for a specific symbol and quantity, so that my cash balance and holdings accurately reflect the simulated sale, and I cannot sell more shares than I own.

**Business Value / Priority**  
- Value: High – core trading simulation  
- Priority: High  
- Estimation guidance: 5–8 story points

**Acceptance Criteria (BDD)**
- **AC1 – Successful sell transaction**  
  - Given I hold `20` shares of `TSLA`  
    And I am on the `Trade` screen  
  - When I choose `TSLA` and quantity `5`  
    And `get_share_price("TSLA")` returns `200`  
  - Then the total sale proceeds are `1000`  
    And my holdings for `TSLA` decrease to `15`  
    And my cash balance increases by `1000`  
    And a transaction is recorded with type `SELL`, symbol, quantity, price per share, total proceeds, timestamp, and resulting balances  
    And I see a success message: `Sell order recorded successfully.`

- **AC2 – Prevent selling more than held**  
  - Given I hold `3` shares of `GOOGL`  
  - When I attempt to sell `5` shares of `GOOGL`  
  - Then the sale is rejected  
    And my holdings and cash balance remain unchanged  
    And I see an error message: `Insufficient shares. You cannot sell more than you hold.`

- **AC3 – Validation of symbol and quantity**  
  - Given I am on the `Trade` screen  
  - When I do any of the following:  
    - Leave symbol empty  
    - Choose a symbol for which I hold zero shares and attempt to sell  
    - Enter quantity `0` or negative  
    - Enter a non-numeric quantity  
  - Then the sell is not processed  
    And I see one of the following messages as applicable:  
      - `Symbol is required.`  
      - `You do not hold any shares of this symbol.`  
      - `Quantity must be greater than 0.`  
      - `Enter a valid numeric quantity.`

- **AC4 – Share price retrieval failure**  
  - Given I have entered a valid symbol and quantity for which I have sufficient holdings  
  - When `get_share_price(symbol)` fails or returns an error  
  - Then the sell transaction is not processed  
    And I see an error message: `Unable to retrieve share price for the selected symbol.`

- **AC5 – Technical errors**  
  - Given I have entered valid symbol and quantity and `get_share_price` returned a price  
  - When a server error occurs while updating holdings or cash balance  
  - Then no changes are committed  
    And I see an error: `Unable to record sell transaction at the moment. Please try again later.`

**UI/UX Specifications**
- Reuses the `Trade` screen described in US-004.  
- `gr.Button` labeled `Sell` adjacent to or below the `Buy` button.  
- Display of current holdings for the selected symbol (e.g., `You currently hold: 20 TSLA`) near the quantity input.
- Feedback:  
  - `gr.Info` for `Sell order recorded successfully.`  
  - `gr.Error` for insufficient holdings and other errors.

**Technical Notes**
- Ensure holdings for a symbol cannot go below zero.  
- Consider storing holdings as integer share counts.

**Definition of Done**
- Users cannot sell more shares than they hold.  
- All successful sells adjust cash, holdings, and transaction log consistently.  
- Tests cover sell logic, including edge cases for zero/insufficient holdings.

**Out of Scope**
- Short selling.  
- Fractional shares.

---

## US-006 – View Current Holdings and Portfolio Value

**User Story**  
As an account holder, I want to see my current holdings and the total value of my portfolio at any point in time, so that I understand the current worth of my investments.

**Business Value / Priority**  
- Value: High – key insight for users  
- Priority: High  
- Estimation guidance: 5–8 story points

**Acceptance Criteria (BDD)**
- **AC1 – Display current holdings list**  
  - Given I have an account with one or more holdings  
  - When I open the `Portfolio` or `Account Overview` screen  
  - Then I see a table of my current holdings with columns:  
    - `Symbol`  
    - `Quantity`  
    - `Current price`  
    - `Market value` (Quantity × Current price)

- **AC2 – Portfolio total value**  
  - Given my account has cash and multiple holdings  
  - When I open the portfolio view  
  - Then the system calls `get_share_price` for each symbol in my holdings  
    And it calculates:  
      - `Total holdings value` = sum of all holdings market values  
      - `Total portfolio value` = cash balance + total holdings value  
    And I see both values clearly labeled.

- **AC3 – Empty portfolio handling**  
  - Given I have an account with no holdings and zero cash  
  - When I open the portfolio view  
  - Then I see a message: `You have no holdings yet.`  
    And total holdings value and total portfolio value display as `0`.

- **AC4 – Share price retrieval failure for a symbol**  
  - Given I have holdings including a symbol not supported by the test `get_share_price` implementation  
  - When the system attempts to load the portfolio  
  - Then it shows the symbol row with quantity, but current price and market value as `N/A`  
    And displays a non-blocking warning: `Some share prices could not be retrieved. Values marked N/A.`  
    And still calculates totals only from symbols with successfully retrieved prices.

**UI/UX Specifications**
- Portfolio/Holdings section on `Account Overview`:
  - `gr.DataFrame` or `gr.DataTable` for holdings with columns: `Symbol`, `Quantity`, `Current price`, `Market value`.  
  - Summary section (e.g., `gr.Markdown` or read-only `gr.Textbox`) showing:  
    - `Cash balance`  
    - `Total holdings value`  
    - `Total portfolio value`.
- Feedback:  
  - `gr.Info` or `gr.Markdown` message for empty portfolio state.  
  - `gr.Warning` for partial price retrieval issues.
- Accessibility:  
  - Table is navigable via keyboard.  
  - Clear text contrast and labels for screen readers.

**Technical Notes**
- Reuse existing `get_share_price` function; batch calls where possible for performance (optional).  
- Ensure deterministic prices for the test symbols.

**Definition of Done**
- Portfolio view correctly reflects current holdings and portfolio value at view time.  
- Handles empty and partial data (N/A prices) gracefully.  
- Automated tests cover value calculations and integration with `get_share_price`.

**Out of Scope**
- Historical portfolio value charting.  
- Real-time auto-refresh of prices (manual refresh only).

---

## US-007 – View Profit or Loss Relative to Initial Deposit

**User Story**  
As an account holder, I want to see my profit or loss relative to my initial deposit at any point in time, so that I can evaluate how my trading strategy is performing.

**Business Value / Priority**  
- Value: High – key performance indicator  
- Priority: High  
- Estimation guidance: 5–8 story points

**Acceptance Criteria (BDD)**
- **AC1 – Track initial deposit baseline**  
  - Given I have made one or more deposits into my account  
  - When the system calculates profit/loss  
  - Then it defines `initial deposit` as the sum of all deposit transactions up to my first trade (or a specified baseline rule agreed with engineering).  

- **AC2 – Profit/loss calculation**  
  - Given my account has a current total portfolio value `V` (from US-006)  
    And my defined initial deposit baseline is `D`  
  - When I open the `Account Overview` screen  
  - Then the system calculates `P/L = V - D`  
    And displays:  
      - Profit if `P/L > 0` with label `Profit`  
      - Loss if `P/L < 0` with label `Loss`  
      - `0` with label `Break-even` if `P/L = 0`.

- **AC3 – Visual indication of profit vs loss**  
  - Given my calculated P/L is positive  
  - When I view it in the UI  
  - Then it is displayed with a green color indicator and prefix `+` (e.g., `+250`).  
  - Given my calculated P/L is negative  
  - Then it is displayed with a red color indicator and `-` sign.  
  - Given P/L is zero  
  - Then it is displayed in neutral color.

- **AC4 – No deposit case**  
  - Given I have never deposited funds into the account  
  - When I view the profit/loss section  
  - Then the system displays `No deposit baseline available.`  
    And P/L displays as `N/A`.

**UI/UX Specifications**
- Profit/Loss widget on `Account Overview`:
  - Use `gr.Markdown` or styled text to show:  
    - `Initial deposit`  
    - `Current portfolio value`  
    - `Profit/Loss` with color coding.  
- Messages:  
  - For missing baseline: `No deposit baseline available.` (neutral style).  
- Accessibility:  
  - Do not rely on color alone; include `Profit`, `Loss`, or `Break-even` text labels.

**Technical Notes**
- Require clear agreement with engineering on the rule for `initial deposit` baseline (e.g., sum of deposits before first trade or first non-zero balance).  
- For the purposes of this simulation, a simple rule (e.g., sum of all deposits to date) may be acceptable but must be consistent.

**Definition of Done**
- P/L is consistently calculated and displayed based on agreed baseline.  
- Visual styling distinguishes profit from loss, with accessible labeling.  
- Unit tests cover multiple scenarios (profit, loss, break-even, no deposits).

**Out of Scope**
- Time-series P/L tracking or charting.  
- Tax or fee calculations.

---

## US-008 – View Holdings and P/L at a Specific Point in Time

**User Story**  
As an account holder, I want to view my holdings, portfolio value, and profit/loss as of a specific point in time, so that I can review historical performance.

**Business Value / Priority**  
- Value: Medium – enhances analysis capabilities  
- Priority: Medium  
- Estimation guidance: 8–13 story points (replay based on transaction history)

**Acceptance Criteria (BDD)**
- **AC1 – Point-in-time selection**  
  - Given I have an account with transaction history  
  - When I open the `History Snapshot` view  
  - Then I can select a date/time (or choose from a list of past transaction timestamps) to view my portfolio state as of that moment.

- **AC2 – Historical holdings reconstruction**  
  - Given I select a timestamp `T`  
  - When the system reconstructs portfolio state based on all transactions up to and including `T`  
  - Then it displays:  
    - Recreated holdings by symbol and quantity  
    - Cash balance at `T`  
    - Portfolio value at `T` using current share prices (or a clearly documented rule, see Technical Notes).

- **AC3 – Historical P/L as of T**  
  - Given I select timestamp `T`  
  - When the system reconstructs the state  
  - Then it calculates profit/loss as of `T` using the same baseline rule from US-007 but constrained to deposits up to `T`.

- **AC4 – No transactions before T**  
  - Given I select a time earlier than my first transaction  
  - When the system attempts reconstruction  
  - Then it shows zero holdings, cash = 0, and P/L `0` (or `N/A` if no deposits baseline), with a message: `No activity before this time.`

- **AC5 – Invalid or out-of-range timestamp**  
  - Given I enter a timestamp outside my account’s existence range  
  - Then the system shows an error: `Selected time is outside the account history range.`

**UI/UX Specifications**
- New `History Snapshot` section or tab:  
  - `gr.Dropdown` populated with transaction timestamps (and human-readable labels), or `gr.Slider` / `gr.Textbox` date-time input.  
  - `gr.Button` labeled `View Snapshot`.  
  - Reuse holdings table and summary from US-006 and P/L widget from US-007 to display reconstructed state.  
  - Info messages:  
    - `No activity before this time.`  
    - `Selected time is outside the account history range.`

**Technical Notes**
- Portfolio state reconstruction should be based solely on the transaction log (deposits, withdrawals, buys, sells).  
- For simplicity, use current `get_share_price` for valuation at historical times unless historical prices are introduced later.

**Definition of Done**
- Users can view consistent reconstructed states for multiple chosen timestamps.  
- Edge cases (no history, very early timestamps, late timestamps) handled with clear messaging.  
- Tests cover reconstruction logic and UI wiring.

**Out of Scope**
- Real historical price data.  
- Visual timeline or charts (table-based only).

---

## US-009 – View Transaction History

**User Story**  
As an account holder, I want to view a list of all transactions (deposits, withdrawals, buys, sells) that I have made over time, so that I can audit and understand how my portfolio evolved.

**Business Value / Priority**  
- Value: High – transparency and auditability  
- Priority: High  
- Estimation guidance: 3–5 story points

**Acceptance Criteria (BDD)**
- **AC1 – List all transactions**  
  - Given I have an account with transaction history  
  - When I open the `Transactions` view  
  - Then I see a table where each row represents a transaction with columns:  
    - `Timestamp`  
    - `Type` (DEPOSIT, WITHDRAWAL, BUY, SELL)  
    - `Symbol` (if applicable)  
    - `Quantity` (if applicable)  
    - `Amount` (cash in/out or total trade value)  
    - `Resulting cash balance`.

- **AC2 – Empty history**  
  - Given my account has no transactions  
  - When I open the `Transactions` view  
  - Then I see a message: `No transactions have been recorded yet.`

- **AC3 – Ordering**  
  - Given I have multiple transactions  
  - When I open the `Transactions` view  
  - Then transactions are shown ordered by timestamp, newest first (or consistently as agreed and documented).

- **AC4 – Basic filtering (optional)**  
  - Given I have many transactions  
  - When I filter by `Type` or by `Symbol`  
  - Then only matching transactions are displayed.

**UI/UX Specifications**
- `Transactions` tab or section on `Account Overview`:
  - `gr.DataFrame` or `gr.DataTable` for the transactions list.  
  - Optional `gr.Dropdown` for `Type` filter and `Symbol` filter.  
  - Info messages via `gr.Info` for empty state.

**Technical Notes**
- Transaction record structure to be consistent across all operations for easy logging and replay.  
- Consider using an in-memory list or simple persistence as per app architecture.

**Definition of Done**
- All transactions are visible and correctly formatted.  
- Empty states and filters work as specified.  
- Tests cover ordering, empty state, and basic filter behavior.

**Out of Scope**
- Export to CSV or external reporting.  
- Advanced filtering or search.

---

## US-010 – Prevent Invalid Operations (Global Rules)

**User Story**  
As a system, I want to consistently prevent invalid financial operations (negative balances, unaffordable buys, selling nonexistent shares), so that the integrity of the trading simulation is preserved.

**Business Value / Priority**  
- Value: High – ensures correctness  
- Priority: High  
- Estimation guidance: 5–8 story points (cross-cutting concerns)

**Acceptance Criteria (BDD)**
- **AC1 – Non-negative cash balance invariant**  
  - Given any operation (deposit, withdrawal, buy, sell) is performed  
  - When it would result in a negative cash balance  
  - Then the system prevents the operation and returns an appropriate error message specific to the action (see US-003, US-004).

- **AC2 – Non-negative holdings invariant**  
  - Given any sell operation is performed  
  - When it would result in negative holdings for a symbol  
  - Then the system prevents the operation and returns the error message: `Insufficient shares. You cannot sell more than you hold.`

- **AC3 – Affordability checks for buys**  
  - Given any buy operation is performed  
  - When the total cost exceeds available cash balance  
  - Then the system prevents the operation and returns the error: `Insufficient funds. You cannot afford this purchase.`

- **AC4 – Transaction atomicity**  
  - Given a trade or money movement is in progress  
  - When an error occurs after some changes are attempted  
  - Then the overall state (cash, holdings, transaction log) is rolled back to pre-operation values.

**UI/UX Specifications**
- Error messages should be shown near the relevant form and in a noticeable but non-obtrusive way using `gr.Error`.  
- Forms should keep user input values after a rejected operation so the user can correct them.

**Technical Notes**
- Consider encapsulating rule checks in domain services or helper functions to ensure they are reused across UI and any API layers.  
- Atomicity may rely on in-memory transaction simulation or database transactions depending on architecture.

**Definition of Done**
- It is impossible (via provided UI operations) to reach a state with negative cash or negative holdings.  
- All invalid operations produce clear, context-appropriate messages.  
- Automated tests assert invariants across all relevant operations.

**Out of Scope**
- Concurrency control across multiple concurrent sessions (single-user assumption for now).  
- Fraud detection or advanced risk controls.
