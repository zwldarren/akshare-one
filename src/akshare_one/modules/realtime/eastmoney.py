import akshare as ak
import pandas as pd

from akshare_one.eastmoney.client import EastMoneyClient
from akshare_one.eastmoney.utils import parse_realtime_data

from ..cache import cache
from ..registry import provider
from .base import RealtimeDataProvider


@provider("realtime", "eastmoney")
class EastmoneyRealtime(RealtimeDataProvider):
    """Realtime A-share quotes.

    For a single ``symbol`` this asks EastMoney for just that quote. The full
    A-share snapshot (``stock_zh_a_spot_em``) is only fetched when no symbol is
    given, because it downloads ~5,500 rows across dozens of paged requests.
    """

    def __init__(self, symbol: str | None) -> None:
        super().__init__(symbol)
        self.client = EastMoneyClient()

    @cache(
        "realtime_cache",
        key=lambda self: f"eastmoney_{self.symbol if self.symbol else 'all'}",
    )
    def get_current_data(self) -> pd.DataFrame:
        """获取沪深京A股实时行情数据

        Returns:
            pd.DataFrame:
            - symbol: 股票代码
            - price: 最新价
            - change: 涨跌额
            - pct_change: 涨跌幅(%)
            - timestamp: 时间戳
            - volume: 成交量(手)
            - amount: 成交额(元)
            - open: 今开
            - high: 最高
            - low: 最低
            - prev_close: 昨收
        """
        if self.symbol:
            raw = self.client.fetch_realtime_quote(self.symbol)
            if raw.get("rc") != 0 or not raw.get("data"):
                raise ValueError(f"No realtime data found for symbol {self.symbol}")
            return parse_realtime_data(raw)

        raw_df = ak.stock_zh_a_spot_em()
        return self._clean_spot_data(raw_df)

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

        df = df.assign(timestamp=lambda x: pd.Timestamp.now(tz="Asia/Shanghai"))

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
