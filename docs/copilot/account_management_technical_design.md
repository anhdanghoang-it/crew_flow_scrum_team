# Account Management & Trading Simulation Technical Design

## 1. Overview & Architecture

### 1.1 Purpose
Provide an implementation-ready design for a Python backend module and a Gradio frontend that together satisfy user stories US-001 through US-010 (Account creation, deposits, withdrawals, buy/sell trades, portfolio valuation, profit/loss, historical snapshots, transaction history, and global invariants).

### 1.2 High-Level Architecture
```
+-------------------+        Gradio Events / Callbacks        +------------------------+
|   Gradio Frontend |  <------------------------------------> |   Python Backend       |
|  (Blocks, Tabs)   |  invoke service layer methods           |  Service Layer         |
|  Validation Layer |  pass validated DTOs                    |  Domain Models         |
|  Rendering Layer  |  display ResponseEnvelope               |  Repository (In-Mem)   |
+-------------------+                                         +-----------+------------+
                                                                   ^      |
                                                                   |      v
                                                             get_share_price(symbol)
                                                             (Price Provider Adapter)
```

### 1.3 Technology Stack
- Python: 3.10–3.13 (per `pyproject.toml` constraint)
- Gradio: >= 4.x (assumed; specify exact version in dependencies section)
- Pydantic: v2.x for data validation & serialization
- Optional: `typing_extensions` for future-proof typing (if needed)

### 1.4 Design Principles
- Separation of Concerns: UI (Gradio) vs Domain Logic (Services) vs Data (Models/Repository)
- Explicit Contracts: Pydantic request/response models
- Atomic Operations: Each state-changing operation performed under a lock to ensure invariants
- Predictable Errors: Custom exception hierarchy mapped to user-facing messages
- Deterministic Simulation: Fixed share prices for test symbols via `PriceProvider`

### 1.5 Module Organization (Proposed File Structure)
```
src/
  trading_sim/
    __init__.py
    config.py
    models.py          # Pydantic models (Account, Holding, Transaction, Requests, Responses)
    exceptions.py      # Custom exception hierarchy
    repository.py      # In-memory AccountRepository
    services.py        # AccountService, TradingService, PortfolioService, SnapshotService
    price_provider.py  # get_share_price adapter
    utils.py           # Shared helpers (time, atomic context)
  ui/
    app.py             # Gradio Blocks assembly
    callbacks.py       # Functions bound to Gradio components calling services
```

## 2. Python Backend Design

### 2.1 Data Models (Pydantic)
```python
from __future__ import annotations
from typing import Optional, Dict, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime

TransactionType = Literal['DEPOSIT','WITHDRAWAL','BUY','SELL']

class Holding(BaseModel):
    symbol: str = Field(min_length=1)
    quantity: int = Field(ge=0)

class Transaction(BaseModel):
    tx_id: str
    timestamp: datetime
    type: TransactionType
    symbol: Optional[str] = None
    quantity: Optional[int] = None  # For BUY/SELL
    amount: float  # For DEPOSIT/WITHDRAWAL total cash change; for BUY total cost; for SELL total proceeds
    price_per_share: Optional[float] = None
    resulting_cash_balance: float
    resulting_holdings: Dict[str, int]

class Account(BaseModel):
    account_id: str
    username: str
    display_name: Optional[str] = None
    cash_balance: float
    holdings: Dict[str, int]  # symbol -> quantity
    transactions: List[Transaction]
    created_at: datetime

# Request Models
class CreateAccountRequest(BaseModel):
    username: str = Field(min_length=1)
    display_name: Optional[str] = None

class DepositRequest(BaseModel):
    account_id: str
    amount: float = Field(gt=0)

class WithdrawRequest(BaseModel):
    account_id: str
    amount: float = Field(gt=0)

class BuyRequest(BaseModel):
    account_id: str
    symbol: str = Field(min_length=1)
    quantity: int = Field(gt=0)

class SellRequest(BaseModel):
    account_id: str
    symbol: str = Field(min_length=1)
    quantity: int = Field(gt=0)

class SnapshotRequest(BaseModel):
    account_id: str
    timestamp: datetime

# Response Envelope for UI consumption
class ResponseEnvelope(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    error_code: Optional[str] = None  # For mapping to UI error types
```

