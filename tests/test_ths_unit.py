"""Offline tests for the Tonghuashun client, parsers and providers.

Everything here is faked -- no network access. These cover:

- the client's own behaviour: the JSONP shell, the browser agent, the retry
  on a CDN wobble and the refusal that is not retried;
- the parsers: the two kinds of period label, the volume the host counts in
  shares, the stub bar, the session-aware resampling;
- the providers: which series a request reads, how the dated and the stamped
  series are merged, and what each domain's frame holds.
"""

from __future__ import annotations

from typing import Any, cast

import pandas as pd
import pytest

from akshare_one.modules.historical.schema import COLUMNS as HISTORICAL_COLUMNS
from akshare_one.modules.historical.ths import ThsHistorical
from akshare_one.modules.info.schema import COLUMNS as INFO_COLUMNS
from akshare_one.modules.info.ths import ThsInfo
from akshare_one.modules.news.schema import COLUMNS as NEWS_COLUMNS
from akshare_one.modules.news.ths import ThsNews
from akshare_one.modules.realtime.schema import COLUMNS as REALTIME_COLUMNS
from akshare_one.modules.realtime.ths import ThsRealtime
from akshare_one.ths.client import ThsClient
from akshare_one.ths.utils import (
    PeriodSeries,
    f10_listing_date,
    parse_period_rows,
    resample_daily,
    resample_intraday,
    snapshot_frame,
    to_ths_code,
)

#: A daily bar and the same bar stamped with its 15:00 close.
DATED_ROW = "20261020,1321.01,1335.00,1316.14,1331.88,3413565,4525399000,0.273"
STAMPED_ROW = "202610201500,1321.01,1335.00,1316.14,1331.88,3413565,4525399000,0.273"

SNAPSHOT = {
    "5": "600519",
    "6": "1324.97",
    "7": "1321.01",
    "8": "1335.00",
    "9": "1316.14",
    "10": "1331.88",
    "13": "3413565.00",
    "19": "4525399000.00",
    "264648": "6.910",
    "199112": "0.52",
    "1968584": "0.273",
    "402": "1250081601.00",
    "407": "1250081601.00",
    "3475914": "1664958700000.000",
    "3541450": "1664958700000.000",
    "name": "贵州茅台",
    "marketid": "17",
    "updateTime": "2026-10-20 15:00",
}


@pytest.fixture(autouse=True)
def _disable_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AKSHARE_ONE_CACHE_ENABLED", "false")


class _Response:
    def __init__(self, body: str = "", status: int = 200) -> None:
        self._body = body
        self.status_code = status
        self.content = body.encode()
        self.encoding = "utf-8"

    @property
    def text(self) -> str:
        return self._body


class TestClient:
    """The client's own behaviour, against a faked session."""

    def _client(self, answers: list[_Response]) -> tuple[ThsClient, list[str]]:
        client = ThsClient(backoff=0)
        seen: list[str] = []

        def fake_get(url: str, timeout: float | None = None) -> _Response:
            seen.append(url)
            return answers[min(len(seen) - 1, len(answers) - 1)]

        client.session.get = cast(Any, fake_get)
        return client, seen

    def test_unwraps_the_jsonp_shell(self) -> None:
        body = 'quotebridge_v6_realhead_x({"items": {"5": "600519"}})'
        client, _ = self._client([_Response(body)])

        items = client.fetch_snapshot("600519")

        assert items["5"] == "600519"

    def test_sends_a_browser_agent(self) -> None:
        client, _ = self._client([_Response('{"items": {}}')])

        client.fetch_snapshot("600519")

        agent = str(client.session.headers["User-Agent"])
        assert "python-requests" not in agent
        assert "Mozilla" in agent

    def test_retries_a_cdn_wobble(self) -> None:
        client, seen = self._client([_Response("", 502), _Response('{"items": {}}')])

        client.fetch_snapshot("600519")

        assert len(seen) == 2

    def test_retries_a_whitespace_only_body(self) -> None:
        client, seen = self._client([_Response("  \n "), _Response('{"items": {}}')])

        client.fetch_snapshot("600519")

        assert len(seen) == 2

    def test_reports_an_unreadable_body_as_a_failure(self) -> None:
        client, seen = self._client([_Response("<html>502 Bad Gateway</html>")])

        with pytest.raises(ConnectionError, match="unreadable"):
            client.fetch_snapshot("600519")

        assert len(seen) == 1

    def test_does_not_retry_a_refusal(self) -> None:
        client, seen = self._client([_Response("", 403)])

        with pytest.raises(ConnectionError, match="403"):
            client.fetch_snapshot("600519")

        assert len(seen) == 1

    def test_reports_a_failure_after_the_last_attempt(self) -> None:
        client, seen = self._client([_Response("", 502)])

        with pytest.raises(ConnectionError, match="502"):
            client.fetch_snapshot("600519")

        assert len(seen) == client.retries


