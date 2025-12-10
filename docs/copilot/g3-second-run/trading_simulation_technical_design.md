# Technical Design: Trading Simulation Platform

**Feature**: Trading Simulation Account Management
**Source**: trading_simulation_user_stories.md
**Status**: Draft
**Author**: Engineering Lead (AI)

## 1. Overview & Architecture

### 1.1 High-Level Architecture
The system follows a clean separation of concerns between the business logic (Backend) and the user interface (Frontend).

*   **Backend**: A Python module (`trading_simulation.py`) containing the core domain logic, data models, and transaction processing. It manages user accounts, portfolios, and trade execution. It uses in-memory storage for simplicity as per requirements.
*   **Frontend**: A Gradio web application (`app.py`) that interacts with the backend. It handles user input, displays real-time updates, and manages the UI state.

### 1.2 Technology Stack
*   **Language**: Python 3.10+
*   **Frontend Framework**: Gradio (latest stable)
*   **Data Validation**: Pydantic
*   **Testing**: Pytest

### 1.3 File Structure
```
src/crew_generated/engineering/
├── trading_simulation.py  # Core backend logic and models
├── app.py                 # Gradio frontend application
└── requirements.txt       # Dependencies
```

---

## 2. Python Backend Design

### 2.1 Module: `trading_simulation.py`

#### 2.1.1 Data Models (Pydantic)

```python
from enum import Enum
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, PositiveFloat

class TransactionType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    BUY = "BUY"
    SELL = "SELL"

class Transaction(BaseModel):
    """Represents a single financial event."""
    timestamp: datetime = Field(default_factory=datetime.now)
    type: TransactionType
    symbol: Optional[str] = None
    quantity: float = 0.0
    price: float = 0.0
    total_amount: float  # Positive for inflow, negative for outflow
    description: str

class Holding(BaseModel):
    """Represents ownership of a specific stock."""
    symbol: str
    quantity: int = 0
    average_cost: float = 0.0

class AccountData(BaseModel):
    """Internal state of a user account."""
    username: str
    cash_balance: float = 0.0
    holdings: Dict[str, Holding] = Field(default_factory=dict)
    transactions: List[Transaction] = Field(default_factory=list)
```

#### 2.1.2 Core Class: `TradingEngine`

This class acts as the facade for all business operations.

```python
class TradingEngine:
    """
    Manages trading accounts and executes operations.
    Currently uses in-memory storage.
    """

    def __init__(self):
        self._accounts: Dict[str, AccountData] = {}

    def create_account(self, username: str) -> str:
        """
        Creates a new account.
        
        Args:
            username: Unique identifier for the user.
            
        Returns:
            Success message.
            
        Raises:
            ValueError: If username is empty or already exists.
        """
        pass

    def get_balance(self, username: str) -> float:
        """Returns current cash balance."""
        pass

    def deposit(self, username: str, amount: float) -> str:
        """
        Deposits funds into account.
        
        Args:
            username: User identifier.
            amount: Positive amount to deposit.
            
        Returns:
            Success message.
            
        Raises:
            ValueError: If amount is <= 0.
            KeyError: If user does not exist.
        """
        pass

    def withdraw(self, username: str, amount: float) -> str:
        """
        Withdraws funds from account.
        
        Raises:
            ValueError: If amount <= 0 or insufficient funds.
        """
        pass

    def get_share_price(self, symbol: str) -> float:
        """
        Mock function to get current share price.
        Supported: AAPL (150.0), TSLA (200.0), GOOGL (2800.0).
        Others return 100.0.
        """
        pass

    def buy_shares(self, username: str, symbol: str, quantity: int) -> str:
        """
        Executes a buy order.
        
        Args:
            username: User identifier.
            symbol: Stock ticker.
            quantity: Number of shares (must be > 0).
            
        Raises:
            ValueError: If quantity <= 0 or insufficient funds.
        """
        pass

    def sell_shares(self, username: str, symbol: str, quantity: int) -> str:
        """
        Executes a sell order.
        
        Raises:
            ValueError: If quantity <= 0 or insufficient shares owned.
        """
        pass

    def get_portfolio_summary(self, username: str) -> List[List]:
        """
        Returns data for the holdings table.
        Format: [[Symbol, Quantity, Current Price, Total Value], ...]
        """
        pass

    def get_transaction_history(self, username: str) -> List[List]:
        """
        Returns data for the transaction history table.
        Format: [[Time, Type, Symbol, Quantity, Price, Total Amount], ...]
        """
        pass
        
    def get_performance_metrics(self, username: str) -> Dict[str, float]:
        """
        Returns {'total_value': float, 'profit_loss': float}
        """
        pass
```

### 2.2 Error Handling Strategy
*   **Custom Exceptions**:
    *   `InsufficientFundsError(Exception)`
    *   `InsufficientHoldingsError(Exception)`
    *   `AccountNotFoundError(Exception)`
*   **Validation**:
    *   Input validation (negative numbers, empty strings) raises `ValueError`.
    *   Business logic validation (funds, holdings) raises custom exceptions.

---

## 3. Gradio Frontend Design

### 3.1 UI Layout & Components

The UI will be organized into a main `gr.Blocks` container with a login/creation row at the top, followed by tabs for different activities.

