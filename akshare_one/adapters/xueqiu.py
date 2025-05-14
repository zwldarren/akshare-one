from typing import Optional
import pandas as pd
import akshare as ak
from cachetools import cached
from .cache.cache import CACHE_CONFIG


class XueQiuAdapter:
    """Adapter for XueQiu insider trading data API"""

    @cached(
        cache=CACHE_CONFIG,
        key=lambda self, symbol=None: f"xueqiu_{symbol}",
    )
    def get_realtime_data(self, symbol: str) -> pd.DataFrame:
        """获取雪球实时行情数据

        Args:
            symbol: 股票代码 ("600000")

        Returns:
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

        Raises:
            ValueError: 如果symbol格式不正确或API返回错误
        """

        raw_df = ak.stock_individual_spot_xq(symbol=self._convert_symbol(symbol))

        # Transform to match EastMoney format
        data = {
            "symbol": symbol,
            "price": float(raw_df.loc[raw_df["item"] == "现价", "value"].values[0]),
            "change": float(raw_df.loc[raw_df["item"] == "涨跌", "value"].values[0]),
            "pct_change": float(
                raw_df.loc[raw_df["item"] == "涨幅", "value"].values[0]
            ),
            "timestamp": pd.to_datetime(
                raw_df.loc[raw_df["item"] == "时间", "value"].values[0]
            )
            .tz_localize("Asia/Shanghai")
            .tz_convert("UTC"),
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

    @cached(
        CACHE_CONFIG["hist_data_cache"],
        key=lambda self, symbol=None: f"inner_trade_{symbol if symbol else 'all'}",
    )
    def get_inner_trade_data(self, symbol: Optional[str] = None) -> pd.DataFrame:
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
        if symbol:
            raw_df = raw_df[raw_df["股票代码"] == symbol]
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
            df["transaction_date"] = (
                pd.to_datetime(df["transaction_date"])
                .dt.tz_localize("Asia/Shanghai")
                .dt.tz_convert("UTC")
            )

        if "filing_date" in df.columns:
            df["filing_date"] = (
                pd.to_datetime(df["filing_date"])
                .dt.tz_localize("Asia/Shanghai")
                .dt.tz_convert("UTC")
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

        return df

    def _convert_symbol(self, symbol: str) -> str:
        """
        Convert Symbol (600000) to XueQiu Symbol (SH600000)
        """
        if symbol.startswith("6"):
            return f"SH{symbol}"
        elif symbol.startswith("0") or symbol.startswith("3"):
            return f"SZ{symbol}"
        else:  # TODO: add more cases
            return symbol
