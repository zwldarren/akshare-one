"""Constants for Tonghuashun's (10jqka) public HTTP endpoints.

Every identifier here was read off a live response: the snapshot field ids out
of the ``items`` object of a ``realhead`` payload, the period codes out of the
K-line endpoint's two-digit period code, the market ids out of a snapshot's
``marketid`` field. Nothing in this module performs I/O.
"""

from __future__ import annotations

from datetime import time

#: Host serving quotes: snapshot, K-line, intraday bars. UTF-8, JSONP.
QUOTE_HOST = "d.10jqka.com.cn"
#: Host serving the per-stock timeline (news, research reports). UTF-8, JSON.
FLOW_HOST = "flow.10jqka.com.cn"
#: Host serving the F10 pages. GB18030, HTML.
BASIC_HOST = "basic.10jqka.com.cn"

#: The F10 host answers a browser and nothing else: a ``python-requests`` agent
#: gets a 403 with an empty body.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

#: Snapshot field id -> what the id means. Only the ids this package reads:
#: the payload carries more, but nothing here asks for them.
SNAPSHOT_FIELDS: dict[str, str] = {
    "code": "5",
    "pre_close": "6",
    "open": "7",
    "high": "8",
    "low": "9",
    "price": "10",
    "volume": "13",
    "amount": "19",
    "total_shares": "402",
    "float_shares": "407",
    "change": "264648",
    "pct_change": "199112",
    "float_market_cap": "3475914",
    "total_market_cap": "3541450",
}

#: Snapshot fields that carry a name rather than an id.
SNAPSHOT_NAME = "name"
SNAPSHOT_MARKET_ID = "marketid"
SNAPSHOT_UPDATE_TIME = "updateTime"

#: Period code granularity (first digit) per bar spacing. ``day`` names the
#: 15:00-stamped series, which is current but only reaches back to 2023;
#: ``day_date`` names the date-stamped one, which holds the whole history but
#: ends a session earlier.
PERIOD_GRANULARITY: dict[str, str] = {
    "day": "7",
    "day_date": "0",
    "week": "1",
    "month": "2",
    "year": "8",
    "1min": "6",
    "5min": "3",
    "30min": "4",
    "60min": "5",
}

#: Period code adjustment (second digit): unadjusted, forward, backward.
PERIOD_ADJUSTMENT: dict[str, str] = {
    "none": "0",
    "qfq": "1",
    "hfq": "2",
}

#: Intraday spacings the quote host serves directly, in minutes. There is no
#: 15-minute spacing; it is resampled from the 5-minute series.
INTRADAY_SPACINGS: tuple[int, ...] = (1, 5, 30, 60)

#: The A-share session, used to bucket resampled intraday bars. The lunch
#: break is not trading time, so it does not advance the bar counter.
SESSION_MORNING = (time(9, 30), time(11, 30))
SESSION_AFTERNOON = (time(13, 0), time(15, 0))

#: The quote host counts volume in shares; the package counts lots (手).
SHARES_PER_LOT = 100

#: Timeline collections: the path segment selects the collection, and the
#: item count the page serves comes from the size segment.
TIMELINE_NEWS = "news"
TIMELINE_REPORT = "noticeReport"

#: Largest number of items one timeline page serves.
TIMELINE_PAGE_SIZE = 60

#: Research reports arrive as their own collection; they are labelled apart
#: from plain news so a caller can tell them apart in the ``source`` column.
SOURCE_NEWS = "同花顺"
SOURCE_REPORT = "同花顺研报"