### 2.2 Exception Hierarchy
```python
class DomainError(Exception):
    code: str = 'DOMAIN_ERROR'
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class ValidationDomainError(DomainError):
    code = 'VALIDATION_ERROR'

class DuplicateUsernameError(DomainError):
    code = 'DUPLICATE_USERNAME'

class NotFoundError(DomainError):
    code = 'NOT_FOUND'

class InsufficientFundsError(DomainError):
    code = 'INSUFFICIENT_FUNDS'

class InsufficientSharesError(DomainError):
    code = 'INSUFFICIENT_SHARES'

class PriceRetrievalError(DomainError):
    code = 'PRICE_RETRIEVAL'

class AtomicityError(DomainError):
    code = 'ATOMICITY_FAILURE'

class SnapshotOutOfRangeError(DomainError):
    code = 'SNAPSHOT_RANGE'
```

### 2.3 Repository
```python
import threading
from typing import Dict
from datetime import datetime
from uuid import uuid4

class AccountRepository:
    def __init__(self):
        self._accounts: Dict[str, Account] = {}
        self._lock = threading.RLock()

    def create_account(self, username: str, display_name: str | None) -> Account:
        with self._lock:
            if any(acc.username == username for acc in self._accounts.values()):
                raise DuplicateUsernameError('Username already exists.')
            account_id = str(uuid4())
            account = Account(
                account_id=account_id,
                username=username,
                display_name=display_name,
                cash_balance=0.0,
                holdings={},
                transactions=[],
                created_at=datetime.utcnow()
            )
            self._accounts[account_id] = account
            return account

    def get(self, account_id: str) -> Account:
        with self._lock:
            if account_id not in self._accounts:
                raise NotFoundError('Account not found.')
            return self._accounts[account_id]

    def update(self, account: Account) -> None:
        with self._lock:
            if account.account_id not in self._accounts:
                raise NotFoundError('Account not found.')
            self._accounts[account.account_id] = account
```

### 2.4 Price Provider
```python
FIXED_PRICES = {'AAPL':150.0, 'TSLA':200.0, 'GOOGL':180.0}

def get_share_price(symbol: str) -> float:
    try:
        return FIXED_PRICES[symbol]
    except KeyError:
        raise PriceRetrievalError('Unable to retrieve share price for the selected symbol.')
```
(Design allows future injection of real data provider through interface.)

### 2.5 Services
Atomicity: combine validation + mutation inside a lock; rollback by reconstructing from pre-operation snapshot if partial failure occurs.

