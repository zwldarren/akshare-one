"""Turns Tonghuashun payloads into the frames the domains promise."""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .constants import (
    SESSION_AFTERNOON,
    SESSION_MORNING,
    SHARES_PER_LOT,
    SNAPSHOT_FIELDS,
    SNAPSHOT_NAME,
    SNAPSHOT_UPDATE_TIME,
)

#: The fields a period row carries that the historical domain keeps, in order.
_PERIOD_FIELDS = (
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
)

#: The listing date an F10 company page states.
_LISTING_DATE = re.compile(r"上市日期[：:]\s*</strong>\s*<span>\s*(\d{4}-\d{2}-\d{2})\s*</span>")

#: The session, in minutes since midnight.
_MORNING_OPEN = SESSION_MORNING[0].hour * 60 + SESSION_MORNING[0].minute
_MORNING_CLOSE = SESSION_MORNING[1].hour * 60 + SESSION_MORNING[1].minute
_AFTERNOON_OPEN = SESSION_AFTERNOON[0].hour * 60 + SESSION_AFTERNOON[0].minute
_MORNING_LENGTH = _MORNING_CLOSE - _MORNING_OPEN


def to_ths_code(symbol: str) -> str:
    """The code Tonghuashun knows a security by.

    The quote host addresses securities by a bare code (``600519``,
    ``1A0001``, ``885728``) and does not care about the exchange, so an
    exchange prefix is dropped. One code cannot be dropped: the SSE
    Composite is ``1A0001`` here and ``000001`` everywhere else.
    """
    code = symbol.strip()
    lowered = code.lower()
    if lowered.startswith(("sh", "sz", "bj")):
        bare = code[2:]
        if lowered.startswith("sh") and bare == "000001":
            return "1A0001"
        return bare
    return code


def snapshot_number(items: Mapping[str, str], name: str) -> float | None:
    """One numeric snapshot field, or None when the host did not send it."""
    raw = items.get(SNAPSHOT_FIELDS[name])
    if raw in (None, "", "-"):
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def snapshot_volume(items: Mapping[str, str]) -> int | None:
    """The traded volume in lots: the host counts shares.

    None when the host did not send a volume, so the column comes back empty
    rather than zero.
    """
    shares = snapshot_number(items, "volume")
    return None if shares is None else round(shares / SHARES_PER_LOT)


def snapshot_timestamp(items: Mapping[str, str]) -> pd.Timestamp:
    """When the host last priced the security, in Beijing time."""
    stamp = pd.to_datetime(items.get(SNAPSHOT_UPDATE_TIME, ""), errors="coerce")
    if pd.isna(stamp):
        return pd.Timestamp.now(tz="Asia/Shanghai")
    if stamp.tzinfo is None:
        return stamp.tz_localize("Asia/Shanghai")
    return stamp


def snapshot_frame(items: Mapping[str, str], symbol: str, columns: Sequence[str]) -> pd.DataFrame:
    """The realtime domain's frame for one snapshot, projected onto ``columns``."""
    return pd.DataFrame(
        [
            {
                "symbol": items.get(SNAPSHOT_FIELDS["code"]) or symbol,
                "price": snapshot_number(items, "price"),
                "change": snapshot_number(items, "change"),
                "pct_change": snapshot_number(items, "pct_change"),
                "timestamp": snapshot_timestamp(items),
                "volume": snapshot_volume(items),
                "amount": snapshot_number(items, "amount"),
                "open": snapshot_number(items, "open"),
                "high": snapshot_number(items, "high"),
                "low": snapshot_number(items, "low"),
                "prev_close": snapshot_number(items, "pre_close"),
            }
        ],
        columns=list(columns),
    )


