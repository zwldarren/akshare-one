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

    @abstractmethod
    def calculate_bollinger_bands(
        self, df: pd.DataFrame, window: int, std: int
    ) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_stoch(
        self, df: pd.DataFrame, window: int, smooth_d: int, smooth_k: int
    ) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_atr(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_cci(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass
