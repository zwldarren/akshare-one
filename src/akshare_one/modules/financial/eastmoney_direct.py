import pandas as pd
import requests

from akshare_one.modules.cache import cache

from .base import FinancialDataProvider


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

    def get_income_statement(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_balance_sheet(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_cash_flow(self) -> pd.DataFrame:
        return pd.DataFrame()

    @cache(
        "financial_cache",
        key=lambda self: f"eastmoney_financial_metrics_{self.symbol}",
    )
    def get_financial_metrics(self) -> pd.DataFrame:
        """获取三大财务报表关键指标"""
        balance_sheet = self._fetch_balance_sheet()
        income_statement = self._fetch_income_statement()
        cash_flow = self._fetch_cash_flow()

        if balance_sheet.empty and income_statement.empty and cash_flow.empty:
            return pd.DataFrame()

        merged = pd.merge(
            balance_sheet, income_statement, on="report_date", how="outer"
        )
        merged = pd.merge(merged, cash_flow, on="report_date", how="outer")

        # Convert report_date to datetime and format as YYYY-MM-DD
        merged["report_date"] = pd.to_datetime(merged["report_date"]).dt.strftime(
            "%Y-%m-%d"
        )

        # Sort by report_date in descending order (most recent first)
        merged = merged.sort_values("report_date", ascending=False).reset_index(
            drop=True
        )

        return merged

    def _fetch_balance_sheet(self) -> pd.DataFrame:
        """
        Get stock balance sheet data from East Money API
        """
        try:
            # API endpoint and parameters
            api_url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
            params = {
                "reportName": "RPT_DMSK_FN_BALANCE",
                "filter": f'(SECURITY_CODE="{self.symbol}")',
                "pageNumber": "1",
                "pageSize": "1000",
                "sortColumns": "REPORT_DATE",
                "sortTypes": "-1",
                "columns": ",".join(self._balance_sheet_rename_map.keys()),
            }

            # Fetch data from API
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract the actual data
            if data.get("result") and data["result"].get("data"):
                df = pd.DataFrame(data["result"]["data"])
                df.rename(columns=self._balance_sheet_rename_map, inplace=True)
                return df
            else:
                print("No balance sheet data found in API response")
                return pd.DataFrame()

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return pd.DataFrame()

    def _fetch_income_statement(self) -> pd.DataFrame:
        """
        Get stock income statement data from East Money API
        """
        try:
            # API endpoint and parameters
            api_url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
            params = {
                "reportName": "RPT_DMSK_FN_INCOME",
                "filter": f'(SECURITY_CODE="{self.symbol}")',
                "pageNumber": "1",
                "pageSize": "1000",
                "sortColumns": "REPORT_DATE",
                "sortTypes": "-1",
                "columns": ",".join(self._income_statement_rename_map.keys()),
            }

            # Fetch data from API
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract the actual data
            if data.get("result") and data["result"].get("data"):
                df = pd.DataFrame(data["result"]["data"])
                df.rename(columns=self._income_statement_rename_map, inplace=True)
                return df
            else:
                print("No income statement data found in API response")
                return pd.DataFrame()

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return pd.DataFrame()

    def _fetch_cash_flow(self) -> pd.DataFrame:
        """
        Get stock cash flow statement data from East Money API
        """
        try:
            # API endpoint and parameters
            api_url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
            params = {
                "reportName": "RPT_DMSK_FN_CASHFLOW",
                "filter": f'(SECURITY_CODE="{self.symbol}")',
                "pageNumber": "1",
                "pageSize": "1000",
                "sortColumns": "REPORT_DATE",
                "sortTypes": "-1",
                "columns": ",".join(self._cash_flow_rename_map.keys()),
            }

            # Fetch data from API
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract the actual data
            if data.get("result") and data["result"].get("data"):
                df = pd.DataFrame(data["result"]["data"])
                df.rename(columns=self._cash_flow_rename_map, inplace=True)
                return df
            else:
                print("No cash flow statement data found in API response")
                return pd.DataFrame()

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return pd.DataFrame()
