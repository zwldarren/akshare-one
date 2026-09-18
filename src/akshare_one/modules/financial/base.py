from abc import ABC, abstractmethod

import pandas as pd


class FinancialDataProvider(ABC):
    #: Parameters that change the answer; the cache key is built from these.
    CACHE_PARAMS = ("symbol",)

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol

    @abstractmethod
    def get_balance_sheet(self) -> pd.DataFrame:
        """Fetches balance sheet data; columns: :mod:`akshare_one.modules.financial.schema`."""
        pass

    @abstractmethod
    def get_income_statement(self) -> pd.DataFrame:
        """Fetches income statement data; columns: :mod:`akshare_one.modules.financial.schema`."""
        pass

    @abstractmethod
    def get_cash_flow(self) -> pd.DataFrame:
        """Fetches cash flow data; columns: :mod:`akshare_one.modules.financial.schema`."""
        pass

    @abstractmethod
    def get_financial_metrics(self) -> pd.DataFrame:
        """Fetch financial metrics; columns: :mod:`akshare_one.modules.financial.schema`."""
        pass
