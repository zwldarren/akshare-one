import unittest
import pandas as pd
from akshare_one import get_info


class TestInfo(unittest.TestCase):
    def test_get_info(self):
        """测试获取股票基本信息"""
        df = get_info("600405")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        self.assertEqual(df.shape[0], 1)

        expected_columns = [
            "price",
            "symbol",
            "name",
            "total_shares",
            "float_shares",
            "total_market_cap",
            "float_market_cap",
            "industry",
            "listing_date",
        ]
        for col in expected_columns:
            self.assertIn(col, df.columns)

        self.assertEqual(df["symbol"].iloc[0], "600405")
        self.assertIsInstance(df["listing_date"].iloc[0], pd.Timestamp)


if __name__ == "__main__":
    unittest.main()
