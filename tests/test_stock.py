import pytest
from akshare_one import get_hist_data, get_realtime_data


class TestHistData:
    def test_basic_hist_data(self):
        """测试基本历史数据获取功能"""
        df = get_hist_data(
            symbol="600000",
            interval="day",
            start_date="2024-01-01",
            end_date="2024-01-31",
        )
        assert not df.empty
        assert set(df.columns) == {
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
        }
        assert len(df) > 0

    def test_hist_data_with_adjust(self):
        """测试复权历史数据"""
        df_qfq = get_hist_data(
            symbol="600000",
            interval="day",
            adjust="qfq",
            start_date="2024-01-01",
            end_date="2024-01-31",
        )
        df_hfq = get_hist_data(
            symbol="600000",
            interval="day",
            adjust="hfq",
            start_date="2024-01-01",
            end_date="2024-01-31",
        )
        assert not df_qfq.equals(df_hfq)

    def test_minute_hist_data(self):
        """测试新浪数据源的分钟级历史数据"""
        df = get_hist_data(
            symbol="600900",
            interval="minute",
            interval_multiplier=5,
            start_date="2025-05-01",
            end_date="2024-05-30",
            source="sina",
        )
        assert not df.empty
        assert len(df) > 0

    def test_invalid_symbol(self):
        """测试无效股票代码"""
        with pytest.raises(Exception):
            get_hist_data(
                symbol="INVALID",
                interval="day",
                start_date="2024-01-01",
                end_date="2024-01-31",
            )


class TestRealtimeData:
    def test_basic_realtime_data(self):
        """测试基本实时数据获取"""
        df = get_realtime_data(symbol="600000")
        assert not df.empty
        assert set(df.columns) == {
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
        }

    def test_all_realtime_data(self):
        """测试获取所有股票实时数据"""
        df = get_realtime_data()
        assert not df.empty
        assert "600000" in df["symbol"].values

    def test_xueqiu_source(self):
        """测试雪球数据源"""
        df = get_realtime_data(symbol="600000", source="xueqiu")
        assert not df.empty
        assert df.iloc[0]["symbol"] == "600000"

    def test_invalid_source(self):
        """测试无效数据源"""
        with pytest.raises(Exception):
            get_realtime_data(symbol="600000", source="invalid")
