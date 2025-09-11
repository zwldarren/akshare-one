import akshare as ak  # type: ignore
import pandas as pd

from ..cache import cache
from .base import HistoricalDataProvider


class EastMoneyHistorical(HistoricalDataProvider):
    """Adapter for EastMoney historical stock data API"""

    @cache(
        "hist_data_cache",
        key=lambda self: (
            f"eastmoney_hist_{self.symbol}_{self.interval}_{self.interval_multiplier}_{self.adjust}"
        ),
    )
    def get_hist_data(self) -> pd.DataFrame:
        """Fetches EastMoney historical market data

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
            if self.interval in ["minute", "hour"]:
                df = self._get_intraday_data()
            else:
                df = self._get_daily_plus_data()

            return df
        except Exception as e:
            raise ValueError(f"Failed to fetch historical data: {str(e)}") from e

    def _get_intraday_data(self) -> pd.DataFrame:
        """Fetches intraday data at minute or hour intervals"""
        # Set trading hours
        start_date = self._ensure_time_format(self.start_date, "09:30:00")
        end_date = self._ensure_time_format(self.end_date, "15:00:00")

        # Get raw data
        period = "1" if self.interval == "minute" else "60"
        raw_df = ak.stock_zh_a_hist_min_em(
            symbol=self.symbol,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust=self._map_adjust_param(self.adjust),
        )

        # Process data
        resampled = self._resample_intraday_data(
            raw_df,
            f"{self.interval_multiplier}min"
            if self.interval == "minute"
            else f"{self.interval_multiplier}h",
        )
        return self._clean_minute_data(resampled, str(self.interval_multiplier))

    def _get_daily_plus_data(self) -> pd.DataFrame:
        """Fetches daily and higher-level data (day/week/month/year)"""
        start_date = self._convert_date_format(self.start_date)
        end_date = self._convert_date_format(self.end_date)

        period_map = {
            "day": "daily",
            "week": "weekly",
            "month": "monthly",
            "year": "monthly",
        }
        period = period_map[self.interval]

        raw_df = ak.stock_zh_a_hist(
            symbol=self.symbol,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust=self._map_adjust_param(self.adjust),
        )

        if self.interval == "year":
            self.interval_multiplier *= 12

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

    def _ensure_time_format(self, date_str: str, default_time: str) -> str:
        """Ensures the date string includes the time part"""
        if " " not in date_str:
            return f"{date_str} {default_time}"
        return date_str

    def _convert_date_format(self, date_str: str) -> str:
        """Converts date format from YYYY-MM-DD to YYYYMMDD"""
        return date_str.replace("-", "") if "-" in date_str else date_str

    def _map_adjust_param(self, adjust: str) -> str:
        """Maps adjustment parameters to the required format"""
        return adjust if adjust != "none" else ""

    def _resample_intraday_data(self, df: pd.DataFrame, freq: str) -> pd.DataFrame:
        """Resamples intraday data to the specified frequency"""
        df["时间"] = pd.to_datetime(df["时间"])
        df = df.set_index("时间")
        resampled = df.resample(freq).agg(
            {
                "开盘": "first",
                "最高": "max",
                "最低": "min",
                "收盘": "last",
                "成交量": "sum",
                "成交额": "sum",
            }
        )
        return resampled.reset_index()

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

        df["日期"] = pd.to_datetime(df["日期"])
        df = df.set_index("日期")
        resampled = df.resample(freq).agg(
            {
                "开盘": "first",
                "最高": "max",
                "最低": "min",
                "收盘": "last",
                "成交量": "sum",
            }
        )
        return resampled.reset_index()

    def _clean_minute_data(self, raw_df: pd.DataFrame, period: str) -> pd.DataFrame:
        """Cleans and standardizes minute/hour level data"""
        column_map = {
            "1": {
                "时间": "timestamp",
                "开盘": "open",
                "收盘": "close",
                "最高": "high",
                "最低": "low",
                "成交量": "volume",
                "成交额": "amount",
                "均价": "vwap",
            },
            "default": {
                "时间": "timestamp",
                "开盘": "open",
                "收盘": "close",
                "最高": "high",
                "最低": "low",
                "涨跌幅": "pct_change",
                "涨跌额": "change",
                "成交量": "volume",
                "成交额": "amount",
                "振幅": "amplitude",
                "换手率": "turnover",
            },
        }

        mapping = column_map["1"] if period == "1" else column_map["default"]
        df = raw_df.rename(columns=mapping)

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize(
                "Asia/Shanghai"
            )

        return self._select_standard_columns(df)

    def _clean_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes daily and higher-level data"""
        column_map = {
            "日期": "timestamp",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
        }

        available_columns = {
            src: target for src, target in column_map.items() if src in raw_df.columns
        }

        if not available_columns:
            raise ValueError("Expected columns not found in raw data")

        df = raw_df.rename(columns=available_columns)

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
