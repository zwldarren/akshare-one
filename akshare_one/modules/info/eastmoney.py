from cachetools import cached
import pandas as pd
import akshare as ak

from ..cache import CACHE_CONFIG
from .base import InfoDataProvider


class EastmoneyInfo(InfoDataProvider):
    _rename_map = {
        "最新": "price",
        "股票代码": "symbol",
        "股票简称": "name",
        "总股本": "total_shares",
        "流通股": "float_shares",
        "总市值": "total_market_cap",
        "流通市值": "float_market_cap",
        "行业": "industry",
        "上市时间": "listing_date",
    }

    @cached(
        CACHE_CONFIG["info_cache"],
        key=lambda self, symbol=None: f"eastmoney_{symbol}",
    )
    def get_info(self) -> pd.DataFrame:
        """获取东方财富个股信息"""
        info_df = ak.stock_individual_info_em(symbol=self.symbol)
        info_df = info_df.set_index("item").T
        info_df.reset_index(drop=True, inplace=True)
        info_df.rename(columns=self._rename_map, inplace=True)

        if "symbol" in info_df.columns:
            info_df["symbol"] = info_df["symbol"].astype(str)

        if "listing_date" in info_df.columns:
            info_df["listing_date"] = pd.to_datetime(
                info_df["listing_date"], format="%Y%m%d"
            )

        numeric_cols = [
            "price",
            "total_shares",
            "float_shares",
            "total_market_cap",
            "float_market_cap",
        ]
        for col in numeric_cols:
            if col in info_df.columns:
                info_df[col] = pd.to_numeric(info_df[col], errors="coerce")

        return info_df
