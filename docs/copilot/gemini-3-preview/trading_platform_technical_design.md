# Trading Platform Technical Design

## 1. Overview & Architecture

### High-Level Architecture
The system follows a clean separation of concerns between the User Interface (Gradio) and the Business Logic (Python Backend).

```mermaid
graph TD
    User[User] <--> UI[Gradio Frontend]
    UI <--> Controller[Integration Layer]
    Controller <--> Backend[Trading Engine (Python)]
    Backend <--> Data[In-Memory Data Store]
    Backend <--> Market[Market Data Service]
```

### Technology Stack
- **Language**: Python 3.10+
- **Frontend Framework**: Gradio 4.x
- **Data Validation**: Pydantic 2.x
- **Testing**: Pytest

### Design Principles
- **Separation of Concerns**: UI code is distinct from business logic.
- **Type Safety**: Extensive use of Python type hints and Pydantic models.
- **Fail-Fast**: Explicit error handling with custom exceptions.
- **Stateless Backend**: The backend methods are designed to be stateless where possible, relying on the data store.

---

## 2. Python Backend Design

### Module Structure
```
src/
├── trading_platform/
│   ├── __init__.py
│   ├── models.py          # Pydantic data models
│   ├── exceptions.py      # Custom exceptions
│   ├── engine.py          # Core business logic
│   └── utils.py           # Helper functions (e.g., get_share_price)
```

### Data Models (`models.py`)

We will use Pydantic for robust data validation and serialization.

```python
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, PositiveFloat, PositiveInt

class TransactionType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    BUY = "BUY"
    SELL = "SELL"

class Transaction(BaseModel):
    id: str = Field(..., description="Unique transaction ID")
    timestamp: datetime = Field(default_factory=datetime.now)
    type: TransactionType
    symbol: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    amount: float = Field(..., description="Total value of transaction")
    balance_after: float

class Holding(BaseModel):
    symbol: str
    quantity: int
    average_cost: float

class Portfolio(BaseModel):
    holdings: List[Holding]
    total_value: float
    cash_balance: float
    initial_deposit: float
    profit_loss: float
    profit_loss_percent: float

class Account(BaseModel):
    username: str
    cash_balance: float = 0.0
    holdings: dict[str, Holding] = Field(default_factory=dict)
    transactions: List[Transaction] = Field(default_factory=list)
    initial_deposit: float = 0.0
```

### Custom Exceptions (`exceptions.py`)

```python
class TradingPlatformError(Exception):
    """Base exception for the application."""
    pass

class UserNotFoundError(TradingPlatformError):
    """Raised when a user account is not found."""
    pass

class UserAlreadyExistsError(TradingPlatformError):
    """Raised when attempting to create a duplicate user."""
    pass

class InsufficientFundsError(TradingPlatformError):
    """Raised when withdrawal or purchase exceeds balance."""
    pass

class InsufficientSharesError(TradingPlatformError):
    """Raised when selling more shares than owned."""
    pass

class InvalidAmountError(TradingPlatformError):
    """Raised for non-positive amounts where positive is required."""
    pass
```

### Core Logic (`engine.py`)

The `TradingEngine` class encapsulates all business rules.

```python
from typing import List, Dict
from .models import Account, Portfolio, Transaction, TransactionType
from .exceptions import *

class TradingEngine:
    def __init__(self):
        self._accounts: Dict[str, Account] = {}

    def create_account(self, username: str) -> Account:
        """
        Creates a new user account.
        
        Args:
            username: Unique identifier for the user.
            
        Returns:
            The created Account object.
            
        Raises:
            UserAlreadyExistsError: If username is taken.
            ValueError: If username is empty.
        """
        pass

    def deposit(self, username: str, amount: float) -> Account:
        """
        Deposits funds into a user's account.
        
        Args:
            username: The user to deposit to.
            amount: Positive amount to deposit.
            
        Returns:
            Updated Account object.
            
        Raises:
            UserNotFoundError: If user doesn't exist.
            InvalidAmountError: If amount <= 0.
        """
        pass

    def withdraw(self, username: str, amount: float) -> Account:
        """
        Withdraws funds from a user's account.
        
        Args:
            username: The user to withdraw from.
            amount: Positive amount to withdraw.
            
        Returns:
            Updated Account object.
            
        Raises:
            UserNotFoundError: If user doesn't exist.
            InvalidAmountError: If amount <= 0.
            InsufficientFundsError: If balance < amount.
        """
        pass

    def buy_shares(self, username: str, symbol: str, quantity: int) -> Transaction:
        """
        Executes a buy order.
        
        Args:
            username: The buyer.
            symbol: Stock symbol (e.g., 'AAPL').
            quantity: Number of shares to buy (must be > 0).
            
        Returns:
            The executed Transaction record.
            
        Raises:
            UserNotFoundError: If user doesn't exist.
            InvalidAmountError: If quantity <= 0.
            InsufficientFundsError: If cost > cash_balance.
        """
        pass

    def sell_shares(self, username: str, symbol: str, quantity: int) -> Transaction:
        """
        Executes a sell order.
        
        Args:
            username: The seller.
            symbol: Stock symbol.
            quantity: Number of shares to sell (must be > 0).
            
        Returns:
            The executed Transaction record.
            
        Raises:
            UserNotFoundError: If user doesn't exist.
            InvalidAmountError: If quantity <= 0.
            InsufficientSharesError: If user owns fewer shares than requested.
        """
        pass

    def get_portfolio(self, username: str) -> Portfolio:
        """
        Calculates current portfolio state including real-time value and P/L.
        
        Args:
            username: The user to query.
            
        Returns:
            Portfolio object with calculated metrics.
        """
        pass

    def get_transaction_history(self, username: str) -> List[Transaction]:
        """
        Retrieves all transactions for a user.
        """
        pass
```

