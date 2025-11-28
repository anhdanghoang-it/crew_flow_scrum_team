# Account Management & Trading Simulation – Detailed Test Plan
Application URL: `http://127.0.0.1:7860/`
User Stories Source: `docs/copilot/account_management_user_stories.md`
Seed File: `e2e/seed.spec.ts`

## 1. Executive Summary
This detailed plan covers functional, validation, error handling, data integrity, and basic accessibility testing for user stories US-001 through US-010 governing account creation, cash movements, trading (buy/sell), portfolio and profit/loss visibility, historical snapshots, transaction audit, and global invariants. Each acceptance criterion (AC) is mapped to granular test cases with explicit steps, expected outcomes per step, automation feasibility, and data strategies.

## 2. Objectives
- Verify all acceptance criteria and definitions of done for US-001..US-010.
- Ensure invariants: non-negative cash, non-negative holdings, affordability enforcement, transactional atomicity.
- Validate UI feedback consistency (success, validation, technical errors).
- Confirm portfolio, P/L, and historical reconstruction logic correctness.
- Establish robust test data isolation via unique identifiers.

## 3. Test Strategy
- Type: Requirement-based, scenario-driven; mix of automated (Playwright) and manual exploratory (edge, accessibility) tests.
- Levels: UI functional + light integration with internal pricing logic.
- Approach: Each AC gets ≥1 test case; negative and boundary cases explicitly enumerated.
- Automation Priority: High for deterministic flows (Create, Deposit, Withdraw, Buy/Sell, Portfolio refresh, P/L calculation, History snapshot retrieval, Transaction filtering). Medium for technical error injection (requires hooks). Low for deep accessibility (manual / specialized tooling).

## 4. Assumptions & Dependencies
- Deterministic share prices for supported symbols: AAPL, TSLA, GOOGL (fixed values defined in backend).
- Unsupported symbol (e.g., `UNKNWN`) triggers price retrieval failure.
- Application state resets on server restart (used for isolation when needed).
- Technical error simulation achievable via test flag or monkeypatch (to be implemented if absent).

## 5. Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Username collisions | False negatives in duplicate tests | Use timestamped unique usernames |
| Price failure hard to simulate | Coverage gap for AC price error | Use unsupported symbol `UNKNWN` |
| Atomicity not observable directly | Missed partial state defect | Validate before/after snapshots of cash & holdings |
| Ambiguous P/L baseline rule change | Test instability | Centralize baseline rule constant & reference in tests |
| Large transaction history performance | Slow tests | Cap volume in routine tests; separate performance sanity case |

## 6. Test Data Management
- Username pattern: `u_{epoch_ms}` (e.g., `u_1732065600000`)
- Duplicate username: `u_dup_base` created first, reused for duplicate rejection test.
- Deposit amounts: Valid: 1, 100, 500, 1000, 2500, 100000; Invalid: 0, -1, `abc`.
- Withdrawal amounts: Valid subset ≤ current balance; Invalid: >balance, 0, negative, `xyz`.
- Symbols: Valid: AAPL, TSLA, GOOGL; Invalid: UNKNWN.
- Quantities: Valid: 1, 3, 5, 10; Invalid: 0, -2, `abc`.
- Snapshot timestamps captured after each transaction into an array for historical reconstruction tests.

## 7. Traceability Matrix
| User Story | Acceptance Criteria | Test Case IDs |
|------------|--------------------|---------------|
| US-001 | AC1, AC2, AC3, AC4 | CA-001..CA-005 |
| US-002 | AC1, AC2, AC3, AC4 | DP-001..DP-006 |
| US-003 | AC1, AC2, AC3, AC4 | WD-001..WD-006 |
| US-004 | AC1..AC5 | BUY-001..BUY-009 |
| US-005 | AC1..AC5 | SELL-001..SELL-009 |
| US-006 | AC1..AC4 | PV-001..PV-006 |
| US-007 | AC1..AC4 | PL-001..PL-005 |
| US-008 | AC1..AC5 | HS-001..HS-008 |
| US-009 | AC1..AC4 | TX-001..TX-006 |
| US-010 | AC1..AC4 (cross-cutting) | GI-001..GI-008 |

