import logging

import pandas as pd

from akshare_one.eastmoney.client import EastMoneyClient
from akshare_one.modules.cache import cached

from ..registry import provider
from ..schema import normalize
from .base import FinancialDataProvider
from .schema import BALANCE_COLUMNS, CASH_FLOW_COLUMNS, INCOME_COLUMNS, METRICS_COLUMNS

logger = logging.getLogger(__name__)


@provider("financial", "eastmoney_direct")
class EastMoneyDirectFinancialReport(FinancialDataProvider):
    _balance_sheet_rename_map = {
        "REPORT_DATE": "report_date",
        "TOTAL_ASSETS": "total_assets",
        "FIXED_ASSET": "fixed_assets_net",
        "MONETARYFUNDS": "cash_and_equivalents",
        "ACCOUNTS_RECE": "accounts_receivable",
        "INVENTORY": "inventory",
        "TOTAL_LIABILITIES": "total_liabilities",
        "ACCOUNTS_PAYABLE": "trade_and_non_trade_payables",
        "ADVANCE_RECEIVABLES": "deferred_revenue",
        "TOTAL_EQUITY": "shareholders_equity",
    }

    _income_statement_rename_map = {
        "REPORT_DATE": "report_date",
        "TOTAL_OPERATE_INCOME": "revenue",
        "TOTAL_OPERATE_COST": "total_operating_costs",
        "OPERATE_PROFIT": "operating_profit",
        "PARENT_NETPROFIT": "net_income_common_stock",
    }

    _cash_flow_rename_map = {
        "REPORT_DATE": "report_date",
        "NETCASH_OPERATE": "net_cash_flow_from_operations",
        "NETCASH_INVEST": "net_cash_flow_from_investing",
        "NETCASH_FINANCE": "net_cash_flow_from_financing",
        "CCE_ADD": "change_in_cash_and_equivalents",
    }

    def __init__(self, symbol: str) -> None:
        super().__init__(symbol)
        self.client = EastMoneyClient()

    def get_income_statement(self) -> pd.DataFrame:
        return self._fetch_income_statement()

    def get_balance_sheet(self) -> pd.DataFrame:
        return self._fetch_balance_sheet()

    def get_cash_flow(self) -> pd.DataFrame:
        return self._fetch_cash_flow()

    @cached("financial")
    def get_financial_metrics(self) -> pd.DataFrame:
        """获取三大财务报表关键指标"""
        balance_sheet = self._fetch_balance_sheet()
        income_statement = self._fetch_income_statement()
        cash_flow = self._fetch_cash_flow()

        if balance_sheet.empty and income_statement.empty and cash_flow.empty:
            return normalize(pd.DataFrame(), METRICS_COLUMNS)

        # Start with the non-empty DataFrame
        if not balance_sheet.empty:
            merged = balance_sheet
        elif not income_statement.empty:
            merged = income_statement
        else:
            merged = cash_flow

        # Merge with the remaining non-empty DataFrames
        if not income_statement.empty and merged is not income_statement:
            merged = pd.merge(merged, income_statement, on="report_date", how="outer")

        if not cash_flow.empty and merged is not cash_flow:
            merged = pd.merge(merged, cash_flow, on="report_date", how="outer")

        # Convert report_date to datetime and format as YYYY-MM-DD
        merged["report_date"] = pd.to_datetime(merged["report_date"]).dt.strftime("%Y-%m-%d")

        # Sort by report_date in descending order (most recent first)
        merged = merged.sort_values("report_date", ascending=False).reset_index(drop=True)

        return normalize(merged, METRICS_COLUMNS)

    @cached("financial")
    def _fetch_balance_sheet(self) -> pd.DataFrame:
        """
        Get stock balance sheet data from East Money API
        """
        return self._fetch_statement(
            report_name="RPT_DMSK_FN_BALANCE",
            rename_map=self._balance_sheet_rename_map,
            columns=BALANCE_COLUMNS,
        )

    @cached("financial")
    def _fetch_income_statement(self) -> pd.DataFrame:
        """
        Get stock income statement data from East Money API
        """
        return self._fetch_statement(
            report_name="RPT_DMSK_FN_INCOME",
            rename_map=self._income_statement_rename_map,
            columns=INCOME_COLUMNS,
        )

    @cached("financial")
    def _fetch_cash_flow(self) -> pd.DataFrame:
        """
        Get stock cash flow statement data from East Money API
        """
        return self._fetch_statement(
            report_name="RPT_DMSK_FN_CASHFLOW",
            rename_map=self._cash_flow_rename_map,
            columns=CASH_FLOW_COLUMNS,
        )

    def _fetch_statement(
        self,
        report_name: str,
        rename_map: dict[str, str],
        columns: tuple[str, ...],
    ) -> pd.DataFrame:
        """Fetch one statement and rename its upstream fields onto ``columns``.

        A report with no rows for this symbol is an empty frame; a transport or
        gateway failure raises rather than masquerading as "no data".
        """
        rows = self.client.fetch_datacenter_report(report_name, self.symbol, list(rename_map))
        if not rows:
            logger.warning("No %s data found in API response for %s", report_name, self.symbol)
            return normalize(pd.DataFrame(), columns)

        return normalize(pd.DataFrame(rows).rename(columns=rename_map), columns)
