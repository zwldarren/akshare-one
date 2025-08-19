import talib # type: ignore
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

    def calculate_adx(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        high = df["high"].values
        low = df["low"].values
        close = df["close"].values
        adx = talib.ADX(high, low, close, timeperiod=window)
        return pd.DataFrame({"adx": adx}, index=df.index)

    def calculate_willr(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        high = df["high"].values
        low = df["low"].values
        close = df["close"].values
        willr = talib.WILLR(high, low, close, timeperiod=window)
        return pd.DataFrame({"willr": willr}, index=df.index)

    def calculate_ad(self, df: pd.DataFrame) -> pd.DataFrame:
        high = df["high"].values
        low = df["low"].values
        close = df["close"].values
        volume = df["volume"].values.astype(float)
        ad = talib.AD(high, low, close, volume)
        return pd.DataFrame({"ad": ad}, index=df.index)

    def calculate_adosc(
        self, df: pd.DataFrame, fast_period: int, slow_period: int
    ) -> pd.DataFrame:
        high = df["high"].values
        low = df["low"].values
        close = df["close"].values
        volume = df["volume"].values.astype(float)
        adosc = talib.ADOSC(
            high, low, close, volume, fastperiod=fast_period, slowperiod=slow_period
        )
        return pd.DataFrame({"adosc": adosc}, index=df.index)

    def calculate_obv(self, df: pd.DataFrame) -> pd.DataFrame:
        close = df["close"].values
        volume = df["volume"].values.astype(float)
        obv = talib.OBV(close, volume)
        return pd.DataFrame({"obv": obv}, index=df.index)

    def calculate_mom(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        close = df["close"].values
        mom = talib.MOM(close, timeperiod=window)
        return pd.DataFrame({"mom": mom}, index=df.index)

    def calculate_sar(
        self, df: pd.DataFrame, acceleration: float, maximum: float
    ) -> pd.DataFrame:
        high = df["high"].values
        low = df["low"].values
        sar = talib.SAR(high, low, acceleration=acceleration, maximum=maximum)
        return pd.DataFrame({"sar": sar}, index=df.index)

    def calculate_tsf(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        close = df["close"].values
        tsf = talib.TSF(close, timeperiod=window)
        return pd.DataFrame({"tsf": tsf}, index=df.index)

    def calculate_apo(
        self, df: pd.DataFrame, fast_period: int, slow_period: int, ma_type: int
    ) -> pd.DataFrame:
        close = df["close"].values
        apo = talib.APO(
            close, fastperiod=fast_period, slowperiod=slow_period, matype=ma_type
        )
        return pd.DataFrame({"apo": apo}, index=df.index)

    def calculate_aroon(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        high = df["high"].values
        low = df["low"].values
        aroon_down, aroon_up = talib.AROON(high, low, timeperiod=window)
        return pd.DataFrame(
            {"aroon_down": aroon_down, "aroon_up": aroon_up}, index=df.index
        )

    def calculate_aroonosc(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        high = df["high"].values
        low = df["low"].values
        aroonosc = talib.AROONOSC(high, low, timeperiod=window)
        return pd.DataFrame({"aroonosc": aroonosc}, index=df.index)

    def calculate_bop(self, df: pd.DataFrame) -> pd.DataFrame:
        open_ = df["open"].values
        high = df["high"].values
        low = df["low"].values
        close = df["close"].values
        bop = talib.BOP(open_, high, low, close)
        return pd.DataFrame({"bop": bop}, index=df.index)

    def calculate_cmo(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        close = df["close"].values
        cmo = talib.CMO(close, timeperiod=window)
        return pd.DataFrame({"cmo": cmo}, index=df.index)

    def calculate_dx(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        high = df["high"].values
        low = df["low"].values
        close = df["close"].values
        dx = talib.DX(high, low, close, timeperiod=window)
        return pd.DataFrame({"dx": dx}, index=df.index)

    def calculate_mfi(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        high = df["high"].values
        low = df["low"].values
        close = df["close"].values
        volume = df["volume"].values.astype(float)
        mfi = talib.MFI(high, low, close, volume, timeperiod=window)
        return pd.DataFrame({"mfi": mfi}, index=df.index)

    def calculate_minus_di(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        high = df["high"].values
        low = df["low"].values
        close = df["close"].values
        minus_di = talib.MINUS_DI(high, low, close, timeperiod=window)
        return pd.DataFrame({"minus_di": minus_di}, index=df.index)

    def calculate_minus_dm(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        high = df["high"].values
        low = df["low"].values
        minus_dm = talib.MINUS_DM(high, low, timeperiod=window)
        return pd.DataFrame({"minus_dm": minus_dm}, index=df.index)

    def calculate_plus_di(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        high = df["high"].values
        low = df["low"].values
        close = df["close"].values
        plus_di = talib.PLUS_DI(high, low, close, timeperiod=window)
        return pd.DataFrame({"plus_di": plus_di}, index=df.index)

    def calculate_plus_dm(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        high = df["high"].values
        low = df["low"].values
        plus_dm = talib.PLUS_DM(high, low, timeperiod=window)
        return pd.DataFrame({"plus_dm": plus_dm}, index=df.index)

    def calculate_ppo(
        self, df: pd.DataFrame, fast_period: int, slow_period: int, ma_type: int
    ) -> pd.DataFrame:
        close = df["close"].values
        ppo = talib.PPO(
            close, fastperiod=fast_period, slowperiod=slow_period, matype=ma_type
        )
        return pd.DataFrame({"ppo": ppo}, index=df.index)

    def calculate_roc(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        close = df["close"].values
        roc = talib.ROC(close, timeperiod=window)
        return pd.DataFrame({"roc": roc}, index=df.index)

    def calculate_rocp(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        close = df["close"].values
        rocp = talib.ROCP(close, timeperiod=window)
        return pd.DataFrame({"rocp": rocp}, index=df.index)

    def calculate_rocr(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        close = df["close"].values
        rocr = talib.ROCR(close, timeperiod=window)
        return pd.DataFrame({"rocr": rocr}, index=df.index)

    def calculate_rocr100(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        close = df["close"].values
        rocr100 = talib.ROCR100(close, timeperiod=window)
        return pd.DataFrame({"rocr100": rocr100}, index=df.index)

    def calculate_trix(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        close = df["close"].values
        trix = talib.TRIX(close, timeperiod=window)
        return pd.DataFrame({"trix": trix}, index=df.index)

    def calculate_ultosc(
        self, df: pd.DataFrame, window1: int, window2: int, window3: int
    ) -> pd.DataFrame:
        high = df["high"].values
        low = df["low"].values
        close = df["close"].values
        ultosc = talib.ULTOSC(
            high,
            low,
            close,
            timeperiod1=window1,
            timeperiod2=window2,
            timeperiod3=window3,
        )
        return pd.DataFrame({"ultosc": ultosc}, index=df.index)
