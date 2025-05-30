import pytest
from akshare_one import get_inner_trade_data
from datetime import datetime, timedelta, timezone


class TestInnerTradeData:
    def test_basic_inner_trade(self):
        """测试基本内部交易数据获取功能"""
        df = get_inner_trade_data(symbol="600405")
        assert not df.empty
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

    def test_transaction_date_range(self):
        """测试交易日期范围"""
        df = get_inner_trade_data(symbol="600405")
        now = datetime.now(timezone.utc)
        one_year_ago = now - timedelta(days=365)

        # 验证交易日期在合理范围内
        assert all(one_year_ago <= ts <= now for ts in df["transaction_date"])

    def test_transaction_value_calculation(self):
        """测试交易金额计算正确性"""
        df = get_inner_trade_data(symbol="600405")
        sample = df.iloc[0]
        calculated_value = (
            sample["transaction_shares"] * sample["transaction_price_per_share"]
        )
        assert abs(sample["transaction_value"] - calculated_value) < 0.01

    def test_invalid_source(self):
        """测试无效数据源"""
        with pytest.raises(Exception):
            get_inner_trade_data("600405", source="invalid")
