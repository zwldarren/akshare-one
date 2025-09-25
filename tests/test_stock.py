from unittest.mock import patch

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
            end_date="2026-01-01",
            source="sina",
        )
        assert not df.empty
        assert len(df) > 0

    def test_hist_data_eastmoney_direct(self):
        """测试 EastMoney Direct 数据源的历史数据"""
        df = get_hist_data(
            symbol="600000",
            interval="day",
            start_date="2024-01-01",
            end_date="2024-01-31",
            source="eastmoney_direct",
        )
        assert not df.empty
        assert len(df) > 0

        df = get_hist_data(
            symbol="00700",  # 港股：腾讯
            interval="day",
            start_date="2024-01-01",
            end_date="2024-01-31",
            source="eastmoney_direct",
        )
        assert not df.empty
        assert len(df) > 0

    def test_invalid_symbol(self):
        """测试无效股票代码"""
        with pytest.raises((ValueError, KeyError)):
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

    def test_historical_data_api_error(self):
        """测试历史数据API错误处理"""
        with patch(
            "akshare_one.modules.historical.eastmoney.EastMoneyHistorical.get_hist_data"
        ) as mock_get:
            mock_get.side_effect = Exception("API error")
            with pytest.raises(Exception, match="API error"):
                get_hist_data(
                    symbol="600000",
                    interval="day",
                    start_date="2024-01-01",
                    end_date="2024-01-31",
                )

    def test_historical_data_invalid_dates(self):
        """测试历史数据无效日期"""
        with pytest.raises(ValueError):
            get_hist_data(
                symbol="600000",
                interval="day",
                start_date="2024-31-01",  # invalid date
                end_date="2024-01-31",
            )

    # def test_all_realtime_data(self):
    #     """测试获取所有股票实时数据"""
    #     df = get_realtime_data(source="eastmoney")
    #     assert not df.empty
    #     assert "600000" in df["symbol"].values

    def test_xueqiu_source(self):
        """测试雪球数据源"""
        df = get_realtime_data(symbol="600000", source="xueqiu")
        assert not df.empty
        assert df.iloc[0]["symbol"] == "600000"

    def test_eastmoney_direct_source(self):
        """测试 EastMoney Direct 实时数据源"""
        df = get_realtime_data(symbol="000001", source="eastmoney_direct")
        assert not df.empty
        assert df.iloc[0]["symbol"] == "000001"

        df = get_realtime_data(symbol="00700", source="eastmoney_direct")
        assert not df.empty
        assert df.iloc[0]["symbol"] == "00700"

    def test_invalid_source(self):
        """测试无效数据源"""
        with pytest.raises((ValueError, KeyError)):
            get_realtime_data(symbol="600000", source="invalid")

    def test_b_share_daily_data(self):
        """测试B股日线数据"""
        df = get_hist_data(
            symbol="sh900901",
            interval="day",
            start_date="2024-01-01",
            end_date="2024-01-31",
            source="sina",
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

    def test_b_share_minute_data(self):
        """测试B股分钟数据"""
        df = get_hist_data(
            symbol="sh900901",
            interval="minute",
            interval_multiplier=5,
            start_date="2024-01-01",
            end_date="2024-01-31",
            source="sina",
        )
        assert not df.empty
        assert len(df) > 0

    def test_api_error_handling(self):
        """测试API错误处理"""
        with patch(
            "akshare_one.modules.realtime.eastmoney.EastmoneyRealtime.get_current_data"
        ) as mock_get:
            mock_get.side_effect = Exception("API error")
            with pytest.raises(Exception, match="API error"):
                get_realtime_data(symbol="600000", source="eastmoney")
