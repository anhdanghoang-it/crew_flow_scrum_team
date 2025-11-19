# Account Management System — Requirements

## Overview

A simple account management system for a trading simulation platform. The system tracks user accounts, cash balances, share holdings, and transactions. It computes portfolio value and profit/loss using current share prices.

## Functional Requirements

- Users can create an account.
- Users can deposit funds into their account.
- Users can withdraw funds (withdrawals that would result in negative cash balance must be prevented).
- Users can record buy and sell transactions for shares; each transaction includes symbol, quantity, price, and timestamp.
- The system calculates the total value of a user's portfolio using current share prices.
- The system calculates the profit or loss relative to the user's initial deposit (net worth minus initial deposit).
- The system can report the user's current holdings (symbols with quantities) at any time.
- The system can report the user's current profit or loss at any time.
- The system can list the user's transactions ordered over time.

## Constraints & Validation Rules

- Prevent withdrawals that would leave a negative cash balance.
- Prevent buy transactions if the user does not have sufficient cash to cover the purchase (price * quantity).
- Prevent sell transactions if the user does not have enough shares of the given symbol.

## External Interface

- The system has access to a function `get_share_price(symbol)` which returns the current price for the given symbol.
- Provide a test implementation of `get_share_price` that returns fixed prices for `AAPL`, `TSLA`, and `GOOGL`.

## Notes & Assumptions

- Transactions should be timestamped and kept in chronological order.
- Portfolio value is calculated as sum(quantity(symbol) * get_share_price(symbol)) plus available cash.
- Profit/loss is calculated as current net worth (cash + portfolio value) minus the initial deposit amount.
- Currency precision (cents) and concurrency concerns are out of scope for the initial implementation but should be considered later.