from cachetools import TTLCache, cached
import os

# 缓存配置
CACHE_CONFIG = {
    "hist_data_cache": TTLCache(maxsize=1000, ttl=3600),  # 历史数据缓存1小时
    "realtime_cache": TTLCache(maxsize=500, ttl=60),  # 实时数据缓存1分钟
    "news_cache": TTLCache(maxsize=500, ttl=3600),  # 新闻数据缓存1小时
    "financial_cache": TTLCache(maxsize=500, ttl=86400),  # 财务数据缓存24小时
    "info_cache": TTLCache(maxsize=500, ttl=86400),  # 信息数据缓存24小时
}


def cache(cache_key, key=None):
    cache_enabled = os.getenv("AKSHARE_ONE_CACHE_ENABLED", "true").lower() in (
        "1",
        "true",
        "yes",
        "on",
    )

    def decorator(func):
        if cache_enabled:
            return cached(CACHE_CONFIG[cache_key], key=key)(func)
        return func

    return decorator
