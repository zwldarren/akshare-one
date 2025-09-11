"""Technical indicators module

Provides common technical analysis indicators like:
- Simple Moving Average (SMA)
- Exponential Moving Average (EMA)
- Relative Strength Index (RSI)
- Moving Average Convergence Divergence (MACD)
- Bollinger Bands (BBANDS)
- Stochastic Oscillator (STOCH)
- Average True Range (ATR)
- Commodity Channel Index (CCI)
- Average Directional Index (ADX)
- Williams' %R (WILLR)
- Chaikin A/D Line (AD)
- Chaikin A/D Oscillator (ADOSC)
- On Balance Volume (OBV)
- Momentum (MOM)
- Parabolic SAR (SAR)
- Time Series Forecast (TSF)
- Absolute Price Oscillator (APO)
- Aroon (AROON)
- Aroon Oscillator (AROONOSC)
- Balance of Power (BOP)
- Chande Momentum Oscillator (CMO)
- Directional Movement Index (DX)
- Money Flow Index (MFI)
- Minus Directional Indicator (MINUS_DI)
- Minus Directional Movement (MINUS_DM)
- Plus Directional Indicator (PLUS_DI)
- Plus Directional Movement (PLUS_DM)
- Percentage Price Oscillator (PPO)
- Rate of change (ROC)
- Rate of change Percentage (ROCP)
- Rate of change ratio (ROCR)
- Rate of change ratio 100 scale (ROCR100)
- 1-day Rate of Change (ROC) of a Triple Smooth EMA (TRIX)
- Ultimate Oscillator (ULTOSC)
"""

import pandas as pd

from .modules.indicators.factory import IndicatorFactory


