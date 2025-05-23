from abc import ABC, abstractmethod
import pandas as pd


def validate_news_data(func):
    """Decorator to validate news data returned by data providers"""

    def wrapper(*args, **kwargs):
        df = func(*args, **kwargs)

        if not isinstance(df, pd.DataFrame):
            raise ValueError("Returned data must be a pandas DataFrame")

        # Required fields
        required_fields = {"title", "publish_time"}
        if not required_fields & set(df.columns):
            raise ValueError(f"Must contain all required fields: {required_fields}")

        # Validate publish_time if present
        if "publish_time" in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df["publish_time"]):
                raise ValueError("publish_time must be datetime64 dtype")
            if (
                df["publish_time"].dt.tz is None
                or str(df["publish_time"].dt.tz) != "UTC"
            ):
                raise ValueError("publish_time must be in UTC timezone")

        return df

    return wrapper


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
            - publish_time: 发布时间 (UTC)
            - source: 文章来源
            - url: 新闻链接
        """
        pass
