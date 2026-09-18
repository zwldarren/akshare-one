from abc import ABC, abstractmethod

import pandas as pd


class RealtimeDataProvider(ABC):
    #: Parameters that change the answer; the cache key is built from these.
    CACHE_PARAMS = ("symbol",)

    def __init__(self, symbol: str | None) -> None:
        """``None`` means "no symbol filter" and is normalized to an empty string."""
        if symbol is None:
            symbol = ""
        elif not isinstance(symbol, str):
            raise ValueError("symbol must be a string")
        self.symbol = symbol

    @abstractmethod
    def get_current_data(self) -> pd.DataFrame:
        """Fetches realtime market data

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
        pass