def get_sma(
    df: pd.DataFrame, window: int = 20, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Simple Moving Average

    Args:
        df: DataFrame with 'close' column
        window: Lookback window size
        calculator_type: ('talib', 'simple')
    """
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_sma(df, window)


def get_ema(
    df: pd.DataFrame, window: int = 20, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Exponential Moving Average

    Args:
        df: DataFrame with 'close' column
        window: Lookback window size
        calculator_type: ('talib', 'simple')
    """
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_ema(df, window)


def get_rsi(
    df: pd.DataFrame, window: int = 14, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Relative Strength Index

    Args:
        df: DataFrame with 'close' column
        window: Lookback window size
        calculator_type: ('talib', 'simple')
    """
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_rsi(df, window)


def get_macd(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    calculator_type: str = "talib",
) -> pd.DataFrame:
    """Calculate MACD

    Args:
        df: DataFrame with 'close' column
        fast: Fast period
        slow: Slow period
        signal: Signal period
        calculator_type: ('talib', 'simple')
    """
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_macd(df, fast, slow, signal)


def get_bollinger_bands(
    df: pd.DataFrame,
    window: int = 20,
    std: int = 2,
    calculator_type: str = "talib",
) -> pd.DataFrame:
    """Calculate Bollinger Bands

    Args:
        df: DataFrame with 'close' column
        window: Lookback window size
        std: Standard deviation
        calculator_type: ('talib', 'simple')
    """
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_bollinger_bands(df, window, std)


def get_stoch(
    df: pd.DataFrame,
    window: int = 14,
    smooth_d: int = 3,
    smooth_k: int = 3,
    calculator_type: str = "talib",
) -> pd.DataFrame:
    """Calculate Stochastic Oscillator

    Args:
        df: DataFrame with 'high', 'low', 'close' columns
        window: Lookback window size
        smooth_d: Smoothing for D line
        smooth_k: Smoothing for K line
        calculator_type: ('talib', 'simple')
    """
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_stoch(df, window, smooth_d, smooth_k)


def get_atr(
    df: pd.DataFrame, window: int = 14, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Average True Range

    Args:
        df: DataFrame with 'high', 'low', 'close' columns
        window: Lookback window size
        calculator_type: ('talib', 'simple')
    """
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_atr(df, window)


def get_cci(
    df: pd.DataFrame, window: int = 14, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Commodity Channel Index

    Args:
        df: DataFrame with 'high', 'low', 'close' columns
        window: Lookback window size
        calculator_type: ('talib', 'simple')
    """
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_cci(df, window)


def get_adx(
    df: pd.DataFrame, window: int = 14, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Average Directional Index

    Args:
        df: DataFrame with 'high', 'low', 'close' columns
        window: Lookback window size
        calculator_type: ('talib', 'simple')
    """
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_adx(df, window)


def get_willr(
    df: pd.DataFrame, window: int = 14, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Williams' %R"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_willr(df, window)


def get_ad(df: pd.DataFrame, calculator_type: str = "talib") -> pd.DataFrame:
    """Calculate Chaikin A/D Line"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_ad(df)


def get_adosc(
    df: pd.DataFrame,
    fast_period: int = 3,
    slow_period: int = 10,
    calculator_type: str = "talib",
) -> pd.DataFrame:
    """Calculate Chaikin A/D Oscillator"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_adosc(df, fast_period, slow_period)


def get_obv(df: pd.DataFrame, calculator_type: str = "talib") -> pd.DataFrame:
    """Calculate On Balance Volume"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_obv(df)


def get_mom(
    df: pd.DataFrame, window: int = 10, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Momentum"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_mom(df, window)


def get_sar(
    df: pd.DataFrame,
    acceleration: float = 0.02,
    maximum: float = 0.2,
    calculator_type: str = "talib",
) -> pd.DataFrame:
    """Calculate Parabolic SAR"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_sar(df, acceleration, maximum)


def get_tsf(
    df: pd.DataFrame, window: int = 14, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Time Series Forecast"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_tsf(df, window)


def get_apo(
    df: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    ma_type: int = 0,
    calculator_type: str = "talib",
) -> pd.DataFrame:
    """Calculate Absolute Price Oscillator"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_apo(df, fast_period, slow_period, ma_type)


def get_aroon(
    df: pd.DataFrame, window: int = 14, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Aroon"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_aroon(df, window)


def get_aroonosc(
    df: pd.DataFrame, window: int = 14, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Aroon Oscillator"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_aroonosc(df, window)


def get_bop(df: pd.DataFrame, calculator_type: str = "talib") -> pd.DataFrame:
    """Calculate Balance of Power"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_bop(df)


def get_cmo(
    df: pd.DataFrame, window: int = 14, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Chande Momentum Oscillator"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_cmo(df, window)


def get_dx(
    df: pd.DataFrame, window: int = 14, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Directional Movement Index"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_dx(df, window)


def get_mfi(
    df: pd.DataFrame, window: int = 14, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Money Flow Index"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_mfi(df, window)


def get_minus_di(
    df: pd.DataFrame, window: int = 14, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Minus Directional Indicator"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_minus_di(df, window)


def get_minus_dm(
    df: pd.DataFrame, window: int = 14, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Minus Directional Movement"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_minus_dm(df, window)


def get_plus_di(
    df: pd.DataFrame, window: int = 14, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Plus Directional Indicator"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_plus_di(df, window)


def get_plus_dm(
    df: pd.DataFrame, window: int = 14, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Plus Directional Movement"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_plus_dm(df, window)


def get_ppo(
    df: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    ma_type: int = 0,
    calculator_type: str = "talib",
) -> pd.DataFrame:
    """Calculate Percentage Price Oscillator"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_ppo(df, fast_period, slow_period, ma_type)


def get_roc(
    df: pd.DataFrame, window: int = 10, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Rate of change"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_roc(df, window)


def get_rocp(
    df: pd.DataFrame, window: int = 10, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Rate of change Percentage"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_rocp(df, window)


def get_rocr(
    df: pd.DataFrame, window: int = 10, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Rate of change ratio"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_rocr(df, window)


def get_rocr100(
    df: pd.DataFrame, window: int = 10, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate Rate of change ratio 100 scale"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_rocr100(df, window)


def get_trix(
    df: pd.DataFrame, window: int = 30, calculator_type: str = "talib"
) -> pd.DataFrame:
    """Calculate 1-day Rate of Change (ROC) of a Triple Smooth EMA"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_trix(df, window)


def get_ultosc(
    df: pd.DataFrame,
    window1: int = 7,
    window2: int = 14,
    window3: int = 28,
    calculator_type: str = "talib",
) -> pd.DataFrame:
    """Calculate Ultimate Oscillator"""
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_ultosc(df, window1, window2, window3)