---

## 3. Gradio Frontend Design

### UI Layout & Workflow

The UI will use `gr.Blocks` with a `gr.Tabs` structure to organize functionality.

**Global State**: `current_user = gr.State(value=None)`

#### Tab 1: Login / Register
- **Input**: `username_input` (Textbox)
- **Action**: `login_btn` (Button), `register_btn` (Button)
- **Output**: `login_status` (Markdown/Info), updates `current_user` state.

#### Tab 2: Dashboard (Portfolio)
- **Display**:
  - `portfolio_summary` (Row of Numbers: Total Value, Cash, P/L)
  - `holdings_table` (DataFrame: Symbol, Qty, Price, Value)
- **Action**: `refresh_btn` (Button)

#### Tab 3: Trade
- **Input**:
  - `trade_symbol` (Dropdown: AAPL, TSLA, GOOGL)
  - `trade_qty` (Number)
  - `trade_action` (Radio/Buttons: Buy, Sell)
- **Output**: `trade_status` (Markdown), updates Dashboard.

#### Tab 4: Funds
- **Input**: `fund_amount` (Number)
- **Action**: `deposit_btn` (Button), `withdraw_btn` (Button)
- **Output**: `fund_status` (Markdown), updates Dashboard.

#### Tab 5: History
- **Display**: `history_table` (DataFrame)

### User-Facing Messages

| Event | Success Message (gr.Info) | Error Message (gr.Error/Warning) |
|-------|---------------------------|----------------------------------|
| Create Account | "Account '{username}' created successfully" | "Username cannot be empty", "Username already exists" |
| Deposit | "Deposited ${amount}" | "Amount must be positive" |
| Withdraw | "Withdrawn ${amount}" | "Insufficient funds", "Amount must be positive" |
| Buy | "Bought {qty} shares of {symbol}..." | "Insufficient funds", "Quantity must be positive" |
| Sell | "Sold {qty} shares of {symbol}..." | "Insufficient shares", "You do not own..." |

---

## 4. Integration Points

### Data Flow
1.  **User Action**: User clicks a button in Gradio.
2.  **Event Handler**: A Python function in `app.py` is triggered.
3.  **Backend Call**: The handler calls a method on the global `trading_engine` instance.
4.  **Exception Handling**: The handler wraps the call in a `try/except` block.
    *   `try`: Returns success message and updates UI components.
    *   `except TradingPlatformError as e`: Raises `gr.Error(str(e))`.
5.  **UI Update**: Gradio updates the components with the returned values.

### Example Integration Code

```python
def on_deposit(username, amount):
    if not username:
        raise gr.Warning("Please login first.")
    try:
        account = engine.deposit(username, amount)
        return f"Deposited ${amount:.2f}. New Balance: ${account.cash_balance:.2f}"
    except InvalidAmountError as e:
        raise gr.Error(str(e))
    except Exception as e:
        raise gr.Error(f"System Error: {str(e)}")
```

---

## 5. Implementation Examples

### Backend Usage
```python
engine = TradingEngine()
try:
    acc = engine.create_account("Trader1")
    engine.deposit("Trader1", 1000.0)
    engine.buy_shares("Trader1", "AAPL", 5)
    portfolio = engine.get_portfolio("Trader1")
    print(f"P/L: {portfolio.profit_loss}")
except InsufficientFundsError:
    print("Not enough money!")
```

### Frontend Skeleton
```python
with gr.Blocks() as app:
    user_state = gr.State()
    
    with gr.Tab("Login"):
        username_in = gr.Textbox(label="Username")
        create_btn = gr.Button("Create Account")
        
    with gr.Tab("Dashboard"):
        # ... components ...
        pass

    # Event wiring
    create_btn.click(
        fn=handle_create_account,
        inputs=[username_in],
        outputs=[user_state, login_msg]
    )
```

---

## 6. Testing & QA Guidelines

### Backend Testing (Pytest)
- **Unit Tests**: Test each method in `TradingEngine` in isolation.
- **Edge Cases**:
  - Zero/Negative amounts for deposit/withdraw.
  - Buying more than affordable.
  - Selling more than owned.
  - Selling unowned symbols.
  - Concurrent transactions (if applicable, though single-threaded here).
- **Fixtures**: Pre-configured `TradingEngine` with populated accounts.

### Frontend Testing
- **Manual Validation**: Follow the User Stories acceptance criteria step-by-step.
- **Validation Points**:
  - Verify error messages appear as popups (`gr.Error`).
  - Verify tables update immediately after transactions.
  - Verify P/L calculations are correct (manual math check).

---

## 7. Dependencies & Setup

### `requirements.txt`
```text
gradio>=4.0.0
pydantic>=2.0.0
pandas>=2.0.0  # For DataFrame handling
pytest>=7.0.0
```

### Setup
1.  Install dependencies: `pip install -r requirements.txt`
2.  Run application: `python src/app.py`
3.  Run tests: `pytest tests/`

---

## 8. Definition of Done
- [ ] `TradingEngine` implemented with all methods and type hints.
- [ ] Pydantic models defined for all data structures.
- [ ] Custom exceptions implemented and used.
- [ ] Gradio UI implemented with all 5 tabs.
- [ ] All User Stories (US-001 to US-006) verified.
- [ ] Code is documented with docstrings.
- [ ] Unit tests passing for backend logic.
