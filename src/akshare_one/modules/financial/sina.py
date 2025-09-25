import akshare as ak  # type: ignore
import pandas as pd

from ..cache import cache
from .base import FinancialDataProvider


class SinaFinancialReport(FinancialDataProvider):
    """Financial data provider for Sina finance reports.

    Provides standardized access to balance sheet, income statement,
    and cash flow data from Sina finance API.
    """

    def __init__(self, symbol: str) -> None:
        super().__init__(symbol)
        self.stock = (
            f"sh{symbol}" if not symbol.startswith(("sh", "sz", "bj")) else symbol
        )

    @cache("financial_cache", key=lambda self: f"sina_balance_{self.symbol}")
    def get_balance_sheet(self) -> pd.DataFrame:
        """获取资产负债表数据

        Args:
            symbol: 股票代码 (如 "600600")

        Returns:
            Standardized DataFrame with balance sheet data
        """
        try:
            raw_df = ak.stock_financial_report_sina(
                stock=self.stock, symbol="资产负债表"
            )
            if raw_df is None or raw_df.empty:
                raise ValueError(f"Invalid stock symbol: {self.symbol}")
            return self._clean_balance_data(raw_df)
        except Exception as e:
            raise ValueError(
                f"Failed to get balance sheet for symbol {self.symbol}: {str(e)}"
            ) from e

    @cache("financial_cache", key=lambda self: f"sina_income_{self.symbol}")
    def get_income_statement(self) -> pd.DataFrame:
        """获取利润表数据

        Args:
            symbol: 股票代码 (如 "600600")

        Returns:
            Standardized DataFrame with income statement data
        """
        try:
            raw_df = ak.stock_financial_report_sina(stock=self.stock, symbol="利润表")
            if raw_df is None or raw_df.empty:
                raise ValueError(f"Invalid stock symbol: {self.symbol}")
            return self._clean_income_data(raw_df)
        except Exception as e:
            raise ValueError(
                f"Failed to get income statement for symbol {self.symbol}: {str(e)}"
            ) from e

    @cache("financial_cache", key=lambda self: f"sina_cash_{self.symbol}")
    def get_cash_flow(self) -> pd.DataFrame:
        """获取现金流量表数据

        Args:
            symbol: 股票代码 (如 "600600")

        Returns:
            Standardized DataFrame with cash flow data
        """
        try:
            raw_df = ak.stock_financial_report_sina(
                stock=self.stock, symbol="现金流量表"
            )
            if raw_df is None or raw_df.empty:
                raise ValueError(f"Invalid stock symbol: {self.symbol}")
            return self._clean_cash_data(raw_df)
        except Exception as e:
            raise ValueError(
                f"Failed to get cash flow statement for symbol {self.symbol}: {str(e)}"
            ) from e

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

        # Define column mappings and required columns
        column_mapping = {
            "币种": "currency",
            "经营活动产生的现金流量净额": "net_cash_flow_from_operations",
            "购建固定资产、无形资产和其他长期资产支付的现金": ("capital_expenditure"),
            "取得子公司及其他营业单位支付的现金净额": (
                "business_acquisitions_and_disposals"
            ),
            "投资活动产生的现金流量净额": "net_cash_flow_from_investing",
            "取得借款收到的现金": "issuance_or_repayment_of_debt_securities",
            "吸收投资收到的现金": "issuance_or_purchase_of_equity_shares",
            "筹资活动产生的现金流量净额": "net_cash_flow_from_financing",
            "现金及现金等价物净增加额": "change_in_cash_and_equivalents",
            "汇率变动对现金及现金等价物的影响": "effect_of_exchange_rate_changes",
            "期末现金及现金等价物余额": "ending_cash_balance",
            "销售商品、提供劳务收到的现金": "cash_from_sales",
            "收到的税费返还": "tax_refunds_received",
            "支付给职工以及为职工支付的现金": "cash_paid_to_employees",
            "支付的各项税费": "taxes_paid",
            "经营活动现金流入小计": "total_cash_inflow_from_operations",
            "经营活动现金流出小计": "total_cash_outflow_from_operations",
            "收回投资所收到的现金": "cash_from_investment_recovery",
            "取得投资收益收到的现金": "cash_from_investment_income",
            "处置固定资产、无形资产收回的现金": "cash_from_asset_sales",
            "投资活动现金流入小计": "total_cash_inflow_from_investing",
            "投资活动现金流出小计": "total_cash_outflow_from_investing",
            "分配股利、利润或偿付利息所支付的现金": (
                "cash_paid_for_dividends_and_interest"
            ),
            "偿还债务支付的现金": "cash_paid_for_debt_repayment",
            "筹资活动现金流入小计": "total_cash_inflow_from_financing",
            "筹资活动现金流出小计": "total_cash_outflow_from_financing",
            "期初现金及现金等价物余额": "beginning_cash_balance",
            "现金的期末余额": "ending_cash",
            "现金等价物的期末余额": "ending_cash_equivalents",
        }

        required_columns = ["report_date"] + list(column_mapping.values())
        return raw_df.rename(columns=column_mapping).reindex(columns=required_columns)

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

        # Define and apply column mappings in one optimized operation
        raw_df = raw_df.rename(
            columns={
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
                "应收账款": "accounts_receivable",
                "预付款项": "prepayments",
                "其他应收款": "other_receivables",
                "固定资产净值": "fixed_assets_net",
                "在建工程": "construction_in_progress",
                "资本公积": "capital_reserve",
                "少数股东权益": "minority_interest",
            }
        )

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
            "accounts_receivable",
            "prepayments",
            "other_receivables",
            "fixed_assets_net",
            "construction_in_progress",
            "capital_reserve",
            "current_ratio",
            "debt_to_assets",
            "minority_interest",
        ]

        # Calculate financial ratios using vectorized operations
        cols = ["current_debt", "non_current_debt"]
        raw_df[cols] = raw_df[cols].apply(pd.to_numeric, errors="coerce")
        raw_df["total_debt"] = raw_df[cols].fillna(0).sum(axis=1)

        # Pre-calculate denominator conditions
        valid_current_liab = raw_df["current_liabilities"].ne(0)
        valid_total_assets = raw_df["total_assets"].ne(0)

        # Calculate ratios in one operation
        ratios = pd.DataFrame(
            {
                "current_ratio": raw_df["current_assets"]
                / raw_df["current_liabilities"],
                "cash_ratio": raw_df["cash_and_equivalents"]
                / raw_df["current_liabilities"],
                "debt_to_assets": raw_df["total_debt"] / raw_df["total_assets"],
            }
        )

        # Apply conditions
        cond = pd.DataFrame(
            {
                "current_ratio": valid_current_liab,
                "cash_ratio": valid_current_liab,
                "debt_to_assets": valid_total_assets,
            },
            index=ratios.index,
        )
        raw_df = raw_df.join(ratios.where(cond))

        return raw_df.reindex(columns=required_columns)

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

        # Define column mappings and required columns
        column_mapping = {
            "币种": "currency",
            "营业总收入": "revenue",
            "营业收入": "operating_revenue",
            "营业总成本": "total_operating_costs",
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
            "投资收益": "investment_income",
            "公允价值变动收益": "fair_value_adjustments",
            "资产减值损失": "asset_impairment_loss",
            "财务费用": "financial_expenses",
            "营业税金及附加": "taxes_and_surcharges",
            "其他综合收益": "other_comprehensive_income",
            "综合收益总额": "total_comprehensive_income",
        }

        required_columns = ["report_date"] + list(column_mapping.values())
        return raw_df.rename(columns=column_mapping).reindex(columns=required_columns)

    def get_financial_metrics(self) -> pd.DataFrame:
        return pd.DataFrame()
