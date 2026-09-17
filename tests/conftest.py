"""Shared pytest configuration.

The default test run is fully offline. Tests that hit live upstream data
providers (EastMoney, Sina, XueQiu, the exchanges) are skipped unless
``--run-network`` is passed, because those endpoints apply aggressive rate
limits and a full run can get the caller temporarily blocked.

    pytest --run-network          # include live network tests
    pytest --run-network -k sina  # only the Sina live tests
"""

from __future__ import annotations

import pytest

# Test modules whose tests call live upstream data providers.
_NETWORK_MODULES = {
    "test_stock.py",
    "test_financial.py",
    "test_futures.py",
    "test_news.py",
    "test_info.py",
    "test_insider.py",
    "test_options.py",
}


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-network",
        action="store_true",
        default=False,
        help="run tests that call live upstream data providers",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--run-network"):
        return

    skip = pytest.mark.skip(
        reason="needs live upstream data (rate limited); pass --run-network to run"
    )
    for item in items:
        if item.path.name in _NETWORK_MODULES:
            item.add_marker(skip)
