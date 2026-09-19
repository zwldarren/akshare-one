"""Offline regression tests for exchange-prefix handling.

The Sina adapters used to force a ``sh`` prefix onto every bare code, so
``000001`` (平安银行, a Shenzhen stock) was fetched as ``sh000001`` (the SSE
Composite index). These tests pin the exchange inference and the call sites.
"""

from unittest.mock import patch

import pandas as pd
import pytest

from akshare_one.modules.financial.sina import SinaFinancialReport
from akshare_one.modules.historical.sina import SinaHistorical
from akshare_one.modules.utils import convert_xieqiu_symbol, to_market_symbol


@pytest.fixture(autouse=True)
def _disable_cache(monkeypatch):
    monkeypatch.setenv("AKSHARE_ONE_CACHE_ENABLED", "false")


@pytest.mark.parametrize(
    ("symbol", "expected"),
    [
        ("600000", "sh600000"),
        ("688981", "sh688981"),
        ("510300", "sh510300"),  # SH ETF
        ("900901", "sh900901"),  # SH B-share
        ("000001", "sz000001"),  # 平安银行, not the SSE Composite
        ("002594", "sz002594"),
        ("300750", "sz300750"),
        ("159915", "sz159915"),  # SZ ETF
        ("200002", "sz200002"),  # SZ B-share
        ("430047", "bj430047"),  # BSE
        ("830799", "bj830799"),  # BSE
    ],
)
def test_to_market_symbol_maps_bare_codes(symbol, expected):
    assert to_market_symbol(symbol) == expected


@pytest.mark.parametrize(
    ("symbol", "expected"),
    [
        ("sh600000", "sh600000"),
        ("SH600000", "sh600000"),
        ("sz000001", "sz000001"),
        ("bj430047", "bj430047"),
    ],
)
def test_to_market_symbol_normalises_existing_prefix(symbol, expected):
    assert to_market_symbol(symbol) == expected


def test_to_market_symbol_upper():
    assert to_market_symbol("000001", upper=True) == "SZ000001"
    assert to_market_symbol("sh600000", upper=True) == "SH600000"


@pytest.mark.parametrize("symbol", ["INVALID", "12345", "700000", "", "sh", "0000012"])
def test_to_market_symbol_rejects_unknown(symbol):
    with pytest.raises(ValueError):
        to_market_symbol(symbol)


def test_convert_xieqiu_symbol_covers_all_markets():
    assert convert_xieqiu_symbol("600000") == "SH600000"
    assert convert_xieqiu_symbol("000001") == "SZ000001"
    assert convert_xieqiu_symbol("430047") == "BJ430047"


def test_sina_historical_prefixes_symbol_by_exchange():
    provider = SinaHistorical("000001")
    with patch.object(provider, "_get_daily_plus_data", return_value=pd.DataFrame()) as mock_data:
        provider.get_hist_data()
    mock_data.assert_called_once_with("sz000001")


def test_sina_historical_keeps_explicit_index_prefix():
    provider = SinaHistorical("sh000001")
    with patch.object(provider, "_get_daily_plus_data", return_value=pd.DataFrame()) as mock_data:
        provider.get_hist_data()
    mock_data.assert_called_once_with("sh000001")


def test_sina_financial_prefixes_symbol_by_exchange():
    assert SinaFinancialReport("000001").stock == "sz000001"
    assert SinaFinancialReport("600600").stock == "sh600600"
    assert SinaFinancialReport("bj430047").stock == "bj430047"