```python
from copy import deepcopy
from datetime import datetime
from uuid import uuid4

class AccountService:
    def __init__(self, repo: AccountRepository):
        self.repo = repo

    def create_account(self, req: CreateAccountRequest) -> ResponseEnvelope:
        try:
            account = self.repo.create_account(req.username, req.display_name)
            return ResponseEnvelope(success=True, message='Account created successfully.', data={'account': account.dict()})
        except DuplicateUsernameError as e:
            return ResponseEnvelope(success=False, message='Username already exists. Please choose another.', error_code=e.code)
        except Exception:
            return ResponseEnvelope(success=False, message='Unable to create account at the moment. Please try again later.', error_code='SERVER_ERROR')

class MoneyService:
    def __init__(self, repo: AccountRepository):
        self.repo = repo

    def deposit(self, req: DepositRequest) -> ResponseEnvelope:
        if req.amount <= 0:
            return ResponseEnvelope(success=False, message='Deposit amount must be greater than 0.', error_code='VALIDATION_ERROR')
        try:
            account = self.repo.get(req.account_id)
            before = deepcopy(account)
            account.cash_balance += req.amount
            tx = Transaction(
                tx_id=str(uuid4()),
                timestamp=datetime.utcnow(),
                type='DEPOSIT',
                amount=req.amount,
                resulting_cash_balance=account.cash_balance,
                resulting_holdings=deepcopy(account.holdings)
            )
            account.transactions.append(tx)
            self.repo.update(account)
            return ResponseEnvelope(success=True, message='Deposit successful.', data={'cash_balance': account.cash_balance})
        except NotFoundError as e:
            return ResponseEnvelope(success=False, message=e.message, error_code=e.code)
        except Exception:
            return ResponseEnvelope(success=False, message='Unable to process deposit at the moment. Please try again later.', error_code='SERVER_ERROR')

    def withdraw(self, req: WithdrawRequest) -> ResponseEnvelope:
        if req.amount <= 0:
            return ResponseEnvelope(success=False, message='Withdrawal amount must be greater than 0.', error_code='VALIDATION_ERROR')
        try:
            account = self.repo.get(req.account_id)
            if account.cash_balance < req.amount:
                return ResponseEnvelope(success=False, message='Insufficient funds. Withdrawal would result in a negative balance.', error_code='INSUFFICIENT_FUNDS')
            account.cash_balance -= req.amount
            tx = Transaction(
                tx_id=str(uuid4()),
                timestamp=datetime.utcnow(),
                type='WITHDRAWAL',
                amount=req.amount,
                resulting_cash_balance=account.cash_balance,
                resulting_holdings=deepcopy(account.holdings)
            )
            account.transactions.append(tx)
            self.repo.update(account)
            return ResponseEnvelope(success=True, message='Withdrawal successful.', data={'cash_balance': account.cash_balance})
        except NotFoundError as e:
            return ResponseEnvelope(success=False, message=e.message, error_code=e.code)
        except Exception:
            return ResponseEnvelope(success=False, message='Unable to process withdrawal at the moment. Please try again later.', error_code='SERVER_ERROR')

class TradingService:
    def __init__(self, repo: AccountRepository, price_provider=get_share_price):
        self.repo = repo
        self.get_price = price_provider

    def buy(self, req: BuyRequest) -> ResponseEnvelope:
        if not req.symbol:
            return ResponseEnvelope(success=False, message='Symbol is required.', error_code='VALIDATION_ERROR')
        if req.quantity <= 0:
            return ResponseEnvelope(success=False, message='Quantity must be greater than 0.', error_code='VALIDATION_ERROR')
        try:
            price = self.get_price(req.symbol)
            total_cost = price * req.quantity
            account = self.repo.get(req.account_id)
            if account.cash_balance < total_cost:
                return ResponseEnvelope(success=False, message='Insufficient funds. You cannot afford this purchase.', error_code='INSUFFICIENT_FUNDS')
            account.cash_balance -= total_cost
            account.holdings[req.symbol] = account.holdings.get(req.symbol, 0) + req.quantity
            tx = Transaction(
                tx_id=str(uuid4()), timestamp=datetime.utcnow(), type='BUY', symbol=req.symbol,
                quantity=req.quantity, amount=total_cost, price_per_share=price,
                resulting_cash_balance=account.cash_balance,
                resulting_holdings=deepcopy(account.holdings)
            )
            account.transactions.append(tx)
            self.repo.update(account)
            return ResponseEnvelope(success=True, message='Buy order recorded successfully.', data={'cash_balance': account.cash_balance, 'holdings': account.holdings})
        except PriceRetrievalError:
            return ResponseEnvelope(success=False, message='Unable to retrieve share price for the selected symbol.', error_code='PRICE_RETRIEVAL')
        except NotFoundError as e:
            return ResponseEnvelope(success=False, message=e.message, error_code=e.code)
        except Exception:
            return ResponseEnvelope(success=False, message='Unable to record buy transaction at the moment. Please try again later.', error_code='SERVER_ERROR')

    def sell(self, req: SellRequest) -> ResponseEnvelope:
        if not req.symbol:
            return ResponseEnvelope(success=False, message='Symbol is required.', error_code='VALIDATION_ERROR')
        if req.quantity <= 0:
            return ResponseEnvelope(success=False, message='Quantity must be greater than 0.', error_code='VALIDATION_ERROR')
        try:
            price = self.get_price(req.symbol)
            account = self.repo.get(req.account_id)
            held = account.holdings.get(req.symbol, 0)
            if held == 0:
                return ResponseEnvelope(success=False, message='You do not hold any shares of this symbol.', error_code='INSUFFICIENT_SHARES')
            if held < req.quantity:
                return ResponseEnvelope(success=False, message='Insufficient shares. You cannot sell more than you hold.', error_code='INSUFFICIENT_SHARES')
            account.holdings[req.symbol] = held - req.quantity
            proceeds = price * req.quantity
            account.cash_balance += proceeds
            if account.holdings[req.symbol] == 0:
                del account.holdings[req.symbol]
            tx = Transaction(
                tx_id=str(uuid4()), timestamp=datetime.utcnow(), type='SELL', symbol=req.symbol,
                quantity=req.quantity, amount=proceeds, price_per_share=price,
                resulting_cash_balance=account.cash_balance,
                resulting_holdings=deepcopy(account.holdings)
            )
            account.transactions.append(tx)
            self.repo.update(account)
            return ResponseEnvelope(success=True, message='Sell order recorded successfully.', data={'cash_balance': account.cash_balance, 'holdings': account.holdings})
        except PriceRetrievalError:
            return ResponseEnvelope(success=False, message='Unable to retrieve share price for the selected symbol.', error_code='PRICE_RETRIEVAL')
        except NotFoundError as e:
            return ResponseEnvelope(success=False, message=e.message, error_code=e.code)
        except Exception:
            return ResponseEnvelope(success=False, message='Unable to record sell transaction at the moment. Please try again later.', error_code='SERVER_ERROR')

class PortfolioService:
    def __init__(self, repo: AccountRepository, price_provider=get_share_price):
        self.repo = repo
        self.get_price = price_provider

    def compute_portfolio(self, account_id: str) -> ResponseEnvelope:
        try:
            account = self.repo.get(account_id)
            rows = []
            total_holdings_value = 0.0
            warning = False
            for symbol, qty in account.holdings.items():
                try:
                    price = self.get_price(symbol)
                    market_value = price * qty
                    rows.append({'Symbol': symbol, 'Quantity': qty, 'Current price': price, 'Market value': market_value})
                    total_holdings_value += market_value
                except PriceRetrievalError:
                    rows.append({'Symbol': symbol, 'Quantity': qty, 'Current price': 'N/A', 'Market value': 'N/A'})
                    warning = True
            total_portfolio_value = account.cash_balance + total_holdings_value
            data = {
                'holdings_table': rows,
                'cash_balance': account.cash_balance,
                'total_holdings_value': total_holdings_value,
                'total_portfolio_value': total_portfolio_value
            }
            message = 'Portfolio loaded.'
            if not account.holdings and account.cash_balance == 0:
                message = 'You have no holdings yet.'
            if warning:
                data['warning'] = 'Some share prices could not be retrieved. Values marked N/A.'
            return ResponseEnvelope(success=True, message=message, data=data)
        except NotFoundError as e:
            return ResponseEnvelope(success=False, message=e.message, error_code=e.code)
        except Exception:
            return ResponseEnvelope(success=False, message='Unable to load portfolio at the moment.', error_code='SERVER_ERROR')

    def compute_profit_loss(self, account_id: str) -> ResponseEnvelope:
        # Baseline rule: sum of all deposit transactions to date
        try:
            account = self.repo.get(account_id)
            baseline = sum(tx.amount for tx in account.transactions if tx.type == 'DEPOSIT')
            port_resp = self.compute_portfolio(account_id)
            if not port_resp.success:
                return port_resp
            total_portfolio_value = port_resp.data['total_portfolio_value']
            if baseline == 0:
                return ResponseEnvelope(success=True, message='No deposit baseline available.', data={'baseline': 0, 'profit_loss': 'N/A'})
            pl = total_portfolio_value - baseline
            status = 'Profit' if pl > 0 else 'Loss' if pl < 0 else 'Break-even'
            return ResponseEnvelope(success=True, message='P/L calculated.', data={'baseline': baseline, 'total_portfolio_value': total_portfolio_value, 'profit_loss': pl, 'status': status})
        except NotFoundError as e:
            return ResponseEnvelope(success=False, message=e.message, error_code=e.code)
        except Exception:
            return ResponseEnvelope(success=False, message='Unable to compute profit/loss at the moment.', error_code='SERVER_ERROR')

class SnapshotService:
    def __init__(self, repo: AccountRepository, price_provider=get_share_price):
        self.repo = repo
        self.get_price = price_provider

    def snapshot(self, req: SnapshotRequest) -> ResponseEnvelope:
        try:
            account = self.repo.get(req.account_id)
            if req.timestamp < account.created_at or req.timestamp > datetime.utcnow():
                return ResponseEnvelope(success=False, message='Selected time is outside the account history range.', error_code='SNAPSHOT_RANGE')
            holdings: Dict[str,int] = {}
            cash = 0.0
            deposits_baseline = 0.0
            for tx in sorted(account.transactions, key=lambda t: t.timestamp):
                if tx.timestamp <= req.timestamp:
                    if tx.type == 'DEPOSIT':
                        cash += tx.amount
                        deposits_baseline += tx.amount
                    elif tx.type == 'WITHDRAWAL':
                        cash -= tx.amount
                    elif tx.type == 'BUY':
                        cash -= tx.amount
                        holdings[tx.symbol] = holdings.get(tx.symbol, 0) + (tx.quantity or 0)
                    elif tx.type == 'SELL':
                        cash += tx.amount
                        holdings[tx.symbol] = holdings.get(tx.symbol, 0) - (tx.quantity or 0)
                        if holdings[tx.symbol] <= 0:
                            del holdings[tx.symbol]
            # Valuation using current prices (simplified rule)
            rows = []
            total_holdings_value = 0.0
            for symbol, qty in holdings.items():
                try:
                    price = self.get_price(symbol)
                    mv = price * qty
                    rows.append({'Symbol': symbol, 'Quantity': qty, 'Current price': price, 'Market value': mv})
                    total_holdings_value += mv
                except PriceRetrievalError:
                    rows.append({'Symbol': symbol, 'Quantity': qty, 'Current price': 'N/A', 'Market value': 'N/A'})
            total_portfolio_value = cash + total_holdings_value
            if not account.transactions or req.timestamp < account.transactions[0].timestamp:
                return ResponseEnvelope(success=True, message='No activity before this time.', data={'holdings_table': [], 'cash_balance': 0.0, 'total_holdings_value': 0.0, 'total_portfolio_value': 0.0, 'profit_loss': 0.0})
            baseline = deposits_baseline
            pl = 'N/A' if baseline == 0 else (total_portfolio_value - baseline)
            data = {
                'timestamp': req.timestamp.isoformat(),
                'holdings_table': rows,
                'cash_balance': cash,
                'total_holdings_value': total_holdings_value,
                'total_portfolio_value': total_portfolio_value,
                'baseline': baseline,
                'profit_loss': pl
            }
            return ResponseEnvelope(success=True, message='Snapshot generated.', data=data)
        except NotFoundError as e:
            return ResponseEnvelope(success=False, message=e.message, error_code=e.code)
        except Exception:
            return ResponseEnvelope(success=False, message='Unable to generate snapshot at the moment.', error_code='SERVER_ERROR')
```

