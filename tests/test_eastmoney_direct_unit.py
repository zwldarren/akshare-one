"""Offline tests for the EastMoney direct client and the providers built on it.

Everything here is mocked -- no network access. These cover:

- host fallback when ``push2.eastmoney.com`` returns 502 / an HTML body;
- basic-info parsing from the raw quote payload;
- single-symbol realtime using one request instead of the full A-share snapshot.
"""

from typing import Any, cast
from unittest.mock import patch

import pandas as pd
import pytest
import requests

from akshare_one.eastmoney.client import EastMoneyClient
from akshare_one.eastmoney.utils import parse_basic_info
from akshare_one.modules.cache import clear
from akshare_one.modules.financial.eastmoney_direct import EastMoneyDirectFinancialReport
from akshare_one.modules.financial.schema import BALANCE_COLUMNS, INCOME_COLUMNS
from akshare_one.modules.info.eastmoney import EastmoneyInfo
from akshare_one.modules.realtime.eastmoney import EastmoneyRealtime


@pytest.fixture(autouse=True)
def _disable_cache(monkeypatch):
    monkeypatch.setenv("AKSHARE_ONE_CACHE_ENABLED", "false")


class _Response:
    def __init__(self, payload=None, status=200):
        self._payload = payload
        self.status_code = status
        self.text = "<html>502 Bad Gateway</html>" if payload is None else "{}"

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")

    def json(self):
        if self._payload is None:
            raise ValueError("Expecting value: line 1 column 1 (char 0)")
        return self._payload


class TestSecurityId:
    @pytest.mark.parametrize(
        ("symbol", "expected"),
        [
            ("600000", "1.600000"),
            ("000001", "0.000001"),
            ("300750", "0.300750"),
            ("688981", "1.688981"),
            ("510300", "1.510300"),
            ("00700", "116.00700"),
            ("SH600000", "1.600000"),
            ("SZ000001", "0.000001"),
            ("HK00700", "116.00700"),
        ],
    )
    def test_security_id(self, symbol, expected):
        assert EastMoneyClient()._get_security_id(symbol) == expected


class TestHostFallback:
    def test_falls_back_on_502(self):
        calls = []

        def fake_get(url: Any, params: Any = None, timeout: Any = None) -> _Response:
            calls.append(url)
            if "push2.eastmoney.com" in url or "82.push2" in url:
                return _Response(status=502)
            return _Response(payload={"rc": 0, "data": {"f57": "600000"}})

        client = EastMoneyClient()
        client.session.get = cast(Any, fake_get)
        result = client.fetch_realtime_quote("600000")

        assert result["rc"] == 0
        assert len(calls) == 3
        assert "push2delay.eastmoney.com" in calls[-1]

    def test_falls_back_on_html_200(self):
        calls = []

        def fake_get(url: Any, params: Any = None, timeout: Any = None) -> _Response:
            calls.append(url)
            if "push2delay" not in url:
                # 200 OK but the body is a gateway error page.
                return _Response(payload=None)
            return _Response(payload={"rc": 0, "data": {"f57": "600000"}})

        client = EastMoneyClient()
        client.session.get = cast(Any, fake_get)
        result = client.fetch_realtime_quote("600000")

        assert result["rc"] == 0
        assert len(calls) == 3

    def test_raises_when_every_host_fails(self):
        client = EastMoneyClient()
        client.session.get = cast(Any, lambda *a, **k: _Response(status=502))
        with pytest.raises(ConnectionError, match="All EastMoney hosts failed"):
            client.fetch_realtime_quote("600000")


class TestParseBasicInfo:
    def test_parses_and_coerces(self):
        payload = {
            "rc": 0,
            "data": {
                "f43": 9.07,
                "f57": "600000",
                "f58": "浦发银行",
                "f84": 29352108000,
                "f85": 29352108000,
                "f116": 266000000000,
                "f117": 266000000000,
                "f127": "银行",
                "f189": 19991110,
            },
        }
        df = parse_basic_info(payload)

        assert list(df.columns) == [
            "price",
            "symbol",
            "name",
            "total_shares",
            "float_shares",
            "total_market_cap",
            "float_market_cap",
            "industry",
            "listing_date",
        ]
        row = df.iloc[0]
        assert row["symbol"] == "600000"
        assert row["name"] == "浦发银行"
        assert row["price"] == pytest.approx(9.07)
        assert row["total_market_cap"] == 266000000000
        assert row["listing_date"] == pd.Timestamp("1999-11-10")

    def test_empty_payload(self):
        """The parser does not own the column contract; the provider projects it.

        The provider-level guarantee that a partial or empty payload still
        returns every declared column is asserted in ``tests/test_schema.py``.
        """
        df = parse_basic_info({"rc": 0, "data": None})
        assert df.empty
        assert list(df.columns) == []


class TestInfoProvider:
    def test_uses_direct_client(self):
        payload = {
            "rc": 0,
            "data": {"f43": 1.0, "f57": "600000", "f58": "浦发银行", "f189": 19991110},
        }
        with patch(
            "akshare_one.modules.info.eastmoney.EastMoneyClient.fetch_basic_info",
            return_value=payload,
        ) as mock_fetch:
            df = EastmoneyInfo("600000").get_basic_info()

        mock_fetch.assert_called_once_with("600000")
        assert df.iloc[0]["name"] == "浦发银行"

    def test_raises_on_error_payload(self):
        with (
            patch(
                "akshare_one.modules.info.eastmoney.EastMoneyClient.fetch_basic_info",
                return_value={"rc": 1, "data": None},
            ),
            pytest.raises(ValueError, match="No basic info found"),
        ):
            EastmoneyInfo("600000").get_basic_info()


