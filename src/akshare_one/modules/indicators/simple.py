import numpy as np
import pandas as pd

from .base import BaseIndicatorCalculator


class SimpleIndicatorCalculator(BaseIndicatorCalculator):
    """Basic pandas-based indicator implementations"""

    def _get_ma(self, series: pd.Series, window: int, ma_type: int) -> pd.Series:
        if ma_type == 0:
            return series.rolling(window=window, min_periods=window).mean()
        elif ma_type == 1:
            return series.ewm(span=window, adjust=False, min_periods=window).mean()
        else:
            raise ValueError(
                f"Unsupported ma_type: {ma_type} in simple calculator. "
                f"Only SMA (0) and EMA (1) are supported."
            )

    def _wilder_smooth(self, series: pd.Series, window: int) -> pd.Series:
        return series.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()

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

        k = 100 * (close - lowest_low) / (highest_high - lowest_low).replace(0, np.nan)
        slow_k = k.rolling(window=smooth_k, min_periods=smooth_k).mean()
        slow_d = slow_k.rolling(window=smooth_d, min_periods=smooth_d).mean()

        return pd.DataFrame({"slow_k": slow_k, "slow_d": slow_d})

    def calculate_atr(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        high = df["high"]
        low = df["low"]
        close = df["close"]

        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        atr = self._wilder_smooth(tr, window)
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

    def calculate_adx(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        dx = self.calculate_dx(df, window)["dx"]
        adx = self._wilder_smooth(dx, window)
        return adx.to_frame("adx")

    def calculate_willr(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        high = df["high"]
        low = df["low"]
        close = df["close"]
        highest_high = high.rolling(window=window, min_periods=window).max()
        lowest_low = low.rolling(window=window, min_periods=window).min()
        willr = -100 * (highest_high - close) / (highest_high - lowest_low)
        return willr.to_frame("willr")

    def calculate_ad(self, df: pd.DataFrame) -> pd.DataFrame:
        high = df["high"]
        low = df["low"]
        close = df["close"]
        volume = df["volume"]
        mfm = ((close - low) - (high - close)) / (high - low).replace(0, np.nan)
        mfm = mfm.fillna(0)
        mfv = mfm * volume
        ad = mfv.cumsum()
        return ad.to_frame("ad")

    def calculate_adosc(
        self, df: pd.DataFrame, fast_period: int, slow_period: int
    ) -> pd.DataFrame:
        ad = self.calculate_ad(df)["ad"]
        ema_fast = ad.ewm(span=fast_period, adjust=False).mean()
        ema_slow = ad.ewm(span=slow_period, adjust=False).mean()
        adosc = ema_fast - ema_slow
        return adosc.to_frame("adosc")

    def calculate_obv(self, df: pd.DataFrame) -> pd.DataFrame:
        close = df["close"]
        volume = df["volume"]
        sign = (close > close.shift(1)).astype(int) - (close < close.shift(1)).astype(
            int
        )
        obv = (volume * sign).cumsum()
        return obv.to_frame("obv")

    def calculate_mom(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        close = df["close"]
        mom = close.diff(periods=window)
        return mom.to_frame("mom")

    def calculate_sar(
        self, df: pd.DataFrame, acceleration: float, maximum: float
    ) -> pd.DataFrame:
        high, low = df["high"], df["low"]
        sar = pd.Series(index=df.index, dtype=float)
        uptrend = True
        accel_factor = acceleration
        extreme_point = high[0]
        sar.iloc[0] = low[0]

        for i in range(1, len(df)):
            prev_sar = sar.iloc[i - 1]

            if uptrend:
                sar.iloc[i] = prev_sar + accel_factor * (extreme_point - prev_sar)
                sar.iloc[i] = min(sar.iloc[i], low.iloc[i - 1])
                if i > 1:
                    sar.iloc[i] = min(sar.iloc[i], low.iloc[i - 2])

                if low[i] < sar.iloc[i]:
                    uptrend = False
                    sar.iloc[i] = extreme_point
                    extreme_point = low[i]
                    accel_factor = acceleration
                else:
                    if high[i] > extreme_point:
                        extreme_point = high[i]
                        accel_factor = min(maximum, accel_factor + acceleration)
            else:
                sar.iloc[i] = prev_sar - accel_factor * (prev_sar - extreme_point)
                sar.iloc[i] = max(sar.iloc[i], high.iloc[i - 1])
                if i > 1:
                    sar.iloc[i] = max(sar.iloc[i], high.iloc[i - 2])

                if high[i] > sar.iloc[i]:
                    uptrend = True
                    sar.iloc[i] = extreme_point
                    extreme_point = high[i]
                    accel_factor = acceleration
                else:
                    if low[i] < extreme_point:
                        extreme_point = low[i]
                        accel_factor = min(maximum, accel_factor + acceleration)

        return sar.to_frame("sar")

    def calculate_tsf(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        close = df["close"]

        def linear_reg_forecast(y: np.ndarray) -> float:
            x = np.arange(1, len(y) + 1)
            b_num = len(x) * np.sum(x * y) - np.sum(x) * np.sum(y)
            b_den = len(x) * np.sum(x * x) - np.sum(x) ** 2
            b = b_num / b_den if b_den != 0 else 0
            a = np.mean(y) - b * np.mean(x)
            result = a + b * len(y)
            return float(result)

        tsf = close.rolling(window=window, min_periods=window).apply(
            linear_reg_forecast, raw=True
        )
        return tsf.to_frame("tsf")

    def calculate_apo(
        self, df: pd.DataFrame, fast_period: int, slow_period: int, ma_type: int
    ) -> pd.DataFrame:
        close = df["close"]
        fast_ma = self._get_ma(close, fast_period, ma_type)
        slow_ma = self._get_ma(close, slow_period, ma_type)
        apo = fast_ma - slow_ma
        return apo.to_frame("apo")

    def calculate_aroon(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        high = df["high"]
        low = df["low"]
        periods_since_high = high.rolling(window=window, min_periods=window).apply(
            lambda x: len(x) - 1 - np.argmax(x), raw=True
        )
        periods_since_low = low.rolling(window=window, min_periods=window).apply(
            lambda x: len(x) - 1 - np.argmin(x), raw=True
        )
        aroon_up = ((window - periods_since_high) / window) * 100
        aroon_down = ((window - periods_since_low) / window) * 100
        return pd.DataFrame({"aroon_up": aroon_up, "aroon_down": aroon_down})

    def calculate_aroonosc(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        aroon_df = self.calculate_aroon(df, window)
        aroonosc = aroon_df["aroon_up"] - aroon_df["aroon_down"]
        return aroonosc.to_frame("aroonosc")

    def calculate_bop(self, df: pd.DataFrame) -> pd.DataFrame:
        bop = (df["close"] - df["open"]) / (df["high"] - df["low"]).replace(0, np.nan)
        bop = bop.fillna(0)
        return bop.to_frame("bop")

    def calculate_cmo(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        close_diff = df["close"].diff(1)
        sum_up = close_diff.where(close_diff > 0, 0).rolling(window=window).sum()  # type: ignore
        sum_down = -close_diff.where(close_diff < 0, 0).rolling(window=window).sum()  # type: ignore
        cmo = 100 * (sum_up - sum_down) / (sum_up + sum_down).replace(0, np.nan)
        cmo = cmo.fillna(0)
        return cmo.to_frame("cmo")

    def calculate_dx(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        plus_di = self.calculate_plus_di(df, window)["plus_di"]
        minus_di = self.calculate_minus_di(df, window)["minus_di"]
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan)
        dx = dx.fillna(0)
        return dx.to_frame("dx")

    def calculate_mfi(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        typical_price = (df["high"] + df["low"] + df["close"]) / 3
        money_flow = typical_price * df["volume"]
        price_diff = typical_price.diff()
        positive_mf = money_flow.where(price_diff > 0, 0)  # type: ignore
        negative_mf = money_flow.where(price_diff < 0, 0)  # type: ignore
        positive_mf_sum = positive_mf.rolling(window=window).sum()
        negative_mf_sum = negative_mf.rolling(window=window).sum()
        money_ratio = positive_mf_sum / negative_mf_sum.replace(0, np.nan)
        money_ratio = money_ratio.fillna(0)
        mfi = 100 - (100 / (1 + money_ratio))
        return mfi.to_frame("mfi")

    def calculate_minus_di(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        atr = self.calculate_atr(df, window)["atr"]
        minus_dm = self.calculate_minus_dm(df, window)["minus_dm"]
        minus_di = 100 * (minus_dm / atr)
        return minus_di.to_frame("minus_di")

    def calculate_minus_dm(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        high = df["high"]
        low = df["low"]
        up_move = high.diff()
        down_move = -low.diff()
        minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)  # type: ignore
        smoothed_minus_dm = self._wilder_smooth(minus_dm, window)
        return smoothed_minus_dm.to_frame("minus_dm")

    def calculate_plus_di(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        atr = self.calculate_atr(df, window)["atr"]
        plus_dm = self.calculate_plus_dm(df, window)["plus_dm"]
        plus_di = 100 * (plus_dm / atr)
        return plus_di.to_frame("plus_di")

    def calculate_plus_dm(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        high = df["high"]
        low = df["low"]
        up_move = high.diff()
        down_move = -low.diff()
        plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)  # type: ignore
        smoothed_plus_dm = self._wilder_smooth(plus_dm, window)
        return smoothed_plus_dm.to_frame("plus_dm")

    def calculate_ppo(
        self, df: pd.DataFrame, fast_period: int, slow_period: int, ma_type: int
    ) -> pd.DataFrame:
        close = df["close"]
        fast_ma = self._get_ma(close, fast_period, ma_type)
        slow_ma = self._get_ma(close, slow_period, ma_type)
        ppo = ((fast_ma - slow_ma) / slow_ma) * 100
        return ppo.to_frame("ppo")

    def calculate_roc(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        close = df["close"]
        roc = (close.diff(window) / close.shift(window)) * 100
        return roc.to_frame("roc")

    def calculate_rocp(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        close = df["close"]
        rocp = close.diff(window) / close.shift(window)
        return rocp.to_frame("rocp")

    def calculate_rocr(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        close = df["close"]
        rocr = close / close.shift(window)
        return rocr.to_frame("rocr")

    def calculate_rocr100(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        close = df["close"]
        rocr100 = (close / close.shift(window)) * 100
        return rocr100.to_frame("rocr100")

    def calculate_trix(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        close = df["close"]
        ema1 = close.ewm(span=window, adjust=False).mean()
        ema2 = ema1.ewm(span=window, adjust=False).mean()
        ema3 = ema2.ewm(span=window, adjust=False).mean()
        trix = 100 * ema3.diff(1) / ema3.shift(1)  # type: ignore
        return pd.DataFrame({"trix": trix}, index=df.index)

    def calculate_ultosc(
        self, df: pd.DataFrame, window1: int, window2: int, window3: int
    ) -> pd.DataFrame:
        low = df["low"]
        high = df["high"]
        close = df["close"]
        close_prev = close.shift(1)
        true_low = pd.concat([low, close_prev], axis=1).min(axis=1)
        true_high = pd.concat([high, close_prev], axis=1).max(axis=1)
        bp = close - true_low
        tr = true_high - true_low
        tr_sum1 = tr.rolling(window=window1).sum()
        tr_sum2 = tr.rolling(window=window2).sum()
        tr_sum3 = tr.rolling(window=window3).sum()
        avg1 = bp.rolling(window=window1).sum() / tr_sum1.replace(0, np.nan)
        avg2 = bp.rolling(window=window2).sum() / tr_sum2.replace(0, np.nan)
        avg3 = bp.rolling(window=window3).sum() / tr_sum3.replace(0, np.nan)
        avg1 = avg1.fillna(0)
        avg2 = avg2.fillna(0)
        avg3 = avg3.fillna(0)
        ultosc = 100 * (4 * avg1 + 2 * avg2 + avg3) / (4 + 2 + 1)
        return pd.DataFrame({"ultosc": ultosc}, index=df.index)
