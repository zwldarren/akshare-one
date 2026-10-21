"""A client for Tonghuashun's public, unauthenticated data endpoints.

Every endpoint this client talks to answers without a login. What the
endpoints will not do is answer a ``python-requests`` user agent -- the F10
host answers that with a 403 and an empty body -- so the session presents a
browser's. They will not answer faster than a browser either, so the client
keeps a gap between two requests to the same host and backs off when the CDN
wobbles.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any
from urllib.parse import urlparse

import requests

from .constants import BASIC_HOST, FLOW_HOST, QUOTE_HOST, USER_AGENT

#: The JSONP shell the quote host wraps its payloads in.
_JSONP = re.compile(r"^\s*[A-Za-z_][A-Za-z0-9_]*\s*\((.*)\)\s*;?\s*$", re.S)

_DEFAULT_TIMEOUT = 15.0
#: The smallest gap kept between two requests to the same host.
_MIN_INTERVAL = 0.1
#: How many times one request is tried before it is reported as failed.
_RETRIES = 6
#: The first backoff step; every further attempt waits this much longer.
_BACKOFF = 0.5


class ThsClient:
    """Reads Tonghuashun's public quote, news and F10 endpoints.

    Args:
        timeout: Seconds one request may take before it is reported failed.
        min_interval: The smallest gap, in seconds, kept between two requests
            to the same host. The hosts throttle, and a browser does not ask
            faster than this either.
        backoff: The first pause, in seconds, after a failed attempt; every
            further attempt waits one step longer.
        retries: How many times one request is tried before it is reported
            failed. A 401 or 403 ends the attempts early: a refusal is not a
            wobble, and repeating the request will not change the answer.
    """

    def __init__(
        self,
        timeout: float = _DEFAULT_TIMEOUT,
        min_interval: float = _MIN_INTERVAL,
        backoff: float = _BACKOFF,
        retries: int = _RETRIES,
    ) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept": "*/*",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Referer": "https://www.10jqka.com.cn/",
            }
        )
        self.timeout = timeout
        self.min_interval = min_interval
        self.backoff = backoff
        self.retries = retries
        self._last_request_at: dict[str, float] = {}

    def fetch_snapshot(self, code: str) -> dict[str, str]:
        """The realtime snapshot of one security.

        The payload's ``items`` object maps field ids to values; a few
        responses keep the named fields beside it instead of inside it, so
        both are read and the named ones are added when they are missing.
        """
        url = f"https://{QUOTE_HOST}/v6/realhead/hs_{code}/last.js"
        payload = self._get_json(url)
        if not isinstance(payload, dict):
            raise ConnectionError(f"No snapshot for {code}: {url}")
        items: dict[str, str] = {
            str(key): str(value) for key, value in (payload.get("items") or {}).items()
        }
        for key, value in payload.items():
            if key != "items":
                items.setdefault(str(key), str(value))
        return items

    def fetch_period(self, code: str, period: str, year: int | None = None) -> dict[str, Any]:
        """One period series of one security.

        The payload holds the rows in ``data`` and says, in ``year``, how many
        rows each calendar year of the history holds. The window of ``last.js``
        is the last 140 bars; the year files carry the rest of the history.
        """
        suffix = f"{year}.js" if year else "last.js"
        url = f"https://{QUOTE_HOST}/v6/line/hs_{code}/{period}/{suffix}"
        payload = self._get_json(url)
        if not isinstance(payload, dict):
            raise ConnectionError(f"No period data for {code}: {url}")
        return payload

    def fetch_timeline(
        self, market_id: str, code: str, kind: str, count: int
    ) -> list[dict[str, Any]]:
        """One page of a security's timeline: news or research reports.

        The page size the host serves comes from the ``count`` segment; the
        collection -- news or research reports -- from the ``kind`` segment.
        """
        url = f"https://{FLOW_HOST}/pc/timeline/v2/base/{kind}/{market_id}/{code}/{count}/first/0"
        payload = self._get_json(url)
        items = payload.get("data") if isinstance(payload, dict) else None
        return [item for item in (items or []) if isinstance(item, dict)]

    def fetch_f10(self, code: str, page: str) -> str:
        """One F10 page of one security, as GB18030 text."""
        url = f"https://{BASIC_HOST}/{code}/{page}"
        return self._get(url, "gb18030")

    def _get_json(self, url: str, encoding: str = "utf-8") -> Any:
        """GET ``url`` and decode it, unwrapping the JSONP shell if present.

        A body that parses to nothing -- an HTML error page the CDN served
        with a 200 -- is reported like every other failed request rather than
        as a decoding error the caller cannot act on.
        """
        text = self._get(url, encoding).strip()
        match = _JSONP.match(text)
        try:
            return json.loads(match.group(1) if match else text)
        except ValueError as exc:
            raise ConnectionError(f"Tonghuashun returned an unreadable body: {url}") from exc

    def _get(self, url: str, encoding: str) -> str:
        """GET ``url`` and return its body, retrying the wobbles.

        The CDN in front of the quote host answers 404 or 502 now and then,
        and once in a while a 200 with an empty body; those are retried, on
        a fresh connection, because a reused one fails more often. A refusal
        is not retried: 401 and 403 mean the host is not going to change its
        mind because the request is repeated.
        """
        host = urlparse(url).netloc
        last_error = "no attempt made"
        for attempt in range(self.retries):
            self._wait_for_host(host)
            try:
                response = self.session.get(url, timeout=self.timeout)
            except requests.RequestException as exc:
                last_error = f"{type(exc).__name__}: {exc}"
            else:
                if response.status_code == 200 and response.content.strip():
                    response.encoding = encoding
                    return response.text
                last_error = f"HTTP {response.status_code} ({len(response.content)} bytes)"
                if response.status_code in (401, 403):
                    break
                self.session.close()
            finally:
                self._last_request_at[host] = time.monotonic()
            if attempt + 1 < self.retries:
                time.sleep(self.backoff * (attempt + 1))
        raise ConnectionError(f"Tonghuashun request failed ({last_error}): {url}")

    def _wait_for_host(self, host: str) -> None:
        """Keep the gap the host asks for between two requests to it."""
        last = self._last_request_at.get(host)
        if last is None:
            return
        wait = self.min_interval - (time.monotonic() - last)
        if wait > 0:
            time.sleep(wait)