### 2.6 Backend Response Format
Consistent JSON-like dict through `ResponseEnvelope`:
```
{
  success: bool,
  message: str,
  data: { ... } | null,
  error_code: str | null
}
```
UI logic chooses component to display based on `success` and `error_code`.

### 2.7 Invariants & Enforcement
- Non-negative `cash_balance` enforced by pre-checks in withdrawal & buy.
- Non-negative holdings enforced by pre-checks in sell.
- Atomic operations: each mutation sequence either fully applied or rolled back (current design avoids partial commit by only mutating in memory before `update`).

## 3. Gradio Frontend Design

### 3.1 Screens & Tabs
Tabs: `Create Account`, `Account Overview`, `Trade`, `History Snapshot`, `Transactions`.

### 3.2 Component Mapping Table
| User Story | Backend Method | Gradio Inputs | Action Button | Feedback Components | Data Display |
|------------|----------------|---------------|---------------|--------------------|--------------|
| US-001 Create | `AccountService.create_account` | `Username: gr.Textbox`, `Display name: gr.Textbox` | `Create Account` | `gr.Info` / `gr.Error` | Post-create account summary `gr.Markdown` |
| US-002 Deposit | `MoneyService.deposit` | `Deposit amount: gr.Number` | `Deposit` | `gr.Info` / `gr.Error` | Updated cash `gr.Markdown` |
| US-003 Withdraw | `MoneyService.withdraw` | `Withdrawal amount: gr.Number` | `Withdraw` | `gr.Info` / `gr.Error` | Updated cash `gr.Markdown` |
| US-004 Buy | `TradingService.buy` | `Symbol: gr.Dropdown`, `Quantity: gr.Number` | `Buy` | `gr.Info` / `gr.Error` | Holdings table refresh |
| US-005 Sell | `TradingService.sell` | `Symbol: gr.Dropdown`, `Quantity: gr.Number` | `Sell` | `gr.Info` / `gr.Error` | Holdings table refresh |
| US-006 Portfolio | `PortfolioService.compute_portfolio` | (account id hidden) | `Refresh Portfolio` | `gr.Info` / `gr.Warning` / `gr.Error` | `gr.DataFrame` holdings + summary |
| US-007 P/L | `PortfolioService.compute_profit_loss` | (trigger from overview) | `Refresh P/L` | `gr.Info` / `gr.Error` | Colored `gr.Markdown` |
| US-008 Snapshot | `SnapshotService.snapshot` | `Timestamp: gr.Dropdown` | `View Snapshot` | `gr.Info` / `gr.Error` | `gr.DataFrame` + summary |
| US-009 Transactions | (repo read) | Optional filters: `Type: gr.Dropdown`, `Symbol: gr.Dropdown` | `Apply Filters` | `gr.Info` / `gr.Error` | `gr.DataFrame` |
| US-010 Global | Enforced in services | — | — | Errors mapped | State remains valid |

