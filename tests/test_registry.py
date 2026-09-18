"""The registry is the seam between the public facade and every provider.

These tests hold two invariants the nine deleted factories could not: the
sources a public call advertises are exactly the sources registered for the
domain it resolves against, and every registered source constructs a provider
of that domain's interface.
"""

from typing import Any, get_args, get_type_hints

import pytest

import akshare_one
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
from akshare_one.modules.registry import (
    DEFAULT_CAPABILITY,
    UnknownProviderError,
    provider,
    registered_sources,
    resolve,
)

#: Public function -> the arguments that carry it as far as the registry.
CALLS: list[tuple[str, dict[str, Any]]] = [
    ("get_basic_info", {"symbol": "600000"}),
    ("get_hist_data", {"symbol": "600000"}),
    ("get_realtime_data", {}),
    ("get_news_data", {"symbol": "300059"}),
    ("get_balance_sheet", {"symbol": "600000"}),
    ("get_income_statement", {"symbol": "600000"}),
    ("get_cash_flow", {"symbol": "600000"}),
    ("get_financial_metrics", {"symbol": "600000"}),
    ("get_inner_trade_data", {"symbol": "600000"}),
    ("get_futures_hist_data", {"symbol": "AG"}),
    ("get_futures_realtime_data", {"symbol": "CF"}),
    ("get_futures_main_contracts", {}),
    ("get_options_chain", {"underlying_symbol": "510300"}),
    ("get_options_realtime", {"symbol": "10004005"}),
    ("get_options_expirations", {"underlying_symbol": "510300"}),
    ("get_options_hist", {"symbol": "10004005"}),
]


class _Routed(Exception):
    """Raised by the recorded call so a public call stops at the seam."""


class _RecordingProvider:
    """Stands in for a provider, recording which interface method is asked for."""

    def __init__(self, calls: list[str]) -> None:
        self._calls = calls

    def __getattr__(self, name: str) -> Any:
        def record(*args: Any, **kwargs: Any) -> Any:
            self._calls.append(name)
            raise _Routed

        return record


def _interface_of(domain: str, capability: str) -> type[Any]:
    """The interface that domain/capability's registered providers implement."""
    return next(
        interface
        for registered_domain, registered_capability, interface, _ in INTERFACES
        if (registered_domain, registered_capability) == (domain, capability)
    )


# Domain capability -> the interface its providers must implement, plus the
# constructor arguments the public facade passes.
INTERFACES: list[tuple[str, str, type[Any], dict[str, Any]]] = [
    ("historical", "default", HistoricalDataProvider, {"symbol": "600000"}),
    ("realtime", "default", RealtimeDataProvider, {"symbol": "600000"}),
    ("info", "default", InfoDataProvider, {"symbol": "600000"}),
    ("news", "default", NewsDataProvider, {"symbol": "600000"}),
    ("financial", "default", FinancialDataProvider, {"symbol": "600000"}),
    ("insider", "default", InsiderDataProvider, {"symbol": "600000"}),
    ("futures", "historical", HistoricalFuturesDataProvider, {"symbol": "AG"}),
    ("futures", "realtime", RealtimeFuturesDataProvider, {"symbol": "AG"}),
    ("options", "default", OptionsDataProvider, {"underlying_symbol": "510300"}),
]


@pytest.mark.parametrize(("name", "kwargs"), CALLS, ids=[name for name, _ in CALLS])
def test_facade_routes_to_the_domain_it_advertises(
    monkeypatch: pytest.MonkeyPatch, name: str, kwargs: dict[str, Any]
) -> None:
    """A public call resolves the domain whose interface and sources it advertises."""
    func = getattr(akshare_one, name)
    documented = set(get_args(get_type_hints(func)["source"]))
    routed: list[tuple[str, str, str]] = []
    called: list[str] = []

    def record(
        domain: str, source: str, capability: str = DEFAULT_CAPABILITY, **passed: Any
    ) -> Any:
        routed.append((domain, capability, source))
        return _RecordingProvider(called)

    monkeypatch.setattr(akshare_one, "resolve", record)
    with pytest.raises(_Routed):
        func(**kwargs)

    assert len(routed) == 1, f"{name} resolved {len(routed)} providers"
    domain, capability, source = routed[0]
    assert set(registered_sources(domain, capability)) == documented, (
        f"{name} resolves {domain}/{capability}, whose sources are not the ones it advertises"
    )
    assert source in documented, f"{name} defaults to an unregistered source {source!r}"
    assert called[0] in _interface_of(domain, capability).__abstractmethods__, (
        f"{name} asks {domain} for {called[0]}, which is not that domain's method"
    )


@pytest.mark.parametrize(
    ("domain", "capability", "interface", "kwargs"),
    INTERFACES,
    ids=[f"{domain}-{capability}" for domain, capability, _, _ in INTERFACES],
)
def test_every_registered_source_constructs_its_domain_interface(
    domain: str, capability: str, interface: type[Any], kwargs: dict[str, Any]
) -> None:
    """Every registered source resolves to a provider of that domain's interface."""
    sources = registered_sources(domain, capability)
    assert sources, f"no provider registered for {domain}/{capability}"
    for source in sources:
        resolved = resolve(domain, source, capability=capability, **kwargs)
        assert isinstance(resolved, interface), f"{source} does not implement {interface.__name__}"


@pytest.mark.parametrize("source", ["invalid", "", "SINA "])
def test_unknown_source_lists_the_known_ones(source: str) -> None:
    with pytest.raises(UnknownProviderError) as excinfo:
        resolve("historical", source, symbol="600000")

    message = str(excinfo.value)
    assert repr(source) in message
    for known in registered_sources("historical"):
        assert known in message


def test_source_lookup_is_case_insensitive() -> None:
    assert type(resolve("historical", "SINA", symbol="600000")) is type(
        resolve("historical", "sina", symbol="600000")
    )


def test_duplicate_registration_of_a_different_class_is_refused() -> None:
    class First:
        pass

    class Second:
        pass

    provider("test_domain", "src")(First)
    with pytest.raises(ValueError, match="already registered"):
        provider("test_domain", "src")(Second)
    assert registered_sources("test_domain") == ("src",)


def test_re_registering_the_same_class_is_idempotent() -> None:
    class Reimported:
        pass

    assert provider("test_domain", "same")(Reimported) is Reimported
    assert provider("test_domain", "same")(Reimported) is Reimported