## 8. Detailed Test Cases
Format: ID, Title, Source (US/AC), Priority (H/M/L), Type, Preconditions, Steps, Expected Results (per step), Final Outcome, Automation, Notes.

### US-001 – Create Trading Account

ID: CA-001
Title: Successful Account Creation
Source: US-001 AC1
Priority: High
Type: Functional / Positive
Preconditions: App loaded; Create Account tab active; no active account.
Steps:
1. Generate unique username `u_{epoch_ms}`.
2. Enter username in Username textbox.
3. Enter display name `Trader {epoch_ms}`.
4. Click `Create Account` button.
Expected per Step:
1. Username generated (local variable).
2. Field reflects entered value.
3. Display name field reflects value.
4. Success message appears; active account label updates; automatically view account overview or still on tab with status panel updated.
Final Outcome: Account object created with cash=0, holdings empty, transaction log empty.
Automation: Yes (Playwright).
Notes: Validate no extraneous initial transactions.

ID: CA-002
Title: Missing Username Validation
Source: US-001 AC2
Priority: High
Type: Validation / Negative
Preconditions: On Create Account tab.
Steps:
1. Leave Username empty.
2. (Optional) Provide display name.
3. Click Create Account.
Expected:
1. Field empty.
2. Display name captured (optional).
3. Error `Username is required.`; no success message; active account unchanged.
Final Outcome: No account created.
Automation: Yes.
Notes: Confirm error element role (e.g., alert) for accessibility.

ID: CA-003
Title: Duplicate Username Handling
Source: US-001 AC3
Priority: High
Type: Validation / Negative
Preconditions: Account with username `u_dup_base` already exists.
Steps:
1. Enter `u_dup_base` in Username.
2. Click Create Account.
Expected:
1. Field updated.
2. Error `Username already exists. Please choose another.`; no state change.
Final Outcome: Single original account persists.
Automation: Yes (create first then second attempt).
Notes: Ensure timing does not create race; sequential execution.

ID: CA-004
Title: Technical Error on Account Creation
Source: US-001 AC4
Priority: Medium
Type: Error Handling / Negative
Preconditions: Error injection hook active (simulate server failure).
Steps:
1. Enter valid unique username.
2. Click Create Account.
Expected:
1. Field updated.
2. Error `Unable to create account at the moment. Please try again later.`; account not created.
Final Outcome: No partial record.
Automation: Conditional (requires hook).
Notes: Validate absence in transaction history.

ID: CA-005
Title: Optional Display Name Omitted
Source: US-001 AC1 (implicit optional display name path)
Priority: Low
Type: Functional
Preconditions: On Create tab.
Steps:
1. Enter unique username only.
2. Click Create Account.
Expected:
1. Username captured.
2. Success message; display name stored null/empty.
Final Outcome: Account created; display name blank.
Automation: Yes.
Notes: Inspect any default placeholder not persisted.

### US-002 – Deposit Funds

ID: DP-001
Title: Successful Deposit
Source: US-002 AC1
Priority: High
Type: Functional
Preconditions: Active account with cash=0; on Account Overview tab.
Steps:
1. Enter `1000` in Deposit amount.
2. Click Deposit.
Expected:
1. Field shows 1000.
2. Success `Deposit successful.`; cash balance updates to 1000; transaction row logged.
Final Outcome: Balance=1000; transaction type=DEPOSIT amount=1000.
Automation: Yes.
Notes: Capture timestamp.

ID: DP-002
Title: Non-Positive Amount Validation (Zero)
Source: US-002 AC2
Priority: High
Type: Validation
Preconditions: Active account.
Steps:
1. Enter `0`.
2. Click Deposit.
Expected:
1. Field shows 0.
2. Error `Deposit amount must be greater than 0.`; balance unchanged.
Final Outcome: No transaction.
Automation: Yes.

