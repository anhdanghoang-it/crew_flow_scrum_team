"""Trading Engine for a Stock Simulation Platform.

This module provides the complete backend logic for a single-user trading
simulation application. It is designed to be completely decoupled from any
frontend framework, communicating through standardized service responses.

It manages an account's state, including cash balance, stock holdings, and
transaction history, and processes all financial operations like deposits,
withdrawals, and trades.

Classes:
    TradingError: Base exception for all trading engine errors.
    InsufficientFundsError: Raised for operations failing due to lack of cash.
    InsufficientHoldingsError: Raised for selling more shares than owned.
    InvalidSymbolError: Raised for an invalid or unfound stock symbol.
    InvalidAmountError: Raised for non-positive or invalid transaction amounts.
    TransactionType: Enum for the type of a transaction.
    Transaction: Pydantic model for a single financial transaction.
    PortfolioMetrics: Pydantic model for a snapshot of portfolio KPIs.
    ServiceResponse: Pydantic model for a standardized method response.
    TradingAccount: The core class managing all account state and logic.

Functions:
    get_share_price(symbol: str) -> Decimal: A mock function to retrieve a
                                             stock's current price.

Usage Example:
    # Instantiate the account
    account = TradingAccount()

    # Initialize with a starting balance
    init_response = account.initialize(100000.0)
    if not init_response.success:
        print(f"Error: {init_response.message}")
        exit()
    print(init_response.message)

    # Execute a trade
    buy_response = account.buy_shares("AAPL", 10)
    print(buy_response.message)

    # Check portfolio metrics
    metrics = account.get_portfolio_metrics()
    print(f"Cash Balance: ${metrics.cash_balance}")
    print(f"Total Portfolio Value: ${metrics.total_portfolio_value}")

    # View holdings
    holdings_df = account.get_holdings_df()
    print("\\nCurrent Holdings:")
    print(holdings_df)

    # View transaction history
    transactions_df = account.get_transactions_df()
    print("\\nTransaction History:")
    print(transactions_df)

Dependencies:
    - pydantic
    - pandas
"""

# Standard library imports
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Dict, List, Optional, Union

# Third-party imports
import pandas as pd
from pydantic import BaseModel, Field


# --- Custom Exception Classes ---

class TradingError(Exception):
    """Base exception for all trading engine errors."""
    pass


class InsufficientFundsError(TradingError):
    """Raised when an operation cannot be completed due to lack of cash."""
    pass


class InsufficientHoldingsError(TradingError):
    """Raised when trying to sell more shares than owned."""
    pass


class InvalidSymbolError(TradingError):
    """Raised when a stock symbol is not found or invalid."""
    pass


class InvalidAmountError(TradingError):
    """Raised for non-positive or otherwise invalid transaction amounts."""
    pass


# --- Data Models (Pydantic) ---

class TransactionType(str, Enum):
    """Enumeration for the types of transactions."""
    INITIALIZE = "INITIALIZE"
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    BUY = "BUY"
    SELL = "SELL"


