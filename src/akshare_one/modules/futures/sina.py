import akshare as ak
import pandas as pd

from ..cache import cache
from .base import HistoricalFuturesDataProvider, RealtimeFuturesDataProvider


class SinaFuturesHistorical(HistoricalFuturesDataProvider):
    """Adapter for Sina futures historical data API"""

    _exchange_map = {
        "CZCE": "CZCE",
        "SHFE": "SHFE",
        "DCE": "DCE",
        "ZCE": "CZCE",
    }

    @cache(
        "futures_hist_cache",
        key=lambda self: (
            f"sina_futures_hist_{self.symbol}_{self.contract}_{self.interval}_"
            f"{self.interval_multiplier}"
        ),
    )
    def get_hist_data(self) -> pd.DataFrame:
        """Fetches Sina historical futures market data

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
        self.interval = self.interval.lower()
        self._validate_interval_params(self.interval, self.interval_multiplier)

        try:
            if self.interval in ["minute", "hour"]:
                df = self._get_intraday_data()
            else:
                df = self._get_daily_data()

            return df
        except Exception as e:
            raise ValueError(f"Failed to fetch futures historical data: {str(e)}") from e

    def _get_intraday_data(self) -> pd.DataFrame:
        """Fetches intraday data at minute or hour intervals"""
        raw_df = ak.futures_zh_minute_sina(symbol=self._normalize_contract())

        if raw_df.empty:
            raise ValueError(f"No intraday data found for futures {self.symbol}:{self.contract}")

        # Filter by date range if needed
        if hasattr(raw_df, "index"):
            raw_df.index = pd.to_datetime(raw_df.index)
            if self.start_date and self.end_date:
                start_dt = pd.to_datetime(self.start_date)
                end_dt = pd.to_datetime(self.end_date) + pd.Timedelta(days=1)
                raw_df = raw_df[(raw_df.index >= start_dt) & (raw_df.index <= end_dt)]

        if self.interval_multiplier > 1:
            freq = (
                f"{self.interval_multiplier}min"
                if self.interval == "minute"
                else f"{self.interval_multiplier}h"
            )
            resampled = self._resample_intraday_data(raw_df, freq)
            return self._clean_intraday_data(resampled)

        return self._clean_intraday_data(raw_df)

    def _get_daily_data(self) -> pd.DataFrame:
        """Fetches daily and higher-level data (day/week/month)"""
        raw_df = ak.futures_zh_daily_sina(symbol=self._normalize_contract())

        if raw_df.empty:
            raise ValueError(f"No data found for futures {self.symbol}:{self.contract}")

        # Filter by date range if needed
        if hasattr(raw_df, "index"):
            raw_df.index = pd.to_datetime(raw_df.index)
            if self.start_date and self.end_date:
                start_dt = pd.to_datetime(self.start_date)
                end_dt = pd.to_datetime(self.end_date) + pd.Timedelta(days=1)
                raw_df = raw_df[(raw_df.index >= start_dt) & (raw_df.index <= end_dt)]

        if self.interval_multiplier > 1:
            raw_df = self._resample_data(raw_df, self.interval, self.interval_multiplier)

        return self._clean_daily_data(raw_df)

    def _normalize_contract(self) -> str:
        """Normalize contract symbol

        For main contracts, append "0" to the symbol (e.g., "CU" -> "CU0")
        as required by the Sina API.
        """
        if self.contract.lower() == "main":
            return f"{self.symbol}0"
        return f"{self.symbol}{self.contract}"

    def _validate_interval_params(self, interval: str, multiplier: int) -> None:
        """Validates the validity of interval and multiplier"""
        if interval not in self.get_supported_intervals():
            raise ValueError(f"Unsupported interval parameter: {interval}")

        if interval in ["minute", "hour"] and multiplier < 1:
            raise ValueError(f"interval_multiplier for {interval} level must be >= 1")

    def _ensure_time_format(self, date_str: str, default_time: str) -> str:
        """Ensures the date string includes the time part"""
        if " " not in date_str:
            return f"{date_str} {default_time}"
        return date_str

    def _convert_date_format(self, date_str: str) -> str:
        """Converts date format from YYYY-MM-DD to YYYYMMDD"""
        return date_str.replace("-", "") if "-" in date_str else date_str

    def _resample_intraday_data(self, df: pd.DataFrame, freq: str) -> pd.DataFrame:
        """Resamples intraday data to the specified frequency"""
        # Convert datetime index if it exists
        if "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"])
            df = df.set_index("datetime")
        elif hasattr(df, "index") and len(df.index) > 0:
            df.index = pd.to_datetime(df.index)

        resampled = df.resample(freq).agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
                "hold": "last",
            }
        )
        return resampled.reset_index()

    def _resample_data(self, df: pd.DataFrame, interval: str, multiplier: int) -> pd.DataFrame:
        """Resamples daily and higher-level data to the specified interval"""
        freq_map = {
            "day": f"{multiplier}D",
            "week": f"{multiplier}W-MON",
            "month": f"{multiplier}MS",
        }
        freq = freq_map[interval]

        # Convert date column if it exists
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date")
        elif hasattr(df, "index") and len(df.index) > 0:
            df.index = pd.to_datetime(df.index)

        resampled = df.resample(freq).agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
                "hold": "last",
                "settle": "last",
            }
        )
        return resampled.reset_index()

    def _clean_intraday_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes intraday data"""
        column_map = {
            "datetime": "timestamp",
            "date": "timestamp",
            "open": "open",
            "close": "close",
            "high": "high",
            "low": "low",
            "volume": "volume",
            "hold": "open_interest",
        }

        # Use raw column names, only map when key exists
        df = raw_df.copy()

        # Map columns if they exist
        for src, target in column_map.items():
            if src in df.columns and src != target:
                df = df.rename(columns={src: target})

        # Handle timestamp column
        if "timestamp" not in df.columns and hasattr(df, "index"):
            df["timestamp"] = df.index
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize("Asia/Shanghai")

        df["symbol"] = self.symbol
        df["contract"] = self.contract
        df["settlement"] = df.get("close")

        return self._select_standard_columns(df)

    def _clean_daily_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes daily data"""
        column_map = {
            "date": "timestamp",
            "open": "open",
            "close": "close",
            "high": "high",
            "low": "low",
            "volume": "volume",
            "hold": "open_interest",
            "settle": "settlement",
        }

        # Use raw column names, only map when key exists
        df = raw_df.copy()

        # Map columns if they exist
        for src, target in column_map.items():
            if src in df.columns and src != target:
                df = df.rename(columns={src: target})

        # Handle timestamp column
        if "timestamp" not in df.columns and hasattr(df, "index"):
            df["timestamp"] = df.index
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize("Asia/Shanghai")

        df["symbol"] = self.symbol
        df["contract"] = self.contract

        if "open_interest" in df.columns:
            df["open_interest"] = df["open_interest"].astype("int64")

        return self._select_standard_columns(df)

    def _select_standard_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Selects and orders the standard output columns"""
        standard_columns = [
            "timestamp",
            "symbol",
            "contract",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "open_interest",
            "settlement",
        ]
        result = df[[col for col in standard_columns if col in df.columns]]
        # Reset index to avoid displaying the original DataFrame index
        return result.reset_index(drop=True)

    def get_main_contracts(self) -> pd.DataFrame:
        """Fetches main contract list

        Returns:
            pd.DataFrame:
            - symbol: 期货代码
            - name: 期货名称
            - contract: 主力合约代码
            - exchange: 交易所
        """
        try:
            # Get futures contract info from different exchanges
            contracts_list = []
            exchanges = {
                "SHFE": "上海期货交易所",
                "DCE": "大连商品交易所",
                "CZCE": "郑州商品交易所",
                "CFFEX": "中国金融期货交易所",
            }

            for exchange_code, _exchange_name in exchanges.items():
                try:
                    # Try different API functions for each exchange
                    if exchange_code == "SHFE":
                        df = ak.futures_contract_info_shfe()
                    elif exchange_code == "DCE":
                        df = ak.futures_contract_info_dce()
                    elif exchange_code == "CZCE":
                        df = ak.futures_contract_info_czce()
                    elif exchange_code == "CFFEX":
                        df = ak.futures_contract_info_cffex()

                    if not df.empty and "symbol" in df.columns:
                        # Extract variety codes (usually first 1-2 characters)
                        df["variety"] = df["symbol"].str.extract(r"([A-Z]+)")[0]
                        df["exchange"] = exchange_code
                        contracts_list.append(df)
                except Exception:
                    continue

            if contracts_list:
                raw_df = pd.concat(contracts_list, ignore_index=True)
                return self._clean_main_contracts(raw_df)
            else:
                # Fallback: return available symbols from real-time data
                raw_df = ak.futures_zh_realtime()
                return self._clean_main_contracts_from_realtime(raw_df)
        except Exception as e:
            raise ValueError(f"Failed to fetch main contracts: {str(e)}") from e

    def _clean_main_contracts(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes main contracts data"""
        # Get unique varieties
        if "variety" in raw_df.columns and "symbol" in raw_df.columns:
            unique_varieties = raw_df[["variety", "exchange"]].drop_duplicates()
            unique_varieties.columns = ["symbol", "exchange"]
            unique_varieties["name"] = unique_varieties["symbol"]
            unique_varieties["contract"] = unique_varieties["symbol"]  # Placeholder
            return unique_varieties.reset_index(drop=True)

        return pd.DataFrame(columns=["symbol", "name", "contract", "exchange"])

    def _clean_main_contracts_from_realtime(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes main contracts from real-time data fallback"""
        if "symbol" in raw_df.columns:
            # Extract variety codes
            raw_df["symbol_root"] = raw_df["symbol"].astype(str).str.extract(r"([A-Z]+)")[0]
            raw_df["exchange"] = raw_df.get("exchange", "")

            # Get unique varieties
            result = raw_df[["symbol_root", "exchange"]].drop_duplicates()
            result.columns = ["symbol", "exchange"]
            result["name"] = result["symbol"]
            result["contract"] = result["symbol"]

            return result.reset_index(drop=True)

        return pd.DataFrame(columns=["symbol", "name", "contract", "exchange"])


def _build_cache_key(provider: "SinaFuturesRealtime") -> str:
    """Build cache key for SinaFuturesRealtime."""
    symbol_part = provider.symbol if provider.symbol else "all"
    contract_part = provider.contract if provider.contract else "all"
    return f"sina_futures_{symbol_part}_{contract_part}"


class SinaFuturesRealtime(RealtimeFuturesDataProvider):
    """Adapter for Sina futures realtime data API"""

    @cache("futures_realtime_cache", key=_build_cache_key)
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
        try:
            raw_df = ak.futures_zh_spot()
        except Exception:
            # Fallback to futures_zh_realtime if futures_zh_spot fails
            raw_df = ak.futures_zh_realtime()
        df = self._clean_spot_data(raw_df)

        # Filter by symbol if provided
        if self.symbol:
            symbol_upper = self.symbol.upper()

            # Check if we have a specific contract (not main)
            if self.contract and self.contract.lower() != "main":
                # Filter by specific contract (e.g., "AG2604")
                full_symbol = f"{symbol_upper}{self.contract}"
                df = df[df["symbol"] == full_symbol].reset_index(drop=True)
            else:
                # Filter by variety code (symbol_root) to get all contracts
                # This handles cases like symbol="CU", symbol="CU0"
                if "symbol_root" in df.columns:
                    df = df[df["symbol_root"] == symbol_upper].reset_index(drop=True)
                else:
                    # Fallback to prefix match
                    df = df[df["symbol"].str.startswith(symbol_upper)].reset_index(drop=True)

        return df

    def get_all_quotes(self) -> pd.DataFrame:
        """Fetches all futures quotes

        Returns:
            pd.DataFrame: All futures market quotes
        """
        return self.get_current_data()

    def _clean_spot_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes realtime futures data.

        Handle both Chinese column names (futures_zh_spot) and
        English column names (futures_zh_realtime).
        """
        chinese_mapping = {
            "代码": "symbol",
            "名称": "name",
            "最新价": "price",
            "涨跌额": "change",
            "涨跌幅": "pct_change",
            "开盘价": "open",
            "最高价": "high",
            "最低价": "low",
            "昨收": "prev_close",
            "成交量": "volume",
            "持仓量": "open_interest",
            "结算价": "settlement",
            "昨结算": "prev_settlement",
        }

        english_mapping = {
            "symbol": "symbol",
            "trade": "price",
            "open": "open",
            "high": "high",
            "low": "low",
            # Note: 'close' column often contains 0, use 'trade' for price instead
            "settlement": "settlement",
            # Use prevsettlement (preferred) or presettlement as fallback
            "prevsettlement": "prev_settlement",
            "volume": "volume",
            "position": "open_interest",
            "changepercent": "pct_change",
        }

        # Detect which format we have
        if any(cn in raw_df.columns for cn in chinese_mapping):
            mapping = chinese_mapping
        else:
            mapping = english_mapping

        # Build available columns, avoiding duplicate target names
        available_columns = {}
        used_targets = set()
        for src, target in mapping.items():
            if src in raw_df.columns and target not in used_targets:
                available_columns[src] = target
                used_targets.add(target)

        df = raw_df.rename(columns=available_columns)

        # Handle presettlement as fallback if prevsettlement wasn't available
        if "prev_settlement" not in df.columns and "presettlement" in raw_df.columns:
            df["prev_settlement"] = raw_df["presettlement"]

        # Calculate change if not present
        if "change" not in df.columns and "price" in df.columns and "prev_settlement" in df.columns:
            df["change"] = df["price"] - df["prev_settlement"]

        # Calculate pct_change if not present
        if (
            "pct_change" not in df.columns
            and "change" in df.columns
            and "prev_settlement" in df.columns
        ):
            df["pct_change"] = (df["change"] / df["prev_settlement"] * 100).round(2)

        df = df.assign(
            timestamp=pd.Timestamp.now(tz="Asia/Shanghai"),
            settlement=lambda x: x.get("settlement", x.get("price")),
        )

        # Extract contract from symbol (e.g., "cu2401" -> "CU", "2401")
        if "symbol" in df.columns:
            # Handle both lowercase and uppercase symbols
            df["symbol"] = df["symbol"].astype(str).str.upper()
            # Extract alphabetic prefix as symbol_root (variety code)
            df["symbol_root"] = df["symbol"].str.extract(r"^([A-Z]+)", expand=False)
            # Extract numeric suffix as contract
            df["contract"] = df["symbol"].str.extract(r"([0-9]+)$", expand=False).fillna("")

        required_columns = [
            "symbol",
            "symbol_root",
            "contract",
            "price",
            "change",
            "pct_change",
            "timestamp",
            "volume",
            "open_interest",
            "open",
            "high",
            "low",
            "prev_settlement",
            "settlement",
        ]
        return df[[col for col in required_columns if col in df.columns]]
