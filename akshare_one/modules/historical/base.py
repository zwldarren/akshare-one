from abc import ABC, abstractmethod
import pandas as pd


def validate_hist_data(func):
    """Decorator to validate historical data returned by data providers"""

    def wrapper(*args, **kwargs):
        df = func(*args, **kwargs)

        if not isinstance(df, pd.DataFrame):
            raise ValueError("Returned data must be a pandas DataFrame")

        required_columns = {"timestamp", "open", "high", "low", "close", "volume"}
        missing_cols = required_columns - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        if "timestamp" in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
                raise ValueError("timestamp must be datetime64 dtype")
            if df["timestamp"].dt.tz is None or str(df["timestamp"].dt.tz) != "UTC":
                raise ValueError("timestamp must be in UTC timezone")

        return df

    return wrapper


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
