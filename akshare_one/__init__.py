"""Akshare One - Unified interface for Chinese market data

Provides standardized access to various financial data sources with:
- Consistent symbol formats
- Unified data schemas
- Cleaned and normalized outputs

Example:
    >>> from akshare_one import get_hist_data
    >>> df = get_hist_data("600000", interval="day")
    >>> print(df.head())
"""

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
