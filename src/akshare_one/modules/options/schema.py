"""The options domain's column contracts, one per interface."""

from __future__ import annotations

#: underlying, symbol, name, option_type, strike, expiration, price, change,
#: pct_change, volume, open_interest, implied_volatility
CHAIN_COLUMNS = (
    "underlying",
    "symbol",
    "name",
    "option_type",
    "strike",
    "expiration",
    "price",
    "change",
    "pct_change",
    "volume",
    "open_interest",
    "implied_volatility",
)

#: symbol, underlying, price, change, pct_change, timestamp, volume,
#: open_interest, iv
REALTIME_COLUMNS = (
    "symbol",
    "underlying",
    "price",
    "change",
    "pct_change",
    "timestamp",
    "volume",
    "open_interest",
    "iv",
)

#: timestamp, symbol, open, high, low, close, volume, open_interest, settlement
HISTORY_COLUMNS = (
    "timestamp",
    "symbol",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "open_interest",
    "settlement",
)
