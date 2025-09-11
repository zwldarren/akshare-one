from abc import ABC, abstractmethod

import pandas as pd


class NewsDataProvider(ABC):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol

    @abstractmethod
    def get_news_data(self) -> pd.DataFrame:
        """Fetches news data for given symbol

        Returns:
            pd.DataFrame:
            - keyword: 关键词
            - title: 新闻标题
            - content: 新闻内容
            - publish_time: 发布时间
            - source: 文章来源
            - url: 新闻链接
        """
        pass
