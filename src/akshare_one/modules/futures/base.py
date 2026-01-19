import re
from abc import ABC, abstractmethod

import pandas as pd


def parse_futures_symbol(symbol: str, contract: str = "main") -> tuple[str, str]:
    """Parse and normalize futures symbol and contract.

    This function intelligently handles various input formats:
    - symbol="CU", contract="main" → ("CU", "main")
    - symbol="CU0", contract="main" → ("CU", "main") - "0" is main contract indicator
    - symbol="AG2604" → ("AG", "2604") - extracts contract from symbol
    - symbol="AG", contract="2604" → ("AG", "2604")

    Args:
        symbol: Futures symbol, can include contract code (e.g., "CU", "CU0", "AG2604")
        contract: Contract code or "main" for main contract

    Returns:
        Tuple of (base_symbol, contract) where base_symbol is the variety code
        and contract is either "main" or the specific contract code
    """
    symbol = symbol.upper().strip()
    contract = contract.strip()

    # Extract the alphabetic prefix (variety code) and numeric suffix
    match = re.match(r"^([A-Z]+)(\d*)$", symbol)
    if not match:
        # If pattern doesn't match, return as-is
        return symbol, contract

    base_symbol = match.group(1)
    symbol_suffix = match.group(2)

    # If symbol has a numeric suffix
    if symbol_suffix:
        # "0" suffix indicates main contract (e.g., "CU0", "AG0")
        if symbol_suffix == "0":
            # This is main contract notation, use "main" as contract
            if contract.lower() == "main" or contract == "0":
                return base_symbol, "main"
            # If user explicitly provided a different contract, use it
            return base_symbol, contract
        else:
            # Symbol contains full contract code (e.g., "AG2604")
            # If contract is "main", the user likely meant to use the symbol's contract
            if contract.lower() == "main":
                return base_symbol, symbol_suffix
            # If contract is explicitly provided and different,
            # prefer contract parameter unless it's the same as symbol_suffix
            if contract != symbol_suffix and contract.lower() != "main":
                return base_symbol, contract
            return base_symbol, symbol_suffix

    # Symbol is just the variety code (e.g., "CU", "AG")
    return base_symbol, contract


class HistoricalFuturesDataProvider(ABC):
    def __init__(
        self,
        symbol: str,
        contract: str = "main",
        interval: str = "day",
        interval_multiplier: int = 1,
        start_date: str = "1970-01-01",
        end_date: str = "2030-12-31",
    ) -> None:
        # Parse and normalize symbol/contract
        self.symbol, self.contract = parse_futures_symbol(symbol, contract)
        self.interval = interval
        self.interval_multiplier = interval_multiplier
        self.start_date = start_date
        self.end_date = end_date
        self._validate_dates()

    def _validate_dates(self) -> None:
        try:
            pd.to_datetime(self.start_date)
            pd.to_datetime(self.end_date)
        except ValueError:
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.") from None

    @classmethod
    def get_supported_intervals(cls) -> list[str]:
        return ["minute", "hour", "day", "week", "month"]

    @abstractmethod
    def get_hist_data(self) -> pd.DataFrame:
        """Fetches historical futures market data

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
        pass

    @abstractmethod
    def get_main_contracts(self) -> pd.DataFrame:
        """Fetches main contract list

        Returns:
            pd.DataFrame:
            - symbol: 期货代码
            - name: 期货名称
            - contract: 主力合约代码
            - exchange: 交易所
        """
        pass


class RealtimeFuturesDataProvider(ABC):
    symbol: str | None
    contract: str | None
    original_symbol: str | None

    def __init__(self, symbol: str | None = None) -> None:
        if symbol:
            # Parse the symbol to extract base symbol for filtering
            # For realtime data, we want to support:
            # - symbol="CU" -> filter by variety code CU
            # - symbol="CU0" -> filter by variety code CU (main contract indicator)
            # - symbol="CU2405" -> filter by specific contract CU2405
            parsed_symbol, parsed_contract = parse_futures_symbol(symbol, "main")
            self.symbol = parsed_symbol
            self.contract = parsed_contract
            # Keep the original input for reference
            self.original_symbol = symbol.upper().strip()
        else:
            self.symbol = None
            self.contract = None
            self.original_symbol = None

    @abstractmethod
    def get_current_data(self) -> pd.DataFrame:
        """Fetches realtime futures market data

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
        pass

    @abstractmethod
    def get_all_quotes(self) -> pd.DataFrame:
        """Fetches all futures quotes

        Returns:
            pd.DataFrame: All futures market quotes
        """
        pass