class TestToThsCode:
    @pytest.mark.parametrize(
        ("symbol", "expected"),
        [
            ("600519", "600519"),
            ("sh600519", "600519"),
            ("SZ000001", "000001"),
            ("bj430047", "430047"),
            ("1A0001", "1A0001"),
            ("399001", "399001"),
            ("sh000001", "1A0001"),
        ],
    )
    def test_code(self, symbol: str, expected: str) -> None:
        assert to_ths_code(symbol) == expected


class TestParsePeriodRows:
    def test_reads_a_dated_row(self) -> None:
        frame = parse_period_rows([DATED_ROW])

        assert frame.iloc[0]["timestamp"] == pd.Timestamp("2026-10-20")
        assert frame.iloc[0]["close"] == 1331.88

    def test_reads_a_stamped_row(self) -> None:
        frame = parse_period_rows([STAMPED_ROW])

        assert frame.iloc[0]["timestamp"] == pd.Timestamp("2026-10-20 15:00")

    def test_counts_the_volume_in_lots(self) -> None:
        frame = parse_period_rows([DATED_ROW])

        assert frame.iloc[0]["volume"] == 34136

    def test_drops_a_bar_the_host_has_not_filled_in(self) -> None:
        frame = parse_period_rows(["20261020,,,,9237.84,0,,0.000"])

        assert frame.empty

    def test_reads_no_rows(self) -> None:
        frame = parse_period_rows([])

        assert frame.empty
        assert list(frame.columns) == [
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]

    def test_keeps_a_missing_volume_empty(self) -> None:
        frame = parse_period_rows(["20261020,1321.01,1335.00,1316.14,1331.88,,0,0"])

        assert pd.isna(frame.iloc[0]["volume"])


class TestPeriodSeries:
    """The window and the yearly counts travel together."""

    def test_holds_the_window_and_its_counts(self) -> None:
        payload = {"data": DATED_ROW, "year": {"2026": 1}}

        series = PeriodSeries.from_payload(payload)

        assert series.first_date == pd.Timestamp("2026-10-20")
        assert series.year_counts == {2026: 1}
        assert len(series.frame()) == 1

    def test_needs_no_year_the_window_holds_in_full(self) -> None:
        series = PeriodSeries.from_payload({"data": DATED_ROW, "year": {"2026": 1}})

        assert series.missing_years(2026, 2026, wanted_from=pd.Timestamp("2026-01-01")) == []

    def test_needs_the_years_the_window_only_holds_the_tail_of(self) -> None:
        series = PeriodSeries.from_payload(
            {"data": DATED_ROW, "year": {"2024": 1, "2025": 1, "2026": 1}}
        )

        assert series.missing_years(2024, 2026, wanted_from=pd.Timestamp("2024-01-01")) == [
            2024,
            2025,
        ]

    def test_needs_every_counted_year_when_the_window_is_empty(self) -> None:
        series = PeriodSeries.from_payload({"data": "", "year": {"2024": 1, "2025": 2}})

        assert series.first_date is None
        assert series.missing_years(2024, 2026, wanted_from=pd.Timestamp("2024-01-01")) == [
            2024,
            2025,
        ]


