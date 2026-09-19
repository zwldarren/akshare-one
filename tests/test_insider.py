from unittest.mock import patch

import pandas as pd
import pytest

from akshare_one import get_inner_trade_data


class TestInnerTradeData:
    @pytest.mark.network
    def test_basic_inner_trade(self):
        """测试基本内部交易数据获取功能"""
        df = get_inner_trade_data(symbol="301300")  # Use a symbol that is likely to have data
        if df.empty:
            pytest.skip("No insider trade data available for this symbol at the moment")

        required_columns = {
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
        }
        assert required_columns.issubset(df.columns)

    @pytest.mark.network
    def test_transaction_date_range(self):
        """测试交易日期范围"""
        df = get_inner_trade_data(symbol="301300")
        if df.empty:
            pytest.skip("No insider trade data available for this symbol at the moment")
        now = pd.Timestamp.now(tz="UTC")
        earliest_reasonable = pd.Timestamp("1970-01-01", tz="UTC")

        # Convert transaction dates to UTC for comparison
        transaction_dates_utc = df["transaction_date"].dt.tz_convert("UTC")

        assert all(earliest_reasonable <= ts <= now for ts in transaction_dates_utc)

    @pytest.mark.network
    def test_transaction_value_calculation(self):
        """测试交易金额计算正确性"""
        df = get_inner_trade_data(symbol="301300")
        if df.empty:
            pytest.skip("No insider trade data available for this symbol at the moment")
        sample = df.iloc[0]
        calculated_value = sample["transaction_shares"] * sample["transaction_price_per_share"]
        assert abs(sample["transaction_value"] - calculated_value) < 0.01

    def test_invalid_source(self):
        """测试无效数据源"""
        with pytest.raises(ValueError, match="Unknown insider provider"):
            get_inner_trade_data("600405", source="invalid")  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]

    def test_api_error_handling(self):
        """测试API错误处理"""
        with patch(
            "akshare_one.modules.insider.xueqiu.XueQiuInsider.get_inner_trade_data"
        ) as mock_get:
            mock_get.side_effect = Exception("API error")
            with pytest.raises(Exception, match="API error"):
                get_inner_trade_data(symbol="600405")
