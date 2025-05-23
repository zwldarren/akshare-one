from abc import ABC, abstractmethod
import pandas as pd


def validate_realtime_data(func):
    """Decorator to validate realtime data returned by data providers"""

    def wrapper(*args, **kwargs):
        df = func(*args, **kwargs)

        if not isinstance(df, pd.DataFrame):
            raise ValueError("Returned data must be a pandas DataFrame")

        # At least one of these core fields must be present
        core_fields = {"timestamp", "price", "volume"}
        if not core_fields & set(df.columns):
            raise ValueError(f"Must contain at least one of: {core_fields}")

        # Validate timestamp if present
        if "timestamp" in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
                raise ValueError("timestamp must be datetime64 dtype")
            if df["timestamp"].dt.tz is None or str(df["timestamp"].dt.tz) != "UTC":
                raise ValueError("timestamp must be in UTC timezone")

        # Validate numeric fields if present
        numeric_fields = {
            "price",
            "change",
            "pct_change",
            "open",
            "high",
            "low",
            "prev_close",
            "amount",
        }
        for field in numeric_fields & set(df.columns):
            if not pd.api.types.is_numeric_dtype(df[field]):
                raise ValueError(f"{field} must be numeric")

        return df

    return wrapper


class RealtimeDataProvider(ABC):
    def __init__(self, symbol: str) -> None:
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
