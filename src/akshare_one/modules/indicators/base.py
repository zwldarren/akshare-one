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

    @abstractmethod
    def calculate_adx(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_willr(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_ad(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_adosc(
        self, df: pd.DataFrame, fast_period: int, slow_period: int
    ) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_obv(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_mom(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_sar(
        self, df: pd.DataFrame, acceleration: float, maximum: float
    ) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_tsf(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_apo(
        self, df: pd.DataFrame, fast_period: int, slow_period: int, ma_type: int
    ) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_aroon(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_aroonosc(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_bop(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_cmo(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_dx(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_mfi(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_minus_di(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_minus_dm(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_plus_di(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_plus_dm(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_ppo(
        self, df: pd.DataFrame, fast_period: int, slow_period: int, ma_type: int
    ) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_roc(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_rocp(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_rocr(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_rocr100(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_trix(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_ultosc(
        self, df: pd.DataFrame, window1: int, window2: int, window3: int
    ) -> pd.DataFrame:
        pass