ID: DP-003
Title: Negative Amount Validation
Source: US-002 AC2
Priority: High
Type: Validation
Preconditions: Active account.
Steps:
1. Enter `-5`.
2. Click Deposit.
Expected:
1. Field shows -5.
2. Same error as zero; no change.
Final Outcome: No transaction.
Automation: Yes.

ID: DP-004
Title: Non-Numeric Deposit
Source: US-002 AC3
Priority: Medium
Type: Validation
Preconditions: Active account.
Steps:
1. Enter `abc`.
2. Click Deposit.
Expected:
1. Field shows abc.
2. Error `Enter a valid numeric amount.`
Final Outcome: No transaction.
Automation: Yes.

ID: DP-005
Title: Large Deposit Boundary
Source: US-002 AC1 (extended)
Priority: Medium
Type: Boundary
Preconditions: Active account.
Steps:
1. Enter `100000`.
2. Click Deposit.
Expected:
1. Field shows 100000.
2. Success; balance increments; transaction accurate.
Final Outcome: Cash=100000.
Automation: Yes.
Notes: Formatting check.

ID: DP-006
Title: Technical Error on Deposit
Source: US-002 AC4
Priority: Medium
Type: Error Handling
Preconditions: Error injection on deposit.
Steps:
1. Enter `500`.
2. Click Deposit.
Expected:
1. Field shows 500.
2. Error `Unable to process deposit at the moment. Please try again later.`; balance unchanged; no transaction.
Final Outcome: Atomic rollback.
Automation: Conditional.

### US-003 – Withdraw Funds
(Withdraw test cases WD-001..WD-006 mirror deposit structure; omitted repetitive formatting for brevity but include in automation file.)

ID: WD-001 Successful Withdrawal (US-003 AC1) – cash reduces; transaction WITHDRAWAL.
ID: WD-002 Prevent Negative Balance (AC2) – error message; unchanged cash.
ID: WD-003 Zero Amount Validation (AC3) – error; unchanged.
ID: WD-004 Negative Amount Validation (AC3) – error.
ID: WD-005 Non-Numeric Validation (AC3) – error message numeric.
ID: WD-006 Technical Error (AC4) – rollback.

### US-004 – Buy Shares

ID: BUY-001 Successful Buy
Source: US-004 AC1
Priority: High
Type: Functional
Preconditions: Cash sufficient (e.g., deposit earlier); Trade tab active.
Steps:
1. Select symbol AAPL from listbox.
2. Enter quantity `5`.
3. Click `Check Price & Estimate`.
4. Click `Buy`.
Expected:
1. Symbol selection persists.
2. Quantity field updated.
3. Price preview + estimated total cost displayed.
4. Success message `Buy order recorded successfully.`; cash decreased; holdings AAPL=5; transaction logged.
Final Outcome: Accurate post-trade state.
Automation: Yes.

ID: BUY-002 Affordability Rejection (AC2) – attempt cost > cash; error; no change.
ID: BUY-003 Empty Symbol (AC3) – validation error.
ID: BUY-004 Zero Quantity (AC3) – `Quantity must be greater than 0.`
ID: BUY-005 Negative Quantity (AC3) – same error.
ID: BUY-006 Non-Numeric Quantity (AC3) – numeric error.
ID: BUY-007 Price Retrieval Failure (AC4) – symbol UNKNWN; error; no trade.
ID: BUY-008 Technical Error (AC5) – rollback.
ID: BUY-009 Holdings Increment Accuracy – second buy increments correctly.