#### 3.1.1 Top Section: Account Management (US-001)
*   **Row**:
    *   `username_input` (`gr.Textbox`): Label="Username"
    *   `create_btn` (`gr.Button`): Label="Create Account", Variant="primary"
    *   `login_btn` (`gr.Button`): Label="Login / Refresh", Variant="secondary"
*   **Output**: `gr.Info` for success, `gr.Warning` for errors.

#### 3.1.2 Tab 1: Dashboard (US-006)
*   **Metrics Row**:
    *   `cash_display` (`gr.Number`): Label="Cash Balance"
    *   `portfolio_value_display` (`gr.Number`): Label="Total Portfolio Value"
    *   `pl_display` (`gr.Number`): Label="Total Profit/Loss"
*   **Holdings**:
    *   `holdings_table` (`gr.DataFrame`): Headers=["Symbol", "Quantity", "Current Price", "Value"]

#### 3.1.3 Tab 2: Trade (US-004, US-005)
*   **Inputs**:
    *   `symbol_input` (`gr.Dropdown`): Choices=["AAPL", "TSLA", "GOOGL"], Label="Symbol"
    *   `quantity_input` (`gr.Number`): Label="Quantity", Precision=0
*   **Actions**:
    *   `buy_btn` (`gr.Button`): Label="Buy Shares", Variant="primary"
    *   `sell_btn` (`gr.Button`): Label="Sell Shares", Variant="stop"

#### 3.1.4 Tab 3: Funds (US-002, US-003)
*   **Input**:
    *   `amount_input` (`gr.Number`): Label="Amount ($)"
*   **Actions**:
    *   `deposit_btn` (`gr.Button`): Label="Deposit"
    *   `withdraw_btn` (`gr.Button`): Label="Withdraw"

#### 3.1.5 Tab 4: History (US-007)
*   `history_table` (`gr.DataFrame`): Headers=["Time", "Type", "Symbol", "Quantity", "Price", "Amount"]

### 3.2 User-Facing Messages
*   **Success**: "Account created...", "Deposited $...", "Bought 5 AAPL..." (displayed via `gr.Info`).
*   **Error**: "Insufficient funds", "Username cannot be empty" (displayed via `gr.Error` or `gr.Warning`).

---

## 4. Integration Points

### 4.1 Data Flow
1.  **User Action**: User clicks a button (e.g., "Buy").
2.  **Frontend Handler**: Gradio callback function is triggered.
3.  **Backend Call**: Handler calls `trading_engine.buy_shares(username, symbol, qty)`.
4.  **Exception Handling**:
    *   `try...except` block wraps the backend call.
    *   If `ValueError` or Custom Exception -> `raise gr.Error(str(e))`.
5.  **Success Response**:
    *   Backend returns success message string.
    *   Frontend shows `gr.Info(message)`.
6.  **UI Update**:
    *   Handler returns updated data for `holdings_table`, `cash_display`, etc., to refresh the view.

### 4.2 State Management
*   A global instance `engine = TradingEngine()` will be instantiated at the module level in `app.py`.
*   The `username` will be passed as an input to every transaction function to identify the context.

---

## 5. Implementation Examples

### 5.1 Backend Method Example
```python
def buy_shares(self, username: str, symbol: str, quantity: int) -> str:
    if quantity <= 0:
        raise ValueError("Quantity must be positive")
    
    account = self._get_account(username)
    price = self.get_share_price(symbol)
    total_cost = price * quantity
    
    if account.cash_balance < total_cost:
        raise InsufficientFundsError(f"Insufficient funds. Required: ${total_cost:.2f}")
    
    # Update state
    account.cash_balance -= total_cost
    # ... update holdings and transactions ...
    
    return f"Bought {quantity} {symbol} @ ${price:.2f}"
```

### 5.2 Frontend Callback Example
```python
def on_buy(username, symbol, quantity):
    try:
        msg = engine.buy_shares(username, symbol, quantity)
        gr.Info(msg)
        # Return updated dashboard data
        return get_dashboard_data(username)
    except Exception as e:
        raise gr.Error(str(e))
```

---

## 6. Testing & QA Guidelines

### 6.1 Unit Tests (`tests/test_trading_backend.py`)
*   **Account Creation**: Verify unique usernames, initial state.
*   **Funds**: Test deposit/withdraw logic, boundary checks (0, negative), insufficient funds.
*   **Trading**: Test buy/sell logic, cost calculation, holding updates, selling unowned shares.
*   **Calculations**: Verify P/L and portfolio value math.

### 6.2 Integration/E2E Tests
*   Use Playwright to interact with the Gradio app.
*   **Flow**: Create Account -> Deposit -> Buy -> Verify Holdings -> Sell -> Withdraw -> Verify History.

---

## 7. Dependencies & Setup

### 7.1 Requirements
```text
gradio>=4.0.0
pydantic>=2.0.0
pandas
```

### 7.2 Setup
1.  Install dependencies: `pip install -r requirements.txt`
2.  Run app: `python src/crew_generated/engineering/app.py`

---

## 8. Definition of Done
*   [ ] `trading_simulation.py` implements all `TradingEngine` methods.
*   [ ] `app.py` implements the full UI layout and connects all buttons.
*   [ ] All User Stories (US-001 to US-007) are demonstrable in the UI.
*   [ ] Code includes type hints and docstrings.
*   [ ] Unit tests cover >80% of backend logic.
