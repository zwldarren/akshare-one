from abc import ABC, abstractmethod

import pandas as pd


class InfoDataProvider(ABC):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol

    @abstractmethod
    def get_basic_info(self) -> pd.DataFrame:
        """Fetches stock basic info data

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
        pass
