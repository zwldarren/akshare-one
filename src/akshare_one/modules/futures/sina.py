import logging

import akshare as ak
import pandas as pd

from ..cache import cached
from ..registry import provider
from ..schema import normalize
from .base import HistoricalFuturesDataProvider, RealtimeFuturesDataProvider
from .schema import CONTRACT_COLUMNS, HIST_COLUMNS, REALTIME_COLUMNS

logger = logging.getLogger(__name__)

# Roots whose quotes Sina serves with the non-commodity column layout.
_CFFEX_ROOTS = frozenset({"IF", "IH", "IC", "IM", "T", "TF", "TS", "TL"})


@provider("futures", "sina", capability="historical")
class SinaFuturesHistorical(HistoricalFuturesDataProvider):
    """Adapter for Sina futures historical data API"""

    _exchange_map = {
        "CZCE": "CZCE",
        "SHFE": "SHFE",
        "DCE": "DCE",
        "ZCE": "CZCE",
    }

    @cached("futures_hist")
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

        raw_df = self._filter_by_date(raw_df)

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

        raw_df = self._filter_by_date(raw_df)

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

    def _filter_by_date(self, df: pd.DataFrame) -> pd.DataFrame:
        """Restrict a raw Sina futures frame to ``[start_date, end_date]``.

        Sina returns the date in a column (``date`` for daily data, ``datetime``
        for intraday data) together with a default ``RangeIndex``. Converting
        that index to datetimes yields 1970 timestamps, so the filter must use
        the date column instead -- otherwise every real date range returns an
        empty frame while the default 1970 range silently passes.
        """
        if df.empty or not (self.start_date and self.end_date):
            return df

        date_col = next((col for col in ("datetime", "date") if col in df.columns), None)
        if date_col is None:
            return df

        dates = pd.to_datetime(df[date_col], errors="coerce")
        start_dt = pd.to_datetime(self.start_date)
        # Half-open upper bound so the whole end day is included but the next
        # day is not.
        end_dt = pd.to_datetime(self.end_date) + pd.Timedelta(days=1)
        mask = ((dates >= start_dt) & (dates < end_dt)).to_numpy()
        return df.loc[mask]

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

        return normalize(df, HIST_COLUMNS).reset_index(drop=True)

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

        return normalize(df, HIST_COLUMNS).reset_index(drop=True)

    # Column holding the contract code in akshare's exchange listings. The name
    # differs per exchange ("合约代码" for SHFE/CZCE/CFFEX, "合约" for DCE).
    _CONTRACT_CODE_COLUMNS = ("合约代码", "合约", "symbol")

    @cached("futures_contracts")
    def get_main_contracts(self) -> pd.DataFrame:
        """Fetches the tradable variety list per exchange.

        akshare's exchange listings name the contract-code column differently
        per exchange, which the previous implementation did not account for, so
        it never matched and always fell through to a broken fallback.

        The CFFEX endpoint is often very slow (minutes), so the result is
        cached for 24 hours. An exchange that errors or returns an unexpected
        shape is skipped with a warning instead of failing the whole call.

        ``contract`` is a placeholder equal to ``symbol``: resolving the actual
        front-month contract requires one request per variety via akshare/sina,
        which is too expensive to do here.

        Returns:
            pd.DataFrame:
            - symbol: 期货品种代码
            - name: 期货品种名称
            - contract: 主力合约代码 (placeholder, currently == symbol)
            - exchange: 交易所
        """
        exchanges = {
            "SHFE": ak.futures_contract_info_shfe,
            "DCE": ak.futures_contract_info_dce,
            "CZCE": ak.futures_contract_info_czce,
            "CFFEX": ak.futures_contract_info_cffex,
        }

        frames = []
        for exchange_code, fetch in exchanges.items():
            try:
                raw = fetch()
            except Exception as exc:
                logger.warning("Failed to fetch %s contract info: %s", exchange_code, exc)
                continue
            if raw is None or raw.empty:
                continue

            code_col = next(
                (col for col in self._CONTRACT_CODE_COLUMNS if col in raw.columns), None
            )
            if code_col is None:
                logger.warning("%s contract info has no contract-code column", exchange_code)
                continue

            # Contract codes look like "CF2601"/"TA601"; the leading letters are
            # the variety code.
            varieties = (
                raw[code_col].astype(str).str.extract(r"^([A-Za-z]+)", expand=False).str.upper()
            )
            frames.append(pd.DataFrame({"symbol": varieties, "exchange": exchange_code}))

        if not frames:
            return normalize(pd.DataFrame(), CONTRACT_COLUMNS)

        all_df = pd.concat(frames, ignore_index=True).dropna(subset=["symbol"])
        all_df = all_df[all_df["symbol"] != ""]
        all_df = all_df.drop_duplicates(subset=["symbol", "exchange"]).reset_index(drop=True)
        all_df["name"] = all_df["symbol"]
        all_df["contract"] = all_df["symbol"]
        return normalize(all_df, CONTRACT_COLUMNS)


@cached("futures_varieties")
def _main_contract_table() -> pd.DataFrame:
    """Main-continuous contract table (symbol/exchange/name) for all varieties.

    Sina has no endpoint that returns the whole futures market at once, so this
    uses akshare's main-contract listing and caches it under the
    ``futures_varieties`` namespace — its key is constant, so the table holds
    one entry no matter how many provider instances ask for it. The first call
    issues one request per listed variety.
    """
    empty = normalize(pd.DataFrame(), CONTRACT_COLUMNS)
    try:
        table = ak.futures_display_main_sina()
    except Exception as exc:  # pragma: no cover - network dependent
        logger.warning("Unable to fetch main futures contracts: %s", exc)
        return empty
    if table is None or table.empty or "symbol" not in table.columns:
        return empty
    return table


