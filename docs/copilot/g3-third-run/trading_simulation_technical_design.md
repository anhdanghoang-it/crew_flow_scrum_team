# Trading Simulation Platform - Technical Design

**Document Version:** 1.0
**Date:** December 10, 2025
**Status:** Draft
**Author:** Engineering Lead (AI)

---

## 1. Overview & Architecture

### System Architecture
The Trading Simulation Platform is a monolithic application built with a Python backend for business logic and a Gradio frontend for the user interface. The system follows a layered architecture where the UI layer interacts with the domain layer through a well-defined API surface.

```mermaid
graph TD
    User[User] <--> UI[Gradio Frontend (app.py)]
    UI <--> Controller[Integration Layer]
    Controller <--> Domain[Trading Domain Logic (trading_backend.py)]
    Domain <--> Data[In-Memory State / Persistence]
    Domain -.-> External[Price Service (Mock)]
```

### Technology Stack
- **Language:** Python 3.10+
- **Frontend Framework:** Gradio 4.x+
- **Data Validation:** Pydantic 2.x
- **Testing:** Pytest (Backend), Playwright (E2E)
- **Dependency Management:** uv / pip

### Module Organization
```
src/crew_generated/engineering/
├── __init__.py
├── app.py                 # Entry point, Gradio UI definition
└── trading_backend.py     # Core domain logic, data models, exceptions
```

---

## 2. Python Backend Design

### File: `src/crew_generated/engineering/trading_backend.py`

#### Data Models (Pydantic)

```python
from enum import Enum
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class TransactionType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    BUY = "BUY"
    SELL = "SELL"

class Transaction(BaseModel):
    id: str
    timestamp: datetime
    type: TransactionType
    symbol: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    amount: float  # Total value of transaction
    balance_after: float

class Holding(BaseModel):
    symbol: str
    quantity: int
    average_cost: float
    
    @property
    def total_cost(self) -> float:
        return self.quantity * self.average_cost

class PortfolioSummary(BaseModel):
    total_cash: float
    total_invested: float
    total_portfolio_value: float
    total_profit_loss: float
    total_profit_loss_percentage: float
    initial_deposit: float
```

#### Exceptions

```python
class TradingError(Exception):
    """Base exception for trading errors."""
    pass

class InsufficientFundsError(TradingError):
    """Raised when attempting to withdraw or buy more than available."""
    pass

class InsufficientSharesError(TradingError):
    """Raised when attempting to sell more shares than owned."""
    pass

class InvalidSymbolError(TradingError):
    """Raised when an unsupported symbol is used."""
    pass

class AccountError(TradingError):
    """Raised for account-related issues (e.g., duplicate username)."""
    pass
```

#### Core Class: `TradingAccount`

```python
class TradingAccount:
    """
    Manages the state of a single user account including balance,
    holdings, and transaction history.
    """
    
    def __init__(self, username: str, initial_deposit: float):
        """
        Initialize a new account.
        
        Args:
            username: Unique identifier for the user.
            initial_deposit: Starting funds (must be > 0).
            
        Raises:
            ValueError: If initial_deposit <= 0 or username is invalid.
        """
        pass

    def deposit(self, amount: float) -> Transaction:
        """
        Add funds to the account.
        
        Args:
            amount: Amount to deposit (must be > 0).
            
        Returns:
            Transaction object recording the deposit.
            
        Raises:
            ValueError: If amount <= 0.
        """
        pass

    def withdraw(self, amount: float) -> Transaction:
        """
        Withdraw funds from the account.
        
        Args:
            amount: Amount to withdraw (must be > 0).
            
        Returns:
            Transaction object recording the withdrawal.
            
        Raises:
            ValueError: If amount <= 0.
            InsufficientFundsError: If amount > available cash.
        """
        pass

    def buy_stock(self, symbol: str, quantity: int, current_price: float) -> Transaction:
        """
        Purchase shares of a stock.
        
        Args:
            symbol: Stock ticker symbol (e.g., "AAPL").
            quantity: Number of shares (must be > 0).
            current_price: Price per share.
            
        Returns:
            Transaction object recording the purchase.
            
        Raises:
            ValueError: If quantity <= 0.
            InsufficientFundsError: If cost > available cash.
            InvalidSymbolError: If symbol is not supported.
        """
        pass

    def sell_stock(self, symbol: str, quantity: int, current_price: float) -> Transaction:
        """
        Sell shares from holdings.
        
        Args:
            symbol: Stock ticker symbol.
            quantity: Number of shares to sell (must be > 0).
            current_price: Price per share.
            
        Returns:
            Transaction object recording the sale.
            
        Raises:
            ValueError: If quantity <= 0.
            InsufficientSharesError: If quantity > owned shares.
            InvalidSymbolError: If symbol is not in holdings.
        """
        pass

    def get_holdings(self) -> List[Holding]:
        """Return list of current holdings."""
        pass

    def get_transaction_history(self, 
                              type_filter: Optional[TransactionType] = None,
                              symbol_filter: Optional[str] = None) -> List[Transaction]:
        """
        Retrieve transaction history with optional filtering.
        """
        pass

    def get_portfolio_summary(self, current_prices: dict[str, float]) -> PortfolioSummary:
        """
        Calculate current portfolio metrics.
        
        Args:
            current_prices: Dictionary mapping symbols to current prices.
        """
        pass
```