class TestRealtimeProvider:
    def _payload(self):
        return {
            "rc": 0,
            "data": {"f57": "600000", "f43": 9.07, "f169": 0.01, "f170": 0.11, "f60": 9.06},
        }

    def test_single_symbol_skips_full_snapshot(self):
        with (
            patch(
                "akshare_one.modules.realtime.eastmoney.EastMoneyClient.fetch_realtime_quote",
                return_value=self._payload(),
            ) as mock_fetch,
            patch("akshare_one.modules.realtime.eastmoney.ak.stock_zh_a_spot_em") as mock_spot,
        ):
            df = EastmoneyRealtime("600000").get_current_data()

        mock_fetch.assert_called_once_with("600000")
        mock_spot.assert_not_called()
        assert df.iloc[0]["symbol"] == "600000"

    def test_no_symbol_uses_full_snapshot(self):
        raw = pd.DataFrame(
            {
                "代码": ["600000"],
                "最新价": [9.07],
                "涨跌额": [0.01],
                "涨跌幅": [0.11],
                "成交量": [100],
                "成交额": [1000],
                "今开": [9.0],
                "最高": [9.1],
                "最低": [8.9],
                "昨收": [9.06],
            }
        )
        with patch(
            "akshare_one.modules.realtime.eastmoney.ak.stock_zh_a_spot_em",
            return_value=raw,
        ) as mock_spot:
            df = EastmoneyRealtime("").get_current_data()

        mock_spot.assert_called_once()
        assert list(df["symbol"]) == ["600000"]


class TestDatacenterReport:
    """The datacenter envelope (`result.data`) is the client's to navigate."""

    def _client(self, payload=None, error=None):
        client = EastMoneyClient()

        def fake_get(url: Any, params: Any = None, timeout: Any = None) -> _Response:
            if error is not None:
                raise error
            return _Response(payload=payload)

        client.session.get = cast(Any, fake_get)
        return client

    def test_returns_the_rows(self):
        rows = [{"REPORT_DATE": "2025-12-31", "TOTAL_ASSETS": 1.0}]
        client = self._client(payload={"result": {"data": rows}})

        fetched = client.fetch_datacenter_report("RPT_DMSK_FN_BALANCE", "600000", ["REPORT_DATE"])

        assert fetched == rows

    def test_no_rows_is_not_an_error(self):
        client = self._client(payload={"result": None})

        assert client.fetch_datacenter_report("RPT_DMSK_FN_BALANCE", "600000", []) == []

    def test_a_failed_request_is_reported(self):
        client = self._client(error=requests.ConnectionError("boom"))

        with pytest.raises(ConnectionError):
            client.fetch_datacenter_report("RPT_DMSK_FN_BALANCE", "600000", ["REPORT_DATE"])


class TestFinancialDirectProvider:
    """Statements come from one request path, renamed onto the domain schema."""

    _ROWS = {
        "RPT_DMSK_FN_BALANCE": [
            {"REPORT_DATE": "2025-12-31", "TOTAL_ASSETS": 100.0, "MONETARYFUNDS": 40.0}
        ],
        "RPT_DMSK_FN_INCOME": [{"REPORT_DATE": "2025-12-31", "TOTAL_OPERATE_INCOME": 10.0}],
        "RPT_DMSK_FN_CASHFLOW": [{"REPORT_DATE": "2025-12-31", "NETCASH_OPERATE": 7.0}],
    }

    def _provider(self, requests_seen=None, error=None):
        provider = EastMoneyDirectFinancialReport("600000")

        def fake_get(url: Any, params: Any = None, timeout: Any = None) -> _Response:
            if requests_seen is not None:
                requests_seen.append(params)
            if error is not None:
                raise error
            return _Response(payload={"result": {"data": self._ROWS[params["reportName"]]}})

        provider.client.session.get = cast(Any, fake_get)
        return provider

    def test_statement_is_renamed_and_projected(self):
        seen: list[dict] = []
        provider = self._provider(requests_seen=seen)

        df = provider.get_balance_sheet()

        assert tuple(df.columns) == BALANCE_COLUMNS
        assert df.iloc[0]["total_assets"] == 100.0
        assert df.iloc[0]["cash_and_equivalents"] == 40.0
        assert [params["reportName"] for params in seen] == ["RPT_DMSK_FN_BALANCE"]

    def test_a_missing_report_is_an_empty_frame_with_the_schema_columns(self):
        provider = self._provider()
        provider.client.session.get = lambda url, params=None, timeout=None: _Response(
            payload={"result": {"data": []}}
        )

        df = provider.get_income_statement()

        assert df.empty
        assert tuple(df.columns) == INCOME_COLUMNS

    def test_a_failed_request_does_not_look_like_no_data(self):
        provider = self._provider(error=requests.ConnectionError("boom"))

        with pytest.raises(ConnectionError):
            provider.get_balance_sheet()

    def test_metrics_reuse_the_cached_statements(self, monkeypatch):
        monkeypatch.setenv("AKSHARE_ONE_CACHE_ENABLED", "true")
        clear("financial")
        seen: list[dict] = []
        provider = self._provider(requests_seen=seen)

        provider.get_balance_sheet()
        provider.get_financial_metrics()

        assert [params["reportName"] for params in seen] == list(self._ROWS)
