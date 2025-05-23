"""新闻数据模块

包含股票新闻相关功能
"""

import pandas as pd
from .modules.news.factory import NewsDataFactory


def get_news_data(symbol: str, source: str = "eastmoney") -> "pd.DataFrame":
    """获取个股新闻数据

    Args:
        symbol: 股票代码 (如 "300059")
        source: 数据源 ('eastmoney')

    Returns:
        pd.DataFrame:
        - keyword: 关键词
        - title: 新闻标题
        - content: 新闻内容
        - publish_time: 发布时间
        - source: 文章来源
        - url: 新闻链接
    """
    provider = NewsDataFactory.get_provider(source, symbol=symbol)
    return provider.get_news_data()