def snapshot_info_frame(
    items: Mapping[str, str],
    symbol: str,
    listing_date: pd.Timestamp | None,
    columns: Sequence[str],
) -> pd.DataFrame:
    """The info domain's frame for one snapshot, projected onto ``columns``.

    The snapshot carries no industry, so the column is left out and comes
    back empty from the projection.
    """
    return pd.DataFrame(
        [
            {
                "price": snapshot_number(items, "price"),
                "symbol": items.get(SNAPSHOT_FIELDS["code"]) or symbol,
                "name": items.get(SNAPSHOT_NAME),
                "total_shares": snapshot_number(items, "total_shares"),
                "float_shares": snapshot_number(items, "float_shares"),
                "total_market_cap": snapshot_number(items, "total_market_cap"),
                "float_market_cap": snapshot_number(items, "float_market_cap"),
                "listing_date": listing_date,
            }
        ],
        columns=list(columns),
    )


def parse_period_rows(rows: Sequence[str]) -> pd.DataFrame:
    """Parse the rows of a period series into a frame.

    A row reads ``datetime, open, high, low, close, volume, amount,
    turnover``; the first field is a date (``20261020``) or a 15:00
    timestamp (``202610201500``). The two trailing fields are dropped: no
    domain promises them. The quote host counts volume in shares and the
    package counts lots, so the volume is scaled on the way in and left empty
    when the host did not send one. A row without an opening price is a bar
    the host has not filled in yet.
    """
    records = []
    for row in rows:
        parts = row.split(",")
        if len(parts) < 7:
            continue
        records.append(parts[: len(_PERIOD_FIELDS)])

    frame = pd.DataFrame(records, columns=list(_PERIOD_FIELDS))
    labels = frame["timestamp"].astype(str)
    dated = pd.to_datetime(labels.str.slice(0, 8), format="%Y%m%d", errors="coerce")
    timed = pd.to_datetime(labels.str.slice(0, 12), format="%Y%m%d%H%M", errors="coerce")
    frame["timestamp"] = dated.where(labels.str.len() < 12, timed)
    for column in _PERIOD_FIELDS[1:]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["volume"] = (frame["volume"] / SHARES_PER_LOT).round().astype("Int64")
    return frame.dropna(subset=["open", "close"])


@dataclass(frozen=True)
class PeriodSeries:
    """One window of a period series, and what the full history holds.

    The host answers a window at a time: ``data`` holds the rows and ``year``
    holds how many rows each calendar year of the history has. Keeping the two
    together is what lets a caller ask which years the window does not reach.
    """

    rows: tuple[str, ...]
    year_counts: dict[int, int]

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> PeriodSeries:
        """Read a period payload into its rows and its yearly counts."""
        rows = tuple(row for row in (payload.get("data") or "").split(";") if row)
        counts = {int(year): int(count) for year, count in (payload.get("year") or {}).items()}
        return cls(rows, counts)

    def frame(self) -> pd.DataFrame:
        """The window's rows as the historical domain's columns."""
        return parse_period_rows(list(self.rows))

    @property
    def first_date(self) -> pd.Timestamp | None:
        """The date the window starts at, or None when it is empty."""
        if not self.rows:
            return None
        return pd.to_datetime(self.rows[0][:8], format="%Y%m%d")

    def missing_years(self, first: int, last: int, *, wanted_from: pd.Timestamp) -> list[int]:
        """The years of the history the window does not hold.

        An empty window holds none of the history, so every year the history
        counts is missing. A window that starts at or before ``wanted_from``
        holds everything the caller asked for. Otherwise a year the window
        holds only the tail of needs a file of its own.
        """
        years = [year for year in range(first, last + 1) if year in self.year_counts]
        start = self.first_date
        if start is None:
            return years
        if wanted_from >= start:
            return []
        held = Counter(row[:4] for row in self.rows)
        return [year for year in years if held.get(str(year), 0) < self.year_counts[year]]


