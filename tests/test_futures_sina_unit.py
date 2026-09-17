"""Offline regression tests for the Sina futures adapters.

These tests mock the upstream akshare calls, so they never touch the network.
They cover bugs that made whole features silently return empty frames:

- ``get_hist_data`` filtered on a ``RangeIndex`` converted to 1970 timestamps.
- ``get_current_data`` never told ``futures_zh_spot`` which contract to fetch.
- ``_clean_spot_data`` did not know the ``current_price``/``hold`` layout.
- ``get_main_contracts`` looked for a ``symbol`` column that does not exist.
"""

from contextlib import ExitStack
from unittest.mock import patch

import pandas as pd
import pytest

from akshare_one.modules.futures.sina import (
    SinaFuturesHistorical,
    SinaFuturesRealtime,
    _main_contract_table,
)


@pytest.fixture(autouse=True)
def _disable_cache(monkeypatch):
    monkeypatch.setenv("AKSHARE_ONE_CACHE_ENABLED", "false")
    _main_contract_table.cache_clear()
    yield
    _main_contract_table.cache_clear()


def _daily_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2026-08-01", "2026-08-04", "2026-09-11"],
            "open": [1.0, 2.0, 3.0],
            "high": [1.0, 2.0, 3.0],
            "low": [1.0, 2.0, 3.0],
            "close": [1.0, 2.0, 3.0],
            "volume": [10, 20, 30],
            "hold": [1, 2, 3],
            "settle": [1.0, 2.0, 3.0],
        }
    )


def _spot_frame(name: str = "棉花连续") -> pd.DataFrame:
    return pd.DataFrame(
        {
            "symbol": [name],
            "time": ["150000"],
            "open": [16045.0],
            "high": [16060.0],
            "low": [15770.0],
            "current_price": [15830.0],
            "bid_price": [15825.0],
            "ask_price": [15830.0],
            "buy_vol": [224],
            "sell_vol": [229],
            "hold": [547406.0],
            "volume": [397458],
            "avg_price": [15885.0],
            "last_close": [15830.0],
            "last_settle_price": [16005.0],
        }
    )


class TestHistoricalDateFilter:
    def test_daily_filter_uses_date_column(self):
        provider = SinaFuturesHistorical(
            symbol="AG0",
            interval="day",
            start_date="2026-08-01",
            end_date="2026-09-10",
        )
        with patch(
            "akshare_one.modules.futures.sina.ak.futures_zh_daily_sina",
            return_value=_daily_frame(),
        ):
            df = provider.get_hist_data()

        # 09-11 must be excluded; 08-01/08-04 kept.
        assert len(df) == 2
        assert list(df["close"]) == [1.0, 2.0]

    def test_default_range_keeps_history(self):
        provider = SinaFuturesHistorical(symbol="AG0", interval="day")
        with patch(
            "akshare_one.modules.futures.sina.ak.futures_zh_daily_sina",
            return_value=_daily_frame(),
        ):
            df = provider.get_hist_data()
        assert len(df) == 3


class TestRealtimeSpot:
    def test_get_current_data_subscribes_to_requested_contract(self):
        provider = SinaFuturesRealtime(symbol="CF")
        with patch(
            "akshare_one.modules.futures.sina.ak.futures_zh_spot",
            return_value=_spot_frame(),
        ) as mock_spot:
            result = provider.get_current_data()

        assert mock_spot.call_args.kwargs["symbol"] == "CF0"
        assert mock_spot.call_args.kwargs["market"] == "CF"

        assert len(result) == 1
        row = result.iloc[0]
        assert row["symbol"] == "CF0"
        assert row["symbol_root"] == "CF"
        assert row["contract"] == "0"
        assert row["price"] == 15830.0
        assert row["open_interest"] == 547406.0
        assert row["prev_settlement"] == 16005.0
        assert row["change"] == pytest.approx(-175.0)
        assert row["pct_change"] == pytest.approx(-1.09, abs=0.01)

    def test_specific_contract_uses_full_code(self):
        provider = SinaFuturesRealtime(symbol="AG2604")
        with patch(
            "akshare_one.modules.futures.sina.ak.futures_zh_spot",
            return_value=_spot_frame("白银2604"),
        ) as mock_spot:
            result = provider.get_current_data()

        assert mock_spot.call_args.kwargs["symbol"] == "AG2604"
        assert result.iloc[0]["symbol"] == "AG2604"
        assert result.iloc[0]["contract"] == "2604"

    def test_cffex_uses_financial_layout(self):
        provider = SinaFuturesRealtime(symbol="IF")
        with patch(
            "akshare_one.modules.futures.sina.ak.futures_zh_spot",
            return_value=_spot_frame("沪深300指数期货连续"),
        ) as mock_spot:
            provider.get_current_data()

        assert mock_spot.call_args.kwargs["market"] == "FF"


