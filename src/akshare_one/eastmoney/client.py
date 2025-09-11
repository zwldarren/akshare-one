from typing import Any

import requests


class EastMoneyClient:
    """
    A client for interacting directly with EastMoney's data APIs.
    This class handles session management, request signing, and API calls.
    """

    def __init__(self) -> None:
        self.session = requests.Session()

    def _get_security_id(self, symbol: str) -> str:
        """
        Converts a stock symbol to EastMoney's internal secid format.
        e.g., '600519' -> '1.600519', '000001' -> '0.000001'
        """
        symbol = symbol.upper()
        if symbol.startswith("SZ"):
            market = "0"
            code = symbol[2:]
        elif symbol.startswith("SH"):
            market = "1"
            code = symbol[2:]
        elif symbol.startswith("HK"):
            market = "116"
            code = symbol[2:]
        elif len(symbol) == 6:
            if symbol.startswith(("000", "001", "002", "003", "300", "200")):
                market = "0"
            elif symbol.startswith(("600", "601", "603", "605", "688", "900")):
                market = "1"
            else:
                market = "0"  # Default to SZ for ambiguity
            code = symbol
        elif len(symbol) == 5:  # HK Market
            market = "116"
            code = symbol
        else:
            market = "0"
            code = symbol
        return f"{market}.{code}"

    def fetch_historical_klines(
        self, symbol: str, klt: str, fqt: str, start_date: str, end_date: str
    ) -> dict[str, Any]:
        """
        Fetches historical K-line (candlestick) data.
        """
        url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        secid = self._get_security_id(symbol)
        params = {
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "klt": klt,
            "fqt": fqt,
            "secid": secid,
            "beg": start_date,
            "end": end_date,
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()  # type: ignore

    def fetch_realtime_quote(self, symbol: str) -> dict[str, Any]:
        """
        Fetches real-time quote data for a single stock.
        """
        url = "https://push2.eastmoney.com/api/qt/stock/get"
        secid = self._get_security_id(symbol)
        params = {
            "invt": "2",
            "fltt": "2",
            "fields": (
                "f43,f57,f58,f169,f170,f46,f60,f44,f51,f168,f47,f164,f163,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530"
            ),
            "secid": secid,
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()  # type: ignore
