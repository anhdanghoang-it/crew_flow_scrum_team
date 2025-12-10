"""
Trading Simulation Backend Module

This module implements the core domain logic for the Trading Simulation Platform.
It includes data models, custom exceptions, and the main TradingAccount class
that manages user state, transactions, and portfolio calculations.

It is designed to integrate seamlessly with a Gradio frontend by providing
structured responses and robust error handling.

Usage Example:
    >>> account = TradingAccount("demo_user", 10000.0)
    >>> tx = account.buy_stock("AAPL", 10, 150.0)
    >>> print(account.cash)
    8500.0
    >>> summary = account.get_portfolio_summary({"AAPL": 160.0})
    >>> print(summary.total_profit_loss)
    100.0
"""

import re
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator

# --- Constants ---

SUPPORTED_SYMBOLS = ["AAPL", "TSLA", "GOOGL"]
USERNAME_REGEX = r"^[a-zA-Z0-9_]{3,50}$"

# --- Exceptions ---

class TradingError(Exception):
    """Base exception for trading errors."""
    def __init__(self, message: str, code: str = "TRADING_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)

class InsufficientFundsError(TradingError):
    """Raised when attempting to withdraw or buy more than available."""
    def __init__(self, message: str):
        super().__init__(message, code="INSUFFICIENT_FUNDS")

class InsufficientSharesError(TradingError):
    """Raised when attempting to sell more shares than owned."""
    def __init__(self, message: str):
        super().__init__(message, code="INSUFFICIENT_SHARES")

class InvalidSymbolError(TradingError):
    """Raised when an unsupported symbol is used."""
    def __init__(self, message: str):
        super().__init__(message, code="INVALID_SYMBOL")

class AccountError(TradingError):
    """Raised for account-related issues (e.g., duplicate username)."""
    def __init__(self, message: str):
        super().__init__(message, code="ACCOUNT_ERROR")

class ValidationError(TradingError):
    """Raised for input validation failures."""
    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR")

# --- Data Models ---

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
    total_invested: float  # Net capital invested (Deposits - Withdrawals)
    total_portfolio_value: float
    total_profit_loss: float
    total_profit_loss_percentage: float
    initial_deposit: float

class ServiceResponse(BaseModel):
    """Standardized response format for UI integration."""
    success: bool
    message: str
    data: Optional[Any] = None
    code: Optional[str] = None

# --- Helper Functions ---

def get_share_price(symbol: str) -> float:
    """
    Mock price service.
    Returns fixed prices: AAPL: 150.0, TSLA: 800.0, GOOGL: 2800.0.
    Raises InvalidSymbolError for others.
    """
    prices = {
        "AAPL": 150.0,
        "TSLA": 800.0,
        "GOOGL": 2800.0
    }
    if symbol not in prices:
        raise InvalidSymbolError(f"Invalid or unsupported stock symbol: {symbol}. Supported symbols: {', '.join(prices.keys())}")
    return prices[symbol]

# --- Core Domain Class ---

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
            ValidationError: If initial_deposit <= 0 or username is invalid.
        """
        self._validate_username(username)
        self._validate_positive_amount(initial_deposit, "Initial deposit")
        
        self.username = username
        self.initial_deposit = initial_deposit
        self.cash = initial_deposit
        self.holdings: Dict[str, Holding] = {}
        self.transactions: List[Transaction] = []
        
        # Record initial deposit transaction (optional but good for history)
        # Note: US-001 says "Initialize account with empty holdings list and transaction history"
        # but usually initial deposit is the first transaction. 
        # However, to strictly follow "empty... transaction history", we might skip it, 
        # but AC1 says "Account... created... with initial balance".
        # Let's not add a transaction record for initialization to keep history clean as per implied requirement,
        # or add it if needed. US-001 doesn't explicitly ask for a transaction record for the init deposit,
        # unlike US-002 which does.
        
        # Tracking net capital invested (Initial + Deposits - Withdrawals)
        self.net_capital_invested = initial_deposit

    def _validate_username(self, username: str):
        if not username or not username.strip():
            raise ValidationError("Username is required and cannot be empty")
        if not re.match(USERNAME_REGEX, username):
            raise ValidationError("Username must contain only letters, numbers, and underscores (3-50 characters)")

    def _validate_positive_amount(self, amount: float, field_name: str):
        if not isinstance(amount, (int, float)):
             raise ValidationError("Please enter a valid numeric amount")
        if amount <= 0:
            raise ValidationError(f"{field_name} must be greater than $0.00")

    def deposit(self, amount: float) -> Transaction:
        """
        Add funds to the account.
        
        Args:
            amount: Amount to deposit (must be > 0).
            
        Returns:
            Transaction object recording the deposit.
            
        Raises:
            ValidationError: If amount <= 0.
        """
        self._validate_positive_amount(amount, "Deposit amount")
        
        self.cash += amount
        self.net_capital_invested += amount
        
        tx = Transaction(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            type=TransactionType.DEPOSIT,
            amount=amount,
            balance_after=self.cash
        )
        self.transactions.append(tx)
        return tx

    def withdraw(self, amount: float) -> Transaction:
        """
        Withdraw funds from the account.
        
        Args:
            amount: Amount to withdraw (must be > 0).
            
        Returns:
            Transaction object recording the withdrawal.
            
        Raises:
            ValidationError: If amount <= 0.
            InsufficientFundsError: If amount > available cash.
        """
        self._validate_positive_amount(amount, "Withdrawal amount")
        
        # Check available cash (US-003 AC6: Withdrawal with Locked Funds)
        # Available cash is simply self.cash. 
        # The requirement says "Insufficient available cash. Available: X (Total: Y, Invested: Z)"
        # Total balance usually means Cash + Invested. 
        # Here self.cash IS the available cash.
        
        if amount > self.cash:
            # Calculate invested for the error message
            invested = sum(h.quantity * get_share_price(h.symbol) for h in self.holdings.values()) # Using current price for value
            # Or using cost basis? Usually market value.
            # Let's stick to simple available cash check first.
            raise InsufficientFundsError(f"Insufficient funds. Available balance: ${self.cash:,.2f}")

        self.cash -= amount
        self.net_capital_invested -= amount
        
        tx = Transaction(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            type=TransactionType.WITHDRAWAL,
            amount=amount,
            balance_after=self.cash
        )
        self.transactions.append(tx)
        return tx

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
            ValidationError: If quantity <= 0 or not integer.
            InsufficientFundsError: If cost > available cash.
            InvalidSymbolError: If symbol is not supported.
        """
        if not symbol:
            raise ValidationError("Stock symbol is required")
        if symbol not in SUPPORTED_SYMBOLS:
             raise InvalidSymbolError(f"Invalid or unsupported stock symbol: {symbol}. Supported symbols: {', '.join(SUPPORTED_SYMBOLS)}")
        
        if not isinstance(quantity, int) or quantity != float(quantity):
             # Check if it's a float like 1.0 which is valid as int, but 1.5 is not
             if isinstance(quantity, float) and not quantity.is_integer():
                 raise ValidationError("Quantity must be a whole number (no fractional shares)")
             if not isinstance(quantity, (int, float)): # Catch non-numbers
                 raise ValidationError("Quantity must be a positive whole number")
        
        quantity = int(quantity)
        if quantity <= 0:
            raise ValidationError("Quantity must be a positive whole number")

        total_cost = quantity * current_price
        
        if total_cost > self.cash:
            raise InsufficientFundsError(f"Insufficient funds. Required: ${total_cost:,.2f}, Available: ${self.cash:,.2f}")
        
        self.cash -= total_cost
        
        # Update Holdings
        if symbol in self.holdings:
            holding = self.holdings[symbol]
            # Calculate new average cost
            total_shares = holding.quantity + quantity
            new_total_cost = (holding.quantity * holding.average_cost) + total_cost
            holding.average_cost = new_total_cost / total_shares
            holding.quantity = total_shares
        else:
            self.holdings[symbol] = Holding(
                symbol=symbol,
                quantity=quantity,
                average_cost=current_price
            )
            
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
            ValidationError: If quantity <= 0.
            InsufficientSharesError: If quantity > owned shares.
            InvalidSymbolError: If symbol is not in holdings.
        """
        if not symbol:
             raise ValidationError("Stock symbol is required")
             
        if not isinstance(quantity, int) and (isinstance(quantity, float) and not quantity.is_integer()):
             raise ValidationError("Quantity must be a whole number (no fractional shares)")
        
        quantity = int(quantity)
        if quantity <= 0:
            raise ValidationError("Quantity must be a positive whole number")

        if symbol not in self.holdings:
            raise InsufficientSharesError(f"You do not own any shares of {symbol}")
            
        holding = self.holdings[symbol]
        
        if quantity > holding.quantity:
            raise InsufficientSharesError(f"Insufficient shares. You own {holding.quantity} shares of {symbol}")
            
        total_proceeds = quantity * current_price
        self.cash += total_proceeds
        
        # Update Holdings
        holding.quantity -= quantity
        if holding.quantity == 0:
            del self.holdings[symbol]
            
        tx = Transaction(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            type=TransactionType.SELL,
            symbol=symbol,
            quantity=quantity,
            price=current_price,
            amount=total_proceeds,
            balance_after=self.cash
        )
        self.transactions.append(tx)
        return tx

    def get_holdings(self) -> List[Holding]:
        """Return list of current holdings."""
        return list(self.holdings.values())

    def get_transaction_history(self, 
                              type_filter: Optional[str] = None,
                              symbol_filter: Optional[str] = None,
                              date_range: Optional[str] = None) -> List[Transaction]:
        """
        Retrieve transaction history with optional filtering.
        """
        filtered = self.transactions.copy()
        
        # Reverse chronological order
        filtered.sort(key=lambda x: x.timestamp, reverse=True)
        
        if type_filter and type_filter != "All":
            # Map UI string to Enum if needed, or assume exact match
            # The UI sends "Deposits", "Withdrawals" etc.
            # Let's map basic ones
            type_map = {
                "Deposits": TransactionType.DEPOSIT,
                "Withdrawals": TransactionType.WITHDRAWAL,
                "Buys": TransactionType.BUY,
                "Sells": TransactionType.SELL
            }
            enum_type = type_map.get(type_filter)
            if enum_type:
                filtered = [t for t in filtered if t.type == enum_type]
                
        if symbol_filter and symbol_filter != "All":
            filtered = [t for t in filtered if t.symbol == symbol_filter]
            
        # Date range logic could be added here (Last 7 days, etc)
        # For now, returning all if not implemented
        
        return filtered

    def get_portfolio_summary(self, current_prices: Dict[str, float]) -> PortfolioSummary:
        """
        Calculate current portfolio metrics.
        
        Args:
            current_prices: Dictionary mapping symbols to current prices.
        """
        holdings_value = 0.0
        for holding in self.holdings.values():
            price = current_prices.get(holding.symbol, holding.average_cost) # Fallback to cost if no price
            holdings_value += holding.quantity * price
            
        total_portfolio_value = self.cash + holdings_value
        total_profit_loss = total_portfolio_value - self.net_capital_invested
        
        if self.net_capital_invested > 0:
            total_profit_loss_percentage = (total_profit_loss / self.net_capital_invested) * 100
        else:
            total_profit_loss_percentage = 0.0
            
        return PortfolioSummary(
            total_cash=self.cash,
            total_invested=self.net_capital_invested,
            total_portfolio_value=total_portfolio_value,
            total_profit_loss=total_profit_loss,
            total_profit_loss_percentage=total_profit_loss_percentage,
            initial_deposit=self.initial_deposit
        )

# --- Service Wrappers for Gradio ---

def create_account_service(username: str, initial_deposit: float) -> Dict[str, Any]:
    try:
        account = TradingAccount(username, initial_deposit)
        return {
            "success": True,
            "message": f"Account '{username}' created successfully with initial balance of ${initial_deposit:,.2f}",
            "data": account,
            "code": None
        }
    except TradingError as e:
        return {
            "success": False,
            "message": e.message,
            "data": None,
            "code": e.code
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "data": None,
            "code": "UNEXPECTED_ERROR"
        }

def deposit_service(account: TradingAccount, amount: float) -> Dict[str, Any]:
    if not account:
        return {"success": False, "message": "No active account", "code": "NO_ACCOUNT"}
    try:
        tx = account.deposit(amount)
        return {
            "success": True,
            "message": f"Successfully deposited ${amount:,.2f}. New balance: ${tx.balance_after:,.2f}",
            "data": tx,
            "code": None
        }
    except TradingError as e:
        return {"success": False, "message": e.message, "code": e.code}

def withdraw_service(account: TradingAccount, amount: float) -> Dict[str, Any]:
    if not account:
        return {"success": False, "message": "No active account", "code": "NO_ACCOUNT"}
    try:
        tx = account.withdraw(amount)
        return {
            "success": True,
            "message": f"Successfully withdrew ${amount:,.2f}. New balance: ${tx.balance_after:,.2f}",
            "data": tx,
            "code": None
        }
    except TradingError as e:
        return {"success": False, "message": e.message, "code": e.code}

def buy_stock_service(account: TradingAccount, symbol: str, quantity: float) -> Dict[str, Any]:
    if not account:
        return {"success": False, "message": "No active account", "code": "NO_ACCOUNT"}
    try:
        # Get price first
        price = get_share_price(symbol)
        # Convert float qty from UI to int
        qty_int = int(quantity) if quantity == int(quantity) else quantity
        
        tx = account.buy_stock(symbol, qty_int, price)
        return {
            "success": True,
            "message": f"Successfully purchased {tx.quantity} shares of {symbol} at ${price:,.2f}/share. Total: ${tx.amount:,.2f}",
            "data": tx,
            "code": None
        }
    except TradingError as e:
        return {"success": False, "message": e.message, "code": e.code}

def sell_stock_service(account: TradingAccount, symbol: str, quantity: float) -> Dict[str, Any]:
    if not account:
        return {"success": False, "message": "No active account", "code": "NO_ACCOUNT"}
    try:
        # Get price first
        price = get_share_price(symbol)
        # Convert float qty from UI to int
        qty_int = int(quantity) if quantity == int(quantity) else quantity
        
        tx = account.sell_stock(symbol, qty_int, price)
        
        # Check if position closed for message
        remaining = 0
        if symbol in account.holdings:
            remaining = account.holdings[symbol].quantity
            
        msg = f"Successfully sold {tx.quantity} shares of {symbol} at ${price:,.2f}/share. Total: ${tx.amount:,.2f}"
        if remaining == 0:
            msg += ". Position closed."
            
        return {
            "success": True,
            "message": msg,
            "data": tx,
            "code": None
        }
    except TradingError as e:
        return {"success": False, "message": e.message, "code": e.code}
