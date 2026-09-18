from abc import ABC, abstractmethod

import pandas as pd


class HistoricalDataProvider(ABC):
    #: Parameters that change the answer; the cache key is built from these.
    CACHE_PARAMS = ("symbol", "interval", "interval_multiplier", "start_date", "end_date", "adjust")

    def __init__(
        self,
        symbol: str,
        interval: str = "day",
        interval_multiplier: int = 1,
        start_date: str = "1970-01-01",
        end_date: str = "2030-12-31",
        adjust: str = "none",
    ) -> None:
        self.symbol = symbol
        self.interval = interval.lower()
        self.interval_multiplier = interval_multiplier
        self.start_date = start_date
        self.end_date = end_date
        self.adjust = adjust
        self._validate_dates()

    def _validate_dates(self) -> None:
        try:
            pd.to_datetime(self.start_date)
            pd.to_datetime(self.end_date)
        except ValueError:
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.") from None

    @classmethod
    def get_supported_intervals(cls) -> list[str]:
        return ["minute", "hour", "day", "week", "month", "year"]

    @abstractmethod
    def get_hist_data(self) -> pd.DataFrame:
        """Fetches historical market data

        Returns:
            pd.DataFrame: the domain's declared columns, see
                :mod:`akshare_one.modules.historical.schema`.
        """
        pass
