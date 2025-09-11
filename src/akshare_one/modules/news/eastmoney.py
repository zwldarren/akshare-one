import akshare as ak  # type: ignore
import pandas as pd

from ..cache import cache
from .base import NewsDataProvider


class EastMoneyNews(NewsDataProvider):
    @cache(
        "news_cache",
        key=lambda self: f"eastmoney_news_{self.symbol}",
    )
    def get_news_data(self) -> pd.DataFrame:
        """获取东方财富个股新闻数据"""
        raw_df = ak.stock_news_em(symbol=self.symbol)
        return self._clean_news_data(raw_df)

    def _clean_news_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """清理和标准化新闻数据"""
        column_mapping = {
            "关键词": "keyword",
            "新闻标题": "title",
            "新闻内容": "content",
            "发布时间": "publish_time",
            "文章来源": "source",
            "新闻链接": "url",
        }

        df = raw_df.rename(columns=column_mapping)

        df["publish_time"] = pd.to_datetime(df["publish_time"]).dt.tz_localize(
            "Asia/Shanghai"
        )

        required_columns = [
            "keyword",
            "title",
            "content",
            "publish_time",
            "source",
            "url",
        ]
        return df[required_columns]
