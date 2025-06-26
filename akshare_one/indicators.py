"""Technical indicators module

Provides common technical analysis indicators like:
- Simple Moving Average (SMA)
- Exponential Moving Average (EMA)
- Relative Strength Index (RSI)
- Moving Average Convergence Divergence (MACD)
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
        calculator_type: 'talib' or 'simple'

    Returns:
        pd.DataFrame with SMA values
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
        calculator_type: 'talib' or 'simple'
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
        calculator_type: 'talib' or 'simple'
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
        calculator_type: 'talib' or 'simple'
    """
    calculator = IndicatorFactory.get_calculator(calculator_type)
    return calculator.calculate_macd(df, fast, slow, signal)
