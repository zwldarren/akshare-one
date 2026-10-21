"""The realtime domain's column contract."""

from __future__ import annotations

#: symbol, price, change, pct_change, timestamp, volume, amount, open, high, low, prev_close
#: ``timestamp`` is the time the quote was priced. A source that states no
#: quote time reports the time of the request instead.
COLUMNS = (
    "symbol",
    "price",
    "change",
    "pct_change",
    "timestamp",
    "volume",
    "amount",
    "open",
    "high",
    "low",
    "prev_close",
)
