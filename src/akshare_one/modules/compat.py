"""Bridge the akshare releases this package supports.

akshare renames interface functions freely and gives no deprecation window: the
old name is simply gone in the release that introduces the new one. Between
1.20.44 and 1.20.65 that removed every historical, futures-minute and options
call this package makes, so each provider raised ``AttributeError`` the moment a
user installed a newer akshare — while ``pip install akshare-one`` happily pulled
one, because the floor is the only version constraint we state.

Two kinds of drift are handled here, and only here:

* **Renamed functions.** :data:`RENAMES` records every name a family of
  interfaces has carried, newest first. :func:`ak_function` resolves the first
  one the installed akshare actually has, so a provider never names a release.

* **Changed signatures.** ``stock_financial_report_sina`` kept its name but
  swapped its keyword arguments at 1.20.52 (``stock``/``symbol`` became
  ``symbol``/``indicator``), and ``option_sse_list_sina`` kept its signature but
  started returning a DataFrame instead of a list at 1.20.65. Neither shows up in
  a name check, so both get an adapter.

Resolution happens on every call rather than at import: that keeps the newest
name from being frozen in at import time, and it means a test can patch either
the resolved name or the older one on :mod:`akshare` and still be seen.

The floor stays at the oldest akshare this package ever supported. Moving it to
1.18.1 (the first release the 1.18 line has on PyPI) keeps the widest range
working, because the compat layer already absorbs every rename between the floor
and today.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any

import akshare as ak
import pandas as pd

#: Interfaces akshare renamed, newest name first. Every name a release has used
#: belongs here, because a user may have any of those releases installed.
#:
#: ``stock_zh_a_daily`` is listed three times' worth of history: it was that, then
#: ``stock_zh_a_daily_sina`` in 1.20.46, then ``stock_zh_a_hist_sina`` in 1.20.64.
#: The B-share pair and the minute pair moved on the same schedule.
RENAMES: dict[str, tuple[str, ...]] = {
    "stock_zh_a_hist": ("stock_zh_a_hist_em", "stock_zh_a_hist"),
    "stock_zh_a_daily": (
        "stock_zh_a_hist_sina",
        "stock_zh_a_daily_sina",
        "stock_zh_a_daily",
    ),
    "stock_zh_a_minute": ("stock_zh_a_hist_min_sina", "stock_zh_a_minute"),
    "stock_zh_b_daily": (
        "stock_zh_b_hist_sina",
        "stock_zh_b_daily_sina",
        "stock_zh_b_daily",
    ),
    "stock_zh_b_minute": ("stock_zh_b_hist_min_sina", "stock_zh_b_minute"),
    "futures_zh_minute_sina": ("futures_zh_min_sina", "futures_zh_minute_sina"),
    "futures_zh_spot": (
        "futures_zh_contract_realtime_sina",
        "futures_zh_spot",
    ),
    "option_sse_spot_price_sina": (
        "option_sse_realtime_sina",
        "option_sse_spot_price_sina",
    ),
}


def candidates(name: str) -> tuple[str, ...]:
    """Names akshare has used for the interface recorded under ``name``.

    A name already known to :data:`RENAMES` returns its recorded family; any
    other name stands for itself, so callers can pass either form.
    """
    return RENAMES.get(name, (name,))


def available_candidate(name: str) -> str | None:
    """The name of this family the installed akshare exposes, or ``None``."""
    return next((alias for alias in candidates(name) if hasattr(ak, alias)), None)


def ak_function(name: str) -> Callable[..., Any]:
    """Resolve an akshare interface across every name it has carried.

    Args:
        name: Any name in the family, e.g. ``"stock_zh_a_daily"``.

    Returns:
        The attribute of the installed akshare, looked up by the newest name it
        still has.

    Raises:
        AttributeError: If no name in the family exists, i.e. the installed
            akshare dropped the interface entirely rather than renaming it. The
            message lists every name that was tried, because that is the whole
            useful content of the failure.
    """
    family = candidates(name)
    for alias in family:
        fn = getattr(ak, alias, None)
        if fn is not None:
            return fn
    raise AttributeError(
        f"akshare has none of {', '.join(family)}; the interface {name!r} was "
        "removed or renamed again and akshare_one.modules.compat needs updating"
    )


#: ``stock_financial_report_sina`` before 1.20.52 named the report ``symbol`` and
#: the stock ``stock``; from 1.20.52 the stock is ``symbol`` and the report is
#: ``indicator``. Passing the wrong pair is a TypeError, and passing the old pair
#: positionally is worse: the same two strings land in the right slots by luck,
#: so it keeps working until someone adds a third parameter.
_FINANCIAL_REPORT_REPORTS = ("资产负债表", "利润表", "现金流量表")


def financial_report_kwargs(
    function: Callable[..., Any], stock: str, report: str
) -> dict[str, str]:
    """Keyword arguments for ``stock_financial_report_sina`` in either spelling.

    Decided from the callable's own parameter names rather than from a version
    check, so it follows the installed akshare even when a test supplies a fake.
    """
    if report not in _FINANCIAL_REPORT_REPORTS:
        raise ValueError(f"Unknown Sina report type: {report!r}")
    parameters = inspect.signature(function).parameters
    if "indicator" in parameters:
        return {"symbol": stock, "indicator": report}
    return {"stock": stock, "symbol": report}


def option_expirations(result: Any) -> list[str]:
    """Normalise ``option_sse_list_sina``'s answer to a list of month strings.

    Up to 1.20.64 it returned ``List[str]``. From 1.20.65 it returns a
    single-column frame, which is a silent change of type: iterating it yields
    the column name ``到期月份`` and ``if not expirations`` raises ValueError
    ("truth value of a DataFrame is ambiguous"), so both call sites failed in a
    different way than a missing function would.
    """
    if isinstance(result, pd.DataFrame):
        if result.empty:
            return []
        return [str(value) for value in result.iloc[:, 0].tolist()]
    return [str(value) for value in result]
