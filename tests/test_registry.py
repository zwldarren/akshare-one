"""The registry is the seam between the public facade and every provider.

These tests hold two invariants the nine deleted factories could not: the
sources a public function advertises are exactly the sources registered for its
domain, and every registered source constructs a provider of that domain's
interface.
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
    UnknownProviderError,
    provider,
    registered_sources,
    resolve,
)

# Public function -> the domain (and futures capability) it resolves against.
FUNCTIONS = [
    ("get_basic_info", "info", "default"),
    ("get_hist_data", "historical", "default"),
    ("get_realtime_data", "realtime", "default"),
    ("get_news_data", "news", "default"),
    ("get_balance_sheet", "financial", "default"),
    ("get_income_statement", "financial", "default"),
    ("get_cash_flow", "financial", "default"),
    ("get_financial_metrics", "financial", "default"),
    ("get_inner_trade_data", "insider", "default"),
    ("get_futures_hist_data", "futures", "historical"),
    ("get_futures_realtime_data", "futures", "realtime"),
    ("get_futures_main_contracts", "futures", "historical"),
    ("get_options_chain", "options", "default"),
    ("get_options_realtime", "options", "default"),
    ("get_options_expirations", "options", "default"),
    ("get_options_hist", "options", "default"),
]

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


@pytest.mark.parametrize(("name", "domain", "capability"), FUNCTIONS)
def test_facade_sources_match_registry(name: str, domain: str, capability: str) -> None:
    """A public function advertises exactly the sources its domain registered."""
    func = getattr(akshare_one, name)
    documented = set(get_args(get_type_hints(func)["source"]))
    registered = set(registered_sources(domain, capability))
    assert documented == registered


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