### 3.3 Layout Specification (Pseudo Code)
```python
with gr.Blocks(title='Trading Simulation') as app:
    state_account_id = gr.State()

    with gr.Tab('Create Account'):
        with gr.Row():
            with gr.Column(scale=1):
                username = gr.Textbox(label='Username', placeholder='Enter a unique username', interactive=True)
                display_name = gr.Textbox(label='Display name', placeholder='Enter a display name (optional)')
                create_btn = gr.Button('Create Account')
                create_msg = gr.Markdown()  # dynamic

    with gr.Tab('Account Overview'):
        with gr.Row():
            cash_box = gr.Markdown()  # shows cash
            pl_box = gr.Markdown()    # profit/loss colored
        refresh_portfolio_btn = gr.Button('Refresh Portfolio')
        refresh_pl_btn = gr.Button('Refresh P/L')
        holdings_df = gr.DataFrame(headers=['Symbol','Quantity','Current price','Market value'])
        warning_box = gr.Markdown(visible=False)

    with gr.Tab('Trade'):
        symbol_dd = gr.Dropdown(choices=['AAPL','TSLA','GOOGL'], label='Symbol')
        quantity_num = gr.Number(label='Quantity', placeholder='Enter number of shares')
        buy_btn = gr.Button('Buy')
        sell_btn = gr.Button('Sell')
        trade_msg = gr.Markdown()

    with gr.Tab('History Snapshot'):
        timestamp_dd = gr.Dropdown(label='Select timestamp')
        snapshot_btn = gr.Button('View Snapshot')
        snapshot_df = gr.DataFrame()
        snapshot_summary = gr.Markdown()

    with gr.Tab('Transactions'):
        filter_type = gr.Dropdown(choices=['ALL','DEPOSIT','WITHDRAWAL','BUY','SELL'], value='ALL', label='Type')
        filter_symbol = gr.Dropdown(choices=['ALL','AAPL','TSLA','GOOGL'], value='ALL', label='Symbol')
        filter_btn = gr.Button('Apply Filters')
        tx_df = gr.DataFrame()
        tx_msg = gr.Markdown()
```

