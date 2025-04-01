from typing import Optional
import pandas as pd
import akshare as ak
from cachetools import cached
from .cache.cache import CACHE_CONFIG


class EastMoneyAdapter:
    """Adapter for EastMoney historical stock data API"""

    @cached(
        CACHE_CONFIG["hist_data_cache"],
        key=lambda self,
        symbol,
        interval,
        interval_multiplier,
        start_date,
        end_date,
        adjust: ("eastmoney", symbol, interval, interval_multiplier, start_date, end_date, adjust),
    )
    def get_hist_data(
        self,
        symbol: str,
        interval: str = "day",
        interval_multiplier: int = 1,
        start_date: str = "1970-01-01",
        end_date: str = "2030-12-31",
        adjust: str = "none",
    ) -> pd.DataFrame:
        """获取东方财富历史行情数据

        Args:
            symbol: Unified symbol format (e.g. '600000')
            interval: Time granularity ('second','minute','hour','day','week','month','year')
            interval_multiplier: Interval multiplier (e.g. 5 for 5 minutes)
            start_date: Start date in YYYY-MM-DD format (will be converted to YYYYMMDD)
            end_date: End date in YYYY-MM-DD format (will be converted to YYYYMMDD)
            adjust: Adjustment type ('none','qfq','hfq')

        Returns:
           Standardized DataFrame with OHLCV data
        """
        # Map standard interval to akshare supported periods
        interval = interval.lower()
        if interval == "second":
            raise ValueError("EastMoney does not support second-level data")
        elif interval == "minute":
            if interval_multiplier < 1:
                raise ValueError("Minute interval multiplier must be >= 1")

            start_date = (
                f"{start_date} 09:30:00" if " " not in start_date else start_date
            )
            end_date = f"{end_date} 15:00:00" if " " not in end_date else end_date

            raw_df = ak.stock_zh_a_hist_min_em(
                symbol=symbol,
                period="1",
                start_date=start_date,
                end_date=end_date,
                adjust=adjust if adjust != "none" else "",
            )
            # Resample the data to the desired minute interval
            raw_df["时间"] = pd.to_datetime(raw_df["时间"])
            raw_df = raw_df.set_index("时间")
            resampled = raw_df.resample(f"{interval_multiplier}min").agg(
                {
                    "开盘": "first",
                    "最高": "max",
                    "最低": "min",
                    "收盘": "last",
                    "成交量": "sum",
                    "成交额": "sum",
                }
            )
            raw_df = resampled.reset_index()
            return self._clean_minute_data(raw_df, str(interval_multiplier))
        elif interval == "hour":
            if interval_multiplier < 1:
                raise ValueError("Hour interval multiplier must be >= 1")

            start_date = (
                f"{start_date} 09:30:00" if " " not in start_date else start_date
            )
            end_date = f"{end_date} 15:00:00" if " " not in end_date else end_date

            raw_df = ak.stock_zh_a_hist_min_em(
                symbol=symbol,
                period="60",
                start_date=start_date,
                end_date=end_date,
                adjust=adjust if adjust != "none" else "",
            )

            # Resample the data to the desired hour interval
            raw_df["时间"] = pd.to_datetime(raw_df["时间"])
            raw_df = raw_df.set_index("时间")
            resampled = raw_df.resample(f"{interval_multiplier}h").agg(
                {
                    "开盘": "first",
                    "最高": "max",
                    "最低": "min",
                    "收盘": "last",
                    "成交量": "sum",
                    "成交额": "sum",
                }
            )
            raw_df = resampled.reset_index()

            return self._clean_minute_data(raw_df, f"{interval_multiplier}H")
        elif interval == "day":
            period = "daily"
        elif interval == "week":
            period = "weekly"
        elif interval == "month":
            period = "monthly"
        elif interval == "year":
            period = "monthly"  # use monthly for yearly data
            interval_multiplier = 12 * interval_multiplier
        else:
            raise ValueError(f"Unsupported interval: {interval}")

        # Convert date format from YYYY-MM-DD to YYYYMMDD if needed
        start_date = start_date.replace("-", "") if "-" in start_date else start_date
        end_date = end_date.replace("-", "") if "-" in end_date else end_date

        # Fetch raw data from akshare
        raw_df = ak.stock_zh_a_hist(
            symbol=symbol,
            period=period,  # daily/weekly/monthly
            start_date=start_date,
            end_date=end_date,
            adjust=adjust if adjust != "none" else "",
        )

        if interval_multiplier > 1:
            raw_df = self._resample_data(raw_df, interval, interval_multiplier)

        # Standardize the data format
        return self._clean_data(raw_df)

    @cached(CACHE_CONFIG["realtime_cache"], key=lambda self, symbol=None: f"eastmoney_{symbol if symbol else 'all'}")
    def get_realtime_data(self, symbol: Optional[str] = None) -> pd.DataFrame:
        """获取沪深京A股实时行情数据"""
        raw_df = ak.stock_zh_a_spot_em()
        df = self._clean_spot_data(raw_df)
        if symbol:
            df = df[df["symbol"] == symbol]
        return df

    def _resample_data(
        self, df: pd.DataFrame, interval: str, multiplier: int
    ) -> pd.DataFrame:
        """Resample the data based on the given interval and multiplier"""
        if interval == "day":
            freq = f"{multiplier}D"
        elif interval == "week":
            freq = f"{multiplier}W-MON"
        elif interval == "month":
            freq = f"{multiplier}MS"
        elif interval == "year":
            freq = f"{multiplier}AS-JAN"

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
        if period == "1":
            column_mapping = {
                "时间": "timestamp",
                "开盘": "open",
                "收盘": "close",
                "最高": "high",
                "最低": "low",
                "成交量": "volume",
                "成交额": "amount",
                "均价": "vwap",
            }
        else:
            column_mapping = {
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
            }

        df = raw_df.rename(columns=column_mapping)

        if "timestamp" in df.columns:
            df["timestamp"] = (
                pd.to_datetime(df["timestamp"])
                .dt.tz_localize("Asia/Shanghai")
                .dt.tz_convert("UTC")
            )
        standard_columns = [
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
        return df[[col for col in standard_columns if col in df.columns]]

    def _clean_data(self, raw_df: pd.DataFrame, adjust: str = "none") -> pd.DataFrame:
        """清理和标准化历史数据格式

        Args:
            raw_df: Raw DataFrame from EastMoney API
            adjust: Adjustment type ('none','qfq','hfq')

        Returns:
            Standardized DataFrame with consistent columns
        """
        # Check if required columns exist in raw data
        required_columns = {
            "日期": "timestamp",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
        }

        # Find available columns in raw data
        available_columns = {}
        for src_col, target_col in required_columns.items():
            if src_col in raw_df.columns:
                available_columns[src_col] = target_col

        if not available_columns:
            raise ValueError("Raw data does not contain any expected columns")

        # Rename available columns
        df = raw_df.rename(columns=available_columns)

        # Process timestamp if available
        if "timestamp" in df.columns:
            df = df.assign(
                timestamp=lambda x: pd.to_datetime(x["timestamp"])
                .dt.tz_localize("Asia/Shanghai")
                .dt.tz_convert("UTC")
            )

        # Process volume if available
        if "volume" in df.columns:
            df = df.assign(volume=lambda x: x["volume"].astype("int64"))

        # Process adjustment flag
        if adjust != "none":
            df = df.assign(is_adjusted=lambda x: x["adjust"] != "none")
        else:
            df = df.assign(is_adjusted=False)

        # Select available standardized columns
        standard_columns = [
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
        return df[[col for col in standard_columns if col in df.columns]]

    @cached(CACHE_CONFIG["news_cache"], key=lambda self, symbol: f"eastmoney_{symbol}")
    def get_news_data(self, symbol: str) -> pd.DataFrame:
        """获取东方财富个股新闻数据"""
        raw_df = ak.stock_news_em(symbol=symbol)

        column_mapping = {
            "关键词": "keyword",
            "新闻标题": "title",
            "新闻内容": "content",
            "发布时间": "publish_time",
            "文章来源": "source",
            "新闻链接": "url",
        }

        df = raw_df.rename(columns=column_mapping)

        if "publish_time" in df.columns:
            df = df.assign(
                publish_time=lambda x: pd.to_datetime(x["publish_time"])
                .dt.tz_localize("Asia/Shanghai")
                .dt.tz_convert("UTC")
            )

        return df

    def _clean_spot_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """清理和标准化实时行情数据"""

        column_mapping = {
            "代码": "symbol",
            "最新价": "price",
            "涨跌额": "change",
            "涨跌幅": "pct_change",
            "成交量": "volume",
            "成交额": "amount",
            "今开": "open",
            "最高": "high",
            "最低": "low",
            "昨收": "prev_close",
        }

        df = raw_df.rename(columns=column_mapping)

        # Change time to UTC
        df = df.assign(
            timestamp=lambda x: pd.Timestamp.now(tz="Asia/Shanghai").tz_convert("UTC")
        )

        required_columns = [
            "symbol",
            "price",
            "change",
            "pct_change",
            "timestamp",
            "volume",
            "amount",
            "open",
            "high",
            "low",
            "prev_close",
        ]
        return df[required_columns]
