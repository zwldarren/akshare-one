from abc import ABC, abstractmethod
import pandas as pd


class HistoricalDataProvider(ABC):
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
        self.interval = interval
        self.interval_multiplier = interval_multiplier
        self.start_date = start_date
        self.end_date = end_date
        self.adjust = adjust

    @classmethod
    def get_supported_intervals(cls):
        return ["minute", "hour", "day", "week", "month", "year"]

    @abstractmethod
    def get_hist_data(self) -> pd.DataFrame:
        """Fetches historical market data

        Returns:
            pd.DataFrame:
            - timestamp (UTC)
            - open
            - high
            - low
            - close
            - volume
        """
        pass
