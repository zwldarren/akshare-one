import akshare as ak
import pandas as pd

from ..cache import cache
from .base import OptionsDataProvider


class SinaOptionsProvider(OptionsDataProvider):
    """Adapter for Sina/EastMoney options data API

    Note: Options data from akshare uses multiple API calls:
    - option_sse_list_sina: Get expiration dates
    - option_sse_codes_sina: Get option codes for a specific expiration
    - option_sse_spot_price_sina: Get realtime data for a specific option
    - option_sse_daily_sina: Get historical data for a specific option
    """

    @cache(
        "options_chain_cache",
        key=lambda self: f"sina_options_chain_{self.underlying_symbol}",
    )
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
        try:
            # Get expiration dates
            expirations = ak.option_sse_list_sina(symbol=self.underlying_symbol, exchange="null")

            if not expirations:
                raise ValueError(
                    f"No options found for underlying symbol: {self.underlying_symbol}"
                )

            # Get option codes for all expirations
            all_options = []
            for expiration in expirations:
                try:
                    # Get call options
                    call_codes = ak.option_sse_codes_sina(
                        symbol="看涨期权",
                        trade_date=expiration,
                        underlying=self.underlying_symbol,
                    )
                    if not call_codes.empty:
                        call_codes["option_type"] = "call"
                        call_codes["expiration"] = expiration
                        all_options.append(call_codes)

                    # Get put options
                    put_codes = ak.option_sse_codes_sina(
                        symbol="看跌期权",
                        trade_date=expiration,
                        underlying=self.underlying_symbol,
                    )
                    if not put_codes.empty:
                        put_codes["option_type"] = "put"
                        put_codes["expiration"] = expiration
                        all_options.append(put_codes)
                except Exception:
                    # Continue with other expirations if one fails
                    continue

            if not all_options:
                raise ValueError(
                    f"No options found for underlying symbol: {self.underlying_symbol}"
                )

            # Combine all options
            df = pd.concat(all_options, ignore_index=True)

            # Rename columns
            df = df.rename(columns={"期权代码": "symbol"})

            # Add underlying symbol
            df["underlying"] = self.underlying_symbol

            # Add placeholder columns for data that requires additional API calls
            df["name"] = ""
            df["strike"] = None
            df["price"] = None
            df["change"] = None
            df["pct_change"] = None
            df["volume"] = None
            df["open_interest"] = None
            df["implied_volatility"] = None

            return self._select_options_columns(df)
        except Exception as e:
            raise ValueError(f"Failed to fetch options chain: {str(e)}") from e

    @cache(
        "options_realtime_cache",
        key=lambda self, symbol: f"sina_options_realtime_{symbol}",
    )
    def get_options_realtime(self, symbol: str) -> pd.DataFrame:
        """Fetches realtime options quote data

        Args:
            symbol: 期权代码 (e.g., '10010459'), 传空字符串则获取该标的下的所有期权

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
        try:
            if not symbol:
                # Get all options for the underlying
                # First get the option chain
                chain_df = self.get_options_chain()
                if chain_df.empty:
                    return pd.DataFrame(
                        columns=[
                            "symbol",
                            "underlying",
                            "price",
                            "change",
                            "pct_change",
                            "timestamp",
                            "volume",
                            "open_interest",
                            "iv",
                        ]
                    )

                # Get realtime data for each option
                all_realtime = []
                for option_symbol in chain_df["symbol"].tolist():
                    try:
                        raw_df = ak.option_sse_spot_price_sina(symbol=option_symbol)
                        if not raw_df.empty:
                            realtime_df = self._clean_single_option(raw_df, option_symbol)
                            all_realtime.append(realtime_df)
                    except Exception:
                        # Skip options that fail to fetch
                        continue

                if not all_realtime:
                    return pd.DataFrame(
                        columns=[
                            "symbol",
                            "underlying",
                            "price",
                            "change",
                            "pct_change",
                            "timestamp",
                            "volume",
                            "open_interest",
                            "iv",
                        ]
                    )

                return pd.concat(all_realtime, ignore_index=True)

            # Get specific option data
            raw_df = ak.option_sse_spot_price_sina(symbol=symbol)

            if raw_df.empty:
                return pd.DataFrame(
                    columns=[
                        "symbol",
                        "underlying",
                        "price",
                        "change",
                        "pct_change",
                        "timestamp",
                        "volume",
                        "open_interest",
                        "iv",
                    ]
                )

            return self._clean_single_option(raw_df, symbol)
        except Exception as e:
            raise ValueError(f"Failed to fetch options realtime data: {str(e)}") from e

    def get_options_expirations(self, underlying_symbol: str) -> list[str]:
        """Fetches available expiration dates for options

        Args:
            underlying_symbol: 标的代码

        Returns:
            list[str]: 可用的到期日列表
        """
        try:
            expirations = ak.option_sse_list_sina(symbol=underlying_symbol, exchange="null")
            if not expirations:
                raise ValueError(f"No options found for underlying symbol: {underlying_symbol}")

            # Validate by trying to get option codes for the first expiration
            # This ensures the symbol is actually valid
            try:
                test_codes = ak.option_sse_codes_sina(
                    symbol="看涨期权",
                    trade_date=expirations[0],
                    underlying=underlying_symbol,
                )
                if test_codes.empty:
                    raise ValueError(f"No options found for underlying symbol: {underlying_symbol}")
            except Exception:
                raise ValueError(
                    f"No options found for underlying symbol: {underlying_symbol}"
                ) from None

            return sorted(expirations)
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to fetch options expirations: {str(e)}") from e

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
        try:
            raw_df = ak.option_sse_daily_sina(symbol=symbol)

            if raw_df.empty:
                return pd.DataFrame(
                    columns=[
                        "timestamp",
                        "symbol",
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume",
                        "open_interest",
                        "settlement",
                    ]
                )

            # Filter by date range
            raw_df["日期"] = pd.to_datetime(raw_df["日期"])
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            raw_df = raw_df[(raw_df["日期"] >= start_dt) & (raw_df["日期"] <= end_dt)]

            return self._clean_options_history(raw_df, symbol)
        except Exception as e:
            raise ValueError(f"Failed to fetch options history: {str(e)}") from e

    def _clean_single_option(self, raw_df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Cleans and standardizes single option data

        The data from option_sse_spot_price_sina is in a key-value format:
        - Column '字段' contains field names
        - Column '值' contains field values

        We need to pivot this into a single row DataFrame
        """
        if raw_df.empty or "字段" not in raw_df.columns or "值" not in raw_df.columns:
            return pd.DataFrame(
                columns=[
                    "symbol",
                    "underlying",
                    "price",
                    "change",
                    "pct_change",
                    "timestamp",
                    "volume",
                    "open_interest",
                    "iv",
                ]
            )

        # Create a dictionary from the key-value pairs
        data_dict = dict(zip(raw_df["字段"], raw_df["值"], strict=True))

        # Map Chinese field names to English
        field_map = {
            "最新价": "price",
            "涨跌额": "change",
            "涨幅": "pct_change",
            "成交量": "volume",
            "持仓量": "open_interest",
            "行情时间": "timestamp",
            "标的股票": "underlying",
            "期权合约简称": "name",
            "行权价": "strike",
            "昨收价": "prev_close",
        }

        # Extract and rename fields
        result = {}
        for chinese_field, english_field in field_map.items():
            value = data_dict.get(chinese_field)
            result[english_field] = value

        # Add symbol
        result["symbol"] = symbol

        # Parse numeric fields
        for field in [
            "price",
            "change",
            "pct_change",
            "volume",
            "open_interest",
            "strike",
            "prev_close",
        ]:
            if result.get(field) is not None:
                try:
                    result[field] = float(result[field])
                except (ValueError, TypeError):
                    result[field] = None

        # Parse timestamp
        if result.get("timestamp"):
            try:
                result["timestamp"] = pd.to_datetime(result["timestamp"])
            except (ValueError, TypeError):
                result["timestamp"] = pd.Timestamp.now(tz="Asia/Shanghai")
        else:
            result["timestamp"] = pd.Timestamp.now(tz="Asia/Shanghai")

        # Add implied volatility placeholder
        result["iv"] = None

        # Create DataFrame
        df = pd.DataFrame([result])

        # Ensure all required columns exist
        required_columns = [
            "symbol",
            "underlying",
            "price",
            "change",
            "pct_change",
            "timestamp",
            "volume",
            "open_interest",
            "iv",
        ]

        for col in required_columns:
            if col not in df.columns:
                df[col] = None

        return df[required_columns]

    def _clean_options_history(self, raw_df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Cleans and standardizes options historical data"""
        column_map = {
            "日期": "timestamp",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
        }

        available_columns = {
            src: target for src, target in column_map.items() if src in raw_df.columns
        }

        if not available_columns:
            raise ValueError("Expected columns not found in options history data")

        df = raw_df.rename(columns=available_columns)

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize("Asia/Shanghai")

        df["symbol"] = symbol

        # Add placeholder columns for missing data
        if "open_interest" not in df.columns:
            df["open_interest"] = None
        if "settlement" not in df.columns:
            df["settlement"] = None

        # Convert numeric columns
        numeric_columns = ["open", "high", "low", "close", "volume"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return self._select_history_columns(df)

    def _select_options_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Selects and orders the standard options chain columns"""
        standard_columns = [
            "underlying",
            "symbol",
            "name",
            "option_type",
            "strike",
            "expiration",
            "price",
            "change",
            "pct_change",
            "volume",
            "open_interest",
            "implied_volatility",
        ]
        return df[[col for col in standard_columns if col in df.columns]]

    def _select_history_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Selects and orders the standard options history columns"""
        standard_columns = [
            "timestamp",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "open_interest",
            "settlement",
        ]
        return df[[col for col in standard_columns if col in df.columns]]
