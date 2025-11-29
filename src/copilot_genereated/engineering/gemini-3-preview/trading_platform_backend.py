"""
Trading Platform Backend Module

This module implements the core business logic and data models for the Trading Platform.
It is designed to integrate seamlessly with a Gradio frontend.

Usage Example:
    service = TradingService()
    
    # Create Account
    response = service.create_account("TraderJoe")
    if response['success']:
        print(response['message'])
        
    # Deposit
    service.deposit("TraderJoe", 1000.0)
    
    # Buy Shares
    service.buy_shares("TraderJoe", "AAPL", 5)
    
    # Get Portfolio for Dashboard
    portfolio_response = service.get_portfolio("TraderJoe")
    if portfolio_response['success']:
        print(portfolio_response['data'])
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union
import uuid

from pydantic import BaseModel, Field

# --- Constants & Messages ---

MSG_ACCOUNT_CREATED = "Account '{username}' created successfully"
MSG_USERNAME_EMPTY = "Username cannot be empty"
MSG_USERNAME_EXISTS = "Username '{username}' already exists"
MSG_DEPOSIT_SUCCESS = "Deposited ${amount:.2f}"
MSG_WITHDRAW_SUCCESS = "Withdrawn ${amount:.2f}"
MSG_INSUFFICIENT_FUNDS = "Insufficient funds. Available: ${available:.2f}"
MSG_AMOUNT_POSITIVE = "Amount must be positive"
MSG_BUY_SUCCESS = "Bought {quantity} shares of {symbol} at ${price:.2f}"
MSG_INSUFFICIENT_FUNDS_COST = "Insufficient funds. Cost: ${cost:.2f}, Available: ${available:.2f}"
MSG_QUANTITY_POSITIVE = "Quantity must be positive"
MSG_SELL_SUCCESS = "Sold {quantity} shares of {symbol} at ${price:.2f}"
MSG_INSUFFICIENT_SHARES = "Insufficient shares. Owned: {owned}"
MSG_NOT_OWNED = "You do not own any shares of {symbol}"
MSG_USER_NOT_FOUND = "User '{username}' not found"
MSG_UNEXPECTED_ERROR = "Unexpected error. Please try again."

# --- Exceptions ---

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
    def __init__(self, message: str, available: float, cost: float = 0.0):
        super().__init__(message)
        self.available = available
        self.cost = cost

class InsufficientSharesError(TradingPlatformError):
    """Raised when selling more shares than owned."""
    def __init__(self, message: str, owned: int):
        super().__init__(message)
        self.owned = owned

class InvalidAmountError(TradingPlatformError):
    """Raised for non-positive amounts where positive is required."""
    pass

class ValidationError(TradingPlatformError):
    """Raised for general validation errors."""
    pass

# --- Data Models ---

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

    def to_display_dict(self) -> Dict[str, Any]:
        """Formats transaction for display in a DataFrame."""
        return {
            "Time": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "Type": self.type.value,
            "Symbol": self.symbol if self.symbol else "-",
            "Quantity": self.quantity if self.quantity else "-",
            "Price": f"${self.price:.2f}" if self.price else "-",
            "Amount": f"${self.amount:.2f}"
        }

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
    holdings: Dict[str, Holding] = Field(default_factory=dict)
    transactions: List[Transaction] = Field(default_factory=list)
    initial_deposit: float = 0.0

# --- Helper Functions ---

def get_share_price(symbol: str) -> float:
    """
    Returns the current price of a share.
    Mock implementation with fixed prices.
    """
    prices = {
        "AAPL": 150.00,
        "TSLA": 200.00,
        "GOOGL": 100.00
    }
    return prices.get(symbol.upper(), 0.0)

# --- Core Business Logic ---

class TradingEngine:
    """
    Encapsulates all business rules and state management.
    """
    def __init__(self):
        self._accounts: Dict[str, Account] = {}

    def create_account(self, username: str) -> Account:
        """Creates a new user account."""
        if not username or not username.strip():
            raise ValidationError(MSG_USERNAME_EMPTY)
        
        if username in self._accounts:
            raise UserAlreadyExistsError(MSG_USERNAME_EXISTS.format(username=username))
            
        account = Account(username=username)
        self._accounts[username] = account
        return account

    def get_account(self, username: str) -> Account:
        """Retrieves an account by username."""
        if username not in self._accounts:
            raise UserNotFoundError(MSG_USER_NOT_FOUND.format(username=username))
        return self._accounts[username]

    def deposit(self, username: str, amount: float) -> Account:
        """Deposits funds into a user's account."""
        if amount <= 0:
            raise InvalidAmountError(MSG_AMOUNT_POSITIVE)
            
        account = self.get_account(username)
        account.cash_balance += amount
        account.initial_deposit += amount # Track net deposits
        
        transaction = Transaction(
            id=str(uuid.uuid4()),
            type=TransactionType.DEPOSIT,
            amount=amount,
            balance_after=account.cash_balance
        )
        account.transactions.append(transaction)
        return account

    def withdraw(self, username: str, amount: float) -> Account:
        """Withdraws funds from a user's account."""
        if amount <= 0:
            raise InvalidAmountError(MSG_AMOUNT_POSITIVE)
            
        account = self.get_account(username)
        if account.cash_balance < amount:
            raise InsufficientFundsError(
                MSG_INSUFFICIENT_FUNDS.format(available=account.cash_balance),
                available=account.cash_balance
            )
            
        account.cash_balance -= amount
        account.initial_deposit -= amount # Track net deposits (withdrawals reduce basis)
        
        transaction = Transaction(
            id=str(uuid.uuid4()),
            type=TransactionType.WITHDRAWAL,
            amount=-amount,
            balance_after=account.cash_balance
        )
        account.transactions.append(transaction)
        return account

    def buy_shares(self, username: str, symbol: str, quantity: int) -> Transaction:
        """Executes a buy order."""
        if quantity <= 0:
            raise InvalidAmountError(MSG_QUANTITY_POSITIVE)
            
        price = get_share_price(symbol)
        if price == 0:
            raise ValidationError(f"Invalid symbol: {symbol}")
            
        cost = price * quantity
        account = self.get_account(username)
        
        if account.cash_balance < cost:
            raise InsufficientFundsError(
                MSG_INSUFFICIENT_FUNDS_COST.format(cost=cost, available=account.cash_balance),
                available=account.cash_balance,
                cost=cost
            )
            
        # Update Balance
        account.cash_balance -= cost
        
        # Update Holdings
        if symbol in account.holdings:
            holding = account.holdings[symbol]
            total_cost = (holding.quantity * holding.average_cost) + cost
            holding.quantity += quantity
            holding.average_cost = total_cost / holding.quantity
        else:
            account.holdings[symbol] = Holding(symbol=symbol, quantity=quantity, average_cost=price)
            
        # Record Transaction
        transaction = Transaction(
            id=str(uuid.uuid4()),
            type=TransactionType.BUY,
            symbol=symbol,
            quantity=quantity,
            price=price,
            amount=-cost,
            balance_after=account.cash_balance
        )
        account.transactions.append(transaction)
        return transaction

    def sell_shares(self, username: str, symbol: str, quantity: int) -> Transaction:
        """Executes a sell order."""
        if quantity <= 0:
            raise InvalidAmountError(MSG_QUANTITY_POSITIVE)
            
        account = self.get_account(username)
        
        if symbol not in account.holdings:
            raise InsufficientSharesError(MSG_NOT_OWNED.format(symbol=symbol), owned=0)
            
        holding = account.holdings[symbol]
        if holding.quantity < quantity:
            raise InsufficientSharesError(
                MSG_INSUFFICIENT_SHARES.format(owned=holding.quantity),
                owned=holding.quantity
            )
            
        price = get_share_price(symbol)
        proceeds = price * quantity
        
        # Update Balance
        account.cash_balance += proceeds
        
        # Update Holdings
        holding.quantity -= quantity
        if holding.quantity == 0:
            del account.holdings[symbol]
            
        # Record Transaction
        transaction = Transaction(
            id=str(uuid.uuid4()),
            type=TransactionType.SELL,
            symbol=symbol,
            quantity=quantity,
            price=price,
            amount=proceeds,
            balance_after=account.cash_balance
        )
        account.transactions.append(transaction)
        return transaction

    def get_portfolio(self, username: str) -> Portfolio:
        """Calculates current portfolio state."""
        account = self.get_account(username)
        
        holdings_list = []
        holdings_value = 0.0
        
        for symbol, holding in account.holdings.items():
            current_price = get_share_price(symbol)
            # Note: We return the holding with current market price for display purposes if needed,
            # but the Holding model stores average_cost. 
            # For the portfolio view, we usually want current value.
            # Let's keep the Holding model as is (average cost) and calculate value here.
            holdings_list.append(holding)
            holdings_value += holding.quantity * current_price
            
        total_value = account.cash_balance + holdings_value
        profit_loss = total_value - account.initial_deposit
        
        pl_percent = 0.0
        if account.initial_deposit > 0:
            pl_percent = (profit_loss / account.initial_deposit) * 100
            
        return Portfolio(
            holdings=holdings_list,
            total_value=total_value,
            cash_balance=account.cash_balance,
            initial_deposit=account.initial_deposit,
            profit_loss=profit_loss,
            profit_loss_percent=pl_percent
        )

    def get_transaction_history(self, username: str) -> List[Transaction]:
        """Retrieves all transactions for a user."""
        account = self.get_account(username)
        # Return reversed list (newest first)
        return list(reversed(account.transactions))

