import pandas as pd
from .base import BaseIndicatorCalculator


class SimpleIndicatorCalculator(BaseIndicatorCalculator):
    """Basic pandas-based indicator implementations"""

    def calculate_sma(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        return (
            df["close"]
            .rolling(window=window, min_periods=window)
            .mean()
            .to_frame("sma")
        )

    def calculate_ema(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        return (
            df["close"]
            .ewm(span=window, adjust=False, min_periods=window)
            .mean()
            .to_frame("ema")
        )

    def calculate_rsi(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        delta = df["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi.clip(0, 100).to_frame("rsi")

    def calculate_macd(
        self, df: pd.DataFrame, fast: int, slow: int, signal: int
    ) -> pd.DataFrame:
        close = df["close"]
        ema_fast = close.ewm(span=fast, adjust=False, min_periods=fast).mean()
        ema_slow = close.ewm(span=slow, adjust=False, min_periods=slow).mean()

        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(
            span=signal, adjust=False, min_periods=signal
        ).mean()

        return pd.DataFrame(
            {
                "macd": macd_line,
                "signal": signal_line,
                "histogram": macd_line - signal_line,
            }
        )
