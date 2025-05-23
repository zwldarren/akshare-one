from abc import ABC, abstractmethod
import pandas as pd


def validate_financial_data(func):
    """Decorator to validate financial data returned by data providers"""

    def wrapper(*args, **kwargs):
        df = func(*args, **kwargs)

        if not isinstance(df, pd.DataFrame):
            raise ValueError("Returned data must be a pandas DataFrame")

        # Validate report_date if present
        if "report_date" in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df["report_date"]):
                raise ValueError("report_date must be datetime64 dtype")

        return df

    return wrapper


class FinancialDataProvider(ABC):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol

    @abstractmethod
    def get_balance_sheet(self) -> pd.DataFrame:
        """Fetches balance sheet data"""
        pass

    @abstractmethod
    def get_income_statement(self) -> pd.DataFrame:
        """Fetches income statement data"""
        pass

    @abstractmethod
    def get_cash_flow(self) -> pd.DataFrame:
        """Fetches cash flow data"""
        pass
