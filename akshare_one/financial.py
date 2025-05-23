"""财务报表数据模块

包含资产负债表、利润表和现金流量表相关功能
"""

import pandas as pd
from akshare_one.modules.financial.factory import FinancialDataFactory


def get_balance_sheet(symbol: str, source: str = "sina") -> "pd.DataFrame":
    """获取资产负债表数据

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 ("sina")
    """
    if source == "sina":
        provider = FinancialDataFactory.get_provider(source, symbol=symbol)
        return provider.get_balance_sheet()
    raise ValueError(f"Unsupported data source: {source}")


def get_income_statement(symbol: str, source: str = "sina") -> "pd.DataFrame":
    """获取利润表数据

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 ("sina")
    """
    if source == "sina":
        provider = FinancialDataFactory.get_provider(source, symbol=symbol)
        return provider.get_income_statement()
    raise ValueError(f"Unsupported data source: {source}")


def get_cash_flow(symbol: str, source: str = "sina") -> "pd.DataFrame":
    """获取现金流量表数据

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 ("sina")
    """
    if source == "sina":
        provider = FinancialDataFactory.get_provider(source, symbol=symbol)
        return provider.get_cash_flow()
    raise ValueError(f"Unsupported data source: {source}")
