"""Tonghuashun's snapshot and F10 profile page as an info data provider."""

from __future__ import annotations

import pandas as pd

from akshare_one.ths.client import ThsClient
from akshare_one.ths.utils import f10_listing_date, snapshot_info_frame, to_ths_code

from ..cache import cached
from ..registry import provider
from ..schema import normalize
from .base import InfoDataProvider
from .schema import COLUMNS

#: The F10 page that states the listing date.
_COMPANY_PAGE = "company.html"


@provider("info", "ths")
class ThsInfo(InfoDataProvider):
    """Adapter for Tonghuashun's public snapshot and F10 profile page.

    The snapshot carries the name, the share counts and the market
    capitalisation; the F10 company page carries the listing date. That page
    is a hundred kilobytes of GB18030 text, and a failure to read it leaves
    the listing date empty rather than failing the whole call.
    """

    def __init__(self, symbol: str) -> None:
        super().__init__(symbol)
        self.client = ThsClient()

    @cached("info")
    def get_basic_info(self) -> pd.DataFrame:
        """获取同花顺个股信息

        Returns:
            pd.DataFrame:
            - price
            - symbol
            - name
            - total_shares
            - float_shares
            - total_market_cap
            - float_market_cap
            - industry: 上游快照不提供，始终为 NaN
            - listing_date
        """
        try:
            code = to_ths_code(self.symbol)
            items = self.client.fetch_snapshot(code)
        except Exception as e:
            raise ValueError(f"Failed to fetch basic info for {self.symbol}: {e}") from e

        listing_date = self._listing_date(code)
        return normalize(snapshot_info_frame(items, self.symbol, listing_date, COLUMNS), COLUMNS)

    def _listing_date(self, code: str) -> pd.Timestamp | None:
        """The listing date the F10 company page states, if it can be read."""
        try:
            html = self.client.fetch_f10(code, _COMPANY_PAGE)
        except Exception:
            return None
        return f10_listing_date(html)