#### Helper Functions

```python
def get_share_price(symbol: str) -> float:
    """
    Mock price service.
    Returns fixed prices: AAPL: 150.0, TSLA: 800.0, GOOGL: 2800.0.
    Raises InvalidSymbolError for others.
    """
    pass
```

---

## 3. Gradio Frontend Design

### File: `src/crew_generated/engineering/app.py`

The UI will use `gr.Blocks` with a tabbed interface. State will be managed using `gr.State` to persist the `TradingAccount` instance across interactions.

#### UI Component Mapping

| User Story | Backend Method | Gradio Components |
|------------|----------------|-------------------|
| **US-001** (Create) | `TradingAccount.__init__` | `gr.Textbox` (Username), `gr.Number` (Deposit), `gr.Button` (Create) |
| **US-002** (Deposit) | `TradingAccount.deposit` | `gr.Number` (Amount), `gr.Button` (Deposit), `gr.Markdown` (Balance) |
| **US-003** (Withdraw) | `TradingAccount.withdraw` | `gr.Number` (Amount), `gr.Button` (Withdraw), `gr.Markdown` (Available) |
| **US-004** (Buy) | `TradingAccount.buy_stock` | `gr.Dropdown` (Symbol), `gr.Number` (Qty), `gr.Button` (Buy) |
| **US-005** (Sell) | `TradingAccount.sell_stock` | `gr.Dropdown` (Symbol), `gr.Number` (Qty), `gr.Button` (Sell) |
| **US-006** (Holdings) | `TradingAccount.get_holdings` | `gr.DataFrame` (Table), `gr.Button` (Refresh) |
| **US-007** (P/L) | `TradingAccount.get_portfolio_summary` | `gr.Markdown` (Stats), `gr.Plot` (Optional) |
| **US-008** (History) | `TradingAccount.get_transaction_history` | `gr.DataFrame` (Table), `gr.Dropdown` (Filters) |

#### Layout Structure

```python
with gr.Blocks(title="Trading Simulator") as app:
    # Global State
    account_state = gr.State(None)  # Holds TradingAccount instance
    
    gr.Markdown("# 📈 Trading Simulation Platform")
    
    # Account Creation Section (Visible initially)
    with gr.Group(visible=True) as account_creation_group:
        # ... US-001 components ...
    
    # Main Dashboard (Hidden initially)
    with gr.Tabs(visible=False) as dashboard_tabs:
        
        with gr.Tab("Funds"):
            # ... US-002 & US-003 components ...
            
        with gr.Tab("Trade"):
            with gr.Row():
                with gr.Column():
                    # ... US-004 Buy components ...
                with gr.Column():
                    # ... US-005 Sell components ...
                    
        with gr.Tab("Portfolio"):
            # ... US-006 & US-007 components ...
            
        with gr.Tab("History"):
            # ... US-008 components ...
```

#### User-Facing Messages

- **Success**: Use `gr.Info("Message")`.
  - Example: "Account 'demo' created successfully."
  - Example: "Bought 10 AAPL at $150.00."
- **Error**: Use `gr.Error("Message")`.
  - Example: "Insufficient funds. Available: $100.00."
  - Example: "Invalid symbol."
- **Warning**: Use `gr.Warning("Message")`.
  - Example: "Selling entire position of TSLA."