class TestResampleIntraday:
    def _frame(self, labels: list[str]) -> pd.DataFrame:
        return parse_period_rows([f"{label},10.0,11.0,9.0,10.5,100,1000,0.1" for label in labels])

    def test_groups_the_minutes_of_one_bar(self) -> None:
        frame = self._frame(
            ["202610201001", "202610201002", "202610201003", "202610201004", "202610201005"]
        )

        resampled = resample_intraday(frame, 1, 5)

        assert list(resampled["timestamp"]) == [pd.Timestamp("2026-10-20 10:05")]
        assert resampled.iloc[0]["open"] == 10.0
        assert resampled.iloc[0]["close"] == 10.5
        assert resampled.iloc[0]["volume"] == 5

    def test_does_not_count_the_lunch_break(self) -> None:
        frame = self._frame(["202610201129", "202610201130", "202610201301", "202610201302"])

        resampled = resample_intraday(frame, 1, 5)

        assert list(resampled["timestamp"]) == [
            pd.Timestamp("2026-10-20 11:30"),
            pd.Timestamp("2026-10-20 13:05"),
        ]

    def test_leaves_a_wider_bar_alone(self) -> None:
        frame = self._frame(["202610201500"])

        assert resample_intraday(frame, 5, 1) is frame


class TestResampleDaily:
    def _frame(self, dates: list[str], volumes: list[str] | None = None) -> pd.DataFrame:
        volumes = volumes or ["100"] * len(dates)
        return parse_period_rows(
            [
                f"{date},10.0,11.0,9.0,10.5,{volume},1000,0.1"
                for date, volume in zip(dates, volumes, strict=True)
            ]
        )

    def test_counts_sessions_rather_than_calendar_days(self) -> None:
        frame = self._frame(["20261019", "20261020", "20261023"])

        resampled = resample_daily(frame, "day", 2)

        assert list(resampled["timestamp"]) == [
            pd.Timestamp("2026-10-20"),
            pd.Timestamp("2026-10-23"),
        ]
        assert list(resampled["volume"]) == [2, 1]

    def test_leaves_a_single_day_alone(self) -> None:
        frame = self._frame(["20261019"])

        assert resample_daily(frame, "day", 1) is frame

    def test_keeps_a_bin_whose_volume_the_host_left_empty(self) -> None:
        frame = self._frame(["20260106", "20260107"], volumes=["100", ""])

        resampled = resample_daily(frame, "week", 2)

        assert len(resampled) == 1
        assert resampled.iloc[0]["close"] == 10.5
        assert resampled.iloc[0]["volume"] == 1

    def test_anchors_a_year_bin_to_january(self) -> None:
        frame = self._frame(["20250815", "20270301"])

        resampled = resample_daily(frame, "year", 2)

        assert list(resampled["timestamp"]) == [
            pd.Timestamp("2025-01-01"),
            pd.Timestamp("2027-01-01"),
        ]


class TestSnapshotFrame:
    def test_maps_the_field_ids(self) -> None:
        frame = snapshot_frame(SNAPSHOT, "600519", REALTIME_COLUMNS)

        row = frame.iloc[0]
        assert row["symbol"] == "600519"
        assert row["price"] == 1331.88
        assert row["change"] == 6.91
        assert row["pct_change"] == 0.52
        assert row["open"] == 1321.01
        assert row["high"] == 1335.0
        assert row["low"] == 1316.14
        assert row["prev_close"] == 1324.97
        assert row["amount"] == 4525399000.0
        assert row["volume"] == 34136
        assert row["timestamp"] == pd.Timestamp("2026-10-20 15:00", tz="Asia/Shanghai")

    def test_leaves_a_field_the_host_did_not_send_empty(self) -> None:
        frame = snapshot_frame({"5": "600519"}, "600519", REALTIME_COLUMNS)

        assert pd.isna(frame.iloc[0]["price"])
        assert pd.isna(frame.iloc[0]["volume"])


class TestListingDate:
    def test_reads_the_date(self) -> None:
        html = '<td><strong class="hltip fl">上市日期：</strong><span>2001-08-27</span></td>'

        assert f10_listing_date(html) == pd.Timestamp("2001-08-27")

    def test_reads_no_date(self) -> None:
        assert f10_listing_date("<html></html>") is None