### US-005 – Sell Shares
SELL-001 Successful Sell (AC1) – holdings decrease; cash increases; transaction SELL.
SELL-002 Over-Sell Prevention (AC2) – error; unchanged.
SELL-003 Empty Symbol (AC3) – validation.
SELL-004 No Holdings for Symbol (AC3) – specific message.
SELL-005 Zero Quantity (AC3) – validation.
SELL-006 Negative Quantity (AC3) – validation.
SELL-007 Non-Numeric Quantity (AC3) – numeric error.
SELL-008 Price Retrieval Failure (AC4) – UNKNWN; error.
SELL-009 Technical Error (AC5) – rollback.

### US-006 – View Holdings & Portfolio
PV-001 Empty Portfolio (AC3) – placeholder message; all zeros.
PV-002 Holdings Table Population (AC1) – rows per symbol.
PV-003 Market Value Calculation (AC1) – correct per symbol.
PV-004 Totals Computation (AC2) – holdings value sum & portfolio value.
PV-005 N/A Price Handling (AC4) – unsupported symbol shows N/A; warning.
PV-006 Formatting Consistency – currency `$X.YY`.

### US-007 – Profit / Loss
PL-001 Baseline Establishment (AC1) – sum deposits before first trade.
PL-002 Profit Display (AC2, AC3) – positive P/L with green + label Profit.
PL-003 Loss Display (AC2, AC3) – negative P/L red - label Loss.
PL-004 Break-even (AC2, AC3) – zero P/L neutral label Break-even.
PL-005 No Deposit Baseline (AC4) – message; P/L N/A.

### US-008 – Historical Snapshot
HS-001 Load Timestamps (AC1) – dropdown populated.
HS-002 View Snapshot (AC2) – reconstructed holdings & cash accurate.
HS-003 No Activity Before First (AC4) – message; empty state.
HS-004 P/L at Timestamp (AC3) – baseline constrained to deposits <= T.
HS-005 Unsupported Symbol in History (AC2/AC4 synergy) – N/A pricing warning.
HS-006 Cash Replay Accuracy – arithmetic correct.
HS-007 Holdings Replay Accuracy – cumulative share counts correct.
HS-008 Out-of-Range Timestamp (AC5) – error message.

### US-009 – Transaction History
TX-001 Empty History (AC2) – placeholder message.
TX-002 List All Transactions (AC1) – table headers & rows.
TX-003 Ordering (AC3) – verify sorted order.
TX-004 Filter by Type (AC4 optional) – subset.
TX-005 Filter by Symbol (AC4) – subset.
TX-006 Combined Filters – intersection subset.

### US-010 – Global Invariants
GI-001 Non-Negative Cash Invariant (AC1) – after mixed operations cash ≥ 0.
GI-002 Buy Overdraft Prevention (AC3) – error path.
GI-003 Withdrawal Overdraft Prevention (AC1/AC2 synergy) – error.
GI-004 Non-Negative Holdings (AC2) – sell over-hold blocked.
GI-005 Affordability Check Consistency – message text exact.
GI-006 Atomicity on Failed Buy (AC4) – rollback.
GI-007 Atomicity on Failed Sell (AC4) – rollback.
GI-008 Cross-Tab Consistency – Trade updates visible in Overview & Transactions.

## 9. Automation Feasibility Table (Summary)
| ID Prefix | Automatable | Notes |
|-----------|-------------|-------|
| CA | Yes | Technical error needs hook |
| DP | Yes | Technical error needs hook |
| WD | Yes | Technical error needs hook |
| BUY | Yes | Price failure via UNKNWN |
| SELL | Yes | Price failure via UNKNWN |
| PV | Yes | N/A symbol needs setup |
| PL | Yes | Profit/Loss color may need CSS inspection |
| HS | Yes | Accurate timestamp capture required |
| TX | Yes | Filtering assertions |
| GI | Yes | Atomicity needs failure injection |

