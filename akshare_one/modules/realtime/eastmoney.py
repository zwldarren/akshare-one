from cachetools import cached
import pandas as pd
import akshare as ak

from ..cache import CACHE_CONFIG
from .base import RealtimeDataProvider


class EastmoneyRealtime(RealtimeDataProvider):
    @cached(
        CACHE_CONFIG["realtime_cache"],
        key=lambda self, symbol=None: f"eastmoney_{symbol if symbol else 'all'}",
    )
    def get_current_data(self) -> pd.DataFrame:
        """获取沪深京A股实时行情数据"""
        raw_df = ak.stock_zh_a_spot_em()
        df = self._clean_spot_data(raw_df)
        if self.symbol:
            df = df[df["symbol"] == self.symbol].reset_index(drop=True)
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
