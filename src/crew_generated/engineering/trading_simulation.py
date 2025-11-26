"""
trading_simulation - A backend module for a stock trading simulation.

This module provides the core business logic for a trading simulation platform.
It is designed to be a self-contained, stateful engine that can be integrated
into any user interface, such as a Gradio web application.

The primary entry point is the `TradingSimulation` class, which manages all
aspects of a user's account, including cash balance, stock holdings, and
transaction history. All financial calculations are performed using Python's
`decimal` module to ensure high precision and avoid floating-point errors.

The module is structured into several logical components, all contained within
this single file for ease of distribution and use:
- **Exceptions**: Custom exceptions for specific business rule violations.
- **Models**: Pydantic models for data validation and clear API contracts.
- **Market Data**: A mock function to simulate fetching stock prices.
- **Simulation Class**: The main `TradingSimulation` class containing all state
  and business logic.

Usage Example:
    # Instantiate the simulation
    sim = TradingSimulation()

    # Initialize the account
    init_response = sim.initialize(100000.0)
    print(init_response.message)

    # Execute a trade
    buy_response = sim.buy_shares("AAPL", 10)
    print(buy_response.message)

    # Check portfolio metrics
    metrics = sim.get_portfolio_metrics()
    print(f"Portfolio Value: ${metrics.total_portfolio_value:,.2f}")

    # Get data for UI display
    holdings_df = sim.get_holdings_df()
    print("\nCurrent Holdings:")
    print(holdings_df)

    transactions_df = sim.get_transactions_df()
    print("\nTransaction History:")
    print(transactions_df)
"""

import pandas as pd
from datetime import datetime
from decimal import Decimal, getcontext
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

# Set precision for Decimal calculations to handle financial data accurately.
getcontext().prec = 28


# --- Custom Exceptions ---

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


# --- Pydantic Data Models ---

class TransactionType(str, Enum):
    """Enumeration for the types of transactions possible."""
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


# --- Market Data Provider (Mock) ---

_mock_prices = {
    "AAPL": Decimal("150.00"),
    "TSLA": Decimal("200.00"),
    "GOOGL": Decimal("130.00"),
}


