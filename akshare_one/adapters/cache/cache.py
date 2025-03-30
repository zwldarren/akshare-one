from cachetools import TTLCache

# 缓存配置
CACHE_CONFIG = {
    'hist_data_cache': TTLCache(maxsize=1000, ttl=3600),  # 历史数据缓存1小时
    'realtime_cache': TTLCache(maxsize=500, ttl=60),      # 实时数据缓存1分钟 
    'news_cache': TTLCache(maxsize=500, ttl=3600),
    'financial_cache': TTLCache(maxsize=500, ttl=86400),  # 财务数据缓存24小时
}
