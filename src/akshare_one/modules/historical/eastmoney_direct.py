from typing import Any

import pandas as pd

from akshare_one.eastmoney.client import EastMoneyClient
from akshare_one.eastmoney.utils import parse_kline_data, resample_historical_data

from ..cache import cache
from .base import HistoricalDataProvider


class EastMoneyDirectHistorical(HistoricalDataProvider):
    """Direct implementation for EastMoney historical stock data API"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.client = EastMoneyClient()

    @cache(
        "hist_data_cache",
        key=lambda self: (
            f"eastmoney_direct_hist_{self.symbol}_{self.interval}_{self.interval_multiplier}_{self.adjust}"
        ),
    )
    def get_hist_data(self) -> pd.DataFrame:
        """Fetches EastMoney historical market data directly from API"""
        self.interval = self.interval.lower()
        self._validate_interval_params()

        try:
            klt = self._get_kline_type()
            fqt = self._get_adjust_type()
            start_date = self.start_date.replace("-", "")
            end_date = self.end_date.replace("-", "")

            raw_data = self.client.fetch_historical_klines(
                symbol=self.symbol,
                klt=klt,
                fqt=fqt,
                start_date=start_date,
                end_date=end_date,
            )

            if raw_data.get("rc") != 0:
                raise ValueError(f"API returned error: {raw_data.get('msg')}")

            df = parse_kline_data(raw_data)

            df = resample_historical_data(df, self.interval, self.interval_multiplier)

            return df

        except Exception as e:
            raise ValueError(
                f"Failed to fetch historical data for {self.symbol}: {e}"
            ) from e

    def _get_kline_type(self) -> str:
        """Get K-line type based on interval."""
        kline_map = {
            "minute": "1",
            "hour": "60",
            "day": "101",
            "week": "102",
            "month": "103",
            "year": "103",
        }

        base_klt = kline_map.get(self.interval, "101")

        if self.interval == "minute" and self.interval_multiplier in [5, 15, 30, 60]:
            return str(self.interval_multiplier)

        return base_klt

    def _get_adjust_type(self) -> str:
        """Get adjustment type."""
        adjust_map = {"none": "0", "qfq": "1", "hfq": "2"}
        return adjust_map.get(self.adjust, "0")

    def _validate_interval_params(self) -> None:
        """Validates the interval and multiplier."""
        if self.interval not in self.get_supported_intervals():
            raise ValueError(f"Unsupported interval: {self.interval}")
        if self.interval in ["minute", "hour"] and self.interval_multiplier < 1:
            raise ValueError("Interval multiplier must be >= 1 for minute/hour.")
