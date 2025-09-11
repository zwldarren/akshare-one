from abc import ABC, abstractmethod

import pandas as pd


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

    @abstractmethod
    def get_financial_metrics(self) -> pd.DataFrame:
        """Fetch financial metrics"""
        pass
