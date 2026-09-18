"""The futures domain's column contracts, one per interface."""

from __future__ import annotations

#: timestamp, symbol, contract, open, high, low, close, volume, open_interest,
#: settlement
HIST_COLUMNS = (
    "timestamp",
    "symbol",
    "contract",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "open_interest",
    "settlement",
)

#: symbol, symbol_root, contract, price, change, pct_change, timestamp, volume,
#: open_interest, open, high, low, prev_settlement, settlement, name
REALTIME_COLUMNS = (
    "symbol",
    "symbol_root",
    "contract",
    "price",
    "change",
    "pct_change",
    "timestamp",
    "volume",
    "open_interest",
    "open",
    "high",
    "low",
    "prev_settlement",
    "settlement",
    "name",
)

#: symbol, name, contract, exchange
CONTRACT_COLUMNS = (
    "symbol",
    "name",
    "contract",
    "exchange",
)