### 3.4 User-Facing Messages Mapping
- Success:
  - Create: `Account created successfully.`
  - Deposit: `Deposit successful.`
  - Withdraw: `Withdrawal successful.`
  - Buy: `Buy order recorded successfully.`
  - Sell: `Sell order recorded successfully.`
- Validation Errors: from service (`Username is required.` / `Deposit amount must be greater than 0.` etc.) displayed in `gr.Markdown` styled as error (or custom CSS); could use `gr.Notification` when available.
- Warnings: `Some share prices could not be retrieved. Values marked N/A.` displayed when portfolio partial.
- Empty States: `You have no holdings yet.`, `No transactions have been recorded yet.`, `No activity before this time.`
- Technical Errors: Generic fallback messages defined in services.

### 3.5 Input Validation (Client-Side + Backend)
- Prior to calling backend: simple checks (non-empty username, numeric >0 amounts) using Python callback; if fail, do not call service.
- Backend always re-validates.

### 3.6 Accessibility & Responsiveness
- Use explicit labels for all inputs.
- Ensure tab order logical: creation form fields followed by button.
- Profit/Loss: include textual status (`Profit`, `Loss`, `Break-even`) in addition to color.
- DataFrames: include captions via adjacent Markdown (e.g., `### Current Holdings`).

