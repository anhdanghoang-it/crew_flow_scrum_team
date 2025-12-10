"""
Trading Simulation Backend Module.

This module implements the core business logic for the Trading Simulation Platform.
It manages user accounts, portfolios, and trade execution using in-memory storage.

Usage:
    engine = TradingEngine()
    engine.create_account("alice")
    engine.deposit("alice", 1000.0)
    engine.buy_shares("alice", "AAPL", 2)
    summary = engine.get_portfolio_summary("alice")
"""

from enum import Enum
from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

# --- Custom Exceptions ---

class BackendError(Exception):
    """Base exception for backend errors."""
    pass

class InsufficientFundsError(BackendError):
    """Raised when an account has insufficient funds for an operation."""
    pass

class InsufficientHoldingsError(BackendError):
    """Raised when an account has insufficient shares for a sale."""
    pass

class AccountNotFoundError(BackendError):
    """Raised when a requested account does not exist."""
    pass

class ValidationError(BackendError):
    """Raised when input validation fails."""
    pass

# --- Data Models ---

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

# --- Core Engine ---

class TradingEngine:
    """
    Manages trading accounts and executes operations.
    Currently uses in-memory storage.
    """

    def __init__(self):
        self._accounts: Dict[str, AccountData] = {}

    def _get_account(self, username: str) -> AccountData:
        """Helper to retrieve account or raise error."""
        if username not in self._accounts:
            raise AccountNotFoundError(f"Account '{username}' not found.")
        return self._accounts[username]

    def create_account(self, username: str) -> str:
        """
        Creates a new account.

        Args:
            username: Unique identifier for the user.

        Returns:
            Success message.

        Raises:
            ValidationError: If username is empty or already exists.
        """
        if not username or not username.strip():
            raise ValidationError("Username cannot be empty")
        
        username = username.strip()
        if username in self._accounts:
            raise ValidationError(f"Account for '{username}' already exists.")

        self._accounts[username] = AccountData(username=username)
        return f"Account created successfully for {username}"

    def get_balance(self, username: str) -> float:
        """Returns current cash balance."""
        account = self._get_account(username)
        return account.cash_balance

    def deposit(self, username: str, amount: float) -> str:
        """
        Deposits funds into account.

        Args:
            username: User identifier.
            amount: Positive amount to deposit.

        Returns:
            Success message.

        Raises:
            ValidationError: If amount is <= 0.
            AccountNotFoundError: If user does not exist.
        """
        if amount <= 0:
            raise ValidationError("Deposit amount must be positive")

        account = self._get_account(username)
        account.cash_balance += amount

        # Record transaction
        tx = Transaction(
            type=TransactionType.DEPOSIT,
            total_amount=amount,
            description=f"Deposit of ${amount:.2f}"
        )
        account.transactions.append(tx)

        return f"Deposited ${amount:.2f}"

    def withdraw(self, username: str, amount: float) -> str:
        """
        Withdraws funds from account.

        Args:
            username: User identifier.
            amount: Positive amount to withdraw.

        Returns:
            Success message.

        Raises:
            ValidationError: If amount <= 0.
            InsufficientFundsError: If insufficient funds.
            AccountNotFoundError: If user does not exist.
        """
        if amount <= 0:
            raise ValidationError("Withdrawal amount must be positive")

        account = self._get_account(username)
        
        if account.cash_balance < amount:
            raise InsufficientFundsError(f"Insufficient funds. Available: ${account.cash_balance:.2f}")

        account.cash_balance -= amount

        # Record transaction
        tx = Transaction(
            type=TransactionType.WITHDRAWAL,
            total_amount=-amount,
            description=f"Withdrawal of ${amount:.2f}"
        )
        account.transactions.append(tx)

        return f"Withdrew ${amount:.2f}"

    def get_share_price(self, symbol: str) -> float:
        """
        Mock function to get current share price.
        Supported: AAPL (150.0), TSLA (200.0), GOOGL (2800.0).
        Others return 100.0.
        """
        symbol = symbol.upper()
        prices = {
            "AAPL": 150.0,
            "TSLA": 200.0,
            "GOOGL": 2800.0
        }
        return prices.get(symbol, 100.0)

    def buy_shares(self, username: str, symbol: str, quantity: int) -> str:
        """
        Executes a buy order.

        Args:
            username: User identifier.
            symbol: Stock ticker.
            quantity: Number of shares (must be > 0).

        Returns:
            Success message.

        Raises:
            ValidationError: If quantity <= 0.
            InsufficientFundsError: If insufficient funds.
            AccountNotFoundError: If user does not exist.
        """
        if quantity <= 0:
            raise ValidationError("Quantity must be positive")

        account = self._get_account(username)
        symbol = symbol.upper()
        price = self.get_share_price(symbol)
        total_cost = price * quantity

        if account.cash_balance < total_cost:
            raise InsufficientFundsError("Insufficient funds for purchase")

        # Update cash
        account.cash_balance -= total_cost

        # Update holdings
        if symbol not in account.holdings:
            account.holdings[symbol] = Holding(symbol=symbol)
        
        holding = account.holdings[symbol]
        # Calculate new average cost
        total_value_before = holding.quantity * holding.average_cost
        holding.quantity += quantity
        holding.average_cost = (total_value_before + total_cost) / holding.quantity

        # Record transaction
        tx = Transaction(
            type=TransactionType.BUY,
            symbol=symbol,
            quantity=quantity,
            price=price,
            total_amount=-total_cost,
            description=f"Bought {quantity} {symbol} @ ${price:.2f}"
        )
        account.transactions.append(tx)

        return f"Bought {quantity} {symbol} @ ${price:.2f}"

    def sell_shares(self, username: str, symbol: str, quantity: int) -> str:
        """
        Executes a sell order.

        Args:
            username: User identifier.
            symbol: Stock ticker.
            quantity: Number of shares (must be > 0).

        Returns:
            Success message.

        Raises:
            ValidationError: If quantity <= 0.
            InsufficientHoldingsError: If insufficient shares owned.
            AccountNotFoundError: If user does not exist.
        """
        if quantity <= 0:
            raise ValidationError("Quantity must be positive")

        account = self._get_account(username)
        symbol = symbol.upper()
        
        if symbol not in account.holdings or account.holdings[symbol].quantity < quantity:
            raise InsufficientHoldingsError("Insufficient shares to sell")

        price = self.get_share_price(symbol)
        total_proceeds = price * quantity

        # Update cash
        account.cash_balance += total_proceeds

        # Update holdings
        holding = account.holdings[symbol]
        holding.quantity -= quantity
        
        # If quantity becomes 0, we can either keep the record or remove it.
        # Keeping it with 0 quantity is often safer for history, but let's leave it.
        # If we wanted to remove: if holding.quantity == 0: del account.holdings[symbol]

        # Record transaction
        tx = Transaction(
            type=TransactionType.SELL,
            symbol=symbol,
            quantity=quantity,
            price=price,
            total_amount=total_proceeds,
            description=f"Sold {quantity} {symbol} @ ${price:.2f}"
        )
        account.transactions.append(tx)

        return f"Sold {quantity} {symbol} @ ${price:.2f}"

    def get_portfolio_summary(self, username: str) -> List[List[Any]]:
        """
        Returns data for the holdings table.
        Format: [[Symbol, Quantity, Current Price, Total Value], ...]
        """
        account = self._get_account(username)
        summary = []
        
        for symbol, holding in account.holdings.items():
            if holding.quantity > 0:
                current_price = self.get_share_price(symbol)
                total_value = holding.quantity * current_price
                summary.append([
                    symbol,
                    holding.quantity,
                    current_price,
                    total_value
                ])
        
        return summary

    def get_transaction_history(self, username: str) -> List[List[Any]]:
        """
        Returns data for the transaction history table.
        Format: [[Time, Type, Symbol, Quantity, Price, Total Amount], ...]
        """
        account = self._get_account(username)
        history = []
        
        for tx in account.transactions:
            history.append([
                tx.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                tx.type.value,
                tx.symbol if tx.symbol else "-",
                tx.quantity if tx.quantity else "-",
                f"${tx.price:.2f}" if tx.price else "-",
                f"${tx.total_amount:.2f}"
            ])
            
        return history

    def get_performance_metrics(self, username: str) -> Dict[str, float]:
        """
        Returns {'total_value': float, 'profit_loss': float}
        """
        account = self._get_account(username)
        
        # Calculate total portfolio value (Cash + Shares)
        share_value = 0.0
        for symbol, holding in account.holdings.items():
            if holding.quantity > 0:
                share_value += holding.quantity * self.get_share_price(symbol)
        
        total_value = account.cash_balance + share_value
        
        # Calculate total deposits (to determine P/L)
        total_deposits = sum(
            tx.total_amount for tx in account.transactions 
            if tx.type == TransactionType.DEPOSIT
        )
        
        # Profit/Loss = Total Value - Total Deposits
        # Note: This is a simplified P/L. 
        # Real P/L might also consider withdrawals, but "Total Value - Total Deposits" 
        # is a common simple metric if we assume withdrawals reduce the basis or we just track net flow.
        # Let's adjust: Net Invested = Deposits - Withdrawals
        net_invested = sum(
            tx.total_amount for tx in account.transactions 
            if tx.type in (TransactionType.DEPOSIT, TransactionType.WITHDRAWAL)
        )
        
        # If we use Net Invested, then P/L = Total Value - Net Invested
        profit_loss = total_value - net_invested

        return {
            "total_value": total_value,
            "profit_loss": profit_loss
        }
