"""Akshare One - Unified interface for Chinese market data

Provides standardized access to various financial data sources with:
- Consistent symbol formats
- Unified data schemas
- Cleaned and normalized outputs

Example:
    >>> from akshare_one import get_hist_data, get_realtime_data
    >>> # 获取股票历史数据
    >>> df = get_hist_data("600000", interval="day")
    >>> print(df.head())
    >>> # 获取股票实时数据
    >>> df = get_realtime_data(symbol="600000")
"""

from typing import Literal

import pandas as pd

from .modules.financial.factory import FinancialDataFactory
from .modules.futures.factory import FuturesDataFactory
from .modules.historical.factory import HistoricalDataFactory
from .modules.info.factory import InfoDataFactory
from .modules.insider.factory import InsiderDataFactory
from .modules.news.factory import NewsDataFactory
from .modules.options.factory import OptionsDataFactory
from .modules.realtime.factory import RealtimeDataFactory


def get_basic_info(
    symbol: str, source: Literal["eastmoney"] = "eastmoney"
) -> pd.DataFrame:
    """获取股票基础信息

    Args:
        symbol: 股票代码 (e.g. '600000')
        source: 数据源 ('eastmoney')

    Returns:
        pd.DataFrame:
        - price: 最新价
        - symbol: 股票代码
        - name: 股票简称
        - total_shares: 总股本
        - float_shares: 流通股
        - total_market_cap: 总市值
        - float_market_cap: 流通市值
        - industry: 行业
        - listing_date: 上市时间
    """
    provider = InfoDataFactory.get_provider(source, symbol=symbol)
    return provider.get_basic_info()


def get_hist_data(
    symbol: str,
    interval: Literal["minute", "hour", "day", "week", "month", "year"] = "day",
    interval_multiplier: int = 1,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    adjust: Literal["none", "qfq", "hfq"] = "none",
    source: Literal["eastmoney", "eastmoney_direct", "sina"] = "eastmoney_direct",
) -> pd.DataFrame:
    """Get historical market data

    Args:
        symbol: 股票代码 (e.g. '600000')
        interval: 时间间隔 ('minute','hour','day','week','month','year')
        interval_multiplier: 时间间隔倍数 (e.g. 5 for 5 minutes)
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        adjust: 复权类型 ('none','qfq','hfq')
        source: 数据源 ('eastmoney', 'eastmoney_direct', 'sina')

    Returns:
        pd.DataFrame:
        - timestamp: 时间戳
        - open: 开盘价
        - high: 最高价
        - low: 最低价
        - close: 收盘价
        - volume: 成交量
    """
    kwargs = {
        "symbol": symbol,
        "interval": interval,
        "interval_multiplier": interval_multiplier,
        "start_date": start_date,
        "end_date": end_date,
        "adjust": adjust,
    }
    provider = HistoricalDataFactory.get_provider(source, **kwargs)
    return provider.get_hist_data()


