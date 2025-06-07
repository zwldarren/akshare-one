import pandas as pd
from cachetools import cached
from .base import RealtimeDataProvider
from ..cache import CACHE_CONFIG
from ..eastmoney.client import EastMoneyClient
from ..eastmoney.utils import parse_realtime_data


class EastMoneyDirectRealtime(RealtimeDataProvider):
    """Direct implementation for EastMoney realtime stock data API"""

    def __init__(self, symbol: str):
        super().__init__(symbol)
        self.client = EastMoneyClient()

    @cached(
        cache=CACHE_CONFIG["realtime_cache"],
        key=lambda self: f"eastmoney_direct_realtime_{self.symbol}",
    )
    def get_current_data(self) -> pd.DataFrame:
        """Get real-time stock data"""
        try:
            raw_data = self.client.fetch_realtime_quote(self.symbol)

            if raw_data.get("rc") != 0:
                raise ValueError(f"API returned error: {raw_data.get('msg')}")

            df = parse_realtime_data(raw_data)

            # Ensure the output matches the base class definition
            if self.symbol:
                df = df[df["symbol"] == self.symbol].reset_index(drop=True)

            return df

        except Exception as e:
            raise ValueError(f"Failed to get real-time data for {self.symbol}: {e}")
