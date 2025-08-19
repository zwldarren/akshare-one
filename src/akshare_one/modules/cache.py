from cachetools import TTLCache, cached
import os
from typing import Any, Callable, TypeVar, Optional

F = TypeVar('F', bound=Callable[..., Any])

# 缓存配置
CACHE_CONFIG: dict[str, TTLCache[Any, Any]] = {
    "hist_data_cache": TTLCache(maxsize=1000, ttl=3600),  # 历史数据缓存1小时
    "realtime_cache": TTLCache(maxsize=500, ttl=60),  # 实时数据缓存1分钟
    "news_cache": TTLCache(maxsize=500, ttl=3600),  # 新闻数据缓存1小时
    "financial_cache": TTLCache(maxsize=500, ttl=86400),  # 财务数据缓存24小时
    "info_cache": TTLCache(maxsize=500, ttl=86400),  # 信息数据缓存24小时
}


def cache(cache_key: str, key: Optional[Callable[..., Any]] = None) -> Callable[[F], F]:
    cache_enabled = os.getenv("AKSHARE_ONE_CACHE_ENABLED", "true").lower() in (
        "1",
        "true",
        "yes",
        "on",
    )

    def decorator(func: F) -> F:
        if cache_enabled:
            return cached(CACHE_CONFIG[cache_key], key=key)(func)  # type: ignore
        return func

    return decorator
