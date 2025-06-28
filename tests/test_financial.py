import pytest
from akshare_one import get_balance_sheet, get_income_statement, get_cash_flow


class TestBalanceSheet:
    def test_basic_balance_sheet(self):
        """测试基本资产负债表获取功能"""
        df = get_balance_sheet(symbol="600600")
        assert not df.empty
        required_columns = {
            "report_date",
            "currency",
            "total_assets",
            "current_assets",
            "cash_and_equivalents",
            "total_liabilities",
            "current_liabilities",
            "shareholders_equity",
        }
        assert required_columns.issubset(df.columns)

    def test_invalid_symbol(self):
        """测试无效股票代码"""
        with pytest.raises(Exception):
            get_balance_sheet(symbol="INVALID")


class TestIncomeStatement:
    def test_basic_income_statement(self):
        """测试基本利润表获取功能"""
        df = get_income_statement(symbol="600600")
        assert not df.empty
        required_columns = {
            "report_date",
            "currency",
            "revenue",
            "cost_of_revenue",
            "operating_profit",
            "net_income",
            "earnings_per_share",
        }
        assert required_columns.issubset(df.columns)

    def test_multiple_periods(self):
        """测试多期数据获取"""
        df = get_income_statement(symbol="600600")
        assert len(df) >= 4  # 至少包含4个季度数据


class TestCashFlow:
    def test_basic_cash_flow(self):
        """测试基本现金流量表获取功能"""
        df = get_cash_flow(symbol="600600")
        assert not df.empty
        required_columns = {
            "report_date",
            "report_type",
            "currency",
            "net_cash_flow_from_operations",
            "net_cash_flow_from_investing",
            "net_cash_flow_from_financing",
            "ending_cash_balance",
        }
        assert required_columns.issubset(df.columns)

    def test_unsupported_source(self):
        """测试不支持的来源"""
        with pytest.raises(ValueError):
            get_balance_sheet(symbol="600600", source="invalid")
        with pytest.raises(ValueError):
            get_income_statement(symbol="600600", source="invalid")
        with pytest.raises(ValueError):
            get_cash_flow(symbol="600600", source="invalid")