class _FakeClient:
    """A client that answers from fixtures instead of the network."""

    def __init__(self) -> None:
        self.snapshots: dict[str, dict[str, str]] = {}
        self.periods: dict[tuple[str, str, int | None], dict[str, Any]] = {}
        self.timelines: dict[tuple[str, str, str, int], list[dict[str, Any]]] = {}
        self.pages: dict[tuple[str, str], str] = {}
        self.calls: list[tuple[Any, ...]] = []

    def fetch_snapshot(self, code: str) -> dict[str, str]:
        self.calls.append(("snapshot", code))
        return self.snapshots[code]

    def fetch_period(self, code: str, period: str, year: int | None = None) -> dict[str, Any]:
        self.calls.append(("period", code, period, year))
        return self.periods[(code, period, year)]

    def fetch_timeline(
        self, market_id: str, code: str, kind: str, count: int
    ) -> list[dict[str, Any]]:
        self.calls.append(("timeline", market_id, code, kind, count))
        return self.timelines.get((market_id, code, kind, count), [])

    def fetch_f10(self, code: str, page: str) -> str:
        self.calls.append(("f10", code, page))
        return self.pages[(code, page)]


def _period(rows: list[str], years: dict[str, int] | None = None) -> dict[str, Any]:
    return {"data": ";".join(rows), "year": years or {}}


class TestRealtimeProvider:
    def test_answers_with_the_snapshot(self) -> None:
        client = _FakeClient()
        client.snapshots["600519"] = SNAPSHOT
        provider = ThsRealtime("600519")
        provider.client = cast(Any, client)

        frame = provider.get_current_data()

        assert tuple(frame.columns) == REALTIME_COLUMNS
        assert frame.iloc[0]["price"] == 1331.88

    def test_needs_a_symbol(self) -> None:
        provider = ThsRealtime(None)

        with pytest.raises(ValueError, match="one security per request"):
            provider.get_current_data()


