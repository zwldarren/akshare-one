import pandas as pd

from akshare_one.eastmoney.client import EastMoneyClient
from akshare_one.eastmoney.utils import parse_basic_info

from ..cache import cache
from ..registry import provider
from .base import InfoDataProvider


@provider("info", "eastmoney")
class EastmoneyInfo(InfoDataProvider):
    """Basic stock info from EastMoney's direct quote API.

    This used to go through ``akshare.stock_individual_info_em``, which hits
    ``push2.eastmoney.com`` directly and therefore broke whenever that host
    answered with a gateway error. The direct client falls back across hosts.
    """

    def __init__(self, symbol: str) -> None:
        super().__init__(symbol)
        self.client = EastMoneyClient()

    @cache(
        "info_cache",
        key=lambda self: f"eastmoney_{self.symbol}",
    )
    def get_basic_info(self) -> pd.DataFrame:
        """获取东方财富个股信息

        Returns:
            pd.DataFrame:
            - price: 最新价
            - symbol: 股票代码
            - name: 股票简称
            - total_shares: 总股本
            - float_shares: 流通股
            - total_market_cap: 总市值
            - float_market_cap: 流通市值
            - industry: 行业
            - listing_date: 上市时间
        """
        try:
            raw = self.client.fetch_basic_info(self.symbol)
        except Exception as e:
            raise ValueError(f"Failed to fetch basic info for {self.symbol}: {e}") from e

        if raw.get("rc") != 0 or not raw.get("data"):
            raise ValueError(f"No basic info found for symbol {self.symbol}")

        return parse_basic_info(raw)
