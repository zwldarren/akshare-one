"""Akshare One - Unified interface for Chinese market data

Provides standardized access to various financial data sources with:
- Consistent symbol formats
- Unified data schemas
- Cleaned and normalized outputs

Example:
    >>> from akshare_one import get_hist_data, get_realtime_data
    >>> # 获取股票历史数据
    >>> df = get_hist_data("600000", interval="day")
    >>> print(df.head())
    >>> # 获取股票实时数据
    >>> df = get_realtime_data(symbol="600000")
"""

from typing import Literal

import pandas as pd

from .modules.financial.factory import FinancialDataFactory
from .modules.historical.factory import HistoricalDataFactory
from .modules.info.factory import InfoDataFactory
from .modules.insider.factory import InsiderDataFactory
from .modules.news.factory import NewsDataFactory
from .modules.realtime.factory import RealtimeDataFactory


def get_basic_info(
    symbol: str, source: Literal["eastmoney"] = "eastmoney"
) -> pd.DataFrame:
    """获取股票基础信息

    Args:
        symbol: 股票代码 (e.g. '600000')
        source: 数据源 ('eastmoney')

    Returns:
        pd.DataFrame:
        - price: 最新价
        - symbol: 股票代码
        - name: 股票简称
        - total_shares: 总股本
        - float_shares: 流通股
        - total_market_cap: 总市值
        - float_market_cap: 流通市值
        - industry: 行业
        - listing_date: 上市时间
    """
    provider = InfoDataFactory.get_provider(source, symbol=symbol)
    return provider.get_basic_info()


def get_hist_data(
    symbol: str,
    interval: Literal["minute", "hour", "day", "week", "month", "year"] = "day",
    interval_multiplier: int = 1,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    adjust: Literal["none", "qfq", "hfq"] = "none",
    source: Literal["eastmoney", "eastmoney_direct", "sina"] = "eastmoney",
) -> pd.DataFrame:
    """Get historical market data

    Args:
        symbol: 股票代码 (e.g. '600000')
        interval: 时间间隔 ('minute','hour','day','week','month','year')
        interval_multiplier: 时间间隔倍数 (e.g. 5 for 5 minutes)
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        adjust: 复权类型 ('none','qfq','hfq')
        source: 数据源 ('eastmoney', 'eastmoney_direct', 'sina') (default: 'eastmoney')

    Returns:
        pd.DataFrame:
        - timestamp: 时间戳
        - open: 开盘价
        - high: 最高价
        - low: 最低价
        - close: 收盘价
        - volume: 成交量
    """
    kwargs = {
        "symbol": symbol,
        "interval": interval,
        "interval_multiplier": interval_multiplier,
        "start_date": start_date,
        "end_date": end_date,
        "adjust": adjust,
    }
    provider = HistoricalDataFactory.get_provider(source, **kwargs)
    return provider.get_hist_data()


def get_realtime_data(
    symbol: str | None = None,
    source: Literal["eastmoney", "eastmoney_direct", "xueqiu"] = "eastmoney_direct",
) -> pd.DataFrame:
    """Get real-time market quotes

    Args:
        symbol: 股票代码 (如 "600000")
        source: 数据源 ('eastmoney', 'eastmoney_direct', 'xueqiu')

    Returns:
        pd.DataFrame:
        - symbol: 股票代码
        - price: 最新价
        - change: 涨跌额
        - pct_change: 涨跌幅(%)
        - timestamp: 时间戳
        - volume: 成交量(手)
        - amount: 成交额(元)
        - open: 今开
        - high: 最高
        - low: 最低
        - prev_close: 昨收
    """
    provider = RealtimeDataFactory.get_provider(source, symbol=symbol)
    return provider.get_current_data()


def get_news_data(
    symbol: str, source: Literal["eastmoney"] = "eastmoney"
) -> pd.DataFrame:
    """获取个股新闻数据

    Args:
        symbol: 股票代码 (如 "300059")
        source: 数据源 ('eastmoney')

    Returns:
        pd.DataFrame:
        - keyword: 关键词
        - title: 新闻标题
        - content: 新闻内容
        - publish_time: 发布时间
        - source: 文章来源
        - url: 新闻链接
    """
    provider = NewsDataFactory.get_provider(source, symbol=symbol)
    return provider.get_news_data()


def get_balance_sheet(symbol: str, source: Literal["sina"] = "sina") -> pd.DataFrame:
    """获取资产负债表数据

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 ("sina")

    Returns:
        pd.DataFrame: 资产负债表数据
    """
    provider = FinancialDataFactory.get_provider(source, symbol=symbol)
    return provider.get_balance_sheet()


def get_income_statement(symbol: str, source: Literal["sina"] = "sina") -> pd.DataFrame:
    """获取利润表数据

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 ("sina")

    Returns:
        pd.DataFrame: 利润表数据
    """
    provider = FinancialDataFactory.get_provider(source, symbol=symbol)
    return provider.get_income_statement()


def get_cash_flow(symbol: str, source: Literal["sina"] = "sina") -> pd.DataFrame:
    """获取现金流量表数据

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 ("sina")

    Returns:
        pd.DataFrame: 现金流量表数据
    """
    provider = FinancialDataFactory.get_provider(source, symbol=symbol)
    return provider.get_cash_flow()


def get_financial_metrics(
    symbol: str, source: Literal["eastmoney_direct"] = "eastmoney_direct"
) -> pd.DataFrame:
    """获取三大财务报表关键指标

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 ('eastmoney_direct')

    Returns:
        pd.DataFrame: 财务关键指标数据
    """
    provider = FinancialDataFactory.get_provider(source, symbol=symbol)
    return provider.get_financial_metrics()


def get_inner_trade_data(
    symbol: str, source: Literal["xueqiu"] = "xueqiu"
) -> pd.DataFrame:
    """获取雪球内部交易数据

    Args:
        symbol: 股票代码，如"600000"
        source: 数据源 (目前支持 "xueqiu")

    Returns:
        pd.DataFrame: 内部交易数据
    """
    provider = InsiderDataFactory.get_provider(source, symbol=symbol)
    return provider.get_inner_trade_data()
