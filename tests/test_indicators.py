import unittest
import pandas as pd
import numpy as np
from akshare_one.indicators import (
    get_sma,
    get_ema,
    get_rsi,
    get_macd,
    get_bollinger_bands,
    get_stoch,
    get_atr,
    get_cci,
)
from akshare_one.modules.indicators.factory import TALIB_AVAILABLE


class TestIndicators(unittest.TestCase):
    def setUp(self):
        # Use a predictable series for easier debugging if needed
        data = {
            "high": np.arange(101, 201, 1.0),
            "low": np.arange(99, 199, 1.0),
            "close": np.arange(100, 200, 1.0),
        }
        self.df = pd.DataFrame(data)

    # Tests for the default behavior (talib if available, otherwise simple)
    def test_default_sma(self):
        result = get_sma(self.df, 20)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("sma" in result.columns)
        self.assertTrue(result.iloc[:19]["sma"].isna().all())
        self.assertFalse(result.iloc[19:]["sma"].isna().any())

    def test_default_ema(self):
        result = get_ema(self.df, 20)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("ema" in result.columns)
        self.assertTrue(result.iloc[:19]["ema"].isna().all())
        self.assertFalse(result.iloc[19:]["ema"].isna().any())

    def test_default_rsi(self):
        result = get_rsi(self.df, 14)
        self.assertTrue("rsi" in result.columns)
        self.assertTrue(result.iloc[:14]["rsi"].isna().all())
        self.assertFalse(result.iloc[14:]["rsi"].isna().any())

    def test_default_macd(self):
        result = get_macd(self.df, 12, 26, 9)
        self.assertEqual(len(result), len(self.df))
        self.assertEqual(set(result.columns), {"macd", "signal", "histogram"})
        self.assertTrue(result.iloc[:25]["macd"].isna().all())
        self.assertTrue(result.iloc[:33]["signal"].isna().all())
        self.assertTrue(result.iloc[:33]["histogram"].isna().all())

    def test_default_bollinger_bands(self):
        result = get_bollinger_bands(self.df, 20, 2)
        self.assertEqual(len(result), len(self.df))
        self.assertEqual(
            set(result.columns), {"upper_band", "middle_band", "lower_band"}
        )
        self.assertTrue(result.iloc[:19]["upper_band"].isna().all())
        self.assertFalse(result.iloc[19:]["upper_band"].isna().any())

    def test_default_stoch(self):
        result = get_stoch(self.df, 14, 3, 3)
        self.assertEqual(len(result), len(self.df))
        self.assertEqual(set(result.columns), {"slow_k", "slow_d"})

    def test_default_atr(self):
        result = get_atr(self.df, 14)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("atr" in result.columns)
        self.assertTrue(result.iloc[:13]["atr"].isna().all())
        self.assertFalse(result.iloc[14:]["atr"].isna().any())

    def test_default_cci(self):
        result = get_cci(self.df, 14)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("cci" in result.columns)

    # Explicitly test simple implementation
    def test_simple_sma(self):
        result = get_sma(self.df, 20, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("sma" in result.columns)
        self.assertTrue(result.iloc[:19]["sma"].isna().all())
        self.assertFalse(result.iloc[19:]["sma"].isna().any())

    def test_simple_ema(self):
        result = get_ema(self.df, 20, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("ema" in result.columns)
        self.assertTrue(result.iloc[:19]["ema"].isna().all())
        self.assertFalse(result.iloc[19:]["ema"].isna().any())

    def test_simple_rsi(self):
        result = get_rsi(self.df, 14, calculator_type="simple")
        self.assertTrue("rsi" in result.columns)
        self.assertTrue(result.iloc[:14]["rsi"].isna().all())
        self.assertFalse(result.iloc[14:]["rsi"].isna().any())

    def test_simple_macd(self):
        result = get_macd(self.df, 12, 26, 9, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertEqual(set(result.columns), {"macd", "signal", "histogram"})
        self.assertTrue(result.iloc[:25]["macd"].isna().all())
        self.assertTrue(result.iloc[:33]["signal"].isna().all())
        self.assertTrue(result.iloc[:33]["histogram"].isna().all())

    def test_simple_bollinger_bands(self):
        result = get_bollinger_bands(self.df, 20, 2, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertEqual(
            set(result.columns), {"upper_band", "middle_band", "lower_band"}
        )
        self.assertTrue(result.iloc[:19]["upper_band"].isna().all())
        self.assertFalse(result.iloc[19:]["upper_band"].isna().any())

    def test_simple_stoch(self):
        result = get_stoch(self.df, 14, 3, 3, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertEqual(set(result.columns), {"slow_k", "slow_d"})

    def test_simple_atr(self):
        result = get_atr(self.df, 14, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("atr" in result.columns)

    def test_simple_cci(self):
        result = get_cci(self.df, 14, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("cci" in result.columns)

    # Explicitly test talib implementation
    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_sma(self):
        result = get_sma(self.df, 20, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("sma" in result.columns)
        self.assertTrue(result.iloc[:19]["sma"].isna().all())
        self.assertFalse(result.iloc[19:]["sma"].isna().any())

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_ema(self):
        result = get_ema(self.df, 20, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("ema" in result.columns)
        self.assertTrue(result.iloc[:19]["ema"].isna().all())
        self.assertFalse(result.iloc[19:]["ema"].isna().any())

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_rsi(self):
        result = get_rsi(self.df, 14, calculator_type="talib")
        self.assertTrue("rsi" in result.columns)
        self.assertTrue(result.iloc[:14]["rsi"].isna().all())
        self.assertFalse(result.iloc[14:]["rsi"].isna().any())

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_macd(self):
        result = get_macd(self.df, 12, 26, 9, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertEqual(set(result.columns), {"macd", "signal", "histogram"})
        self.assertTrue(result.iloc[:25]["macd"].isna().all())
        self.assertTrue(result.iloc[:33]["signal"].isna().all())
        self.assertTrue(result.iloc[:33]["histogram"].isna().any())

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_bollinger_bands(self):
        result = get_bollinger_bands(self.df, 20, 2, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertEqual(
            set(result.columns), {"upper_band", "middle_band", "lower_band"}
        )
        self.assertTrue(result.iloc[:19]["upper_band"].isna().all())
        self.assertFalse(result.iloc[19:]["upper_band"].isna().any())

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_stoch(self):
        result = get_stoch(self.df, 14, 3, 3, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertEqual(set(result.columns), {"slow_k", "slow_d"})

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_atr(self):
        result = get_atr(self.df, 14, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("atr" in result.columns)
        self.assertTrue(result.iloc[:13]["atr"].isna().all())
        self.assertFalse(result.iloc[14:]["atr"].isna().any())

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_cci(self):
        result = get_cci(self.df, 14, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("cci" in result.columns)