def resample_intraday(frame: pd.DataFrame, spacing: int, target: int) -> pd.DataFrame:
    """Rebuild intraday bars at a wider spacing.

    The quote host labels a bar with the minute it ends at, so a bar starts
    one spacing earlier. Bars are grouped by their start inside the trading
    session -- the lunch break is not trading time and does not advance the
    counter -- and each group is labelled with the minute it ends at.
    """
    if frame.empty or target <= spacing:
        return frame

    starts = frame["timestamp"] - pd.Timedelta(minutes=spacing)
    offsets = _trading_minutes(starts)
    bucket = (offsets // target) * target
    ends = bucket + target
    clock = np.where(
        ends <= _MORNING_LENGTH,
        ends + _MORNING_OPEN,
        ends - _MORNING_LENGTH + _AFTERNOON_OPEN,
    )
    labels = frame["timestamp"].dt.normalize() + pd.to_timedelta(clock, unit="m")

    grouped = (
        frame.assign(_label=labels)
        .groupby("_label", sort=True)
        .agg(
            timestamp=("_label", "first"),
            open=("open", "first"),
            high=("high", "max"),
            low=("low", "min"),
            close=("close", "last"),
            volume=("volume", "sum"),
        )
        .reset_index(drop=True)
    )
    return grouped


def resample_daily(frame: pd.DataFrame, interval: str, multiplier: int) -> pd.DataFrame:
    """Rebuild daily bars at a wider spacing, e.g. two weeks in one bar."""
    if frame.empty or multiplier <= 1:
        return frame

    if interval == "day":
        # One bar per `multiplier` consecutive sessions, labelled with the
        # session it ends at: calendar days would let weekends and holidays
        # shift the grouping, and could stamp a bar with a non-trading day.
        return (
            frame.assign(_group=np.arange(len(frame)) // multiplier)
            .groupby("_group", sort=True)
            .agg(
                timestamp=("timestamp", "last"),
                open=("open", "first"),
                high=("high", "max"),
                low=("low", "min"),
                close=("close", "last"),
                volume=("volume", "sum"),
            )
            .reset_index(drop=True)
        )

    rule = {
        "week": f"{multiplier}W-MON",
        "month": f"{multiplier}MS",
        "year": f"{multiplier}YS",
    }[interval]
    return (
        frame.set_index("timestamp")
        .resample(rule)
        .agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }
        )
        .dropna(subset=["open", "high", "low", "close"])
        .reset_index()
    )


def timeline_frame(
    items: Sequence[dict[str, Any]], keyword: str, source: str, columns: Sequence[str]
) -> pd.DataFrame:
    """Turn timeline items into the news domain's frame.

    A timeline item carries no publication name, only a title, an abstract
    and a collection tag, so ``source`` is the collection the item came from
    rather than the outlet that wrote it.
    """
    return pd.DataFrame(
        [
            {
                "keyword": keyword,
                "title": item.get("title"),
                "content": item.get("abstract"),
                "publish_time": _publish_time(item.get("time")),
                "source": source,
                "url": item.get("jumpUrl"),
            }
            for item in items
        ],
        columns=list(columns),
    )


def f10_listing_date(html: str) -> pd.Timestamp | None:
    """The listing date an F10 company page states."""
    match = _LISTING_DATE.search(html)
    if not match:
        return None
    stamp = pd.to_datetime(match.group(1), errors="coerce")
    return None if pd.isna(stamp) else stamp


def _trading_minutes(timestamps: pd.Series) -> pd.Series:
    """Minutes of trading time since the morning open, lunch break excluded."""
    clock = timestamps.dt.hour * 60 + timestamps.dt.minute
    morning = clock - _MORNING_OPEN
    afternoon = clock - _AFTERNOON_OPEN + _MORNING_LENGTH
    return pd.Series(np.where(clock < _MORNING_CLOSE, morning, afternoon), index=timestamps.index)


def _publish_time(raw: Any) -> pd.Timestamp | None:
    """The publication time of a timeline item, in Beijing time."""
    try:
        stamp = pd.to_datetime(raw, unit="s", utc=True)
    except (TypeError, ValueError):
        return None
    if pd.isna(stamp):
        return None
    return stamp.tz_convert("Asia/Shanghai")
