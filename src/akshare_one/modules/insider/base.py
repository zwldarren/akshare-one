from abc import ABC, abstractmethod

import pandas as pd


class InsiderDataProvider(ABC):
    #: Parameters that change the answer; the cache key is built from these.
    CACHE_PARAMS = ("symbol",)

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol

    @abstractmethod
    def get_inner_trade_data(self) -> pd.DataFrame:
        """Fetches insider trade data

        Returns:
            pd.DataFrame: the domain's declared columns, see
                :mod:`akshare_one.modules.insider.schema`.
        """
        pass
