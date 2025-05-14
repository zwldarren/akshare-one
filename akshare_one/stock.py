"""股票市场数据模块

包含股票历史数据和实时数据相关功能
"""

from typing import Optional
import pandas as pd

from akshare_one.adapters.xueqiu import XueQiuAdapter
from .adapters import EastMoneyAdapter, SinaAdapter


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
        symbol: 股票代码 (e.g. '600000')
        interval: 时间间隔 ('minute','hour','day','week','month','year')
        interval_multiplier: 时间间隔倍数 (e.g. 5 for 5 minutes)
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        adjust: 复权类型 ('none','qfq','hfq')
        source: 数据源 ('eastmoney', 'sina')

    Returns:
        pd.DataFrame:
        - timestamp: 时间戳(UTC时区)
        - open: 开盘价
        - high: 最高价
        - low: 最低价
        - close: 收盘价
        - volume: 成交量
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
    elif source == "sina":
        return SinaAdapter().get_hist_data(
            symbol=symbol,
            interval=interval,
            interval_multiplier=interval_multiplier,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
        )
    raise ValueError(f"Unsupported data source: {source}")


def get_realtime_data(
    source: str = "xueqiu", symbol: Optional[str] = None
) -> "pd.DataFrame":
    """Get real-time market quotes

    Args:
        symbol: 股票代码 (如 "600000")
        source: 数据源 ('eastmoney', 'xueqiu')

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
    if source == "eastmoney" or symbol is None:
        return EastMoneyAdapter().get_realtime_data(symbol=symbol)
    elif source == "xueqiu":
        if not symbol:
            raise ValueError("XueQiu source requires a symbol parameter")
        return XueQiuAdapter().get_realtime_data(symbol=symbol)
    raise ValueError(f"Unsupported data source: {source}")
