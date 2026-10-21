"""Tonghuashun's public realtime snapshot as a realtime data provider."""

from __future__ import annotations

import pandas as pd

from akshare_one.ths.client import ThsClient
from akshare_one.ths.utils import snapshot_frame, to_ths_code

from ..cache import cached
from ..registry import provider
from ..schema import normalize
from .base import RealtimeDataProvider
from .schema import COLUMNS


@provider("realtime", "ths")
class ThsRealtime(RealtimeDataProvider):
    """Adapter for Tonghuashun's public realtime snapshot.

    The host serves one security per request and has no batch endpoint, so a
    symbol is required. Volume arrives in shares and is reported in lots, as
    elsewhere in this package.

    ``timestamp`` is the time the host last priced the security, which is
    what the column promises; a source that states no quote time (EastMoney)
    falls back to the time of the request.
    """

    def __init__(self, symbol: str | None) -> None:
        super().__init__(symbol)
        self.client = ThsClient()

    @cached("realtime")
    def get_current_data(self) -> pd.DataFrame:
        """Get real-time stock data

        Returns:
            pd.DataFrame:
            - symbol
            - price
            - change
            - pct_change
            - timestamp
            - volume
            - amount
            - open
            - high
            - low
            - prev_close
        """
        if not self.symbol:
            raise ValueError("The ths source serves one security per request; pass a symbol.")

        try:
            items = self.client.fetch_snapshot(to_ths_code(self.symbol))
        except Exception as e:
            raise ValueError(f"Failed to get real-time data for {self.symbol}: {e}") from e

        return normalize(snapshot_frame(items, self.symbol, COLUMNS), COLUMNS)