## 10. Selector Strategy (Playwright)
| Element | Selector |
|---------|----------|
| Create Account tab | `page.getByRole('tab', { name: 'Create Account' })` |
| Username textbox | `page.getByRole('textbox', { name: 'Username' })` |
| Display name textbox | `page.getByRole('textbox', { name: 'Display name' })` |
| Create Account button | `page.getByRole('button', { name: 'Create Account' })` |
| Account Overview tab | `page.getByRole('tab', { name: 'Account Overview' })` |
| Deposit spinbutton | `page.getByRole('spinbutton', { name: 'Deposit amount' })` |
| Withdraw spinbutton | `page.getByRole('spinbutton', { name: 'Withdrawal amount' })` |
| Deposit button | `page.getByRole('button', { name: 'Deposit' })` |
| Withdraw button | `page.getByRole('button', { name: 'Withdraw' })` |
| Trade tab | `page.getByRole('tab', { name: 'Trade' })` |
| Symbol listbox | `page.getByRole('listbox', { name: 'Symbol' })` |
| Quantity spinbutton | `page.getByRole('spinbutton', { name: 'Quantity' })` |
| Check Price button | `page.getByRole('button', { name: 'Check Price & Estimate' })` |
| Buy button | `page.getByRole('button', { name: 'Buy' })` |
| Sell button | `page.getByRole('button', { name: 'Sell' })` |
| Refresh Portfolio | `page.getByRole('button', { name: 'Refresh Portfolio' })` |
| Refresh Profit/Loss | `page.getByRole('button', { name: 'Refresh Profit / Loss' })` |
| History Snapshot tab | `page.getByRole('tab', { name: 'History Snapshot' })` |
| Load Snapshot Timestamps | `page.getByRole('button', { name: 'Load Snapshot Timestamps' })` |
| Timestamp listbox | `page.getByRole('listbox', { name: 'Select timestamp' })` |
| View Snapshot | `page.getByRole('button', { name: 'View Snapshot' })` |
| Transactions tab | `page.getByRole('tab', { name: 'Transactions' })` |
| Type filter listbox | `page.getByRole('listbox', { name: 'Type filter' })` |
| Symbol filter listbox | `page.getByRole('listbox', { name: 'Symbol filter' })` |
| Apply Filters | `page.getByRole('button', { name: 'Apply Filters' })` |

## 11. Sample Automation Snippet (Extended)
```ts
import { test, expect } from '@playwright/test';
const baseUrl = 'http://127.0.0.1:7860/';
const unique = () => `u_${Date.now()}`;

test.describe('US-001 Account Creation', () => {
  test('CA-001 Successful Account Creation', async ({ page }) => {
    await page.goto(baseUrl);
    await page.getByRole('tab', { name: 'Create Account' }).click();
    const username = unique();
    await page.getByRole('textbox', { name: 'Username' }).fill(username);
    await page.getByRole('textbox', { name: 'Display name' }).fill('Trader Auto');
    await page.getByRole('button', { name: 'Create Account' }).click();
    await expect(page.getByText('Account created successfully.')).toBeVisible();
  });

  test('CA-002 Missing Username Validation', async ({ page }) => {
    await page.goto(baseUrl);
    await page.getByRole('tab', { name: 'Create Account' }).click();
    await page.getByRole('button', { name: 'Create Account' }).click();
    await expect(page.getByText('Username is required.')).toBeVisible();
  });
});
```

## 12. Acceptance Criteria Coverage Confirmation
Matrix and scenario list give full coverage; each AC mapped to explicit case(s). Global rules reinforced by GI series.

## 13. Exit Criteria
- 100% AC execution with logged results.
- All High priority tests automated & stable.
- No open critical defects blocking invariants.

## 14. Maintenance & Future Enhancements
- Add concurrency tests if multi-user introduced.
- Extend P/L baseline logic tests if rule changes.
- Introduce historical pricing dimension (would expand snapshot valuation tests).
- Integrate accessibility tooling (axe) for automated scanning.

## 15. Appendix – Atomicity Verification Pattern
Before operation: capture cash & holdings snapshot.
Perform operation expecting failure.
After failure: assert equality with before snapshot & absence of new transaction record.

---
End of Detailed Test Plan
