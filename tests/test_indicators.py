import unittest
import pandas as pd
import numpy as np
from akshare_one.indicators import get_sma, get_ema, get_rsi, get_macd
from akshare_one.modules.indicators.factory import TALIB_AVAILABLE


class TestIndicators(unittest.TestCase):
    def setUp(self):
        # Use a predictable series for easier debugging if needed
        self.df = pd.DataFrame({"close": np.arange(100, 200, 1.0)})

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
