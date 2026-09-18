"""The cache seam's interface: keys, the env switch, and the policy table.

Offline. The second adapter at this seam is a stub provider that counts its
calls; the end-to-end case goes through the public facade with the EastMoney
transport faked, so it needs no network.
"""

import inspect
import typing

import pandas as pd
import pytest

import akshare_one.modules.financial as financial_pkg
import akshare_one.modules.futures as futures_pkg
import akshare_one.modules.historical as historical_pkg
import akshare_one.modules.info as info_pkg
import akshare_one.modules.insider as insider_pkg
import akshare_one.modules.news as news_pkg
import akshare_one.modules.options as options_pkg
import akshare_one.modules.realtime as realtime_pkg
from akshare_one import get_basic_info
from akshare_one.modules.cache import cached, clear, enabled
from akshare_one.modules.financial.base import FinancialDataProvider
from akshare_one.modules.futures.base import (
    HistoricalFuturesDataProvider,
    RealtimeFuturesDataProvider,
)
from akshare_one.modules.historical.base import HistoricalDataProvider
from akshare_one.modules.info.base import InfoDataProvider
from akshare_one.modules.insider.base import InsiderDataProvider
from akshare_one.modules.news.base import NewsDataProvider
from akshare_one.modules.options.base import OptionsDataProvider
from akshare_one.modules.realtime.base import RealtimeDataProvider

DOMAIN_PACKAGES = [
    financial_pkg,
    futures_pkg,
    historical_pkg,
    info_pkg,
    insider_pkg,
    news_pkg,
    options_pkg,
    realtime_pkg,
]

BASE_CLASSES = [
    FinancialDataProvider,
    HistoricalDataProvider,
    HistoricalFuturesDataProvider,
    InfoDataProvider,
    InsiderDataProvider,
    NewsDataProvider,
    OptionsDataProvider,
    RealtimeDataProvider,
    RealtimeFuturesDataProvider,
]


class _Stub:
    """A provider-shaped object: declared parameters plus a call counter."""

    CACHE_PARAMS = ("symbol", "window")

    def __init__(self, symbol: str, window: int = 1) -> None:
        self.symbol = symbol
        self.window = window
        self.calls = 0

    @cached("info")
    def fetch(self) -> str:
        """Fetch the stub value."""
        self.calls += 1
        return f"{self.symbol}:{self.window}:{self.calls}"

    @cached("info")
    def fetch_for(self, symbol: str) -> str:
        self.calls += 1
        return f"{symbol}:{self.calls}"


def test_declared_parameters_are_part_of_the_key() -> None:
    clear("info")
    stub = _Stub("600000")

    assert stub.fetch() == "600000:1:1"
    assert stub.fetch() == "600000:1:1"
    assert stub.calls == 1

    other = _Stub("600000", window=5)
    other.fetch()
    assert other.calls == 1  # a different window is a different key


def test_call_arguments_are_part_of_the_key() -> None:
    clear("info")
    stub = _Stub("600000")

    stub.fetch_for("a")
    stub.fetch_for("a")
    assert stub.calls == 1

    stub.fetch_for("b")
    assert stub.calls == 2


def test_disabling_the_cache_bypasses_it(monkeypatch: pytest.MonkeyPatch) -> None:
    clear("info")
    stub = _Stub("600000")

    monkeypatch.setenv("AKSHARE_ONE_CACHE_ENABLED", "false")
    assert enabled() is False
    stub.fetch()
    stub.fetch()
    assert stub.calls == 2


def test_an_undeclared_namespace_fails_at_decoration_time() -> None:
    with pytest.raises(KeyError, match="Unknown cache namespace"):
        cached("not_a_namespace")


def test_the_wrapper_keeps_the_method_name_and_docstring() -> None:
    assert _Stub.fetch.__name__ == "fetch"
    assert _Stub.fetch.__doc__ == "Fetch the stub value."


def test_a_public_call_is_served_from_the_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    """The second identical public call does not reach the client again."""
    requests: list[str] = []

    def fake_fetch_basic_info(self, symbol: str) -> dict[str, typing.Any]:
        requests.append(symbol)
        return {"rc": 0, "data": {"f57": symbol, "f58": "stub"}}

    monkeypatch.setattr(
        "akshare_one.modules.info.eastmoney.EastMoneyClient.fetch_basic_info",
        fake_fetch_basic_info,
    )
    clear("info")

    first = get_basic_info("600000")
    second = get_basic_info("600000")
    assert requests == ["600000"]
    pd.testing.assert_frame_equal(first, second)

    monkeypatch.setenv("AKSHARE_ONE_CACHE_ENABLED", "false")
    get_basic_info("600000")
    assert requests == ["600000", "600000"]


def _cache_declaring_classes() -> list[type[typing.Any]]:
    classes: set[type[typing.Any]] = set(BASE_CLASSES)
    for package in DOMAIN_PACKAGES:
        for name in package.__all__:
            candidate = getattr(package, name)
            if isinstance(candidate, type) and hasattr(candidate, "CACHE_PARAMS"):
                classes.add(candidate)
    return sorted(classes, key=lambda cls: cls.__qualname__)


def _constructor_parameters(cls: type[typing.Any]) -> set[str]:
    return {
        name
        for name, param in inspect.signature(cls).parameters.items()
        if param.kind in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY)
    }


@pytest.mark.parametrize("cls", _cache_declaring_classes(), ids=lambda cls: cls.__qualname__)
def test_declared_parameters_cover_the_constructor(cls: type[typing.Any]) -> None:
    """A parameter that changes the answer cannot be missing from the key."""
    missing = _constructor_parameters(cls) - set(cls.CACHE_PARAMS)
    assert not missing, f"{cls.__qualname__} does not declare {sorted(missing)} in CACHE_PARAMS"
