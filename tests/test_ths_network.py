"""Live tests for the Tonghuashun source.

These call the real endpoints, so they are marked ``network`` and skipped
unless ``--run-network`` is passed (see ``tests/conftest.py``). The host
serves one security per request and rate-limits, so the calls are few and
the ranges are short.
"""

from __future__ import annotations

import pandas as pd
import pytest

from akshare_one import (
    get_basic_info,
    get_hist_data,
    get_news_data,
    get_realtime_data,
)
from akshare_one.modules.historical.schema import COLUMNS as HISTORICAL_COLUMNS
from akshare_one.modules.info.schema import COLUMNS as INFO_COLUMNS
from akshare_one.modules.news.schema import COLUMNS as NEWS_COLUMNS
from akshare_one.modules.realtime.schema import COLUMNS as REALTIME_COLUMNS


class TestHistorical:
    @pytest.mark.network
    def test_daily_data(self) -> None:
        df = get_hist_data(
            symbol="600519",
            interval="day",
            start_date="2024-01-01",
            end_date="2024-03-31",
            source="ths",
        )

        assert not df.empty
        assert tuple(df.columns) == HISTORICAL_COLUMNS
        assert df["timestamp"].is_monotonic_increasing
        assert (df["high"] >= df["low"]).all()

    @pytest.mark.network
    def test_adjusted_data_differs(self) -> None:
        unadjusted = get_hist_data(
            symbol="600519",
            interval="day",
            start_date="2024-01-01",
            end_date="2024-03-31",
            source="ths",
        )
        adjusted = get_hist_data(
            symbol="600519",
            interval="day",
            adjust="hfq",
            start_date="2024-01-01",
            end_date="2024-03-31",
            source="ths",
        )

        assert not unadjusted.empty
        assert not adjusted.empty
        assert not unadjusted["close"].equals(adjusted["close"])

    @pytest.mark.network
    def test_weekly_data(self) -> None:
        df = get_hist_data(
            symbol="600519",
            interval="week",
            start_date="2024-01-01",
            end_date="2024-12-31",
            source="ths",
        )

        assert not df.empty
        assert tuple(df.columns) == HISTORICAL_COLUMNS

    @pytest.mark.network
    def test_minute_data(self) -> None:
        # The host serves a short window of intraday bars, so the test asks
        # for the series rather than for a range that may fall outside it.
        df = get_hist_data(
            symbol="600519",
            interval="minute",
            interval_multiplier=30,
            source="ths",
        )

        assert not df.empty
        assert tuple(df.columns) == HISTORICAL_COLUMNS

    @pytest.mark.network
    def test_index_data(self) -> None:
        df = get_hist_data(
            symbol="1A0001",
            interval="day",
            start_date="2024-01-01",
            end_date="2024-03-31",
            source="ths",
        )

        assert not df.empty
        assert tuple(df.columns) == HISTORICAL_COLUMNS


class TestRealtime:
    @pytest.mark.network
    def test_snapshot(self) -> None:
        df = get_realtime_data(symbol="600519", source="ths")

        assert not df.empty
        assert tuple(df.columns) == REALTIME_COLUMNS
        assert df.iloc[0]["symbol"] == "600519"
        assert df.iloc[0]["price"] > 0


class TestNews:
    @pytest.mark.network
    def test_timeline(self) -> None:
        df = get_news_data(symbol="600519", source="ths")

        assert not df.empty
        assert tuple(df.columns) == NEWS_COLUMNS
        assert df["title"].notna().all()
        assert df["url"].str.startswith("http").all()
        assert isinstance(df.iloc[0]["publish_time"], pd.Timestamp)


class TestInfo:
    @pytest.mark.network
    def test_basic_info(self) -> None:
        df = get_basic_info(symbol="600519", source="ths")

        assert not df.empty
        assert tuple(df.columns) == INFO_COLUMNS
        assert df.iloc[0]["name"] == "贵州茅台"
        assert df.iloc[0]["listing_date"] == pd.Timestamp("2001-08-27")
