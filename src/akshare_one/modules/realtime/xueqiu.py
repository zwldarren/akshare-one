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

        # Convert to dictionary for easier lookup
        data_map = dict(zip(raw_df["item"], raw_df["value"], strict=True))

        def _get_value(key: str, type_func: type = float) -> float | str:
            val = data_map.get(key)
            if val is None:
                return 0.0 if type_func in (float, int) else ""
            try:
                return type_func(val)
            except (ValueError, TypeError):
                return 0.0 if type_func in (float, int) else ""

        # Transform to match standard format
        data = {
            "symbol": self.symbol,
            "price": _get_value("现价"),
            "change": _get_value("涨跌"),
            "pct_change": _get_value("涨幅"),
            "timestamp": pd.to_datetime(_get_value("时间", str)).tz_localize(
                "Asia/Shanghai"
            ),
            "volume": float(_get_value("成交量", int)) / 100,
            "amount": _get_value("成交额"),
            "open": _get_value("今开"),
            "high": _get_value("最高"),
            "low": _get_value("最低"),
            "prev_close": _get_value("昨收"),
        }

        return pd.DataFrame([data])
