import unittest
from cachetools import TTLCache
import pandas as pd
import os
import time
from akshare_one import get_basic_info
from akshare_one.modules.cache import CACHE_CONFIG


class TestInfo(unittest.TestCase):
    def test_get_info(self):
        """测试获取股票基本信息"""
        df = get_basic_info("600405")
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

    def test_cache(self):
        """测试缓存功能是否生效"""
        cache = CACHE_CONFIG["info_cache"]
        cache.clear()

        # 测试缓存命中
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "true"

        # 第一次调用 - 应该缓存未命中
        initial_size = cache.currsize
        df1 = get_basic_info("600405")
        self.assertEqual(cache.currsize, initial_size + 1)  # 缓存应增加

        # 第二次调用 - 应该缓存命中
        df2 = get_basic_info("600405")
        self.assertEqual(cache.currsize, initial_size + 1)  # 缓存大小不变
        pd.testing.assert_frame_equal(df1, df2)

        # 测试缓存禁用
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"
        disabled_size = cache.currsize
        df3 = get_basic_info("600405")
        self.assertEqual(cache.currsize, disabled_size)

        # 测试缓存过期
        os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "true"

        # 创建临时缓存并替换原缓存
        original_cache = cache
        temp_cache = TTLCache(maxsize=1000, ttl=1)
        CACHE_CONFIG["info_cache"] = temp_cache

        # 填充缓存
        get_basic_info("600405")
        expired_size = temp_cache.currsize

        # 等待缓存过期
        time.sleep(1.1)

        # 过期后调用 - 应该缓存未命中
        df4 = get_basic_info("600405")
        self.assertEqual(temp_cache.currsize, expired_size)  # 缓存被替换，大小不变

        CACHE_CONFIG["info_cache"] = original_cache


if __name__ == "__main__":
    unittest.main()
