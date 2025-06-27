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

    def calculate_bollinger_bands(
        self, df: pd.DataFrame, window: int, std: int
    ) -> pd.DataFrame:
        close = df["close"]
        sma = close.rolling(window=window, min_periods=window).mean()
        rolling_std = close.rolling(window=window, min_periods=window).std()
        upper_band = sma + (rolling_std * std)
        lower_band = sma - (rolling_std * std)
        return pd.DataFrame(
            {"upper_band": upper_band, "middle_band": sma, "lower_band": lower_band}
        )

    def calculate_stoch(
        self, df: pd.DataFrame, window: int, smooth_d: int, smooth_k: int
    ) -> pd.DataFrame:
        high = df["high"]
        low = df["low"]
        close = df["close"]

        lowest_low = low.rolling(window=window).min()
        highest_high = high.rolling(window=window).max()

        k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        slow_k = k.rolling(window=smooth_k).mean()
        slow_d = slow_k.rolling(window=smooth_d).mean()

        return pd.DataFrame({"slow_k": slow_k, "slow_d": slow_d})

    def calculate_atr(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        high = df["high"]
        low = df["low"]
        close = df["close"]

        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        atr = tr.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
        return atr.to_frame("atr")

    def calculate_cci(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        high = df["high"]
        low = df["low"]
        close = df["close"]

        tp = (high + low + close) / 3
        tp_sma = tp.rolling(window=window, min_periods=window).mean()
        mean_dev = tp.rolling(window=window, min_periods=window).apply(
            lambda x: (x - x.mean()).abs().mean()
        )

        cci = (tp - tp_sma) / (0.015 * mean_dev)
        return cci.to_frame("cci")