def _market_for(root: str) -> str:
    """Sina serves financial (CFFEX) futures with a different column layout."""
    return "FF" if root.upper() in _CFFEX_ROOTS else "CF"


@provider("futures", "sina", capability="realtime")
class SinaFuturesRealtime(RealtimeFuturesDataProvider):
    """Adapter for Sina futures realtime data API"""

    def _requested_contract(self) -> str:
        """Contract code to subscribe to, e.g. ``CF0`` or ``CF2701``."""
        if self.contract and self.contract.lower() != "main":
            return f"{self.symbol}{self.contract}"
        return f"{self.symbol}0"

    @cached("futures_realtime")
    def get_current_data(self) -> pd.DataFrame:
        """Fetches realtime futures market data for one variety/contract.

        ``ak.futures_zh_spot`` must be told which contract to subscribe to:
        without an explicit symbol it defaults to a long-expired contract, so
        the result used to always be an empty frame.

        Returns:
            pd.DataFrame: the domain's declared columns, see
                :mod:`akshare_one.modules.futures.schema`.
        """
        if not self.symbol:
            return self.get_all_quotes()

        contract = self._requested_contract()
        raw_df = ak.futures_zh_spot(
            symbol=contract,
            market=_market_for(self.symbol),
            adjust="0",
        )
        df = self._clean_spot_data(raw_df)
        return self._attach_contract_identity(df, [contract])

    def get_all_quotes(self) -> pd.DataFrame:
        """Fetches main-continuous quotes for every listed commodity variety.

        Financial (CFFEX) varieties are handled by :meth:`get_current_data`
        because Sina reports them with a different column layout.

        Returns:
            pd.DataFrame: Futures market quotes.
        """
        table = _main_contract_table()
        if table.empty:
            return normalize(pd.DataFrame(), REALTIME_COLUMNS)

        commodities = [
            str(code)
            for code in table["symbol"].tolist()
            if str(code).strip().rstrip("0123456789").upper() not in _CFFEX_ROOTS
        ]
        if not commodities:
            return normalize(pd.DataFrame(), REALTIME_COLUMNS)

        raw_df = ak.futures_zh_spot(
            symbol=",".join(commodities),
            market="CF",
            adjust="0",
        )
        df = self._clean_spot_data(raw_df)

        # futures_zh_spot reports the Chinese contract name, not the code, so
        # translate it back through the main-contract table.
        if "name" in df.columns and "name" in table.columns:
            name_to_code = dict(zip(table["name"], table["symbol"], strict=True))
            df["symbol"] = df["name"].map(name_to_code).fillna(df["name"])
        return self._attach_contract_identity(df, [])

    @staticmethod
    def _attach_contract_identity(df: pd.DataFrame, contracts: list[str]) -> pd.DataFrame:
        """Derive ``symbol``/``symbol_root``/``contract`` from requested codes."""
        if df.empty:
            return normalize(df, REALTIME_COLUMNS)

        df = df.reset_index(drop=True)
        if contracts and len(contracts) == len(df):
            df["symbol"] = [code.upper() for code in contracts]

        if "symbol" in df.columns:
            symbols = df["symbol"].astype(str).str.upper()
            df["symbol"] = symbols
            df["symbol_root"] = symbols.str.extract(r"^([A-Z]+)", expand=False)
            df["contract"] = symbols.str.extract(r"([0-9]+)$", expand=False).fillna("")

        return normalize(df, REALTIME_COLUMNS)

    def _clean_spot_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes realtime futures data.

        Handles the three upstream shapes seen in practice:
        - ``futures_zh_spot`` (``current_price`` / ``hold`` / ``last_settle_price``);
        - ``futures_zh_realtime`` (English ``trade`` / ``position`` columns);
        - legacy Chinese column names.
        """
        spot_mapping = {
            # futures_zh_spot reports the Chinese contract name under 'symbol';
            # the caller re-attaches the real contract code afterwards.
            "symbol": "name",
            "current_price": "price",
            "hold": "open_interest",
            "last_settle_price": "prev_settlement",
            "last_close": "prev_close",
            "avg_price": "vwap",
            "open": "open",
            "high": "high",
            "low": "low",
            "volume": "volume",
        }

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

        # Detect which format we have: futures_zh_spot uses 'current_price',
        # futures_zh_realtime uses English names, the legacy shape uses Chinese.
        if "current_price" in raw_df.columns:
            mapping = spot_mapping
        elif any(cn in raw_df.columns for cn in chinese_mapping):
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

        # Extract contract from symbol (e.g., "cu2401" -> "CU", "2401").
        # futures_zh_spot rows carry the Chinese contract name instead and are
        # identified by the caller via _attach_contract_identity.
        if "symbol" in df.columns:
            df["symbol"] = df["symbol"].astype(str).str.upper()
            df["symbol_root"] = df["symbol"].str.extract(r"^([A-Z]+)", expand=False)
            df["contract"] = df["symbol"].str.extract(r"([0-9]+)$", expand=False).fillna("")

        # Keep 'name' when present so callers can map the Chinese contract
        # name back to a code (futures_zh_spot does not return the code).
        return normalize(df, REALTIME_COLUMNS)
