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
    get_adx,
    get_willr,
    get_ad,
    get_adosc,
    get_obv,
    get_mom,
    get_sar,
    get_tsf,
    get_apo,
    get_aroon,
    get_aroonosc,
    get_bop,
    get_cmo,
    get_dx,
    get_mfi,
    get_minus_di,
    get_minus_dm,
    get_plus_di,
    get_plus_dm,
    get_ppo,
    get_roc,
    get_rocp,
    get_rocr,
    get_rocr100,
    get_trix,
    get_ultosc,
)
from akshare_one.modules.indicators.factory import TALIB_AVAILABLE


class TestIndicators(unittest.TestCase):
    def setUp(self):
        # Use a predictable series for easier debugging if needed
        data = {
            "open": np.arange(100, 200, 1.0),
            "high": np.arange(101, 201, 1.0),
            "low": np.arange(99, 199, 1.0),
            "close": np.arange(100, 200, 1.0),
            "volume": np.arange(1000, 2000, 10.0),
        }
        self.df = pd.DataFrame(data)

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

    def test_simple_adx(self):
        result = get_adx(self.df, 14, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("adx" in result.columns)

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

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_adx(self):
        result = get_adx(self.df, 14, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("adx" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_willr(self):
        result = get_willr(self.df, 14)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("willr" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_ad(self):
        result = get_ad(self.df)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("ad" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_adosc(self):
        result = get_adosc(self.df, 3, 10)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("adosc" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_obv(self):
        result = get_obv(self.df)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("obv" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_mom(self):
        result = get_mom(self.df, 10)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("mom" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_sar(self):
        result = get_sar(self.df, 0.02, 0.2)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("sar" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_tsf(self):
        result = get_tsf(self.df, 14)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("tsf" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_apo(self):
        result = get_apo(self.df, 12, 26, 0)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("apo" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_aroon(self):
        result = get_aroon(self.df, 14)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("aroon_down" in result.columns)
        self.assertTrue("aroon_up" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_aroonosc(self):
        result = get_aroonosc(self.df, 14)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("aroonosc" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_bop(self):
        result = get_bop(self.df)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("bop" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_cmo(self):
        result = get_cmo(self.df, 14)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("cmo" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_dx(self):
        result = get_dx(self.df, 14)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("dx" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_mfi(self):
        result = get_mfi(self.df, 14)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("mfi" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_minus_di(self):
        result = get_minus_di(self.df, 14)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("minus_di" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_minus_dm(self):
        result = get_minus_dm(self.df, 14)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("minus_dm" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_plus_di(self):
        result = get_plus_di(self.df, 14)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("plus_di" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_plus_dm(self):
        result = get_plus_dm(self.df, 14)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("plus_dm" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_ppo(self):
        result = get_ppo(self.df, 12, 26, 0)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("ppo" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_roc(self):
        result = get_roc(self.df, 10)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("roc" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_rocp(self):
        result = get_rocp(self.df, 10)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("rocp" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_rocr(self):
        result = get_rocr(self.df, 10)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("rocr" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_rocr100(self):
        result = get_rocr100(self.df, 10)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("rocr100" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_trix(self):
        result = get_trix(self.df, 30)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("trix" in result.columns)

    @unittest.skipUnless(TALIB_AVAILABLE, "talib not installed")
    def test_talib_ultosc(self):
        result = get_ultosc(self.df, 7, 14, 28)
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("ultosc" in result.columns)
