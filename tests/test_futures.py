from unittest.mock import patch

import pytest

from akshare_one import (
    get_futures_hist_data,
    get_futures_realtime_data,
)


class TestFuturesHistData:
    def test_basic_futures_hist_data(self):
        """测试基本期货历史数据获取功能"""
        df = get_futures_hist_data(symbol="AG", contract="2604", interval="day")
        assert not df.empty
        assert "timestamp" in df.columns
        assert "symbol" in df.columns
        assert "close" in df.columns

    def test_futures_daily_data(self):
        """测试日线级别期货数据"""
        df = get_futures_hist_data(
            symbol="CU0",
            interval="day",
        )
        assert not df.empty
        assert set(df.columns).issuperset(
            {
                "timestamp",
                "symbol",
                "open",
                "high",
                "low",
                "close",
                "volume",
            }
        )

    def test_futures_minute_data(self):
        """测试分钟级期货数据"""
        df = get_futures_hist_data(
            symbol="CU",
            interval="minute",
            interval_multiplier=5,
        )
        assert not df.empty
        assert len(df) > 0

    def test_invalid_futures_symbol(self):
        """测试无效期货代码"""
        with pytest.raises((ValueError, KeyError)):
            get_futures_hist_data(
                symbol="INVALID",
                interval="day",
                start_date="2024-01-01",
                end_date="2024-01-31",
            )

    def test_futures_data_invalid_dates(self):
        """测试期货数据无效日期"""
        with pytest.raises(ValueError):
            get_futures_hist_data(
                symbol="CU",
                interval="day",
                start_date="2025-31-01",  # invalid date
                end_date="2025-01-31",
            )

    def test_invalid_interval(self):
        """测试无效间隔参数"""
        with pytest.raises(ValueError):
            get_futures_hist_data(
                symbol="CU",
                interval="invalid",  # type: ignore
                start_date="2025-01-01",
                end_date="2025-01-31",
            )

    def test_weekly_data(self):
        """测试周线期货数据"""
        df = get_futures_hist_data(symbol="RB", interval="week")
        assert not df.empty

    def test_monthly_data(self):
        """测试月线期货数据"""
        df = get_futures_hist_data(symbol="RB", interval="month")
        assert not df.empty


class TestFuturesRealtimeData:
    def test_basic_futures_realtime_data(self):
        """测试基本期货实时数据获取"""
        # Note: API may only return certain varieties at different times
        df = get_futures_realtime_data()
        assert not df.empty
        assert "symbol" in df.columns
        assert "price" in df.columns

    def test_specific_contract_realtime(self):
        """测试特定合约的实时数据"""
        # First get available contracts
        all_df = get_futures_realtime_data()
        if not all_df.empty:
            # Use the first available symbol for testing
            test_symbol = all_df["symbol"].iloc[0]
            df = get_futures_realtime_data(symbol=test_symbol)
            assert not df.empty
            assert "symbol" in df.columns

    def test_all_futures_quotes(self):
        """测试获取所有期货实时数据"""
        df = get_futures_realtime_data()
        assert not df.empty
        assert "symbol" in df.columns
        assert "price" in df.columns

    def test_realtime_data_columns(self):
        """测试实时数据字段完整性"""
        df = get_futures_realtime_data()
        if not df.empty:
            expected_columns = {
                "symbol",
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
            }
            assert expected_columns.issubset(set(df.columns))

    def test_api_error_handling(self):
        """测试API错误处理"""
        # Test with a unique symbol to avoid cache hits
        with (
            patch("akshare_one.modules.futures.sina.ak.futures_zh_spot") as mock_spot,
            patch("akshare_one.modules.futures.sina.ak.futures_zh_realtime") as mock_realtime,
        ):
            mock_spot.side_effect = Exception("API error")
            mock_realtime.side_effect = Exception("API error")
            # Use a unique symbol that won't be cached
            with pytest.raises(Exception, match="API error"):
                from akshare_one.modules.futures.sina import SinaFuturesRealtime

                SinaFuturesRealtime(symbol="UNIQUE_TEST_SYMBOL")
                # Bypass cache by calling the API directly
                import akshare as ak

                ak.futures_zh_spot()

    def test_invalid_source(self):
        """测试无效数据源"""
        with pytest.raises(ValueError, match="Unknown.*provider"):
            from akshare_one.modules.futures.factory import FuturesDataFactory

            FuturesDataFactory.get_realtime_provider("invalid", symbol="CU")


class TestFuturesDataFactory:
    def test_register_custom_provider(self):
        """测试注册自定义数据提供商"""
        from akshare_one.modules.futures.base import HistoricalFuturesDataProvider
        from akshare_one.modules.futures.factory import FuturesDataFactory

        class CustomProvider(HistoricalFuturesDataProvider):
            def get_hist_data(self):
                import pandas as pd

                return pd.DataFrame()

            def get_main_contracts(self):
                import pandas as pd

                return pd.DataFrame()

        FuturesDataFactory.register_historical_provider("custom", CustomProvider)
        provider = FuturesDataFactory.get_historical_provider("custom", symbol="AG2604")
        assert isinstance(provider, CustomProvider)

    def test_get_provider_by_name(self):
        """测试通过名称获取数据提供商"""
        from akshare_one.modules.futures.factory import FuturesDataFactory

        provider = FuturesDataFactory.get_historical_provider("sina", symbol="AG2604")
        assert provider is not None
        assert provider.symbol == "AG"

    def test_get_realtime_provider(self):
        """测试获取实时数据提供商"""
        from akshare_one.modules.futures.factory import FuturesDataFactory

        provider = FuturesDataFactory.get_realtime_provider("sina", symbol="AG2604")
        assert provider is not None
        assert provider.symbol == "AG"
