"""Shared pytest configuration.

The default test run is fully offline. Tests that call live upstream data
providers (EastMoney, Sina, XueQiu, the exchanges) are marked ``network`` and
skipped unless ``--run-network`` is passed, because those endpoints apply
aggressive rate limits and a full run can get the caller temporarily blocked.

The marker is per test, not per file, so a test that fakes its upstream still
runs in the default suite.

    pytest --run-network          # include live network tests
    pytest --run-network -k sina  # only the Sina live tests
"""

from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-network",
        action="store_true",
        default=False,
        help="run tests that call live upstream data providers",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "network: test calls a live upstream data provider (skipped unless --run-network)",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--run-network"):
        return

    skip = pytest.mark.skip(
        reason="needs live upstream data (rate limited); pass --run-network to run"
    )
    for item in items:
        if "network" in item.keywords:
            item.add_marker(skip)
