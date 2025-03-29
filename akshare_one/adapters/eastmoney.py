from typing import Optional
import pandas as pd
import akshare as ak


class EastMoneyAdapter:
    """Adapter for EastMoney historical stock data API"""

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
        elif interval == "day":
            period = "daily"
        elif interval == "week":
            period = "weekly"
        elif interval == "month":
            period = "monthly"
        elif interval == "year":
            period = "monthly"  # use monthly for yearly data
            interval_multiplier *= 12
        else:
            raise ValueError(
                f"Unsupported interval: {interval}. For minute/hour data, please use other APIs"
            )

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

        # Standardize the data format
        return self._clean_data(raw_df)

    def get_realtime_data(self, symbol: Optional[str] = None) -> pd.DataFrame:
        """获取沪深京A股实时行情数据"""
        raw_df = ak.stock_zh_a_spot_em()
        df = self._clean_spot_data(raw_df)
        if symbol:
            df = df[df["symbol"] == symbol]
        return df

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
            "is_adjusted",
        ]
        return df[[col for col in standard_columns if col in df.columns]]

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
