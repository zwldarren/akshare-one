"""Akshare One - Unified interface for Chinese market data

Provides standardized access to various financial data sources with:
- Consistent symbol formats
- Unified data schemas
- Cleaned and normalized outputs

Example:
    >>> from akshare_one import get_hist_data, get_realtime_data
    >>> df = get_hist_data("600000", interval="day")
    >>> print(df.head())
    >>> # 获取单只股票实时数据
    >>> df = get_realtime_data(symbol="600000")
    >>> # 获取所有股票实时数据
    >>> df = get_realtime_data()
"""

from .stock import get_hist_data, get_realtime_data
from .news import get_news_data
from .insider import get_inner_trade_data
from .financial import get_balance_sheet, get_income_statement, get_cash_flow


__all__ = [
    "get_hist_data",
    "get_realtime_data",
    "get_news_data",
    "get_inner_trade_data",
    "get_balance_sheet",
    "get_income_statement",
    "get_cash_flow",
]
