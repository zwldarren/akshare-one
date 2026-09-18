import pytest

from akshare_one import (
    get_futures_hist_data,
    get_futures_realtime_data,
)


class TestFuturesHistData:
    @pytest.mark.network
    def test_basic_futures_hist_data(self):
        """测试基本期货历史数据获取功能"""
        df = get_futures_hist_data(symbol="AG", contract="2604", interval="day")
        assert not df.empty
        assert "timestamp" in df.columns
        assert "symbol" in df.columns
        assert "close" in df.columns

    @pytest.mark.network
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

    @pytest.mark.network
    def test_futures_minute_data(self):
        """测试分钟级期货数据"""
        df = get_futures_hist_data(
            symbol="CU",
            interval="minute",
            interval_multiplier=5,
        )
        assert not df.empty
        assert len(df) > 0

    @pytest.mark.network
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

    @pytest.mark.network
    def test_weekly_data(self):
        """测试周线期货数据"""
        df = get_futures_hist_data(symbol="RB", interval="week")
        assert not df.empty

    @pytest.mark.network
    def test_monthly_data(self):
        """测试月线期货数据"""
        df = get_futures_hist_data(symbol="RB", interval="month")
        assert not df.empty


class TestFuturesRealtimeData:
    @pytest.mark.network
    def test_basic_futures_realtime_data(self):
        """测试基本期货实时数据获取"""
        # Note: API may only return certain varieties at different times
        df = get_futures_realtime_data()
        assert not df.empty
        assert "symbol" in df.columns
        assert "price" in df.columns

    @pytest.mark.network
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

    @pytest.mark.network
    def test_all_futures_quotes(self):
        """测试获取所有期货实时数据"""
        df = get_futures_realtime_data()
        assert not df.empty
        assert "symbol" in df.columns
        assert "price" in df.columns

    @pytest.mark.network
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

    def test_invalid_source(self):
        """测试无效数据源"""
        with pytest.raises(ValueError, match="Unknown futures provider"):
            get_futures_realtime_data(symbol="CU", source="invalid")  # type: ignore[arg-type]
