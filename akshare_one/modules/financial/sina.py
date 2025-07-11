from cachetools import cached
import pandas as pd
import akshare as ak

from akshare_one.modules.cache import CACHE_CONFIG
from .base import FinancialDataProvider


class SinaFinancialReport(FinancialDataProvider):
    def __init__(self, symbol: str) -> None:
        super().__init__(symbol)
        self.stock = (
            f"sh{symbol}" if not symbol.startswith(("sh", "sz", "bj")) else symbol
        )

    @cached(
        CACHE_CONFIG["financial_cache"],
        key=lambda self, symbol=None: f"sina_balance_{self.symbol}",
    )
    def get_balance_sheet(self) -> pd.DataFrame:
        """获取资产负债表数据

        Args:
            symbol: 股票代码 (如 "600600")

        Returns:
            Standardized DataFrame with balance sheet data
        """
        raw_df = ak.stock_financial_report_sina(stock=self.stock, symbol="资产负债表")
        return self._clean_balance_data(raw_df)

    @cached(
        CACHE_CONFIG["financial_cache"],
        key=lambda self, symbol=None: f"sina_income_{self.symbol}",
    )
    def get_income_statement(self) -> pd.DataFrame:
        """获取利润表数据

        Args:
            symbol: 股票代码 (如 "600600")

        Returns:
            Standardized DataFrame with income statement data
        """
        raw_df = ak.stock_financial_report_sina(stock=self.stock, symbol="利润表")
        return self._clean_income_data(raw_df)

    @cached(
        CACHE_CONFIG["financial_cache"],
        key=lambda self, symbol=None: f"sina_cash_{self.symbol}",
    )
    def get_cash_flow(self) -> pd.DataFrame:
        """获取现金流量表数据

        Args:
            symbol: 股票代码 (如 "600600")

        Returns:
            Standardized DataFrame with cash flow data
        """
        raw_df = ak.stock_financial_report_sina(stock=self.stock, symbol="现金流量表")
        return self._clean_cash_data(raw_df)

    def _clean_cash_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """清理和标准化现金流量表数据

        Args:
            raw_df: Raw DataFrame from Sina API

        Returns:
            Standardized DataFrame with consistent columns
        """
        # Convert timestamp columns if exists
        if "报告日" in raw_df.columns:
            raw_df = raw_df.rename(columns={"报告日": "report_date"})
            raw_df["report_date"] = pd.to_datetime(
                raw_df["report_date"], format="%Y%m%d"
            )

        if "更新日期" in raw_df.columns:
            raw_df = raw_df.rename(columns={"更新日期": "update_time"})
            raw_df["update_time"] = pd.to_datetime(raw_df["update_time"])

        # Standardize column names
        column_mapping = {
            "类型": "report_type",
            "币种": "currency",
            "净利润": "net_income",
            "经营活动产生的现金流量净额": "net_cash_flow_from_operations",
            "购建固定资产、无形资产和其他长期资产支付的现金": "capital_expenditure",
            "取得子公司及其他营业单位支付的现金净额": "business_acquisitions_and_disposals",
            "投资活动产生的现金流量净额": "net_cash_flow_from_investing",
            "取得借款收到的现金": "issuance_or_repayment_of_debt_securities",
            "吸收投资收到的现金": "issuance_or_purchase_of_equity_shares",
            "筹资活动产生的现金流量净额": "net_cash_flow_from_financing",
            "现金及现金等价物净增加额": "change_in_cash_and_equivalents",
            "汇率变动对现金及现金等价物的影响": "effect_of_exchange_rate_changes",
            "期末现金及现金等价物余额": "ending_cash_balance",
        }
        raw_df = raw_df.rename(columns=column_mapping)

        # Select only required columns
        required_columns = ["report_date"]
        required_columns.extend(column_mapping.values())

        # Ensure all required columns are present, fill with NaN if not
        for col in required_columns:
            if col not in raw_df.columns:
                raw_df[col] = pd.NA

        # Filter columns
        available_columns = [col for col in required_columns if col in raw_df.columns]
        return raw_df[available_columns]

    def _clean_balance_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """清理和标准化资产负债表数据

        Args:
            raw_df: Raw DataFrame from Sina API

        Returns:
            Standardized DataFrame with consistent columns
        """
        # Convert timestamp columns if exists
        if "报告日" in raw_df.columns:
            raw_df = raw_df.rename(columns={"报告日": "report_date"})
            raw_df["report_date"] = pd.to_datetime(
                raw_df["report_date"], format="%Y%m%d"
            )

        if "更新日期" in raw_df.columns:
            raw_df = raw_df.rename(columns={"更新日期": "update_time"})
            raw_df["update_time"] = pd.to_datetime(raw_df["update_time"])

        # Standardize column names
        column_mapping = {
            "类型": "report_type",
            "币种": "currency",
            "资产总计": "total_assets",
            "流动资产合计": "current_assets",
            "货币资金": "cash_and_equivalents",
            "存货": "inventory",
            "交易性金融资产": "current_investments",
            "应收票据及应收账款": "trade_and_non_trade_receivables",
            "非流动资产合计": "non_current_assets",
            "固定资产": "property_plant_and_equipment",
            "商誉": "goodwill_and_intangible_assets",
            "长期股权投资": "investments",
            "其他非流动金融资产": "non_current_investments",
            "实收资本(或股本)": "outstanding_shares",
            "递延所得税资产": "tax_assets",
            "负债合计": "total_liabilities",
            "流动负债合计": "current_liabilities",
            "短期借款": "current_debt",
            "应付票据及应付账款": "trade_and_non_trade_payables",
            "合同负债": "deferred_revenue",
            "吸收存款及同业存放": "deposit_liabilities",
            "非流动负债合计": "non_current_liabilities",
            "长期借款": "non_current_debt",
            "递延所得税负债": "tax_liabilities",
            "所有者权益(或股东权益)合计": "shareholders_equity",
            "未分配利润": "retained_earnings",
            "其他综合收益": "accumulated_other_comprehensive_income",
        }
        raw_df = raw_df.rename(columns=column_mapping)

        # Select only required columns
        required_columns = [
            "report_date",
            "currency",
            "total_assets",
            "current_assets",
            "cash_and_equivalents",
            "inventory",
            "current_investments",
            "trade_and_non_trade_receivables",
            "non_current_assets",
            "property_plant_and_equipment",
            "goodwill_and_intangible_assets",
            "investments",
            "non_current_investments",
            "outstanding_shares",
            "tax_assets",
            "total_liabilities",
            "current_liabilities",
            "current_debt",
            "trade_and_non_trade_payables",
            "deferred_revenue",
            "deposit_liabilities",
            "non_current_liabilities",
            "non_current_debt",
            "tax_liabilities",
            "shareholders_equity",
            "retained_earnings",
            "accumulated_other_comprehensive_income",
        ]

        # Calculate total_debt
        if "current_debt" in raw_df.columns and "non_current_debt" in raw_df.columns:
            raw_df["total_debt"] = raw_df["current_debt"] + raw_df["non_current_debt"]
            required_columns.append("total_debt")

        # Filter columns
        available_columns = [col for col in required_columns if col in raw_df.columns]
        return raw_df[available_columns]

    def _clean_income_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """清理和标准化利润表数据

        Args:
            raw_df: Raw DataFrame from Sina API

        Returns:
            Standardized DataFrame with consistent columns
        """
        # Convert timestamp columns if exists
        if "报告日" in raw_df.columns:
            raw_df = raw_df.rename(columns={"报告日": "report_date"})
            raw_df["report_date"] = pd.to_datetime(
                raw_df["report_date"], format="%Y%m%d"
            )

        if "更新日期" in raw_df.columns:
            raw_df = raw_df.rename(columns={"更新日期": "update_time"})
            raw_df["update_time"] = pd.to_datetime(raw_df["update_time"])

        # Standardize column names
        column_mapping = {
            "类型": "report_type",
            "币种": "currency",
            "营业总收入": "revenue",
            "营业成本": "cost_of_revenue",
            "营业利润": "operating_profit",
            "销售费用": "selling_general_and_administrative_expenses",
            "管理费用": "operating_expense",
            "研发费用": "research_and_development",
            "利息支出": "interest_expense",
            "利润总额": "ebit",
            "所得税费用": "income_tax_expense",
            "净利润": "net_income",
            "归属于母公司所有者的净利润": "net_income_common_stock",
            "少数股东损益": "net_income_non_controlling_interests",
            "基本每股收益": "earnings_per_share",
            "稀释每股收益": "earnings_per_share_diluted",
        }
        raw_df = raw_df.rename(columns=column_mapping)

        # Select only required columns
        required_columns = [
            "report_date",
            "currency",
            "revenue",
            "cost_of_revenue",
            "operating_profit",
            "operating_expense",
            "selling_general_and_administrative_expenses",
            "research_and_development",
            "interest_expense",
            "ebit",
            "income_tax_expense",
            "net_income",
            "net_income_common_stock",
            "net_income_non_controlling_interests",
            "earnings_per_share",
            "earnings_per_share_diluted",
        ]

        # Filter columns
        available_columns = [col for col in required_columns if col in raw_df.columns]
        return raw_df[available_columns]
