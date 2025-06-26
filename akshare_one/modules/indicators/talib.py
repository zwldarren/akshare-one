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
