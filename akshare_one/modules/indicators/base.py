from abc import ABC, abstractmethod
import pandas as pd


class BaseIndicatorCalculator(ABC):
    """Base class for indicator calculators"""

    @abstractmethod
    def calculate_sma(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_ema(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_rsi(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_macd(
        self, df: pd.DataFrame, fast: int, slow: int, signal: int
    ) -> pd.DataFrame:
        pass
