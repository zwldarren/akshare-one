"""Tonghuashun's per-stock timeline as a news data provider."""

from __future__ import annotations

import pandas as pd

from akshare_one.ths.client import ThsClient
from akshare_one.ths.constants import (
    SNAPSHOT_MARKET_ID,
    SOURCE_NEWS,
    SOURCE_REPORT,
    TIMELINE_NEWS,
    TIMELINE_PAGE_SIZE,
    TIMELINE_REPORT,
)
from akshare_one.ths.utils import timeline_frame, to_ths_code

from ..cache import cached
from ..registry import provider
from ..schema import normalize
from .base import NewsDataProvider
from .schema import COLUMNS


@provider("news", "ths")
class ThsNews(NewsDataProvider):
    """Adapter for Tonghuashun's per-stock timeline.

    The timeline is read per security and per market, so the snapshot is read
    first: it says which market the security trades in. News and research
    reports live in two collections; both are read, and the reports are
    labelled apart so a caller can tell them from the news.

    A timeline item carries no publication name and no full article text, so
    ``source`` holds the collection the item came from and ``content`` holds
    the upstream abstract. One page per collection is all the host serves, so
    the answer holds at most ``TIMELINE_PAGE_SIZE`` items of each kind.
    """

    def __init__(self, symbol: str) -> None:
        super().__init__(symbol)
        self.client = ThsClient()

    @cached("news")
    def get_news_data(self) -> pd.DataFrame:
        """获取同花顺个股新闻数据

        Returns:
            pd.DataFrame:
            - keyword
            - title
            - content
            - publish_time
            - source
            - url
        """
        try:
            code = to_ths_code(self.symbol)
            items = self.client.fetch_snapshot(code)
            market_id = items.get(SNAPSHOT_MARKET_ID, "")
            news = self.client.fetch_timeline(market_id, code, TIMELINE_NEWS, TIMELINE_PAGE_SIZE)
            reports = self.client.fetch_timeline(
                market_id, code, TIMELINE_REPORT, TIMELINE_PAGE_SIZE
            )
        except Exception as e:
            raise ValueError(f"Failed to fetch news data for {self.symbol}: {e}") from e

        frame = pd.concat(
            [
                timeline_frame(news, self.symbol, SOURCE_NEWS, COLUMNS),
                timeline_frame(reports, self.symbol, SOURCE_REPORT, COLUMNS),
            ],
            ignore_index=True,
        )
        frame = frame.sort_values("publish_time", ascending=False, ignore_index=True)
        return normalize(frame, COLUMNS)
