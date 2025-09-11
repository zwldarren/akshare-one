import os
from collections.abc import Callable
from typing import Any, TypeVar

from cachetools import TTLCache, cached

F = TypeVar("F", bound=Callable[..., Any])

# 缓存配置
CACHE_CONFIG: dict[str, TTLCache[Any, Any]] = {
    "hist_data_cache": TTLCache(maxsize=1000, ttl=3600),  # 历史数据缓存1小时
    "realtime_cache": TTLCache(maxsize=500, ttl=60),  # 实时数据缓存1分钟
    "news_cache": TTLCache(maxsize=500, ttl=3600),  # 新闻数据缓存1小时
    "financial_cache": TTLCache(maxsize=500, ttl=86400),  # 财务数据缓存24小时
    "info_cache": TTLCache(maxsize=500, ttl=86400),  # 信息数据缓存24小时
}


def cache(cache_key: str, key: Callable[..., Any] | None = None) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache_enabled = os.getenv("AKSHARE_ONE_CACHE_ENABLED", "true").lower() in (
                "1",
                "true",
                "yes",
                "on",
            )

            if cache_enabled:
                if cache_key not in CACHE_CONFIG:
                    raise KeyError(
                        f"Cache configuration '{cache_key}' not found. "
                        f"Available keys: {list(CACHE_CONFIG.keys())}"
                    )
                if key is not None:
                    return cached(CACHE_CONFIG[cache_key], key=key)(func)(
                        *args, **kwargs
                    )
                else:
                    return cached(CACHE_CONFIG[cache_key])(func)(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator
