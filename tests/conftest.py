"""Shared pytest configuration.

The default test run is fully offline. Tests that call live upstream data
providers (EastMoney, Sina, XueQiu, Tonghuashun, the exchanges) are marked
``network`` and skipped unless ``--run-network`` is passed, because those
endpoints apply aggressive rate limits and a full run can get the caller
temporarily blocked.

The marker is per test, not per file, so a test that fakes its upstream still
runs in the default suite.

    pytest --run-network          # include live network tests
    pytest --run-network -k sina  # only the Sina live tests
"""

from __future__ import annotations

from unittest.mock import patch

import pytest


@pytest.fixture
def patch_ak():
    """Patch an akshare interface by the name akshare-one knows it by.

    akshare renames interfaces without a deprecation window (see
    :mod:`akshare_one.modules.compat`), so a test that patches
    ``akshare.futures_zh_spot`` stops being able to patch at all the release that
    renames it -- and then it fails with ``AttributeError`` from mock rather than
    testing anything. Resolving the name first keeps the test measuring this
    package instead of measuring which akshare is installed.

        def test_x(patch_ak):
            with patch_ak("futures_zh_spot", return_value=frame) as mock:
                ...
    """
    from akshare_one.modules.compat import available_candidate

    def _patch(family: str, **kwargs):
        name = available_candidate(family) or family
        return patch(f"akshare.{name}", **kwargs)

    return _patch


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
