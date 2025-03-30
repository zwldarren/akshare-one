"""Akshare One - Unified interface for Chinese market data

Provides standardized access to various financial data sources with:
- Consistent symbol formats
- Unified data schemas
- Cleaned and normalized outputs

Example:
    >>> from akshare_one import get_hist_data, get_realtime_data
    >>> df = get_hist_data("600000", interval="day")
    >>> print(df.head())
    >>> # 获取单只股票实时数据
    >>> df = get_realtime_data(symbol="600000")
    >>> # 获取所有股票实时数据
    >>> df = get_realtime_data()
"""

from typing import Optional
import pandas as pd
from .adapters import EastMoneyAdapter, SinaAdapter


def get_hist_data(
    symbol: str,
    interval: str,
    interval_multiplier: int = 1,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    adjust: str = "none",
    source: str = "eastmoney",
) -> "pd.DataFrame":
    """Get historical market data

    Args:
        symbol: Unified symbol format (e.g. '600000')
        interval: Time granularity ('second','minute','hour','day','week','month','year')
        interval_multiplier: Interval multiplier (e.g. 5 for 5 minutes)
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        adjust: Adjustment type ('none','qfq','hfq')
        source: Data source ('eastmoney')

    Returns:
        Standardized DataFrame with OHLCV data
    """
    if source == "eastmoney":
        return EastMoneyAdapter().get_hist_data(
            symbol=symbol,
            interval=interval,
            interval_multiplier=interval_multiplier,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
        )
    raise ValueError(f"Unsupported data source: {source}")


def get_realtime_data(
    source: str = "eastmoney", symbol: Optional[str] = None
) -> "pd.DataFrame":
    """Get real-time market quotes

    Returns:
        DataFrame:
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
    """
    if source == "eastmoney":
        return EastMoneyAdapter().get_realtime_data(symbol=symbol)
    raise ValueError(f"Unsupported data source: {source}")


def get_news_data(symbol: str, source: str = "eastmoney") -> "pd.DataFrame":
    """获取个股新闻数据

    Args:
        symbol: 股票代码 (如 "300059")
        source: 数据源 (目前仅支持 "eastmoney")

    Returns:
        DataFrame 包含:
        - keyword: 关键词
        - title: 新闻标题
        - content: 新闻内容
        - publish_time: 发布时间
        - source: 文章来源
        - url: 新闻链接
    """
    if source == "eastmoney":
        return EastMoneyAdapter().get_news_data(symbol=symbol)
    raise ValueError(f"Unsupported data source: {source}")


def get_balance_sheet(symbol: str, source: str = "sina") -> "pd.DataFrame":
    """获取资产负债表数据

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 (目前支持 "sina")

    Returns:
        DataFrame 包含标准化后的资产负债表数据，包含以下列：
        - report_date: 报告日期
        - report_period: 报告期
        - period: 期间
        - currency: 币种
        - total_assets: 资产总计
        - current_assets: 流动资产合计
        - cash_and_equivalents: 货币资金
        - inventory: 存货
        - current_investments: 交易性金融资产
        - trade_and_non_trade_receivables: 应收票据及应收账款
        - non_current_assets: 非流动资产合计
        - property_plant_and_equipment: 固定资产
        - goodwill_and_intangible_assets: 商誉
        - investments: 长期股权投资
        - non_current_investments: 其他非流动金融资产
        - outstanding_shares: 实收资本(或股本)
        - tax_assets: 递延所得税资产
        - total_liabilities: 负债合计
        - current_liabilities: 流动负债合计
        - current_debt: 短期借款
        - trade_and_non_trade_payables: 应付票据及应付账款
        - deferred_revenue: 合同负债
        - deposit_liabilities: 吸收存款及同业存放
        - non_current_liabilities: 非流动负债合计
        - non_current_debt: 长期借款
        - tax_liabilities: 递延所得税负债
        - shareholders_equity: 所有者权益(或股东权益)合计
        - retained_earnings: 未分配利润
        - accumulated_other_comprehensive_income: 其他综合收益
        - total_debt: 总债务(短期借款+长期借款)
    """
    if source == "sina":
        return SinaAdapter().get_balance_sheet(symbol=symbol)
    raise ValueError(f"Unsupported data source: {source}")


def get_income_statement(symbol: str, source: str = "sina") -> "pd.DataFrame":
    """获取利润表数据

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 (目前支持 "sina")

    Returns:
        DataFrame 包含标准化后的利润表数据，包含以下列：
        - report_date: 报告日期
        - report_period: 报告期
        - period: 期间
        - currency: 币种
        - revenue: 营业总收入
        - cost_of_revenue: 营业成本
        - gross_profit: 营业利润
        - operating_expense: 管理费用
        - selling_general_and_administrative_expenses: 销售费用
        - research_and_development: 研发费用
        - operating_income: 营业利润
        - interest_expense: 利息支出
        - ebit: 利润总额
        - income_tax_expense: 所得税费用
        - net_income: 净利润
        - net_income_common_stock: 归属于母公司所有者的净利润
        - net_income_non_controlling_interests: 少数股东损益
        - earnings_per_share: 基本每股收益
        - earnings_per_share_diluted: 稀释每股收益
    """
    if source == "sina":
        return SinaAdapter().get_income_statement(symbol=symbol)
    raise ValueError(f"Unsupported data source: {source}")


def get_cash_flow(symbol: str, source: str = "sina") -> "pd.DataFrame":
    """获取现金流量表数据

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 (目前支持 "sina")

    Returns:
        DataFrame 包含标准化后的现金流量表数据，包含以下列：
        - report_date: 报告日期
        - report_period: 报告期
        - period: 期间
        - currency: 币种
        - net_income: 净利润
        - depreciation_and_amortization: 固定资产折旧、油气资产折耗、生产性生物资产折旧
        - share_based_compensation: 无形资产摊销
        - net_cash_flow_from_operations: 经营活动产生的现金流量净额
        - capital_expenditure: 购建固定资产、无形资产和其他长期资产支付的现金
        - business_acquisitions_and_disposals: 取得子公司及其他营业单位支付的现金净额
        - investment_acquisitions_and_disposals: 投资支付的现金
        - net_cash_flow_from_investing: 投资活动产生的现金流量净额
        - issuance_or_repayment_of_debt_securities: 取得借款收到的现金
        - issuance_or_purchase_of_equity_shares: 吸收投资收到的现金
        - dividends_and_other_cash_distributions: 分配股利、利润或偿付利息支付的现金
        - net_cash_flow_from_financing: 筹资活动产生的现金流量净额
        - change_in_cash_and_equivalents: 现金及现金等价物净增加额
        - effect_of_exchange_rate_changes: 汇率变动对现金及现金等价物的影响
        - ending_cash_balance: 期末现金及现金等价物余额
        - free_cash_flow: 自由现金流
    """
    if source == "sina":
        return SinaAdapter().get_cash_flow(symbol=symbol)
    raise ValueError(f"Unsupported data source: {source}")
