"""Tonghuashun's public K-line endpoint as a historical data provider."""

from __future__ import annotations

from typing import Any

import pandas as pd

from akshare_one.ths.client import ThsClient
from akshare_one.ths.constants import (
    INTRADAY_SPACINGS,
    PERIOD_ADJUSTMENT,
    PERIOD_GRANULARITY,
)
from akshare_one.ths.utils import (
    PeriodSeries,
    resample_daily,
    resample_intraday,
    to_ths_code,
)

from ..cache import cached
from ..registry import provider
from ..schema import normalize
from .base import HistoricalDataProvider
from .schema import COLUMNS


@provider("historical", "ths")
class ThsHistorical(HistoricalDataProvider):
    """Adapter for Tonghuashun's public K-line endpoint.

    The endpoint answers without a login and serves one security at a time.
    Three things about it are worth knowing before reading its output:

    - the daily series arrives a window at a time: ``last.js`` holds the last
      140 sessions and the earlier history comes one year per request;
    - the date-stamped series ends a session before the host has priced the
      last one, and the 15:00-stamped series -- which is current, but only
      reaches back to 2023 -- is read alongside it;
    - a bar is labelled with the minute it ends at, and the 5-minute series
      comes back empty now and then, in which case the 1-minute series is
      read and resampled instead.

    Volume arrives in shares and is reported in lots, as elsewhere in this
    package.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.client = ThsClient()

    @cached("hist_data")
    def get_hist_data(self) -> pd.DataFrame:
        """Fetches Tonghuashun historical market data

        Returns:
            pd.DataFrame:
                - timestamp
                - open
                - high
                - low
                - close
                - volume
        """
        self._validate_interval_params()

        try:
            code = to_ths_code(self.symbol)
            if self.interval in ("minute", "hour"):
                frame = self._intraday(code)
            else:
                frame = self._daily(code)
            return normalize(self._within_range(frame), COLUMNS)
        except Exception as e:
            raise ValueError(f"Failed to fetch historical data for {self.symbol}: {e}") from e

    def _intraday(self, code: str) -> pd.DataFrame:
        """Intraday bars, read at the spacing the host serves them at.

        The host rebuilds its coarser series on its own schedule, so the one
        the caller asked for can be a session behind the finest one -- and
        the 5-minute series comes back empty now and then. When the range
        the caller asked for comes back empty, a finer series is read and
        resampled instead.
        """
        target = self.interval_multiplier * (60 if self.interval == "hour" else 1)
        frame = pd.DataFrame()
        for spacing in self._spacings_to_try(target):
            rows = self._intraday_rows(code, spacing)
            frame = self._in_beijing_time(resample_intraday(rows, spacing, target), daily=False)
            if not self._within_range(frame).empty:
                break
        return frame

    def _spacings_to_try(self, target: int) -> list[int]:
        """The series to try, from the spacing asked for down to the finest."""
        usable = [spacing for spacing in INTRADAY_SPACINGS if spacing <= target]
        return sorted(usable, reverse=True)

    def _daily(self, code: str) -> pd.DataFrame:
        """Daily, weekly, monthly and yearly bars."""
        adjust = PERIOD_ADJUSTMENT[self.adjust]
        if self.interval == "day":
            frame = self._daily_series(code, adjust)
        else:
            period = PERIOD_GRANULARITY[self.interval] + adjust
            frame = self._series(code, period)
        frame = resample_daily(frame, self.interval, self.interval_multiplier)
        return self._in_beijing_time(frame, daily=True)

    def _daily_series(self, code: str, adjust: str) -> pd.DataFrame:
        """The daily series, which the host serves a window at a time.

        The date-stamped series holds the whole history but ends a session
        before the host has priced the last one; the 15:00-stamped series is
        the other way round -- current, but reaching back only to 2023. Both
        are read, and the years the window does not hold are fetched.
        """
        stamped = PeriodSeries.from_payload(
            self.client.fetch_period(code, PERIOD_GRANULARITY["day"] + adjust)
        )
        if self._within_window(stamped):
            return self._merge([stamped.frame()])

        dated = self._series(code, PERIOD_GRANULARITY["day_date"] + adjust)
        return self._merge([dated, stamped.frame()])

    def _series(self, code: str, period: str) -> pd.DataFrame:
        """One period series, with the years the window does not hold filled in."""
        window = PeriodSeries.from_payload(self.client.fetch_period(code, period))
        frames = [window.frame()]
        for year in window.missing_years(
            self._first_year(),
            self._last_year(),
            wanted_from=pd.Timestamp(self.start_date),
        ):
            payload = self.client.fetch_period(code, period, year=year)
            frames.append(PeriodSeries.from_payload(payload).frame())
        return self._merge(frames)

    def _within_window(self, series: PeriodSeries) -> bool:
        """Whether the window already holds every day the caller asked for."""
        start = series.first_date
        return start is not None and pd.Timestamp(self.start_date) >= start

    def _intraday_rows(self, code: str, spacing: int) -> pd.DataFrame:
        """One intraday series, at the spacing the host serves it at."""
        period = PERIOD_GRANULARITY[f"{spacing}min"] + PERIOD_ADJUSTMENT[self.adjust]
        payload = self.client.fetch_period(code, period)
        return PeriodSeries.from_payload(payload).frame()

    def _merge(self, frames: list[pd.DataFrame]) -> pd.DataFrame:
        """One frame out of several, with the later frame winning."""
        frame = pd.concat(frames, ignore_index=True)
        frame["timestamp"] = frame["timestamp"].dt.normalize()
        return (
            frame.drop_duplicates(subset="timestamp", keep="last")
            .sort_values("timestamp")
            .reset_index(drop=True)
        )

    def _within_range(self, frame: pd.DataFrame) -> pd.DataFrame:
        """The bars the caller asked for."""
        if frame.empty:
            return frame
        start = pd.Timestamp(self.start_date).tz_localize("Asia/Shanghai")
        end = pd.Timestamp(self.end_date).tz_localize("Asia/Shanghai") + pd.Timedelta(days=1)
        return frame[(frame["timestamp"] >= start) & (frame["timestamp"] < end)]

    def _in_beijing_time(self, frame: pd.DataFrame, daily: bool) -> pd.DataFrame:
        """The bars in Beijing time; daily bars sit at midnight."""
        if frame.empty:
            return frame
        stamps = frame["timestamp"]
        if daily:
            stamps = stamps.dt.normalize()
        frame = frame.copy()
        frame["timestamp"] = stamps.dt.tz_localize("Asia/Shanghai")
        return frame

    def _first_year(self) -> int:
        return pd.Timestamp(self.start_date).year

    def _last_year(self) -> int:
        return pd.Timestamp(self.end_date).year
