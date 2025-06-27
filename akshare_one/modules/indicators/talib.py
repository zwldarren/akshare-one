import talib
import pandas as pd
from .base import BaseIndicatorCalculator


class TalibIndicatorCalculator(BaseIndicatorCalculator):
    """TA-Lib based indicator implementations"""

    def calculate_sma(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        close = df["close"].values
        sma = talib.SMA(close, timeperiod=window)
        return pd.DataFrame({"sma": sma}, index=df.index)

    def calculate_ema(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        close = df["close"].values
        ema = talib.EMA(close, timeperiod=window)
        return pd.DataFrame({"ema": ema}, index=df.index)

    def calculate_rsi(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        close = df["close"].values
        rsi = talib.RSI(close, timeperiod=window)
        return pd.DataFrame({"rsi": rsi}, index=df.index)

    def calculate_macd(
        self, df: pd.DataFrame, fast: int, slow: int, signal: int
    ) -> pd.DataFrame:
        close = df["close"].values
        macd, signal_line, histogram = talib.MACD(
            close, fastperiod=fast, slowperiod=slow, signalperiod=signal
        )
        return pd.DataFrame(
            {"macd": macd, "signal": signal_line, "histogram": histogram},
            index=df.index,
        )

    def calculate_bollinger_bands(
        self, df: pd.DataFrame, window: int, std: int
    ) -> pd.DataFrame:
        close = df["close"].values
        upper, middle, lower = talib.BBANDS(
            close, timeperiod=window, nbdevup=std, nbdevdn=std, matype=talib.MA_Type.SMA
        )
        return pd.DataFrame(
            {"upper_band": upper, "middle_band": middle, "lower_band": lower},
            index=df.index,
        )

    def calculate_stoch(
        self, df: pd.DataFrame, window: int, smooth_d: int, smooth_k: int
    ) -> pd.DataFrame:
        high = df["high"].values
        low = df["low"].values
        close = df["close"].values
        slow_k, slow_d = talib.STOCH(
            high,
            low,
            close,
            fastk_period=window,
            slowk_period=smooth_k,
            slowk_matype=talib.MA_Type.SMA,
            slowd_period=smooth_d,
            slowd_matype=talib.MA_Type.SMA,
        )
        return pd.DataFrame({"slow_k": slow_k, "slow_d": slow_d}, index=df.index)

    def calculate_atr(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        high = df["high"].values
        low = df["low"].values
        close = df["close"].values
        atr = talib.ATR(high, low, close, timeperiod=window)
        return pd.DataFrame({"atr": atr}, index=df.index)

    def calculate_cci(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        high = df["high"].values
        low = df["low"].values
        close = df["close"].values
        cci = talib.CCI(high, low, close, timeperiod=window)
        return pd.DataFrame({"cci": cci}, index=df.index)
