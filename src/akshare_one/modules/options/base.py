from abc import ABC, abstractmethod

import pandas as pd


class OptionsDataProvider(ABC):
    """Abstract base class for options data providers"""

    def __init__(
        self,
        underlying_symbol: str,
        option_type: str | None = None,
    ) -> None:
        """Initialize the options data provider

        Args:
            underlying_symbol: 标的代码 (e.g., '510300' for 300ETF期权)
            option_type: 期权类型 (call/put), 默认为 None
        """
        self.underlying_symbol = underlying_symbol
        self.option_type = option_type

    @abstractmethod
    def get_options_chain(self) -> pd.DataFrame:
        """Fetches options chain data

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
        pass

    @abstractmethod
    def get_options_realtime(self, symbol: str) -> pd.DataFrame:
        """Fetches realtime options quote data

        Args:
            symbol: 期权代码 (e.g., '10004005')

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
        pass

    @abstractmethod
    def get_options_expirations(self, underlying_symbol: str) -> list[str]:
        """Fetches available expiration dates for options

        Args:
            underlying_symbol: 标的代码

        Returns:
            list[str]: 可用的到期日列表
        """
        pass

    @abstractmethod
    def get_options_history(
        self,
        symbol: str,
        start_date: str = "1970-01-01",
        end_date: str = "2030-12-31",
    ) -> pd.DataFrame:
        """Fetches options historical data

        Args:
            symbol: 期权代码
            start_date: 开始日期
            end_date: 结束日期

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
        pass