def get_realtime_data(
    symbol: str | None = None,
    source: Literal["eastmoney", "eastmoney_direct", "xueqiu"] = "eastmoney_direct",
) -> pd.DataFrame:
    """Get real-time market quotes

    Args:
        symbol: 股票代码 (如 "600000")
        source: 数据源 ('eastmoney', 'eastmoney_direct', 'xueqiu')

    Returns:
        pd.DataFrame:
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
    provider = RealtimeDataFactory.get_provider(source, symbol=symbol)
    return provider.get_current_data()


def get_news_data(
    symbol: str, source: Literal["eastmoney"] = "eastmoney"
) -> pd.DataFrame:
    """获取个股新闻数据

    Args:
        symbol: 股票代码 (如 "300059")
        source: 数据源 ('eastmoney')

    Returns:
        pd.DataFrame:
        - keyword: 关键词
        - title: 新闻标题
        - content: 新闻内容
        - publish_time: 发布时间
        - source: 文章来源
        - url: 新闻链接
    """
    provider = NewsDataFactory.get_provider(source, symbol=symbol)
    return provider.get_news_data()


def get_balance_sheet(symbol: str, source: Literal["sina"] = "sina") -> pd.DataFrame:
    """获取资产负债表数据

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 ("sina")

    Returns:
        pd.DataFrame: 资产负债表数据
    """
    provider = FinancialDataFactory.get_provider(source, symbol=symbol)
    return provider.get_balance_sheet()


def get_income_statement(symbol: str, source: Literal["sina"] = "sina") -> pd.DataFrame:
    """获取利润表数据

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 ("sina")

    Returns:
        pd.DataFrame: 利润表数据
    """
    provider = FinancialDataFactory.get_provider(source, symbol=symbol)
    return provider.get_income_statement()


def get_cash_flow(symbol: str, source: Literal["sina"] = "sina") -> pd.DataFrame:
    """获取现金流量表数据

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 ("sina")

    Returns:
        pd.DataFrame: 现金流量表数据
    """
    provider = FinancialDataFactory.get_provider(source, symbol=symbol)
    return provider.get_cash_flow()


def get_financial_metrics(
    symbol: str, source: Literal["eastmoney_direct"] = "eastmoney_direct"
) -> pd.DataFrame:
    """获取三大财务报表关键指标

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 ('eastmoney_direct')

    Returns:
        pd.DataFrame: 财务关键指标数据
    """
    provider = FinancialDataFactory.get_provider(source, symbol=symbol)
    return provider.get_financial_metrics()


def get_inner_trade_data(
    symbol: str, source: Literal["xueqiu"] = "xueqiu"
) -> pd.DataFrame:
    """获取雪球内部交易数据

    Args:
        symbol: 股票代码，如"600000"
        source: 数据源 (目前支持 "xueqiu")

    Returns:
        pd.DataFrame: 内部交易数据
    """
    provider = InsiderDataFactory.get_provider(source, symbol=symbol)
    return provider.get_inner_trade_data()


# ==================== Futures API ====================


def get_futures_hist_data(
    symbol: str,
    contract: str = "main",
    interval: Literal["minute", "hour", "day", "week", "month"] = "day",
    interval_multiplier: int = 1,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["sina"] = "sina",
) -> pd.DataFrame:
    """获取期货历史数据

    Args:
        symbol: 期货代码 (e.g., 'AG0' for 白银)
        contract: 合约代码 (默认 'main' 为主力合约，也可指定如 '2602')
        interval: 时间间隔 ('minute', 'hour', 'day', 'week', 'month')
        interval_multiplier: 时间间隔倍数 (e.g. 5 for 5 minutes)
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        source: 数据源 ('sina')

    Returns:
        pd.DataFrame:
        - timestamp: 时间戳
        - symbol: 期货代码
        - contract: 合约代码
        - open: 开盘价
        - high: 最高价
        - low: 最低价
        - close: 收盘价
        - volume: 成交量
        - open_interest: 持仓量
        - settlement: 结算价
    """
    kwargs = {
        "symbol": symbol,
        "contract": contract,
        "interval": interval,
        "interval_multiplier": interval_multiplier,
        "start_date": start_date,
        "end_date": end_date,
    }
    provider = FuturesDataFactory.get_historical_provider(source, **kwargs)
    return provider.get_hist_data()


def get_futures_realtime_data(
    symbol: str | None = None,
    source: Literal["sina"] = "sina",
) -> pd.DataFrame:
    """获取期货实时行情数据

    Args:
        symbol: 期货代码 (如 "CF")，为 None 时返回所有期货
        source: 数据源 ('sina')

    Returns:
        pd.DataFrame:
        - symbol: 期货代码
        - contract: 合约代码
        - price: 最新价
        - change: 涨跌额
        - pct_change: 涨跌幅(%)
        - timestamp: 时间戳
        - volume: 成交量
        - open_interest: 持仓量
        - open: 今开
        - high: 最高
        - low: 最低
        - prev_settlement: 昨结算
        - settlement: 最新结算价
    """
    provider = FuturesDataFactory.get_realtime_provider(source, symbol=symbol or "")
    if symbol:
        return provider.get_current_data()
    return provider.get_all_quotes()


def get_futures_main_contracts(
    source: Literal["sina"] = "sina",
) -> pd.DataFrame:
    """获取期货主力合约列表

    Args:
        source: 数据源 ('sina')

    Returns:
        pd.DataFrame:
        - symbol: 期货代码
        - name: 期货名称
        - contract: 主力合约代码
        - exchange: 交易所
    """
    from .modules.futures.sina import SinaFuturesHistorical

    provider = SinaFuturesHistorical(symbol="")
    return provider.get_main_contracts()


# ==================== Options API ====================


def get_options_chain(
    underlying_symbol: str,
    source: Literal["sina"] = "sina",
) -> pd.DataFrame:
    """获取期权链数据

    Args:
        underlying_symbol: 标的代码 (e.g., '510300' for 300ETF期权)
        source: 数据源 ('sina')

    Returns:
        pd.DataFrame:
        - underlying: 标的代码
        - symbol: 期权代码
        - name: 期权名称
        - option_type: 期权类型 (call/put)
        - strike: 行权价
        - expiration: 到期日
        - price: 最新价
        - change: 涨跌额
        - pct_change: 涨跌幅(%)
        - volume: 成交量
        - open_interest: 持仓量
        - implied_volatility: 隐含波动率
    """
    provider = OptionsDataFactory.get_provider(
        source, underlying_symbol=underlying_symbol
    )
    return provider.get_options_chain()


def get_options_realtime(
    symbol: str | None = None,
    underlying_symbol: str = "510300",
    source: Literal["sina"] = "sina",
) -> pd.DataFrame:
    """获取期权实时行情数据

    Args:
        symbol: 期权代码 (如 "10004005")，为 None 时返回标的下所有期权
        underlying_symbol: 标的代码 (e.g., '510300' for 300ETF期权)
        source: 数据源 ('sina')

    Returns:
        pd.DataFrame:
        - symbol: 期权代码
        - underlying: 标的代码
        - price: 最新价
        - change: 涨跌额
        - pct_change: 涨跌幅(%)
        - timestamp: 时间戳
        - volume: 成交量
        - open_interest: 持仓量
        - iv: 隐含波动率
    """
    if symbol:
        provider = OptionsDataFactory.get_provider(
            source, underlying_symbol=underlying_symbol
        )
        return provider.get_options_realtime(symbol)
    else:
        provider = OptionsDataFactory.get_provider(
            source, underlying_symbol=underlying_symbol
        )
        return provider.get_options_realtime("")


def get_options_expirations(
    underlying_symbol: str,
    source: Literal["sina"] = "sina",
) -> list[str]:
    """获取期权可用到期日列表

    Args:
        underlying_symbol: 标的代码
        source: 数据源 ('sina')

    Returns:
        list[str]: 可用的到期日列表
    """
    from .modules.options.sina import SinaOptionsProvider

    provider = SinaOptionsProvider(underlying_symbol=underlying_symbol)
    return provider.get_options_expirations(underlying_symbol)


def get_options_hist(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["sina"] = "sina",
) -> pd.DataFrame:
    """获取期权历史数据

    Args:
        symbol: 期权代码
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        source: 数据源 ('sina')

    Returns:
        pd.DataFrame:
        - timestamp: 时间戳
        - symbol: 期权代码
        - open: 开盘价
        - high: 最高价
        - low: 最低价
        - close: 收盘价
        - volume: 成交量
        - open_interest: 持仓量
        - settlement: 结算价
    """
    kwargs = {
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
    }
    provider = OptionsDataFactory.get_provider(source, underlying_symbol="")
    return provider.get_options_history(**kwargs)