class TestHistoricalProvider:
    def _provider(self, client: _FakeClient, **kwargs: Any) -> ThsHistorical:
        provider = ThsHistorical(symbol=kwargs.pop("symbol", "600519"), **kwargs)
        provider.client = cast(Any, client)
        return provider

    def test_reads_the_stamped_series_for_a_recent_range(self) -> None:
        client = _FakeClient()
        client.periods[("600519", "70", None)] = _period(
            ["202610201500,1321.01,1335.00,1316.14,1331.88,3413565,4525399000,0.273"]
        )

        provider = self._provider(
            client, start_date="2026-10-20", end_date="2026-10-20", adjust="none"
        )
        frame = provider.get_hist_data()

        assert tuple(frame.columns) == HISTORICAL_COLUMNS
        assert len(frame) == 1
        assert frame.iloc[0]["timestamp"] == pd.Timestamp("2026-10-20", tz="Asia/Shanghai")
        assert frame.iloc[0]["close"] == 1331.88
        assert frame.iloc[0]["volume"] == 34136
        assert [call for call in client.calls if call[0] == "period"] == [
            ("period", "600519", "70", None)
        ]

    def test_merges_the_dated_history_with_the_stamped_window(self) -> None:
        client = _FakeClient()
        client.periods[("600519", "70", None)] = _period(
            [
                "202610191500,1322.50,1348.60,1321.00,1324.97,3972894,5308935900,0.318",
                "202610201500,1321.01,1335.00,1316.14,1331.88,3413565,4525399000,0.273",
            ]
        )
        client.periods[("600519", "00", None)] = _period(
            ["202610191500,1322.50,1348.60,1321.00,1324.97,3972894,5308935900,0.318"],
            {"2026": 2},
        )
        client.periods[("600519", "00", 2026)] = _period(
            [
                "20260105,1385.00,1431.88,1385.00,1426.00,7094942,10018086400,0.567",
                "202610191500,1322.50,1348.60,1321.00,1324.97,3972894,5308935900,0.318",
            ]
        )

        provider = self._provider(client, start_date="2026-01-01", end_date="2026-10-20")
        frame = provider.get_hist_data()

        assert list(frame["timestamp"]) == [
            pd.Timestamp("2026-01-05", tz="Asia/Shanghai"),
            pd.Timestamp("2026-10-19", tz="Asia/Shanghai"),
            pd.Timestamp("2026-10-20", tz="Asia/Shanghai"),
        ]

    def test_reads_the_years_the_window_does_not_hold(self) -> None:
        client = _FakeClient()
        client.periods[("600519", "70", None)] = _period(
            ["202610201500,1321.01,1335.00,1316.14,1331.88,3413565,4525399000,0.273"]
        )
        client.periods[("600519", "00", None)] = _period(
            ["20261019,1322.50,1348.60,1321.00,1324.97,3972894,5308935900,0.318"],
            {"2024": 1, "2025": 1, "2026": 1},
        )
        client.periods[("600519", "00", 2024)] = _period(
            ["20240102,1715.00,1718.19,1678.10,1685.01,3215644,5440082500,0.256"]
        )
        client.periods[("600519", "00", 2025)] = _period(
            ["20250102,1524.00,1524.49,1480.00,1488.00,5002870,7490883800,0.398"]
        )

        provider = self._provider(client, start_date="2024-01-01", end_date="2026-10-20")
        frame = provider.get_hist_data()

        assert len(frame) == 4
        assert list(frame["timestamp"].dt.date) == [
            pd.Timestamp("2024-01-02").date(),
            pd.Timestamp("2025-01-02").date(),
            pd.Timestamp("2026-10-19").date(),
            pd.Timestamp("2026-10-20").date(),
        ]
        assert ("period", "600519", "00", 2024) in client.calls
        assert ("period", "600519", "00", 2025) in client.calls

    def test_reads_the_weekly_series(self) -> None:
        client = _FakeClient()
        client.periods[("600519", "10", None)] = _period(
            ["20261016,1262.95,1329.88,1261.00,1329.00,17808050,23095015000,1.425"],
            {"2026": 1},
        )

        provider = self._provider(
            client, interval="week", start_date="2026-10-16", end_date="2026-10-20"
        )
        frame = provider.get_hist_data()

        assert len(frame) == 1
        assert frame.iloc[0]["close"] == 1329.0
        assert [call for call in client.calls if call[0] == "period"] == [
            ("period", "600519", "10", None)
        ]

    def test_reads_the_adjusted_series_of_the_adjustment(self) -> None:
        client = _FakeClient()
        client.periods[("600519", "72", None)] = _period(
            ["202610201500,9238.06,9316.80,9210.66,9299.24,3413565,4525399000,0.273"]
        )

        provider = self._provider(
            client, adjust="hfq", start_date="2026-10-20", end_date="2026-10-20"
        )
        frame = provider.get_hist_data()

        assert frame.iloc[0]["close"] == 9299.24

    def test_falls_back_to_a_finer_series(self) -> None:
        client = _FakeClient()
        client.periods[("600519", "50", None)] = _period([])
        client.periods[("600519", "40", None)] = _period(
            [
                "202610201000,1321.01,1335.00,1316.14,1328.66,892700,1415350000,0.085",
                "202610201030,1328.67,1330.03,1323.97,1324.32,358600,473300000,0.034",
            ]
        )

        provider = self._provider(
            client, interval="hour", start_date="2026-10-20", end_date="2026-10-20"
        )
        frame = provider.get_hist_data()

        assert len(frame) == 1
        assert frame.iloc[0]["timestamp"] == pd.Timestamp("2026-10-20 10:30", tz="Asia/Shanghai")
        assert frame.iloc[0]["close"] == 1324.32

    def test_rejects_an_unknown_interval(self) -> None:
        provider = self._provider(_FakeClient(), interval="tick")

        with pytest.raises(ValueError, match="Unsupported interval"):
            provider.get_hist_data()

    def test_rejects_a_multiplier_below_one(self) -> None:
        provider = self._provider(_FakeClient(), interval="minute", interval_multiplier=0)

        with pytest.raises(ValueError, match="multiplier"):
            provider.get_hist_data()


