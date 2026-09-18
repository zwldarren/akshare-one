from typing import Any

import requests

# EastMoney serves the same quote API from several hosts. Some of them
# (notably ``push2.eastmoney.com`` when queried from outside mainland China)
# intermittently answer 502 or drop the connection, so requests fall back to
# the next host before giving up.
_QUOTE_HOSTS = (
    "push2.eastmoney.com",
    "82.push2.eastmoney.com",
    "push2delay.eastmoney.com",
)
_KLINE_HOSTS = ("push2his.eastmoney.com",)
# Financial statements come from the datacenter API, which is a separate host
# and returns a different envelope (``result.data``).
_DATACENTER_HOSTS = ("datacenter-web.eastmoney.com",)
_DEFAULT_TIMEOUT = 15.0


class EastMoneyClient:
    """
    A client for interacting directly with EastMoney's data APIs.
    This class handles session management, request signing, and API calls.
    """

    def __init__(self, timeout: float = _DEFAULT_TIMEOUT) -> None:
        self.session = requests.Session()
        self.timeout = timeout

    def _get_json(
        self, path: str, params: dict[str, Any], hosts: tuple[str, ...]
    ) -> dict[str, Any]:
        """GET ``path`` from the first host that returns usable JSON.

        EastMoney gateway errors are sometimes served with HTTP 200 and an HTML
        body, so a failed ``response.json()`` is treated like a transport error
        and the next host is tried. The last error is re-raised when every host
        fails.
        """
        last_error: Exception | None = None
        for host in hosts:
            url = f"https://{host}{path}"
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except Exception as exc:
                last_error = exc
        raise ConnectionError(
            f"All EastMoney hosts failed for {path}: {last_error}"
        ) from last_error

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
            elif symbol.startswith(("600", "601", "603", "605", "688", "900", "5", "6")):
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
        params = {
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "klt": klt,
            "fqt": fqt,
            "secid": self._get_security_id(symbol),
            "beg": start_date,
            "end": end_date,
        }
        return self._get_json("/api/qt/stock/kline/get", params, _KLINE_HOSTS)

    def fetch_realtime_quote(self, symbol: str) -> dict[str, Any]:
        """
        Fetches real-time quote data for a single stock.
        """
        params = {
            "invt": "2",
            "fltt": "2",
            "fields": (
                "f43,f57,f58,f169,f170,f46,f60,f44,f51,f168,f47,f164,f163,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530"
            ),
            "secid": self._get_security_id(symbol),
        }
        return self._get_json("/api/qt/stock/get", params, _QUOTE_HOSTS)

    def fetch_basic_info(self, symbol: str) -> dict[str, Any]:
        """
        Fetches basic profile data (name, shares, market cap, industry, ...)
        for a single stock.
        """
        params = {
            "fltt": "2",
            "invt": "2",
            "fields": "f43,f57,f58,f84,f85,f116,f117,f127,f189",
            "secid": self._get_security_id(symbol),
        }
        return self._get_json("/api/qt/stock/get", params, _QUOTE_HOSTS)

    def fetch_datacenter_report(
        self, report_name: str, symbol: str, fields: list[str]
    ) -> list[dict[str, Any]]:
        """
        Fetches one financial report body for a single stock.

        Args:
            report_name: EastMoney report id, e.g. ``"RPT_DMSK_FN_BALANCE"``.
            symbol: Security code, e.g. ``"600000"``.
            fields: Upstream field names to request, which is also the set of
                keys each returned row carries.

        Returns:
            list[dict]: The report rows, newest first; empty when the report has
            no rows for ``symbol``.

        Raises:
            ConnectionError: If every host fails. A transport or gateway failure
                is deliberately not folded into the empty result, so a caller can
                tell "this company has no such report" from "the request failed".
        """
        params = {
            "reportName": report_name,
            "filter": f'(SECURITY_CODE="{symbol}")',
            "pageNumber": "1",
            "pageSize": "1000",
            "sortColumns": "REPORT_DATE",
            "sortTypes": "-1",
            "columns": ",".join(fields),
        }
        payload = self._get_json("/api/data/v1/get", params, _DATACENTER_HOSTS)
        result = payload.get("result") or {}
        rows = result.get("data") or []
        return list(rows)