## 4. Integration Points

### 4.1 Callback Pattern
Each button binds to a Python function that:
1. Extracts component values.
2. Builds Request Pydantic model (handling validation errors -> UI error message).
3. Calls service method.
4. Parses `ResponseEnvelope` to update UI components (data tables, textboxes, messages).

### 4.2 Data Flow Example (Buy Operation)
```
User inputs -> Symbol & Quantity -> Click Buy
  -> Gradio callback builds BuyRequest
    -> TradingService.buy() validates & executes
      -> Repository mutation + transaction append
        -> ResponseEnvelope(success=True, data={cash_balance, holdings})
          -> UI updates cash_box, holdings_df, trade_msg
```

### 4.3 Error Propagation
- Service returns `success=False` + `error_code` → UI chooses styling (red text, persistent form values).
- Price retrieval failures produce specific message; holdings not changed.

### 4.4 Message Mapping Table (Errors)
| error_code | UI Message | Component |
|------------|------------|-----------|
| DUPLICATE_USERNAME | Username already exists. Please choose another. | Create form message |
| VALIDATION_ERROR | Specific field validation message | Adjacent Markdown |
| INSUFFICIENT_FUNDS | Insufficient funds. You cannot afford this purchase. / Withdrawal negative balance variant | Trade / Withdraw message |
| INSUFFICIENT_SHARES | Insufficient shares. You cannot sell more than you hold. | Trade message |
| PRICE_RETRIEVAL | Unable to retrieve share price for the selected symbol. | Trade / Portfolio warning |
| SNAPSHOT_RANGE | Selected time is outside the account history range. | Snapshot message |
| NOT_FOUND | Account not found. | Global error message |
| SERVER_ERROR | Generic operation-specific failure text | Relevant tab message |

### 4.5 Snapshot Reconstruction Flow
1. User selects timestamp -> callback retrieves list of transaction timestamps -> builds `SnapshotRequest`.
2. `SnapshotService.snapshot()` reconstructs state; valuations use current prices.
3. Response data populates snapshot DF + summary.

## 5. Implementation Examples

### 5.1 Instantiating Services
```python
repo = AccountRepository()
account_service = AccountService(repo)
money_service = MoneyService(repo)
trading_service = TradingService(repo)
portfolio_service = PortfolioService(repo)
snapshot_service = SnapshotService(repo)
```

### 5.2 Example Gradio Callback (Create Account)
```python
def on_create(username: str, display_name: str):
    if not username.strip():
        return 'Username is required.', ''
    req = CreateAccountRequest(username=username.strip(), display_name=display_name or None)
    resp = account_service.create_account(req)
    if resp.success:
        account_id = resp.data['account']['account_id']
        return resp.message, account_id
    else:
        return resp.message, ''

create_btn.click(on_create, inputs=[username, display_name], outputs=[create_msg, state_account_id])
```