class Transaction(BaseModel):
    """Represents a single financial transaction in the account history."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    type: TransactionType
    symbol: Optional[str] = None
    quantity: Optional[int] = None
    price_per_share: Optional[Decimal] = None
    total_value: Decimal


class PortfolioMetrics(BaseModel):
    """A snapshot of key performance indicators for the portfolio."""
    cash_balance: Decimal
    total_holdings_value: Decimal
    total_portfolio_value: Decimal
    profit_loss: Decimal


class ServiceResponse(BaseModel):
    """A standardized response object for all service layer methods."""
    success: bool
    message: str
    data: Optional[Union[PortfolioMetrics, Transaction]] = None


# --- Market Data Provider ---

_mock_prices: Dict[str, Decimal] = {
    "AAPL": Decimal("150.00"),
    "TSLA": Decimal("200.00"),
    "GOOGL": Decimal("130.00"),
}


def get_share_price(symbol: str) -> Decimal:
    """Retrieves the current price for a given stock symbol.

    Args:
        symbol: The stock ticker symbol (e.g., 'AAPL').

    Raises:
        InvalidSymbolError: If the symbol is not found in the mock data.

    Returns:
        The price of the share as a Decimal object.
    """
    price = _mock_prices.get(symbol.upper())
    if price is None:
        raise InvalidSymbolError(
            f"Trade failed. Stock symbol '{symbol}' not found."
        )
    return price


# --- Primary Class Definition ---

class TradingAccount:
    """
    Manages the state and operations of a trading simulation account.

    This class encapsulates all business logic related to account management,
    including cash transactions, trades, and portfolio calculations. It is
    designed to be stateful but interacts with the outside world via
    standardized ServiceResponse objects, making it suitable for integration
    with various frontends.
    """

    def __init__(self) -> None:
        """Initializes an empty and uninitialized trading account."""
        self.cash_balance: Decimal = Decimal("0.0")
        self.holdings: Dict[str, int] = {}
        self.transactions: List[Transaction] = []
        self.total_deposits: Decimal = Decimal("0.0")
        self.total_withdrawals: Decimal = Decimal("0.0")
        self.initialized: bool = False

    def initialize(self, deposit_amount: float) -> ServiceResponse:
        """Initializes the account with a starting cash balance.

        This method can only be called once on a non-initialized account. It
        sets the initial cash balance, total deposits, and logs the first
        transaction.

        Args:
            deposit_amount: The initial amount of cash to deposit. Must be
                            a positive number.

        Returns:
            A ServiceResponse indicating success or failure. On success, the
            message confirms initialization. On failure, it provides a
            user-friendly error message.
        """
        if self.initialized:
            return ServiceResponse(
                success=False,
                message="Account already initialized."
            )
        if not isinstance(deposit_amount, (int, float)) or deposit_amount <= 0:
            return ServiceResponse(
                success=False,
                message="Initial deposit must be a positive number."
            )

        amount = Decimal(str(deposit_amount)).quantize(Decimal("0.01"))
        self.cash_balance = amount
        self.total_deposits = amount
        self.initialized = True

        tx = Transaction(type=TransactionType.INITIALIZE, total_value=amount)
        self.transactions.append(tx)

        return ServiceResponse(
            success=True,
            message=f"Account initialized with a balance of ${amount:,.2f}."
        )

    def deposit(self, amount: float) -> ServiceResponse:
        """Deposits additional cash into the account.

        Args:
            amount: The amount of cash to deposit. Must be a positive number.

        Returns:
            A ServiceResponse indicating success or failure with a
            corresponding user-friendly message.
        """
        try:
            if not isinstance(amount, (int, float)) or amount <= 0:
                raise InvalidAmountError("Amount must be a positive number.")

            dec_amount = Decimal(str(amount)).quantize(Decimal("0.01"))
            self.cash_balance += dec_amount
            self.total_deposits += dec_amount

            tx = Transaction(type=TransactionType.DEPOSIT, total_value=dec_amount)
            self.transactions.append(tx)

            return ServiceResponse(
                success=True,
                message=f"Successfully deposited ${dec_amount:,.2f}."
            )
        except InvalidAmountError as e:
            return ServiceResponse(success=False, message=str(e))

    def withdraw(self, amount: float) -> ServiceResponse:
        """Withdraws cash from the account, checking for sufficient funds.

        Args:
            amount: The amount to withdraw. Must be a positive number and not
                    exceed the current cash balance.

        Returns:
            A ServiceResponse indicating success or failure. On failure, the
            message specifies the reason (e.g., insufficient funds).
        """
        try:
            if not isinstance(amount, (int, float)) or amount <= 0:
                raise InvalidAmountError("Amount must be a positive number.")

            dec_amount = Decimal(str(amount)).quantize(Decimal("0.01"))
            if dec_amount > self.cash_balance:
                raise InsufficientFundsError(
                    "Withdrawal failed. Insufficient funds. "
                    f"Available: ${self.cash_balance:,.2f}."
                )

            self.cash_balance -= dec_amount
            self.total_withdrawals += dec_amount

            tx = Transaction(type=TransactionType.WITHDRAW, total_value=-dec_amount)
            self.transactions.append(tx)

            return ServiceResponse(
                success=True,
                message=f"Successfully withdrew ${dec_amount:,.2f}."
            )
        except (InvalidAmountError, InsufficientFundsError) as e:
            return ServiceResponse(success=False, message=str(e))

    def buy_shares(self, symbol: str, quantity: int) -> ServiceResponse:
        """Executes a buy order for a given stock.

        Validates that the quantity is a positive integer, the symbol is valid,
        and there are sufficient funds to cover the total cost. If all checks
        pass, it updates the cash balance and holdings, and logs the transaction.

        Args:
            symbol: The stock ticker symbol to buy.
            quantity: The number of shares to purchase.

        Returns:
            A ServiceResponse indicating success or failure. On failure, the
            message provides details about the error.
        """
        try:
            if not isinstance(quantity, int) or quantity <= 0:
                raise InvalidAmountError("Quantity must be a positive integer.")

            price_per_share = get_share_price(symbol)
            total_cost = (price_per_share * quantity).quantize(Decimal("0.01"))
            if total_cost > self.cash_balance:
                raise InsufficientFundsError(
                    f"Buy order failed. Insufficient funds. Required: "
                    f"${total_cost:,.2f}, Available: ${self.cash_balance:,.2f}."
                )

            # --- State Modification: Only after all validations pass ---
            self.cash_balance -= total_cost
            self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity

            tx = Transaction(
                type=TransactionType.BUY,
                symbol=symbol,
                quantity=quantity,
                price_per_share=price_per_share,
                total_value=-total_cost,
            )
            self.transactions.append(tx)

            return ServiceResponse(
                success=True,
                message=f"Successfully purchased {quantity} shares of {symbol} for ${total_cost:,.2f}."
            )
        except (InvalidSymbolError, InvalidAmountError, InsufficientFundsError) as e:
            return ServiceResponse(success=False, message=str(e))

    def sell_shares(self, symbol: str, quantity: int) -> ServiceResponse:
        """Executes a sell order for a given stock.

        Validates that the quantity is a positive integer, the symbol is valid,
        and the account holds enough shares to sell. If all checks pass, it
        updates the cash balance and holdings, and logs the transaction.

        Args:
            symbol: The stock ticker symbol to sell.
            quantity: The number of shares to sell.

        Returns:
            A ServiceResponse indicating success or failure with a relevant
            user-friendly message.
        """
        try:
            if not isinstance(quantity, int) or quantity <= 0:
                raise InvalidAmountError("Quantity must be a positive integer.")

            current_holding = self.holdings.get(symbol, 0)
            if quantity > current_holding:
                raise InsufficientHoldingsError(
                    f"Sell order failed. You cannot sell {quantity} shares "
                    f"of {symbol}. You only own {current_holding}."
                )

            price_per_share = get_share_price(symbol)
            total_proceeds = (price_per_share * quantity).quantize(Decimal("0.01"))

            # --- State Modification: Only after all validations pass ---
            self.cash_balance += total_proceeds
            self.holdings[symbol] -= quantity
            if self.holdings[symbol] == 0:
                del self.holdings[symbol]

            tx = Transaction(
                type=TransactionType.SELL,
                symbol=symbol,
                quantity=quantity,
                price_per_share=price_per_share,
                total_value=total_proceeds,
            )
            self.transactions.append(tx)

            return ServiceResponse(
                success=True,
                message=f"Successfully sold {quantity} shares of {symbol} for ${total_proceeds:,.2f}."
            )
        except (InvalidSymbolError, InvalidAmountError, InsufficientHoldingsError) as e:
            return ServiceResponse(success=False, message=str(e))

    def get_portfolio_metrics(self) -> PortfolioMetrics:
        """Calculates and returns key portfolio metrics.

        The metrics include cash balance, total value of all stock holdings,
        the combined portfolio value, and the overall profit or loss.

        Returns:
            A PortfolioMetrics Pydantic model containing the calculated values.
        """
        total_holdings_value = Decimal("0.0")
        for symbol, quantity in self.holdings.items():
            try:
                price = get_share_price(symbol)
                total_holdings_value += price * quantity
            except InvalidSymbolError:
                # In this simulation, we assume prices are always available
                # for stocks that are currently held.
                pass

        total_portfolio_value = self.cash_balance + total_holdings_value
        profit_loss = (
            total_portfolio_value - self.total_deposits + self.total_withdrawals
        )

        return PortfolioMetrics(
            cash_balance=self.cash_balance.quantize(Decimal("0.01")),
            total_holdings_value=total_holdings_value.quantize(Decimal("0.01")),
            total_portfolio_value=total_portfolio_value.quantize(Decimal("0.01")),
            profit_loss=profit_loss.quantize(Decimal("0.01")),
        )

    def get_holdings_df(self) -> pd.DataFrame:
        """Returns current holdings as a Pandas DataFrame for UI display.

        The DataFrame is structured with columns suitable for direct rendering
        in a Gradio table, including formatted monetary values.

        Returns:
            A pandas DataFrame with columns: "Symbol", "Quantity",
            "Current Price", and "Market Value". Returns an empty DataFrame
            with the same columns if there are no holdings.
        """
        data = []
        for symbol, quantity in sorted(self.holdings.items()):
            try:
                price = get_share_price(symbol)
                market_value = price * quantity
                data.append({
                    "Symbol": symbol,
                    "Quantity": quantity,
                    "Current Price": f"${price:,.2f}",
                    "Market Value": f"${market_value:,.2f}",
                })
            except InvalidSymbolError:
                # Should not happen for existing holdings
                continue

        columns = ["Symbol", "Quantity", "Current Price", "Market Value"]
        if not data:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame(data, columns=columns)

    def get_transactions_df(self) -> pd.DataFrame:
        """Returns transaction history as a Pandas DataFrame for UI display.

        Transactions are sorted in reverse chronological order and formatted
        for display, with N/A for fields not applicable to a given
        transaction type.

        Returns:
            A pandas DataFrame with columns: "Timestamp", "Type", "Symbol",
            "Quantity", "Price/Share", and "Total Value".
        """
        data = []
        for tx in reversed(self.transactions):
            data.append({
                "Timestamp": tx.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "Type": tx.type.value,
                "Symbol": tx.symbol or "N/A",
                "Quantity": tx.quantity or "N/A",
                "Price/Share": f"${tx.price_per_share:,.2f}" if tx.price_per_share else "N/A",
                "Total Value": f"{'+' if tx.total_value > 0 and tx.type != TransactionType.INITIALIZE else ''}${tx.total_value:,.2f}",
            })

        columns = [
            "Timestamp", "Type", "Symbol", "Quantity",
            "Price/Share", "Total Value"
        ]
        if not data:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame(data, columns=columns)