# --- Service Layer (Gradio Integration) ---

class TradingService:
    """
    Wrapper around TradingEngine to return structured dictionaries
    suitable for Gradio UI consumption.
    """
    def __init__(self):
        self.engine = TradingEngine()

    def _success(self, message: str, data: Any = None) -> Dict[str, Any]:
        return {'success': True, 'message': message, 'data': data, 'code': None}

    def _error(self, message: str, code: str = "ERROR") -> Dict[str, Any]:
        return {'success': False, 'message': message, 'data': None, 'code': code}

    def create_account(self, username: str) -> Dict[str, Any]:
        try:
            self.engine.create_account(username)
            return self._success(MSG_ACCOUNT_CREATED.format(username=username))
        except UserAlreadyExistsError as e:
            return self._error(str(e), "DUPLICATE_USER")
        except ValidationError as e:
            return self._error(str(e), "VALIDATION_ERROR")
        except Exception as e:
            return self._error(MSG_UNEXPECTED_ERROR, "UNEXPECTED_ERROR")

    def deposit(self, username: str, amount: float) -> Dict[str, Any]:
        try:
            account = self.engine.deposit(username, amount)
            return self._success(
                MSG_DEPOSIT_SUCCESS.format(amount=amount),
                {'cash_balance': account.cash_balance}
            )
        except (UserNotFoundError, InvalidAmountError) as e:
            return self._error(str(e), "VALIDATION_ERROR")
        except Exception:
            return self._error(MSG_UNEXPECTED_ERROR)

    def withdraw(self, username: str, amount: float) -> Dict[str, Any]:
        try:
            account = self.engine.withdraw(username, amount)
            return self._success(
                MSG_WITHDRAW_SUCCESS.format(amount=amount),
                {'cash_balance': account.cash_balance}
            )
        except InsufficientFundsError as e:
            return self._error(str(e), "INSUFFICIENT_FUNDS")
        except (UserNotFoundError, InvalidAmountError) as e:
            return self._error(str(e), "VALIDATION_ERROR")
        except Exception:
            return self._error(MSG_UNEXPECTED_ERROR)

    def buy_shares(self, username: str, symbol: str, quantity: int) -> Dict[str, Any]:
        try:
            txn = self.engine.buy_shares(username, symbol, quantity)
            return self._success(
                MSG_BUY_SUCCESS.format(quantity=quantity, symbol=symbol, price=txn.price),
                txn.model_dump()
            )
        except InsufficientFundsError as e:
            return self._error(str(e), "INSUFFICIENT_FUNDS")
        except (UserNotFoundError, InvalidAmountError, ValidationError) as e:
            return self._error(str(e), "VALIDATION_ERROR")
        except Exception:
            return self._error(MSG_UNEXPECTED_ERROR)

    def sell_shares(self, username: str, symbol: str, quantity: int) -> Dict[str, Any]:
        try:
            txn = self.engine.sell_shares(username, symbol, quantity)
            return self._success(
                MSG_SELL_SUCCESS.format(quantity=quantity, symbol=symbol, price=txn.price),
                txn.model_dump()
            )
        except InsufficientSharesError as e:
            return self._error(str(e), "INSUFFICIENT_SHARES")
        except (UserNotFoundError, InvalidAmountError) as e:
            return self._error(str(e), "VALIDATION_ERROR")
        except Exception:
            return self._error(MSG_UNEXPECTED_ERROR)

    def get_portfolio(self, username: str) -> Dict[str, Any]:
        try:
            portfolio = self.engine.get_portfolio(username)
            
            # Format holdings for DataFrame
            holdings_data = []
            for h in portfolio.holdings:
                current_price = get_share_price(h.symbol)
                holdings_data.append([
                    h.symbol,
                    h.quantity,
                    f"${current_price:.2f}",
                    f"${(h.quantity * current_price):.2f}"
                ])
            
            data = {
                'total_value': portfolio.total_value,
                'cash_balance': portfolio.cash_balance,
                'profit_loss': portfolio.profit_loss,
                'profit_loss_str': f"${portfolio.profit_loss:+.2f} ({portfolio.profit_loss_percent:+.2f}%)",
                'holdings_table': holdings_data
            }
            return self._success("Portfolio retrieved", data)
        except UserNotFoundError as e:
            return self._error(str(e), "USER_NOT_FOUND")
        except Exception:
            return self._error(MSG_UNEXPECTED_ERROR)

    def get_transaction_history(self, username: str) -> Dict[str, Any]:
        try:
            txns = self.engine.get_transaction_history(username)
            # Format for DataFrame
            history_data = [t.to_display_dict() for t in txns]
            # Convert list of dicts to list of lists if needed, or keep as is for Gradio DataFrame
            # Gradio DataFrame accepts list of lists or pandas dataframe. 
            # Let's return list of lists to be safe and consistent with holdings.
            # Headers: ["Time", "Type", "Symbol", "Quantity", "Price", "Amount"]
            
            table_data = []
            for t in history_data:
                table_data.append([
                    t["Time"],
                    t["Type"],
                    t["Symbol"],
                    t["Quantity"],
                    t["Price"],
                    t["Amount"]
                ])
                
            return self._success("History retrieved", table_data)
        except UserNotFoundError as e:
            return self._error(str(e), "USER_NOT_FOUND")
        except Exception:
            return self._error(MSG_UNEXPECTED_ERROR)
