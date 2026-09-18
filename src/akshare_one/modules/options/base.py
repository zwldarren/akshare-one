from abc import ABC, abstractmethod

import pandas as pd


class OptionsDataProvider(ABC):
    """Abstract base class for options data providers"""

    #: Parameters that change the answer; the cache key is built from these.
    CACHE_PARAMS = ("underlying_symbol", "symbol")

    def __init__(
        self,
        underlying_symbol: str = "",
        symbol: str | None = None,
    ) -> None:
        """Initialize the options data provider

        Args:
            underlying_symbol: 标的代码 (e.g., '510300' for 300ETF期权)
            symbol: 期权代码 (e.g., '10004005')；为空表示该标的下的所有期权
        """
        self.underlying_symbol = underlying_symbol
        self.symbol = symbol or ""

    @abstractmethod
    def get_options_chain(self) -> pd.DataFrame:
        """Fetches options chain data

        Returns:
            pd.DataFrame: the domain's declared columns, see
                :mod:`akshare_one.modules.options.schema`.
        """
        pass

    @abstractmethod
    def get_options_realtime(self) -> pd.DataFrame:
        """Fetches realtime options quote data

        The option code comes from the constructor's ``symbol``; an empty one
        means every option of ``underlying_symbol``.

        Returns:
            pd.DataFrame: the domain's declared columns, see
                :mod:`akshare_one.modules.options.schema`.
        """
        pass

    @abstractmethod
    def get_options_expirations(self) -> list[str]:
        """Fetches available expiration dates for options

        Returns:
            list[str]: 可用的到期日列表
        """
        pass

    @abstractmethod
    def get_options_history(
        self,
        start_date: str = "1970-01-01",
        end_date: str = "2030-12-31",
    ) -> pd.DataFrame:
        """Fetches options historical data

        The option code comes from the constructor's ``symbol``.

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: the domain's declared columns, see
                :mod:`akshare_one.modules.options.schema`.
        """
        pass
