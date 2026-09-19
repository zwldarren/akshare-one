"""Shared symbol helpers."""

_MARKET_PREFIXES = ("sh", "sz", "bj")

# Exchange ranges for bare six-digit A-share codes. Shanghai also serves 000xxx
# indices, but a caller passing a bare code means the stock listing, so 000001
# resolves to sz000001 (平安银行) rather than the SSE Composite index; an index
# has to be requested with an explicit "sh" prefix.
_SHANGHAI = ("5", "6", "9")  # funds/ETFs, stocks, B-shares
_SHANGHAI_BONDS = ("110", "111", "113", "118")
_SHENZHEN = ("0", "1", "2", "3")  # stocks, funds/bonds, B-shares, ChiNext
_BEIJING = ("4", "8")  # Beijing Stock Exchange


def to_market_symbol(symbol: str, *, upper: bool = False) -> str:
    """Normalise an A-share code to its exchange-prefixed form.

    ``600000`` -> ``sh600000``, ``000001`` -> ``sz000001``, ``430047`` ->
    ``bj430047``. An already-prefixed symbol keeps its prefix and is only
    re-cased. Raises ``ValueError`` when the exchange cannot be determined,
    rather than silently guessing one.
    """
    code = symbol.strip()
    lowered = code.lower()
    if lowered.startswith(_MARKET_PREFIXES):
        prefix, bare = lowered[:2], code[2:]
    else:
        prefix, bare = _exchange_prefix(lowered), code

    if len(bare) != 6 or not bare.isdigit():
        raise ValueError(f"Cannot determine the exchange for symbol: {symbol!r}")

    normalised = f"{prefix}{bare}"
    return normalised.upper() if upper else normalised


def _exchange_prefix(code: str) -> str:
    if len(code) != 6 or not code.isdigit():
        raise ValueError(f"Cannot determine the exchange for symbol: {code!r}")
    if code.startswith(_SHANGHAI) or code.startswith(_SHANGHAI_BONDS):
        return "sh"
    if code.startswith(_SHENZHEN):
        return "sz"
    if code.startswith(_BEIJING):
        return "bj"
    raise ValueError(f"Cannot determine the exchange for symbol: {code!r}")


def convert_xieqiu_symbol(symbol: str) -> str:
    """Convert Symbol (600000) to XueQiu Symbol (SH600000)."""
    return to_market_symbol(symbol, upper=True)