---

## 4. Integration Points

### Data Flow: Buy Shares Example

1.  **User Action**: Selects "AAPL", enters quantity "10", clicks "Buy".
2.  **Frontend Validation**: Checks if inputs are valid (numeric, >0).
3.  **Backend Call**:
    -   `app.py` calls wrapper function `execute_buy(account, symbol, qty)`.
    -   Wrapper calls `get_share_price("AAPL")`.
    -   Wrapper calls `account.buy_stock("AAPL", 10, 150.0)`.
4.  **Backend Processing**:
    -   Validates balance >= 1500.0.
    -   Deducts cash, updates holdings.
    -   Records transaction.
    -   Returns `Transaction` object.
5.  **Response Handling**:
    -   Wrapper catches exceptions (`InsufficientFundsError`) -> raises `gr.Error`.
    -   On success -> returns updated UI strings (Balance, Status) and `gr.Info`.
6.  **UI Update**:
    -   Balance display updates.
    -   Holdings table refreshes (via chained event or manual refresh).

### Error Handling Strategy

All backend methods raise specific exceptions. The frontend wrapper functions must use `try...except` blocks to catch these and convert them into Gradio user feedback.

```python
def on_deposit(account, amount):
    if account is None:
        raise gr.Error("Please create an account first.")
    try:
        account.deposit(amount)
        return f"Balance: ${account.cash:,.2f}", gr.Info("Deposit successful")
    except ValueError as e:
        raise gr.Error(str(e))
```

---

## 5. Implementation Examples

### Backend: `buy_stock`

```python
def buy_stock(self, symbol: str, quantity: int, current_price: float) -> Transaction:
    if quantity <= 0:
        raise ValueError("Quantity must be positive")
    
    total_cost = quantity * current_price
    if total_cost > self.cash:
        raise InsufficientFundsError(f"Required: ${total_cost:.2f}, Available: ${self.cash:.2f}")
        
    self.cash -= total_cost
    
    # Update holdings logic here...
    # ...
    
    tx = Transaction(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(),
        type=TransactionType.BUY,
        symbol=symbol,
        quantity=quantity,
        price=current_price,
        amount=total_cost,
        balance_after=self.cash
    )
    self.transactions.append(tx)
    return tx
```

### Frontend: Tab Visibility Toggle

```python
def create_account_handler(username, deposit):
    try:
        new_account = TradingAccount(username, deposit)
        # Return: Update State, Hide Creation, Show Dashboard, Update Balance Label
        return (
            new_account, 
            gr.Group(visible=False), 
            gr.Tabs(visible=True), 
            f"Balance: ${new_account.cash:,.2f}",
            gr.Info(f"Welcome {username}!")
        )
    except Exception as e:
        raise gr.Error(str(e))
```

---

## 6. Testing & QA Guidelines

### Backend Unit Tests (`tests/test_backend.py`)
-   **Account Creation**: Test valid/invalid inputs.
-   **Deposit/Withdraw**: Test boundaries (0, negative, >balance).
-   **Trading**: Test buy/sell logic, cost basis calculation, insufficient funds/shares.
-   **History**: Test filtering and sorting.

### Integration Tests
-   **Full Flow**: Create Account -> Deposit -> Buy -> Sell -> Withdraw.
-   **State Persistence**: Ensure account state remains consistent across multiple operations.

### Frontend/E2E Tests (Playwright)
-   Verify UI elements exist (IDs/Labels).
-   Test error message visibility (Red toasts).
-   Test success message visibility (Green toasts).
-   Verify table updates after trading.

---

## 7. Dependencies & Setup

### Requirements
```text
gradio>=4.0.0
pydantic>=2.0.0
pandas>=2.0.0  # For DataFrame handling
pytest>=7.0.0
```

### Setup
1.  Install dependencies: `pip install -r requirements.txt`
2.  Run app: `python src/crew_generated/engineering/app.py`

---

## 8. Definition of Done

-   [ ] `trading_backend.py` implemented with 100% type hints and docstrings.
-   [ ] `app.py` implemented with all tabs and components defined in User Stories.
-   [ ] All User Stories (US-001 to US-008) acceptance criteria met.
-   [ ] Unit tests passing for backend logic.
-   [ ] Manual or automated verification of UI flows.
-   [ ] Code formatted with `black` and `isort`.
