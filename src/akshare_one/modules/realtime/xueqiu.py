import akshare as ak  # type: ignore
import pandas as pd

from ..cache import cache
from ..utils import convert_xieqiu_symbol
from .base import RealtimeDataProvider


class XueQiuRealtime(RealtimeDataProvider):
    @cache(
        "realtime_cache",
        key=lambda self: f"xueqiu_{self.symbol}",
    )
    def get_current_data(self) -> pd.DataFrame:
        """获取雪球实时行情数据

        Args:
            symbol: 股票代码 ("600000")

        Returns:
            pd.DataFrame with columns:
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
        raw_df = ak.stock_individual_spot_xq(symbol=convert_xieqiu_symbol(self.symbol))

        # Transform to match standard format
        data = {
            "symbol": self.symbol,
            "price": float(raw_df.loc[raw_df["item"] == "现价", "value"].values[0]),
            "change": float(raw_df.loc[raw_df["item"] == "涨跌", "value"].values[0]),
            "pct_change": float(
                raw_df.loc[raw_df["item"] == "涨幅", "value"].values[0]
            ),
            "timestamp": pd.to_datetime(
                raw_df.loc[raw_df["item"] == "时间", "value"].values[0]
            ).tz_localize("Asia/Shanghai"),
            "volume": int(raw_df.loc[raw_df["item"] == "成交量", "value"].values[0])
            / 100,
            "amount": float(raw_df.loc[raw_df["item"] == "成交额", "value"].values[0]),
            "open": float(raw_df.loc[raw_df["item"] == "今开", "value"].values[0]),
            "high": float(raw_df.loc[raw_df["item"] == "最高", "value"].values[0]),
            "low": float(raw_df.loc[raw_df["item"] == "最低", "value"].values[0]),
            "prev_close": float(
                raw_df.loc[raw_df["item"] == "昨收", "value"].values[0]
            ),
        }

        return pd.DataFrame([data])
