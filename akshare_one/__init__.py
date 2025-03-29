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

from typing import Optional
import pandas as pd
from .adapters import EastMoneyAdapter


def get_hist_data(
    symbol: str,
    interval: str,
    interval_multiplier: int = 1,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    adjust: str = "none",
    source: str = "eastmoney",
) -> "pd.DataFrame":
    """Get historical market data

    Args:
        symbol: Unified symbol format (e.g. '600000')
        interval: Time granularity ('second','minute','hour','day','week','month','year')
        interval_multiplier: Interval multiplier (e.g. 5 for 5 minutes)
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        adjust: Adjustment type ('none','qfq','hfq')
        source: Data source ('eastmoney')

    Returns:
        Standardized DataFrame with OHLCV data
    """
    if source == "eastmoney":
        return EastMoneyAdapter().get_hist_data(
            symbol=symbol,
            interval=interval,
            interval_multiplier=interval_multiplier,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
        )
    raise ValueError(f"Unsupported data source: {source}")


def get_realtime_data(
    source: str = "eastmoney", symbol: Optional[str] = None
) -> "pd.DataFrame":
    """Get real-time market quotes

    Returns:
        DataFrame:
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
    if source == "eastmoney":
        return EastMoneyAdapter().get_realtime_data(symbol=symbol)
    raise ValueError(f"Unsupported data source: {source}")


def get_news_data(symbol: str, source: str = "eastmoney") -> "pd.DataFrame":
    """获取个股新闻数据

    Args:
        symbol: 股票代码 (如 "300059")
        source: 数据源 (目前仅支持 "eastmoney")

    Returns:
        DataFrame 包含:
        - keyword: 关键词
        - title: 新闻标题
        - content: 新闻内容
        - publish_time: 发布时间
        - source: 文章来源
        - url: 新闻链接
    """
    if source == "eastmoney":
        return EastMoneyAdapter().get_news_data(symbol=symbol)
    raise ValueError(f"Unsupported data source: {source}")
