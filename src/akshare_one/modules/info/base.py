from abc import ABC, abstractmethod

import pandas as pd


class InfoDataProvider(ABC):
    #: Parameters that change the answer; the cache key is built from these.
    CACHE_PARAMS = ("symbol",)

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol

    @abstractmethod
    def get_basic_info(self) -> pd.DataFrame:
        """Fetches stock basic info data

        Returns:
            pd.DataFrame: the domain's declared columns, see
                :mod:`akshare_one.modules.info.schema`.
        """
        pass
