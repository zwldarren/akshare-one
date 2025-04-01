import pandas as pd
import akshare as ak
from cachetools import cached
from .cache.cache import CACHE_CONFIG


class SinaAdapter:
    """Adapter for Sina financial data API

    Includes:
    - Financial reports (balance sheet, income statement, cash flow)
    - Historical market data
    """

    @cached(CACHE_CONFIG["financial_cache"], key=lambda self, symbol: symbol)
    def get_balance_sheet(self, symbol: str) -> pd.DataFrame:
        """获取资产负债表数据

        Args:
            symbol: 股票代码 (如 "600600")

        Returns:
            Standardized DataFrame with balance sheet data
        """
        stock = f"sh{symbol}" if not symbol.startswith(("sh", "sz", "bj")) else symbol
        raw_df = ak.stock_financial_report_sina(stock=stock, symbol="资产负债表")
        return self._clean_balance_data(raw_df)

    @cached(CACHE_CONFIG["financial_cache"], key=lambda self, symbol: symbol)
    def get_income_statement(self, symbol: str) -> pd.DataFrame:
        """获取利润表数据

        Args:
            symbol: 股票代码 (如 "600600")

        Returns:
            Standardized DataFrame with income statement data
        """
        stock = f"sh{symbol}" if not symbol.startswith(("sh", "sz", "bj")) else symbol
        raw_df = ak.stock_financial_report_sina(stock=stock, symbol="利润表")
        return self._clean_income_data(raw_df)

    @cached(CACHE_CONFIG["financial_cache"], key=lambda self, symbol: symbol)
    def get_cash_flow(self, symbol: str) -> pd.DataFrame:
        """获取现金流量表数据

        Args:
            symbol: 股票代码 (如 "600600")

        Returns:
            Standardized DataFrame with cash flow data
        """
        stock = f"sh{symbol}" if not symbol.startswith(("sh", "sz", "bj")) else symbol
        raw_df = ak.stock_financial_report_sina(stock=stock, symbol="现金流量表")
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
            "固定资产折旧、油气资产折耗、生产性生物资产折旧": "depreciation_and_amortization",
            "无形资产摊销": "share_based_compensation",
            "经营活动产生的现金流量净额": "net_cash_flow_from_operations",
            "购建固定资产、无形资产和其他长期资产支付的现金": "capital_expenditure",
            "取得子公司及其他营业单位支付的现金净额": "business_acquisitions_and_disposals",
            "投资支付的现金": "investment_acquisitions_and_disposals",
            "投资活动产生的现金流量净额": "net_cash_flow_from_investing",
            "取得借款收到的现金": "issuance_or_repayment_of_debt_securities",
            "吸收投资收到的现金": "issuance_or_purchase_of_equity_shares",
            "分配股利、利润或偿付利息支付的现金": "dividends_and_other_cash_distributions",
            "筹资活动产生的现金流量净额": "net_cash_flow_from_financing",
            "现金及现金等价物净增加额": "change_in_cash_and_equivalents",
            "汇率变动对现金及现金等价物的影响": "effect_of_exchange_rate_changes",
            "期末现金及现金等价物余额": "ending_cash_balance",
            "自由现金流": "free_cash_flow",
        }
        raw_df = raw_df.rename(columns=column_mapping)

        # Select only required columns
        required_columns = [
            "report_date",
            "report_period",
            "period",
            "currency",
            "net_income",
            "depreciation_and_amortization",
            "share_based_compensation",
            "net_cash_flow_from_operations",
            "capital_expenditure",
            "business_acquisitions_and_disposals",
            "investment_acquisitions_and_disposals",
            "net_cash_flow_from_investing",
            "issuance_or_repayment_of_debt_securities",
            "issuance_or_purchase_of_equity_shares",
            "dividends_and_other_cash_distributions",
            "net_cash_flow_from_financing",
            "change_in_cash_and_equivalents",
            "effect_of_exchange_rate_changes",
            "ending_cash_balance",
            "free_cash_flow",
        ]

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
            "report_period",
            "period",
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

    @cached(
        CACHE_CONFIG["hist_data_cache"],
        key=lambda self,
        symbol,
        interval,
        interval_multiplier,
        start_date,
        end_date,
        adjust: (symbol, interval, interval_multiplier, start_date, end_date, adjust),
    )
    def get_hist_data(
        self,
        symbol: str,
        interval: str = "day",
        interval_multiplier: int = 1,
        start_date: str = "1970-01-01",
        end_date: str = "2030-12-31",
        adjust: str = "none",
    ) -> pd.DataFrame:
        """获取新浪历史行情数据

        Args:
            symbol: 股票代码 (如 "600000")
            interval: 时间粒度
            interval_multiplier: 时间间隔倍数
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            adjust: 复权类型 ('none','qfq','hfq','qfq-factor','hfq-factor')

        Returns:
            Standardized DataFrame with OHLCV data
        """
        # Map standard interval to supported periods
        interval = interval.lower()
        if interval not in ["day", "week", "month", "year"]:
            raise ValueError("Sina only supports day/week/month/year intervals")

        # Convert date format from YYYY-MM-DD to YYYYMMDD
        start_date = start_date.replace("-", "") if "-" in start_date else start_date
        end_date = end_date.replace("-", "") if "-" in end_date else end_date

        stock = f"sh{symbol}" if not symbol.startswith(("sh", "sz", "bj")) else symbol

        raw_df = ak.stock_zh_a_daily(
            symbol=stock,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust if adjust != "none" else "",
        )

        if interval_multiplier > 1:
            raw_df = self._resample_data(raw_df, interval, interval_multiplier)

        return self._clean_hist_data(raw_df, adjust)

    def _resample_data(
        self, df: pd.DataFrame, interval: str, multiplier: int
    ) -> pd.DataFrame:
        if interval == "day":
            freq = f"{multiplier}D"
        elif interval == "week":
            freq = f"{multiplier}W-MON"
        elif interval == "month":
            freq = f"{multiplier}MS"
        elif interval == "year":
            freq = f"{multiplier}AS-JAN"

        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")
        resampled = df.resample(freq).agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }
        )
        return resampled.reset_index()

    def _clean_hist_data(self, raw_df: pd.DataFrame, adjust: str) -> pd.DataFrame:
        """清理和标准化历史行情数据

        Args:
            raw_df: 原始数据DataFrame
            adjust: 复权类型

        Returns:
            标准化后的DataFrame
        """
        column_mapping = {
            "date": "timestamp",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
        }

        df = raw_df.rename(columns=column_mapping)

        # Process timestamp
        if "timestamp" in df.columns:
            df["timestamp"] = (
                pd.to_datetime(df["timestamp"])
                .dt.tz_localize("Asia/Shanghai")
                .dt.tz_convert("UTC")
            )

        # Process volume
        if "volume" in df.columns:
            df["volume"] = df["volume"].astype("int64")

        # Select and order columns
        standard_columns = [
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]

        return df[[col for col in standard_columns if col in df.columns]]

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
            "营业利润": "gross_profit",
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
            "report_period",
            "period",
            "currency",
            "revenue",
            "cost_of_revenue",
            "gross_profit",
            "operating_expense",
            "selling_general_and_administrative_expenses",
            "research_and_development",
            "operating_income",
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