def get_share_price(symbol: str) -> Decimal:
    """
    Retrieves the current price for a given stock symbol from a mock source.

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
            f"Could not fetch price for {symbol}. Please try again later."
        )
    return price


# --- Primary Simulation Class ---

class TradingSimulation:
    """
    Manages the state and operations of a trading simulation account.

    This class is the core of the backend business logic, responsible for
    all calculations and state modifications. It is designed to be completely
    independent of any user interface, consuming raw Python types and
    returning structured `ServiceResponse` objects.
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
        """
        Initializes the account with a starting cash balance.

        This method can only be called once. It sets the initial cash,
        logs the first transaction, and marks the account as initialized.

        Args:
            deposit_amount: The initial amount of cash to deposit.

        Returns:
            A ServiceResponse indicating success or failure and a
            user-friendly message.
        """
        if self.initialized:
            return ServiceResponse(
                success=False, message="Account already initialized."
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
        """
        Deposits additional cash into the account.

        Args:
            amount: The positive amount of cash to deposit.

        Returns:
            A ServiceResponse indicating success or failure.
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
        """
        Withdraws cash from the account, checking for sufficient funds.

        Args:
            amount: The positive amount of cash to withdraw.

        Returns:
            A ServiceResponse indicating success or failure.
        """
        try:
            if not isinstance(amount, (int, float)) or amount <= 0:
                raise InvalidAmountError("Amount must be a positive number.")

            dec_amount = Decimal(str(amount)).quantize(Decimal("0.01"))
            if dec_amount > self.cash_balance:
                raise InsufficientFundsError(
                    f"Withdrawal failed. Insufficient funds. "
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
        """
        Executes a buy order for a given stock.

        Validates inputs, checks for sufficient funds, and updates account
        state only if all checks pass.

        Args:
            symbol: The stock ticker symbol (e.g., 'AAPL').
            quantity: The number of shares to purchase.

        Returns:
            A ServiceResponse indicating success or failure.
        """
        try:
            if not isinstance(quantity, int) or quantity <= 0:
                raise InvalidAmountError("Quantity must be a positive integer.")

            upper_symbol = symbol.upper()
            price_per_share = get_share_price(upper_symbol)
            total_cost = (price_per_share * quantity).quantize(Decimal("0.01"))

            if total_cost > self.cash_balance:
                raise InsufficientFundsError(
                    f"Buy order failed. Insufficient funds. Required: "
                    f"${total_cost:,.2f}, Available: ${self.cash_balance:,.2f}."
                )

            # --- Atomic State Modification ---
            self.cash_balance -= total_cost
            self.holdings[upper_symbol] = self.holdings.get(upper_symbol, 0) + quantity

            tx = Transaction(
                type=TransactionType.BUY,
                symbol=upper_symbol,
                quantity=quantity,
                price_per_share=price_per_share,
                total_value=-total_cost,
            )
            self.transactions.append(tx)

            return ServiceResponse(
                success=True,
                message=f"Successfully purchased {quantity} shares of "
                        f"{upper_symbol} for ${total_cost:,.2f}."
            )
        except (InvalidSymbolError, InvalidAmountError, InsufficientFundsError) as e:
            return ServiceResponse(success=False, message=str(e))

    def sell_shares(self, symbol: str, quantity: int) -> ServiceResponse:
        """
        Executes a sell order for a given stock.

        Validates inputs, checks for sufficient holdings, and updates account
        state only if all checks pass.

        Args:
            symbol: The stock ticker symbol to sell.
            quantity: The number of shares to sell.

        Returns:
            A ServiceResponse indicating success or failure.
        """
        try:
            if not isinstance(quantity, int) or quantity <= 0:
                raise InvalidAmountError("Quantity must be a positive integer.")

            upper_symbol = symbol.upper()
            current_holding = self.holdings.get(upper_symbol, 0)
            if quantity > current_holding:
                raise InsufficientHoldingsError(
                    f"Sell order failed. You cannot sell {quantity} shares of "
                    f"{upper_symbol}. You only own {current_holding}."
                )

            price_per_share = get_share_price(upper_symbol)
            total_proceeds = (price_per_share * quantity).quantize(Decimal("0.01"))

            # --- Atomic State Modification ---
            self.cash_balance += total_proceeds
            self.holdings[upper_symbol] -= quantity
            if self.holdings[upper_symbol] == 0:
                del self.holdings[upper_symbol]

            tx = Transaction(
                type=TransactionType.SELL,
                symbol=upper_symbol,
                quantity=quantity,
                price_per_share=price_per_share,
                total_value=total_proceeds,
            )
            self.transactions.append(tx)

            return ServiceResponse(
                success=True,
                message=f"Successfully sold {quantity} shares of "
                        f"{upper_symbol} for ${total_proceeds:,.2f}."
            )
        except (InvalidSymbolError, InvalidAmountError, InsufficientHoldingsError) as e:
            return ServiceResponse(success=False, message=str(e))

    def get_portfolio_metrics(self) -> PortfolioMetrics:
        """
        Calculates and returns key portfolio metrics.

        Returns:
            A PortfolioMetrics object containing the current state of the
            account's performance.
        """
        total_holdings_value = Decimal("0.0")
        for symbol, quantity in self.holdings.items():
            try:
                price = get_share_price(symbol)
                total_holdings_value += price * quantity
            except InvalidSymbolError:
                # Per requirements, assume prices are available for owned stocks.
                # In a real system, this might be handled by using the last
                # known price or marking the holding as having a stale price.
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
        """
        Returns current holdings as a Pandas DataFrame for UI display.

        The DataFrame is pre-formatted with strings suitable for direct
        rendering in a UI component like Gradio's `gr.DataFrame`.

        Returns:
            A Pandas DataFrame of current stock holdings.
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
                data.append({
                    "Symbol": symbol,
                    "Quantity": quantity,
                    "Current Price": "N/A",
                    "Market Value": "N/A",
                })

        columns = ["Symbol", "Quantity", "Current Price", "Market Value"]
        if not data:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame(data, columns=columns)

    def get_transactions_df(self) -> pd.DataFrame:
        """
        Returns transaction history as a Pandas DataFrame for UI display.

        The DataFrame is pre-formatted with strings and is sorted in reverse
        chronological order (most recent transaction first).

        Returns:
            A Pandas DataFrame of the account's transaction history.
        """
        data = []
        for tx in reversed(self.transactions):
            total_value_str = f"{tx.total_value:,.2f}"
            if tx.total_value > 0 and tx.type != TransactionType.INITIALIZE:
                total_value_str = f"+${total_value_str}"
            elif tx.total_value < 0:
                total_value_str = f"-${abs(tx.total_value):,.2f}"
            else:
                total_value_str = f"${total_value_str}"

            data.append({
                "Timestamp": tx.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "Type": tx.type.value,
                "Symbol": tx.symbol or "N/A",
                "Quantity": tx.quantity or "N/A",
                "Price/Share": (
                    f"${tx.price_per_share:,.2f}" if tx.price_per_share else "N/A"
                ),
                "Total Value": total_value_str,
            })

        columns = [
            "Timestamp", "Type", "Symbol", "Quantity", "Price/Share", "Total Value"
        ]
        if not data:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame(data, columns=columns)