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
            pd.DataFrame: the domain's declared columns, see
                :mod:`akshare_one.modules.realtime.schema`.
        """
        pass