class TestAllQuotes:
    def test_get_all_quotes_maps_names_back_to_codes(self):
        table = pd.DataFrame(
            {
                "symbol": ["CF0", "AG0", "IF0"],
                "exchange": ["czce", "shfe", "cffex"],
                "name": ["棉花连续", "白银连续", "沪深300指数期货连续"],
            }
        )
        spot = pd.concat([_spot_frame("棉花连续"), _spot_frame("白银连续")], ignore_index=True)
        with (
            patch(
                "akshare_one.modules.futures.sina.ak.futures_display_main_sina",
                return_value=table,
            ),
            patch(
                "akshare_one.modules.futures.sina.ak.futures_zh_spot",
                return_value=spot,
            ) as mock_spot,
        ):
            provider = SinaFuturesRealtime()
            result = provider.get_all_quotes()

        # CFFEX variety must not be part of the commodity batch request.
        assert "IF0" not in mock_spot.call_args.kwargs["symbol"]
        assert "CF0" in mock_spot.call_args.kwargs["symbol"]
        assert list(result["symbol"]) == ["CF0", "AG0"]


class TestMainContracts:
    def _patch_exchanges(self, frames):
        patches = []
        for name, frame in frames.items():
            patches.append(
                patch(
                    f"akshare_one.modules.futures.sina.ak.futures_contract_info_{name}",
                    return_value=frame,
                )
            )
        return patches

    def test_reads_chinese_contract_code_columns(self):
        frames = {
            "shfe": pd.DataFrame({"合约代码": ["CU2601", "AG2602"]}),
            "dce": pd.DataFrame({"合约": ["M2601", "I2605"]}),
            "czce": pd.DataFrame({"合约代码": ["CF601", "TA601"]}),
            "cffex": pd.DataFrame({"合约代码": ["IF2601"]}),
        }
        started = self._patch_exchanges(frames)
        with ExitStack() as stack:
            for p in started:
                stack.enter_context(p)
            result = SinaFuturesHistorical(symbol="").get_main_contracts()

        assert set(result["symbol"]) == {"CU", "AG", "M", "I", "CF", "TA", "IF"}
        assert set(result["exchange"]) == {"SHFE", "DCE", "CZCE", "CFFEX"}
        assert result["contract"].tolist() == result["symbol"].tolist()

    def test_empty_when_every_exchange_fails(self):
        started = [
            patch(
                "akshare_one.modules.futures.sina.ak.futures_contract_info_shfe",
                side_effect=RuntimeError("boom"),
            ),
            patch(
                "akshare_one.modules.futures.sina.ak.futures_contract_info_dce",
                side_effect=RuntimeError("boom"),
            ),
            patch(
                "akshare_one.modules.futures.sina.ak.futures_contract_info_czce",
                side_effect=RuntimeError("boom"),
            ),
            patch(
                "akshare_one.modules.futures.sina.ak.futures_contract_info_cffex",
                side_effect=RuntimeError("boom"),
            ),
        ]
        with ExitStack() as stack:
            for p in started:
                stack.enter_context(p)
            result = SinaFuturesHistorical(symbol="").get_main_contracts()

        assert result.empty
        assert list(result.columns) == ["symbol", "name", "contract", "exchange"]
