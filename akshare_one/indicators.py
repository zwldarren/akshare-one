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
