from abc import ABC, abstractmethod

import pandas as pd


class NewsDataProvider(ABC):
    #: Parameters that change the answer; the cache key is built from these.
    CACHE_PARAMS = ("symbol",)

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol

    @abstractmethod
    def get_news_data(self) -> pd.DataFrame:
        """Fetches news data for given symbol

        Returns:
            pd.DataFrame: the domain's declared columns, see
                :mod:`akshare_one.modules.news.schema`.
        """
        pass
