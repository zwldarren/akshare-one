import akshare as ak  # type: ignore
import pandas as pd

from ..cache import cache
from .base import HistoricalDataProvider


class SinaHistorical(HistoricalDataProvider):
    """Adapter for Sina historical stock data API"""

    @cache(
        "hist_data_cache",
        key=lambda self: (
            f"sina_hist_{self.symbol}_{self.interval}_{self.interval_multiplier}_{self.adjust}"
        ),
    )
    def get_hist_data(self) -> pd.DataFrame:
        """Fetches Sina historical market data

        Returns:
            pd.DataFrame:
                - timestamp
                - open
                - high
                - low
                - close
                - volume
        """
        self.interval = self.interval.lower()
        self._validate_interval_params(self.interval, self.interval_multiplier)

        try:
            stock = (
                f"sh{self.symbol}"
                if not self.symbol.startswith(("sh", "sz", "bj"))
                else self.symbol
            )

            if self.interval == "minute":
                df = self._get_minute_data(stock)
            elif self.interval == "hour":
                df = self._get_hour_data(stock)
            else:
                df = self._get_daily_plus_data(stock)

            return df
        except Exception as e:
            raise ValueError(f"Failed to fetch historical data: {str(e)}") from e

    def _get_minute_data(self, stock: str) -> pd.DataFrame:
        """Fetches minute level data"""
        raw_df = ak.stock_zh_a_minute(
            symbol=stock,
            period="1",
            adjust=self._map_adjust_param(self.adjust),
        )
        raw_df = raw_df.rename(columns={"day": "date"})
        raw_df["date"] = pd.to_datetime(raw_df["date"])
        raw_df = raw_df.set_index("date")
        raw_df = (
            raw_df.resample(f"{self.interval_multiplier}min")
            .agg(
                {
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum",
                }
            )
            .reset_index()
        )
        return self._clean_minute_data(raw_df)

    def _get_hour_data(self, stock: str) -> pd.DataFrame:
        """Fetches hour level data"""
        if self.interval_multiplier < 1:
            raise ValueError("Hour interval multiplier must be >= 1")

        raw_df = ak.stock_zh_a_minute(
            symbol=stock,
            period="60",
            adjust=self._map_adjust_param(self.adjust),
        )
        raw_df = raw_df.rename(columns={"day": "date"})
        raw_df["date"] = pd.to_datetime(raw_df["date"])
        raw_df = raw_df.set_index("date")
        raw_df = (
            raw_df.resample(f"{self.interval_multiplier}h")
            .agg(
                {
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum",
                }
            )
            .reset_index()
        )
        return self._clean_minute_data(raw_df)

    def _get_b_share_data(self, stock: str) -> pd.DataFrame:
        """Fetches B-share historical data"""
        start_date = self._convert_date_format(self.start_date)
        end_date = self._convert_date_format(self.end_date)

        if self.interval in ["minute", "hour"]:
            period = "1" if self.interval == "minute" else "60"
            raw_df = ak.stock_zh_b_minute(
                symbol=stock,
                period=period,
                adjust=self._map_adjust_param(self.adjust),
            )
            # Rename 'day' to 'date' for consistency
            raw_df = raw_df.rename(columns={"day": "date"})

            if self.interval_multiplier > 1:
                raw_df = self._resample_data(
                    raw_df, self.interval, self.interval_multiplier
                )
        else:
            raw_df = ak.stock_zh_b_daily(
                symbol=stock,
                start_date=start_date,
                end_date=end_date,
                adjust=self._map_adjust_param(self.adjust),
            )
            if self.interval_multiplier > 1:
                raw_df = self._resample_data(
                    raw_df, self.interval, self.interval_multiplier
                )

        return self._clean_data(raw_df)

    def _get_daily_plus_data(self, stock: str) -> pd.DataFrame:
        """Fetches daily and higher-level data (day/week/month/year)"""
        # Check if it's a B-share symbol
        if stock.startswith(("sh9", "sz2")):
            return self._get_b_share_data(stock)

        start_date = self._convert_date_format(self.start_date)
        end_date = self._convert_date_format(self.end_date)

        raw_df = ak.stock_zh_a_daily(
            symbol=stock,
            start_date=start_date,
            end_date=end_date,
            adjust=self._map_adjust_param(self.adjust),
        )

        if self.interval_multiplier > 1:
            raw_df = self._resample_data(
                raw_df, self.interval, self.interval_multiplier
            )

        return self._clean_data(raw_df)

    def _validate_interval_params(self, interval: str, multiplier: int) -> None:
        """Validates the validity of interval and multiplier"""
        if interval not in self.get_supported_intervals():
            raise ValueError(f"Unsupported interval parameter: {interval}")

        if interval in ["minute", "hour"] and multiplier < 1:
            raise ValueError(f"interval_multiplier for {interval} level must be ≥ 1")

    def _convert_date_format(self, date_str: str) -> str:
        """Converts date format from YYYY-MM-DD to YYYYMMDD"""
        return date_str.replace("-", "") if "-" in date_str else date_str

    def _map_adjust_param(self, adjust: str) -> str:
        """Maps adjustment parameters to the required format"""
        return adjust if adjust != "none" else ""

    def _resample_data(
        self, df: pd.DataFrame, interval: str, multiplier: int
    ) -> pd.DataFrame:
        """Resamples daily and higher-level data to the specified interval"""
        freq_map = {
            "day": f"{multiplier}D",
            "week": f"{multiplier}W-MON",
            "month": f"{multiplier}MS",
            "year": f"{multiplier}AS-JAN",
        }
        freq = freq_map[interval]

        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")
        resampled = df.resample(freq).agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }
        )
        return resampled.reset_index()

    def _clean_minute_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes minute/hour level data"""
        column_map = {
            "date": "timestamp",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
        }

        df = raw_df.rename(columns=column_map)

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize(
                "Asia/Shanghai"
            )

        return self._select_standard_columns(df)

    def _clean_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes daily and higher-level data"""
        column_map = {
            "date": "timestamp",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
        }

        df = raw_df.rename(columns=column_map)

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize(
                "Asia/Shanghai"
            )

        if "volume" in df.columns:
            df["volume"] = df["volume"].astype("int64")

        return self._select_standard_columns(df)

    def _select_standard_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Selects and orders the standard output columns"""
        standard_columns = [
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
        return df[[col for col in standard_columns if col in df.columns]]
