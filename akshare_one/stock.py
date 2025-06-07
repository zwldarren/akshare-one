"""股票市场数据模块

包含股票历史数据和实时数据相关功能
"""

from typing import Optional
import pandas as pd

from akshare_one.modules.historical.factory import HistoricalDataFactory
from akshare_one.modules.realtime.factory import RealtimeDataFactory


def get_hist_data(
    symbol: str,
    interval: str = "day",
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
        source: 数据源 ('eastmoney', 'eastmoney_direct', 'sina') (default: 'eastmoney')

    Returns:
        pd.DataFrame:
        - timestamp: 时间戳(UTC时区)
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
    symbol: Optional[str] = None, source: str = "xueqiu"
) -> "pd.DataFrame":
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
