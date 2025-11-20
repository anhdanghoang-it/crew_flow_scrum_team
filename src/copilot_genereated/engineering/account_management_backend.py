"""
Account management and trading simulation backend module.

This module implements the complete backend service layer for the trading simulation
experience described in the engineering design. It exposes request/response driven
services that validate input, enforce business invariants, and emit structured
`ResponseEnvelope` objects that the Gradio UI can render directly.

Classes:
    DomainError: Base exception for predictable domain failures.
    ResponseEnvelope: Standard structure returned to the UI.
    AccountRepository: Thread-safe in-memory persistence layer.
    AccountService: Handles account creation and metadata retrieval.
    MoneyService: Implements deposit and withdrawal flows.
    TradingService: Records buy and sell operations with affordability checks.
    PortfolioService: Computes holdings tables and profit/loss metrics.
    SnapshotService: Reconstructs historical portfolio states.
    TransactionHistoryService: Provides transaction listings and snapshot options.

Functions:
    get_share_price: Deterministic adapter that returns fixed share prices for
        supported symbols and raises a `PriceRetrievalError` when a symbol is unknown.

Example:
    Basic usage example::

        from scrum_team.engineering.account_management_backend import (
            AccountRepository,
            AccountService,
            MoneyService,
            TradingService,
        )

        repo = AccountRepository()
        account_service = AccountService(repo)
        money_service = MoneyService(repo)
        trading_service = TradingService(repo)

        create_resp = account_service.create_account(username="alex")
        account_id = create_resp.data["account"]["account_id"]
        money_service.deposit(account_id=account_id, amount=1000)
        trading_service.buy(account_id=account_id, symbol="AAPL", quantity=2)

Dependencies:
    - Python 3.10+
    - pydantic >= 2.6

Testing:
    Syntax verification::

        python -m compileall src/scrum_team/engineering/account_management_backend.py
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
import threading
from typing import Any, Callable, Dict, List, Literal, Optional, Sequence
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, ValidationError

TransactionType = Literal["DEPOSIT", "WITHDRAWAL", "BUY", "SELL"]

SUCCESS_ACCOUNT_CREATED = "Account created successfully."
SUCCESS_DEPOSIT = "Deposit successful."
SUCCESS_WITHDRAWAL = "Withdrawal successful."
SUCCESS_BUY = "Buy order recorded successfully."
SUCCESS_SELL = "Sell order recorded successfully."
SUCCESS_PORTFOLIO_LOADED = "Portfolio loaded."
SUCCESS_TRANSACTIONS_LOADED = "Transactions loaded."
SUCCESS_SNAPSHOT = "Snapshot generated."
NO_ACTIVITY_MESSAGE = "No activity before this time."
EMPTY_PORTFOLIO_MESSAGE = "You have no holdings yet."
NO_BASELINE_MESSAGE = "No deposit baseline available."
PRICE_WARNING_MESSAGE = "Some share prices could not be retrieved. Values marked N/A."
USERNAME_REQUIRED_MESSAGE = "Username is required."
DEPOSIT_AMOUNT_REQUIRED_MESSAGE = "Deposit amount must be greater than 0."
WITHDRAW_AMOUNT_REQUIRED_MESSAGE = "Withdrawal amount must be greater than 0."
NUMERIC_AMOUNT_MESSAGE = "Enter a valid numeric amount."
QUANTITY_REQUIRED_MESSAGE = "Quantity must be greater than 0."
NUMERIC_QUANTITY_MESSAGE = "Enter a valid numeric quantity."
SYMBOL_REQUIRED_MESSAGE = "Symbol is required."
INSUFFICIENT_FUNDS_PURCHASE = "Insufficient funds. You cannot afford this purchase."
INSUFFICIENT_FUNDS_WITHDRAWAL = "Insufficient funds. Withdrawal would result in a negative balance."
INSUFFICIENT_SHARES_MESSAGE = "Insufficient shares. You cannot sell more than you hold."
NO_HOLDINGS_FOR_SYMBOL_MESSAGE = "You do not hold any shares of this symbol."
PRICE_RETRIEVAL_MESSAGE = "Unable to retrieve share price for the selected symbol."
DEPOSIT_SERVER_ERROR = "Unable to process deposit at the moment. Please try again later."
WITHDRAWAL_SERVER_ERROR = "Unable to process withdrawal at the moment. Please try again later."
BUY_SERVER_ERROR = "Unable to record buy transaction at the moment. Please try again later."
SELL_SERVER_ERROR = "Unable to record sell transaction at the moment. Please try again later."
ACCOUNT_CREATION_SERVER_ERROR = "Unable to create account at the moment. Please try again later."
PORTFOLIO_SERVER_ERROR = "Unable to load portfolio at the moment."
PL_SERVER_ERROR = "Unable to compute profit/loss at the moment."
SNAPSHOT_SERVER_ERROR = "Unable to generate snapshot at the moment."
TRANSACTION_SERVER_ERROR = "Unable to load transactions at the moment."
SNAPSHOT_RANGE_MESSAGE = "Selected time is outside the account history range."
ACCOUNT_NOT_FOUND_MESSAGE = "Account not found."
DUPLICATE_USERNAME_MESSAGE = "Username already exists. Please choose another."

FIXED_PRICES: Dict[str, float] = {
    "AAPL": 150.0,
    "TSLA": 200.0,
    "GOOGL": 180.0,
}
SUPPORTED_SYMBOLS: Sequence[str] = tuple(FIXED_PRICES.keys())
DEFAULT_CURRENCY = "USD"


def _now() -> datetime:
    return datetime.utcnow()


def _format_timestamp(value: datetime) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S")


def _clone_holdings(holdings: Dict[str, int]) -> Dict[str, int]:
    return {symbol: qty for symbol, qty in holdings.items() if qty > 0}


class DomainError(Exception):
    """Base predictable error that maps to a user-facing message."""

    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ValidationDomainError(DomainError):
    code = "VALIDATION_ERROR"


class DuplicateUsernameError(DomainError):
    code = "DUPLICATE_USERNAME"


class NotFoundError(DomainError):
    code = "NOT_FOUND"


class InsufficientFundsError(DomainError):
    code = "INSUFFICIENT_FUNDS"


class InsufficientSharesError(DomainError):
    code = "INSUFFICIENT_SHARES"


class PriceRetrievalError(DomainError):
    code = "PRICE_RETRIEVAL"


class AtomicityError(DomainError):
    code = "ATOMICITY_FAILURE"


class SnapshotOutOfRangeError(DomainError):
    code = "SNAPSHOT_RANGE"


class Holding(BaseModel):
    """Represents a symbol position stored in an account."""

    symbol: str = Field(min_length=1)
    quantity: int = Field(ge=0)


class Transaction(BaseModel):
    """Immutable record of a money movement or trade."""

    model_config = ConfigDict(frozen=True)

    tx_id: str
    timestamp: datetime
    type: TransactionType
    symbol: Optional[str] = None
    quantity: Optional[int] = None
    amount: float
    price_per_share: Optional[float] = None
    resulting_cash_balance: float
    resulting_holdings: Dict[str, int]


class Account(BaseModel):
    """Trading account with holdings, balance, and transactions."""

    model_config = ConfigDict(validate_assignment=True)

    account_id: str
    username: str
    display_name: Optional[str] = None
    cash_balance: float
    holdings: Dict[str, int]
    transactions: List[Transaction]
    created_at: datetime


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


class TransactionFilter(BaseModel):
    account_id: str
    tx_type: Optional[TransactionType] = None
    symbol: Optional[str] = None


class ResponseEnvelope(BaseModel):
    """Standard payload consumed by the Gradio UI."""

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None

    def to_payload(self) -> Dict[str, Any]:
        """Return a plain dict for serialization or UI consumption."""

        return self.model_dump()


def build_response(
    success: bool,
    message: str,
    data: Optional[Dict[str, Any]] = None,
    error_code: Optional[str] = None,
) -> ResponseEnvelope:
    """Helper to construct a `ResponseEnvelope`."""

    return ResponseEnvelope(success=success, message=message, data=data, error_code=error_code)


class AccountRepository:
    """Thread-safe in-memory repository for `Account` objects."""

    def __init__(self) -> None:
        self._accounts: Dict[str, Account] = {}
        self._lock = threading.RLock()

    def create_account(self, username: str, display_name: Optional[str]) -> Account:
        """Create a new account with default balances."""

        cleaned_username = username.strip()
        with self._lock:
            lowered = cleaned_username.lower()
            if any(acc.username.lower() == lowered for acc in self._accounts.values()):
                raise DuplicateUsernameError(DUPLICATE_USERNAME_MESSAGE)
            account_id = str(uuid4())
            account = Account(
                account_id=account_id,
                username=cleaned_username,
                display_name=display_name,
                cash_balance=0.0,
                holdings={},
                transactions=[],
                created_at=_now(),
            )
            self._accounts[account_id] = account
            return account.model_copy(deep=True)

    def get(self, account_id: str) -> Account:
        """Retrieve an account copy by identifier."""

        with self._lock:
            if account_id not in self._accounts:
                raise NotFoundError(ACCOUNT_NOT_FOUND_MESSAGE)
            return self._accounts[account_id].model_copy(deep=True)

    def mutate(self, account_id: str, mutator: Callable[[Account], None]) -> Account:
        """Execute an atomic mutation guarded by a lock."""

        with self._lock:
            if account_id not in self._accounts:
                raise NotFoundError(ACCOUNT_NOT_FOUND_MESSAGE)
            account = self._accounts[account_id]
            snapshot = account.model_copy(deep=True)
            try:
                mutator(account)
            except DomainError:
                self._accounts[account_id] = snapshot
                raise
            except Exception as exc:  # pragma: no cover - safety fallback
                self._accounts[account_id] = snapshot
                raise AtomicityError("Atomic operation failed.") from exc
            return account.model_copy(deep=True)

    def list_transaction_timestamps(self, account_id: str) -> List[datetime]:
        account = self.get(account_id)
        return sorted({tx.timestamp for tx in account.transactions})

    def list_transactions(self, account_id: str) -> List[Transaction]:
        account = self.get(account_id)
        return sorted(account.transactions, key=lambda tx: tx.timestamp, reverse=True)


def get_share_price(symbol: str) -> float:
    """Return deterministic price for supported symbols."""

    key = symbol.upper()
    try:
        return FIXED_PRICES[key]
    except KeyError as exc:
        raise PriceRetrievalError(PRICE_RETRIEVAL_MESSAGE) from exc


def _create_transaction(
    account: Account,
    tx_type: TransactionType,
    amount: float,
    symbol: Optional[str] = None,
    quantity: Optional[int] = None,
    price_per_share: Optional[float] = None,
) -> Transaction:
    return Transaction(
        tx_id=str(uuid4()),
        timestamp=_now(),
        type=tx_type,
        symbol=symbol,
        quantity=quantity,
        amount=round(amount, 2),
        price_per_share=price_per_share,
        resulting_cash_balance=round(account.cash_balance, 2),
        resulting_holdings=_clone_holdings(account.holdings),
    )


@dataclass(frozen=True)
class _ValidationResult:
    request: Optional[BaseModel]
    error: Optional[ResponseEnvelope]


class _ServiceBase:
    """Shared helpers for service classes."""

    def __init__(self, repo: AccountRepository) -> None:
        self.repo = repo

    def _validation_error(self, message: str, code: str = "VALIDATION_ERROR") -> ResponseEnvelope:
        return build_response(False, message, error_code=code)

    def _handle_validation(self, model: type[BaseModel], **kwargs: Any) -> _ValidationResult:
        try:
            return _ValidationResult(request=model(**kwargs), error=None)
        except ValidationError as err:
            return _ValidationResult(request=None, error=self._map_validation_error(model, err))

    def _map_validation_error(self, model: type[BaseModel], err: ValidationError) -> ResponseEnvelope:
        if model is DepositRequest:
            return self._map_amount_error(err, deposit=True)
        if model is WithdrawRequest:
            return self._map_amount_error(err, deposit=False)
        if model in (BuyRequest, SellRequest):
            message = self._map_trade_error(err)
            return self._validation_error(message)
        if model is SnapshotRequest:
            return self._validation_error("Enter a valid timestamp.")
        if model is CreateAccountRequest:
            return self._validation_error(USERNAME_REQUIRED_MESSAGE)
        if model is TransactionFilter:
            return self._validation_error("Enter valid filter criteria.")
        return self._validation_error("Validation failed.")

    def _map_amount_error(self, err: ValidationError, deposit: bool) -> ResponseEnvelope:
        message = NUMERIC_AMOUNT_MESSAGE
        for issue in err.errors():
            if issue.get("type") == "greater_than":
                message = DEPOSIT_AMOUNT_REQUIRED_MESSAGE if deposit else WITHDRAW_AMOUNT_REQUIRED_MESSAGE
                break
        return self._validation_error(message)

    def _map_trade_error(self, err: ValidationError) -> str:
        for issue in err.errors():
            field = issue.get("loc", [""])[0]
            if field == "symbol":
                return SYMBOL_REQUIRED_MESSAGE
            if field == "quantity" and issue.get("type") == "greater_than":
                return QUANTITY_REQUIRED_MESSAGE
        return NUMERIC_QUANTITY_MESSAGE


class AccountService(_ServiceBase):
    """Service responsible for account creation and metadata retrieval."""

    def create_account(self, username: Any, display_name: Optional[Any] = None) -> ResponseEnvelope:
        username_value = username.strip() if isinstance(username, str) else ""
        if not username_value:
            return self._validation_error(USERNAME_REQUIRED_MESSAGE)
        display = display_name.strip() if isinstance(display_name, str) and display_name.strip() else None
        validation = self._handle_validation(
            CreateAccountRequest,
            username=username_value,
            display_name=display,
        )
        if validation.error:
            return validation.error
        try:
            account = self.repo.create_account(validation.request.username, validation.request.display_name)
            data = {"account": account.model_dump()}
            return build_response(True, SUCCESS_ACCOUNT_CREATED, data=data)
        except DuplicateUsernameError as err:
            return build_response(False, err.message, error_code=err.code)
        except DomainError as err:
            return build_response(False, err.message, error_code=err.code)
        except Exception:
            return build_response(False, ACCOUNT_CREATION_SERVER_ERROR, error_code="SERVER_ERROR")


class MoneyService(_ServiceBase):
    """Handles deposits and withdrawals while enforcing cash invariants."""

    def deposit(self, account_id: Any, amount: Any) -> ResponseEnvelope:
        validation = self._handle_validation(DepositRequest, account_id=str(account_id), amount=amount)
        if validation.error:
            return validation.error
        request = validation.request
        try:
            updated = self.repo.mutate(
                request.account_id,
                lambda account: self._apply_deposit(account, request.amount),
            )
            payload = {
                "cash_balance": round(updated.cash_balance, 2),
                "transaction": updated.transactions[-1].model_dump(),
            }
            return build_response(True, SUCCESS_DEPOSIT, data=payload)
        except NotFoundError as err:
            return build_response(False, err.message, error_code=err.code)
        except AtomicityError:
            return build_response(False, DEPOSIT_SERVER_ERROR, error_code="SERVER_ERROR")
        except DomainError as err:
            return build_response(False, err.message, error_code=err.code)
        except Exception:
            return build_response(False, DEPOSIT_SERVER_ERROR, error_code="SERVER_ERROR")

    def withdraw(self, account_id: Any, amount: Any) -> ResponseEnvelope:
        validation = self._handle_validation(WithdrawRequest, account_id=str(account_id), amount=amount)
        if validation.error:
            return validation.error
        request = validation.request
        try:
            updated = self.repo.mutate(
                request.account_id,
                lambda account: self._apply_withdrawal(account, request.amount),
            )
            payload = {
                "cash_balance": round(updated.cash_balance, 2),
                "transaction": updated.transactions[-1].model_dump(),
            }
            return build_response(True, SUCCESS_WITHDRAWAL, data=payload)
        except NotFoundError as err:
            return build_response(False, err.message, error_code=err.code)
        except AtomicityError:
            return build_response(False, WITHDRAWAL_SERVER_ERROR, error_code="SERVER_ERROR")
        except DomainError as err:
            return build_response(False, err.message, error_code=err.code)
        except Exception:
            return build_response(False, WITHDRAWAL_SERVER_ERROR, error_code="SERVER_ERROR")

    def _apply_deposit(self, account: Account, amount: float) -> None:
        account.cash_balance = round(account.cash_balance + amount, 2)
        tx = _create_transaction(account, "DEPOSIT", amount)
        account.transactions.append(tx)

    def _apply_withdrawal(self, account: Account, amount: float) -> None:
        if account.cash_balance < amount:
            raise InsufficientFundsError(INSUFFICIENT_FUNDS_WITHDRAWAL)
        account.cash_balance = round(account.cash_balance - amount, 2)
        tx = _create_transaction(account, "WITHDRAWAL", amount)
        account.transactions.append(tx)


class TradingService(_ServiceBase):
    """Processes buy and sell operations with affordability enforcement."""

    def __init__(self, repo: AccountRepository, price_provider: Callable[[str], float] = get_share_price) -> None:
        super().__init__(repo)
        self.get_price = price_provider

    def buy(self, account_id: Any, symbol: Any, quantity: Any) -> ResponseEnvelope:
        validation = self._handle_validation(
            BuyRequest,
            account_id=str(account_id),
            symbol=str(symbol).upper() if isinstance(symbol, str) else symbol,
            quantity=quantity,
        )
        if validation.error:
            return validation.error
        request = validation.request
        try:
            price = self.get_price(request.symbol)
            total_cost = price * request.quantity
            updated = self.repo.mutate(
                request.account_id,
                lambda account: self._apply_buy(account, request, price, total_cost),
            )
            payload = {
                "cash_balance": round(updated.cash_balance, 2),
                "holdings": deepcopy(updated.holdings),
                "transaction": updated.transactions[-1].model_dump(),
            }
            return build_response(True, SUCCESS_BUY, data=payload)
        except PriceRetrievalError as err:
            return build_response(False, err.message, error_code=err.code)
        except NotFoundError as err:
            return build_response(False, err.message, error_code=err.code)
        except AtomicityError:
            return build_response(False, BUY_SERVER_ERROR, error_code="SERVER_ERROR")
        except DomainError as err:
            return build_response(False, err.message, error_code=err.code)
        except Exception:
            return build_response(False, BUY_SERVER_ERROR, error_code="SERVER_ERROR")

    def sell(self, account_id: Any, symbol: Any, quantity: Any) -> ResponseEnvelope:
        validation = self._handle_validation(
            SellRequest,
            account_id=str(account_id),
            symbol=str(symbol).upper() if isinstance(symbol, str) else symbol,
            quantity=quantity,
        )
        if validation.error:
            return validation.error
        request = validation.request
        try:
            price = self.get_price(request.symbol)
            proceeds = price * request.quantity
            updated = self.repo.mutate(
                request.account_id,
                lambda account: self._apply_sell(account, request, price, proceeds),
            )
            payload = {
                "cash_balance": round(updated.cash_balance, 2),
                "holdings": deepcopy(updated.holdings),
                "transaction": updated.transactions[-1].model_dump(),
            }
            return build_response(True, SUCCESS_SELL, data=payload)
        except PriceRetrievalError as err:
            return build_response(False, err.message, error_code=err.code)
        except NotFoundError as err:
            return build_response(False, err.message, error_code=err.code)
        except AtomicityError:
            return build_response(False, SELL_SERVER_ERROR, error_code="SERVER_ERROR")
        except DomainError as err:
            return build_response(False, err.message, error_code=err.code)
        except Exception:
            return build_response(False, SELL_SERVER_ERROR, error_code="SERVER_ERROR")

    def _apply_buy(self, account: Account, request: BuyRequest, price: float, total_cost: float) -> None:
        if account.cash_balance < total_cost:
            raise InsufficientFundsError(INSUFFICIENT_FUNDS_PURCHASE)
        account.cash_balance = round(account.cash_balance - total_cost, 2)
        account.holdings[request.symbol] = account.holdings.get(request.symbol, 0) + request.quantity
        tx = _create_transaction(
            account,
            "BUY",
            total_cost,
            symbol=request.symbol,
            quantity=request.quantity,
            price_per_share=price,
        )
        account.transactions.append(tx)

    def _apply_sell(self, account: Account, request: SellRequest, price: float, proceeds: float) -> None:
        held = account.holdings.get(request.symbol, 0)
        if held == 0:
            raise InsufficientSharesError(NO_HOLDINGS_FOR_SYMBOL_MESSAGE)
        if held < request.quantity:
            raise InsufficientSharesError(INSUFFICIENT_SHARES_MESSAGE)
        remaining = held - request.quantity
        if remaining == 0:
            del account.holdings[request.symbol]
        else:
            account.holdings[request.symbol] = remaining
        account.cash_balance = round(account.cash_balance + proceeds, 2)
        tx = _create_transaction(
            account,
            "SELL",
            proceeds,
            symbol=request.symbol,
            quantity=request.quantity,
            price_per_share=price,
        )
        account.transactions.append(tx)


class PortfolioService(_ServiceBase):
    """Calculates holdings table, totals, and profit/loss."""

    def __init__(self, repo: AccountRepository, price_provider: Callable[[str], float] = get_share_price) -> None:
        super().__init__(repo)
        self.get_price = price_provider

    def compute_portfolio(self, account_id: Any) -> ResponseEnvelope:
        try:
            account = self.repo.get(str(account_id))
            rows: List[Dict[str, Any]] = []
            total_holdings_value = 0.0
            warning = False
            for symbol, qty in sorted(account.holdings.items()):
                try:
                    price = self.get_price(symbol)
                    market_value = round(price * qty, 2)
                    total_holdings_value += market_value
                    rows.append(
                        {
                            "Symbol": symbol,
                            "Quantity": qty,
                            "Current price": round(price, 2),
                            "Market value": market_value,
                        }
                    )
                except PriceRetrievalError:
                    warning = True
                    rows.append(
                        {
                            "Symbol": symbol,
                            "Quantity": qty,
                            "Current price": "N/A",
                            "Market value": "N/A",
                        }
                    )
            total_portfolio_value = round(account.cash_balance + total_holdings_value, 2)
            data = {
                "holdings_table": rows,
                "cash_balance": round(account.cash_balance, 2),
                "total_holdings_value": round(total_holdings_value, 2),
                "total_portfolio_value": total_portfolio_value,
            }
            message = SUCCESS_PORTFOLIO_LOADED
            if not account.holdings and account.cash_balance == 0:
                message = EMPTY_PORTFOLIO_MESSAGE
            if warning:
                data["warning"] = PRICE_WARNING_MESSAGE
            return build_response(True, message, data=data)
        except NotFoundError as err:
            return build_response(False, err.message, error_code=err.code)
        except Exception:
            return build_response(False, PORTFOLIO_SERVER_ERROR, error_code="SERVER_ERROR")

    def compute_profit_loss(self, account_id: Any) -> ResponseEnvelope:
        portfolio = self.compute_portfolio(account_id)
        if not portfolio.success:
            return portfolio
        try:
            account = self.repo.get(str(account_id))
            baseline = sum(tx.amount for tx in account.transactions if tx.type == "DEPOSIT")
            if baseline == 0:
                data = {
                    "baseline": 0.0,
                    "total_portfolio_value": portfolio.data["total_portfolio_value"] if portfolio.data else 0.0,
                    "profit_loss": None,
                    "status": "NO_BASELINE",
                    "display": "N/A",
                }
                return build_response(True, NO_BASELINE_MESSAGE, data=data)
            total_value = portfolio.data["total_portfolio_value"] if portfolio.data else 0.0
            profit_loss = round(total_value - baseline, 2)
            status = "Profit" if profit_loss > 0 else "Loss" if profit_loss < 0 else "Break-even"
            sign = "+" if profit_loss > 0 else "" if profit_loss == 0 else ""
            display = f"{sign}{profit_loss}" if profit_loss != 0 else "0"
            data = {
                "baseline": round(baseline, 2),
                "total_portfolio_value": total_value,
                "profit_loss": profit_loss,
                "status": status,
                "display": display,
            }
            return build_response(True, "P/L calculated.", data=data)
        except NotFoundError as err:
            return build_response(False, err.message, error_code=err.code)
        except Exception:
            return build_response(False, PL_SERVER_ERROR, error_code="SERVER_ERROR")


class SnapshotService(_ServiceBase):
    """Reconstructs historical portfolio states at arbitrary timestamps."""

    def __init__(self, repo: AccountRepository, price_provider: Callable[[str], float] = get_share_price) -> None:
        super().__init__(repo)
        self.get_price = price_provider

    def snapshot(self, account_id: Any, timestamp: Any) -> ResponseEnvelope:
        validation = self._handle_validation(SnapshotRequest, account_id=str(account_id), timestamp=timestamp)
        if validation.error:
            return validation.error
        request = validation.request
        try:
            account = self.repo.get(request.account_id)
            now_value = _now()
            if request.timestamp < account.created_at or request.timestamp > now_value:
                raise SnapshotOutOfRangeError(SNAPSHOT_RANGE_MESSAGE)
            holdings: Dict[str, int] = {}
            cash = 0.0
            deposits_baseline = 0.0
            transactions_applied = 0
            for tx in sorted(account.transactions, key=lambda item: item.timestamp):
                if tx.timestamp > request.timestamp:
                    break
                transactions_applied += 1
                if tx.type == "DEPOSIT":
                    cash += tx.amount
                    deposits_baseline += tx.amount
                elif tx.type == "WITHDRAWAL":
                    cash -= tx.amount
                elif tx.type == "BUY" and tx.symbol:
                    cash -= tx.amount
                    holdings[tx.symbol] = holdings.get(tx.symbol, 0) + (tx.quantity or 0)
                elif tx.type == "SELL" and tx.symbol:
                    cash += tx.amount
                    holdings[tx.symbol] = holdings.get(tx.symbol, 0) - (tx.quantity or 0)
                    if holdings[tx.symbol] <= 0:
                        holdings.pop(tx.symbol, None)
            rows: List[Dict[str, Any]] = []
            warning = False
            total_holdings_value = 0.0
            for symbol, qty in sorted(holdings.items()):
                try:
                    price = self.get_price(symbol)
                    market = round(price * qty, 2)
                    total_holdings_value += market
                    rows.append(
                        {
                            "Symbol": symbol,
                            "Quantity": qty,
                            "Current price": round(price, 2),
                            "Market value": market,
                        }
                    )
                except PriceRetrievalError:
                    warning = True
                    rows.append(
                        {
                            "Symbol": symbol,
                            "Quantity": qty,
                            "Current price": "N/A",
                            "Market value": "N/A",
                        }
                    )
            total_portfolio_value = round(cash + total_holdings_value, 2)
            profit_loss = None
            status = "NO_BASELINE"
            message = SUCCESS_SNAPSHOT
            if deposits_baseline > 0:
                profit_loss = round(total_portfolio_value - deposits_baseline, 2)
                status = "Profit" if profit_loss > 0 else "Loss" if profit_loss < 0 else "Break-even"
            elif transactions_applied == 0:
                message = NO_ACTIVITY_MESSAGE
            data = {
                "holdings_table": rows,
                "cash_balance": round(cash, 2),
                "total_holdings_value": round(total_holdings_value, 2),
                "total_portfolio_value": total_portfolio_value,
                "baseline": round(deposits_baseline, 2),
                "profit_loss": profit_loss,
                "status": status,
                "timestamp": _format_timestamp(request.timestamp),
            }
            if warning:
                data["warning"] = PRICE_WARNING_MESSAGE
            return build_response(True, message, data=data)
        except SnapshotOutOfRangeError as err:
            return build_response(False, err.message, error_code=err.code)
        except NotFoundError as err:
            return build_response(False, err.message, error_code=err.code)
        except Exception:
            return build_response(False, SNAPSHOT_SERVER_ERROR, error_code="SERVER_ERROR")


class TransactionHistoryService(_ServiceBase):
    """Provides transaction listings and snapshot dropdown data."""

    def list_transactions(
        self,
        account_id: Any,
        tx_type: Optional[str] = None,
        symbol: Optional[str] = None,
    ) -> ResponseEnvelope:
        filter_type = tx_type.upper() if isinstance(tx_type, str) and tx_type.upper() != "ALL" else None
        filter_symbol = symbol.upper() if isinstance(symbol, str) and symbol.upper() != "ALL" else None
        try:
            transactions = self.repo.list_transactions(str(account_id))
            rows: List[Dict[str, Any]] = []
            for tx in transactions:
                if filter_type and tx.type != filter_type:
                    continue
                if filter_symbol and (tx.symbol or "").upper() != filter_symbol:
                    continue
                rows.append(
                    {
                        "Timestamp": _format_timestamp(tx.timestamp),
                        "Type": tx.type,
                        "Symbol": tx.symbol or "",
                        "Quantity": tx.quantity or "",
                        "Amount": tx.amount,
                        "Resulting cash balance": tx.resulting_cash_balance,
                    }
                )
            if not transactions:
                return build_response(True, "No transactions have been recorded yet.", data={"transactions": []})
            if not rows:
                return build_response(True, "No transactions match the selected filters.", data={"transactions": []})
            return build_response(True, SUCCESS_TRANSACTIONS_LOADED, data={"transactions": rows})
        except NotFoundError as err:
            return build_response(False, err.message, error_code=err.code)
        except Exception:
            return build_response(False, TRANSACTION_SERVER_ERROR, error_code="SERVER_ERROR")

    def snapshot_options(self, account_id: Any) -> ResponseEnvelope:
        try:
            timestamps = self.repo.list_transaction_timestamps(str(account_id))
            options = [
                {
                    "value": ts.isoformat(),
                    "label": f"{_format_timestamp(ts)} ({idx + 1})",
                }
                for idx, ts in enumerate(timestamps)
            ]
            message = "Snapshot timestamps loaded."
            if not options:
                message = "No transactions have been recorded yet."
            return build_response(True, message, data={"timestamps": options})
        except NotFoundError as err:
            return build_response(False, err.message, error_code=err.code)
        except Exception:
            return build_response(False, TRANSACTION_SERVER_ERROR, error_code="SERVER_ERROR")


class TradingSimulationBackend:
    """Facade that wires repository and services for UI consumption."""

    def __init__(self) -> None:
        self.repo = AccountRepository()
        self.account_service = AccountService(self.repo)
        self.money_service = MoneyService(self.repo)
        self.trading_service = TradingService(self.repo)
        self.portfolio_service = PortfolioService(self.repo)
        self.snapshot_service = SnapshotService(self.repo)
        self.history_service = TransactionHistoryService(self.repo)

    def create_account(self, username: Any, display_name: Optional[Any] = None) -> ResponseEnvelope:
        return self.account_service.create_account(username, display_name)

    def deposit(self, account_id: Any, amount: Any) -> ResponseEnvelope:
        return self.money_service.deposit(account_id, amount)

    def withdraw(self, account_id: Any, amount: Any) -> ResponseEnvelope:
        return self.money_service.withdraw(account_id, amount)

    def buy(self, account_id: Any, symbol: Any, quantity: Any) -> ResponseEnvelope:
        return self.trading_service.buy(account_id, symbol, quantity)

    def sell(self, account_id: Any, symbol: Any, quantity: Any) -> ResponseEnvelope:
        return self.trading_service.sell(account_id, symbol, quantity)

    def portfolio(self, account_id: Any) -> ResponseEnvelope:
        return self.portfolio_service.compute_portfolio(account_id)

    def profit_loss(self, account_id: Any) -> ResponseEnvelope:
        return self.portfolio_service.compute_profit_loss(account_id)

    def snapshot(self, account_id: Any, timestamp: Any) -> ResponseEnvelope:
        ts_value = timestamp
        if isinstance(timestamp, str) and timestamp:
            ts_value = datetime.fromisoformat(timestamp)
        return self.snapshot_service.snapshot(account_id, ts_value)

    def snapshot_options(self, account_id: Any) -> ResponseEnvelope:
        return self.history_service.snapshot_options(account_id)

    def transactions(self, account_id: Any, tx_type: Optional[str] = None, symbol: Optional[str] = None) -> ResponseEnvelope:
        return self.history_service.list_transactions(account_id, tx_type, symbol)

    def share_price(self, symbol: Any) -> ResponseEnvelope:
        try:
            value = get_share_price(str(symbol))
            data = {"symbol": str(symbol).upper(), "price": value}
            return build_response(True, "Price retrieved.", data=data)
        except DomainError as err:
            return build_response(False, err.message, error_code=err.code)

    def supported_symbols(self) -> List[str]:
        return list(SUPPORTED_SYMBOLS)