class TestNewsProvider:
    def _provider(self, client: _FakeClient) -> ThsNews:
        provider = ThsNews("600519")
        provider.client = cast(Any, client)
        return provider

    def test_answers_with_the_timeline(self) -> None:
        client = _FakeClient()
        client.snapshots["600519"] = SNAPSHOT
        client.timelines[("17", "600519", "news", 60)] = [
            {
                "itemId": "1",
                "title": "一则新闻",
                "abstract": "摘要",
                "time": 1792487169,
                "jumpUrl": "http://news.10jqka.com.cn/1.shtml",
            }
        ]
        client.timelines[("17", "600519", "noticeReport", 60)] = [
            {
                "itemId": "2",
                "title": "一篇研报",
                "abstract": "摘要",
                "time": 1792024604,
                "jumpUrl": "http://news.10jqka.com.cn/2.shtml",
            }
        ]

        frame = self._provider(client).get_news_data()

        assert tuple(frame.columns) == NEWS_COLUMNS
        assert len(frame) == 2
        assert frame.iloc[0]["title"] == "一则新闻"
        assert frame.iloc[0]["keyword"] == "600519"
        assert frame.iloc[0]["publish_time"] == pd.Timestamp(
            "2026-10-20 17:06:09", tz="Asia/Shanghai"
        )
        assert frame.iloc[1]["source"] == "同花顺研报"

    def test_reads_the_market_of_the_security(self) -> None:
        client = _FakeClient()
        client.snapshots["600519"] = SNAPSHOT

        self._provider(client).get_news_data()

        assert ("timeline", "17", "600519", "news", 60) in client.calls


class TestInfoProvider:
    def _provider(self, client: _FakeClient) -> ThsInfo:
        provider = ThsInfo("600519")
        provider.client = cast(Any, client)
        return provider

    def test_answers_with_the_snapshot_and_the_listing_date(self) -> None:
        client = _FakeClient()
        client.snapshots["600519"] = SNAPSHOT
        client.pages[("600519", "company.html")] = (
            '<td><strong class="hltip fl">上市日期：</strong><span>2001-08-27</span></td>'
        )

        frame = self._provider(client).get_basic_info()

        assert tuple(frame.columns) == INFO_COLUMNS
        row = frame.iloc[0]
        assert row["symbol"] == "600519"
        assert row["name"] == "贵州茅台"
        assert row["total_shares"] == 1250081601.0
        assert row["total_market_cap"] == 1664958700000.0
        assert row["listing_date"] == pd.Timestamp("2001-08-27")

    def test_keeps_the_listing_date_empty_when_the_page_fails(self) -> None:
        client = _FakeClient()
        client.snapshots["600519"] = SNAPSHOT

        def failing_f10(code: str, page: str) -> str:
            raise ConnectionError("boom")

        client.fetch_f10 = cast(Any, failing_f10)

        frame = self._provider(client).get_basic_info()

        assert pd.isna(frame.iloc[0]["listing_date"])
        assert frame.iloc[0]["name"] == "贵州茅台"


class TestPublicSurface:
    """The public functions reach the THS providers."""

    def test_news_data(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from akshare_one import get_news_data

        monkeypatch.setattr(
            "akshare_one.ths.client.ThsClient.fetch_snapshot",
            lambda self, code: SNAPSHOT,
        )
        monkeypatch.setattr(
            "akshare_one.ths.client.ThsClient.fetch_timeline",
            lambda self, market_id, code, kind, count: [],
        )

        frame = get_news_data(symbol="600519", source="ths")

        assert tuple(frame.columns) == NEWS_COLUMNS
        assert frame.empty

    def test_realtime_data(self) -> None:
        from akshare_one import get_realtime_data

        with pytest.raises(ValueError, match="one security per request"):
            get_realtime_data(symbol=None, source="ths")

    def test_hist_data_rejects_an_unknown_interval(self) -> None:
        from akshare_one import get_hist_data

        with pytest.raises(ValueError, match="Unsupported interval"):
            get_hist_data(symbol="600519", interval="tick", source="ths")  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]
