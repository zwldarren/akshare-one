"""The insider domain's column contract."""

from __future__ import annotations

#: symbol, issuer, name, title, transaction_date, transaction_shares,
#: transaction_price_per_share, shares_owned_after_transaction, relationship,
#: is_board_director, transaction_value, shares_owned_before_transaction
COLUMNS = (
    "symbol",
    "issuer",
    "name",
    "title",
    "transaction_date",
    "transaction_shares",
    "transaction_price_per_share",
    "shares_owned_after_transaction",
    "relationship",
    "is_board_director",
    "transaction_value",
    "shares_owned_before_transaction",
)