### 5.3 Updating Holdings Table After Trade
```python
def refresh_portfolio(account_id: str):
    if not account_id:
        return [], 'No account selected.', '', '', ''
    resp = portfolio_service.compute_portfolio(account_id)
    if resp.success:
        rows = resp.data['holdings_table']
        cash = resp.data['cash_balance']
        thv = resp.data['total_holdings_value']
        tpv = resp.data['total_portfolio_value']
        warning = resp.data.get('warning','')
        return rows, f"Cash: {cash}", f"Holdings Value: {thv}", f"Portfolio Value: {tpv}", warning
    else:
        return [], resp.message, '', '', ''
```

### 5.4 Unit Test Skeleton (Pytest)
```python
def test_create_account_success():
    repo = AccountRepository()
    svc = AccountService(repo)
    req = CreateAccountRequest(username='alice')
    resp = svc.create_account(req)
    assert resp.success
    assert resp.data['account']['cash_balance'] == 0

def test_buy_insufficient_funds():
    repo = AccountRepository()
    acc_resp = AccountService(repo).create_account(CreateAccountRequest(username='bob'))
    acc_id = acc_resp.data['account']['account_id']
    trading = TradingService(repo)
    resp = trading.buy(BuyRequest(account_id=acc_id, symbol='AAPL', quantity=10))
    assert not resp.success
    assert resp.error_code == 'INSUFFICIENT_FUNDS'
```

## 6. Testing & QA Guidelines

### 6.1 Backend Tests
- Coverage Targets: ≥90% for services.
- Scenarios:
  - Account creation (duplicate, success, server error simulation)
  - Deposit/Withdraw (boundary: 0, negative, large values)
  - Buy/Sell (affordability, holdings check, price retrieval failure)
  - Portfolio computation (empty, partial price failure)
  - Profit/Loss (no deposits, profit, loss, break-even)
  - Snapshot (early timestamp, mid history, after latest, out-of-range)
  - Invariant enforcement (attempt negative cash / negative holdings)

### 6.2 Frontend Tests
- Gradio interaction tests (Playwright or Selenium):
  - Create account flow snapshot.
  - Deposit then verify updated cash.
  - Buy trade updates holdings table.
  - Sell trade reduces holdings.
  - Portfolio refresh displays warning for unsupported symbol.
  - Snapshot selection renders expected state.
  - Filters in Transactions tab.

### 6.3 Integration Tests
- End-to-end scenario: Create -> Deposit -> Buy -> Sell -> Portfolio -> P/L -> Snapshot -> Transactions ordering.
- Assert message strings exactly match acceptance criteria.

### 6.4 Accessibility Testing
- Keyboard navigation (Tab sequence) across all tabs.
- Profit/Loss color + textual status.
- Table headers announced by screen reader (verify DOM structure).

## 7. Dependencies & Setup

### 7.1 Python Dependencies (Add to `pyproject.toml`)
- `pydantic>=2.6.0`
- `gradio>=4.0.0`
- `pytest` (dev)
- `typing_extensions` (optional)

### 7.2 Installation
```bash
pip install pydantic gradio pytest
```

### 7.3 Runtime Configuration
- No external services required.
- Fixed price provider by default; override with environment var `PRICE_PROVIDER=real` (future extension).

## 8. Definition of Done
- All user stories US-001..US-010 satisfied with specified messages.
- Backend services implemented with full type hints & docstrings.
- Gradio UI provides tabs and interactive components per mapping.
- ResponseEnvelope consistently used; no raw dict outputs.
- Automated tests achieve coverage target and pass CI.
- No operation can produce negative cash or negative holdings.
- Profit/Loss baseline consistent (sum of all deposits to date) and documented.
- Snapshot reconstruction validated for multiple timestamps.
- Accessibility checks passed (textual status + keyboard navigation).
- Documentation (this file) stored under version control.

## 9. Future Extensions (Non-Blocking)
- Historical price storage for accurate time-based valuations.
- Persistent storage layer (SQLite/PostgreSQL) replacing in-memory repo.
- Real-time updates via WebSockets.
- Export transactions to CSV.

---
**End of Technical Design**
