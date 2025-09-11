import akshare as ak  # type: ignore
import pandas as pd

from ..cache import cache
from ..utils import convert_xieqiu_symbol
from .base import InsiderDataProvider


class XueQiuInsider(InsiderDataProvider):
    """Provider for XueQiu insider trading data"""

    @cache(
        "financial_cache",
        key=lambda self: f"xueqiu_insider_{self.symbol if self.symbol else 'all'}",
    )
    def get_inner_trade_data(self) -> pd.DataFrame:
        """获取雪球内部交易数据

        Args:
            symbol: 可选股票代码，如"600000"，不传则返回所有数据

        Returns:
            Standardized DataFrame with insider trading data:
            - symbol: 股票代码
            - name: 股票名称
            - change_date: 变动日期
            - insider: 变动人
            - shares_changed: 变动股数
            - avg_price: 成交均价
            - shares_after: 变动后持股数
            - relationship: 与董监高关系
            - position: 董监高职务
        """
        raw_df = ak.stock_inner_trade_xq()
        if self.symbol:
            xueqiu_symbol = convert_xieqiu_symbol(self.symbol)
            raw_df = raw_df[raw_df["股票代码"] == xueqiu_symbol]
        return self._clean_insider_data(raw_df)

    def _clean_insider_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """清理和标准化内部交易数据

        Args:
            raw_df: Raw DataFrame from XueQiu API

        Returns:
            Standardized DataFrame with consistent columns
        """
        column_mapping = {
            "股票代码": "symbol",
            "股票名称": "issuer",
            "变动人": "name",
            "董监高职务": "title",
            "变动日期": "transaction_date",
            "变动股数": "transaction_shares",
            "成交均价": "transaction_price_per_share",
            "变动后持股数": "shares_owned_after_transaction",
            "与董监高关系": "relationship",
        }

        df = raw_df.rename(columns=column_mapping)

        # Convert symbol back to original format (remove SH/SZ prefix)
        if "symbol" in df.columns:
            df["symbol"] = df["symbol"].str.replace(r"^[A-Z]{2}", "", regex=True)

        # Add is_board_director column
        df["is_board_director"] = df["title"].str.contains("董事")

        # Calculate transaction_value
        if (
            "transaction_shares" in df.columns
            and "transaction_price_per_share" in df.columns
        ):
            df["transaction_value"] = (
                df["transaction_shares"] * df["transaction_price_per_share"]
            )

        # Add shares_owned_before_transaction if possible
        if (
            "shares_owned_after_transaction" in df.columns
            and "transaction_shares" in df.columns
        ):
            df["shares_owned_before_transaction"] = (
                df["shares_owned_after_transaction"] - df["transaction_shares"]
            )

        # Convert date format
        if "transaction_date" in df.columns:
            df["transaction_date"] = pd.to_datetime(
                df["transaction_date"]
            ).dt.tz_localize("Asia/Shanghai")

        if "filing_date" in df.columns:
            df["filing_date"] = pd.to_datetime(df["filing_date"]).dt.tz_localize(
                "Asia/Shanghai"
            )

        # Convert numeric columns
        numeric_cols = [
            "transaction_shares",
            "transaction_price_per_share",
            "transaction_value",
            "shares_owned_before_transaction",
            "shares_owned_after_transaction",
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df.reset_index(drop=True)
