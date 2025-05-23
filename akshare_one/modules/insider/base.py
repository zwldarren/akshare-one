from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional


def validate_insider_data(func):
    """Decorator to validate insider trading data returned by data providers"""

    def wrapper(*args, **kwargs):
        df = func(*args, **kwargs)

        if not isinstance(df, pd.DataFrame):
            raise ValueError("Returned data must be a pandas DataFrame")

        # Required fields for insider trading data
        required_fields = {
            "symbol",
            "issuer",
            "name",
            "transaction_date",
            "transaction_shares",
            "transaction_price_per_share",
        }
        if not required_fields.issubset(df.columns):
            missing = required_fields - set(df.columns)
            raise ValueError(f"Missing required fields: {missing}")

        # Validate timestamp if present
        if "transaction_date" in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df["transaction_date"]):
                raise ValueError("transaction_date must be datetime64 dtype")
            if (
                df["transaction_date"].dt.tz is None
                or str(df["transaction_date"].dt.tz) != "UTC"
            ):
                raise ValueError("transaction_date must be in UTC timezone")

        # Validate numeric fields
        numeric_fields = {
            "transaction_shares",
            "transaction_price_per_share",
            "transaction_value",
            "shares_owned_before_transaction",
            "shares_owned_after_transaction",
        }
        for field in numeric_fields & set(df.columns):
            if not pd.api.types.is_numeric_dtype(df[field]):
                raise ValueError(f"{field} must be numeric")

        return df

    return wrapper


class InsiderDataProvider(ABC):
    def __init__(self, symbol: Optional[str] = None) -> None:
        self.symbol = symbol

    @abstractmethod
    def get_inner_trade_data(self, symbol: Optional[str] = None) -> pd.DataFrame:
        """Fetches insider trade data

        Returns:
            pd.DataFrame:
            - symbol: 股票代码
            - issuer: 股票名称
            - name: 变动人
            - title: 董监高职务
            - transaction_date: 变动日期(UTC时区)
            - transaction_shares: 变动股数
            - transaction_price_per_share: 成交均价
            - shares_owned_after_transaction: 变动后持股数
            - relationship: 与董监高关系
            - is_board_director: 是否为董事会成员
            - transaction_value: 交易金额(变动股数*成交均价)
            - shares_owned_before_transaction: 变动前持股数
        """
        pass
