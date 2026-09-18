"""One owner per column contract, and the prose agrees with it.

`modules/<domain>/schema.py` declares the columns; the public function
docstrings and the published docs pages restate them, so this file checks both
against the declaration instead of letting them drift apart.
"""

import re
from pathlib import Path
from typing import Any

import pandas as pd
import pytest

from akshare_one import get_basic_info, get_inner_trade_data
from akshare_one.modules.cache import clear
from akshare_one.modules.financial.schema import (
    BALANCE_COLUMNS,
    CASH_FLOW_COLUMNS,
    INCOME_COLUMNS,
    METRICS_COLUMNS,
)
from akshare_one.modules.futures.schema import (
    CONTRACT_COLUMNS,
    HIST_COLUMNS,
)
from akshare_one.modules.futures.schema import (
    REALTIME_COLUMNS as FUTURES_REALTIME_COLUMNS,
)
from akshare_one.modules.historical.schema import COLUMNS as HISTORICAL_COLUMNS
from akshare_one.modules.info.schema import COLUMNS as INFO_COLUMNS
from akshare_one.modules.insider.schema import COLUMNS as INSIDER_COLUMNS
from akshare_one.modules.news.schema import COLUMNS as NEWS_COLUMNS
from akshare_one.modules.options.schema import (
    CHAIN_COLUMNS,
    HISTORY_COLUMNS,
)
from akshare_one.modules.options.schema import (
    REALTIME_COLUMNS as OPTIONS_REALTIME_COLUMNS,
)
from akshare_one.modules.realtime.schema import COLUMNS as REALTIME_COLUMNS

DOCS = Path(__file__).resolve().parents[1] / "docs" / "api"

#: Public function -> the schema tuples it returns, and the page that documents it.
CONTRACTS: list[tuple[str, tuple[tuple[str, ...], ...], str]] = [
    ("get_basic_info", (INFO_COLUMNS,), "basic-info.md"),
    ("get_hist_data", (HISTORICAL_COLUMNS,), "historical.md"),
    ("get_realtime_data", (REALTIME_COLUMNS,), "realtime.md"),
    ("get_news_data", (NEWS_COLUMNS,), "news.md"),
    ("get_inner_trade_data", (INSIDER_COLUMNS,), "insider.md"),
    ("get_balance_sheet", (BALANCE_COLUMNS,), "financial.md"),
    ("get_income_statement", (INCOME_COLUMNS,), "financial.md"),
    ("get_cash_flow", (CASH_FLOW_COLUMNS,), "financial.md"),
    ("get_financial_metrics", (METRICS_COLUMNS,), "financial.md"),
    ("get_futures_hist_data", (HIST_COLUMNS,), "futures.md"),
    ("get_futures_realtime_data", (FUTURES_REALTIME_COLUMNS,), "futures.md"),
    ("get_futures_main_contracts", (CONTRACT_COLUMNS,), "futures.md"),
    ("get_options_chain", (CHAIN_COLUMNS,), "options.md"),
    ("get_options_realtime", (OPTIONS_REALTIME_COLUMNS,), "options.md"),
    ("get_options_hist", (HISTORY_COLUMNS,), "options.md"),
]

ALL_SCHEMAS = [columns for _, schemas, _ in CONTRACTS for columns in schemas]

IDS = [name for name, _, _ in CONTRACTS]


def _contracts_by_page() -> dict[str, list[tuple[str, tuple[tuple[str, ...], ...]]]]:
    """The contracts each docs page documents, in the page's own order."""
    pages: dict[str, list[tuple[str, tuple[tuple[str, ...], ...]]]] = {}
    for name, schemas, page in CONTRACTS:
        pages.setdefault(page, []).append((name, schemas))
    return pages


PAGES = _contracts_by_page()


def _docstring_columns(func: Any) -> tuple[str, ...]:
    """The `- column: description` bullets of a public function's Returns block."""
    return tuple(re.findall(r"^\s*- (\w+):", func.__doc__ or "", re.MULTILINE))


#: A page's column table: the header names the field column, its rows the fields.
_COLUMN_TABLE_HEAD = re.compile(r"^\|\s*(?:字段名|列名)\s*\|")
_COLUMN_TABLE_ROW = re.compile(r"^\s*\|\s*`([a-z_][a-z0-9_]*)`\s*\|")


def _documented_column_tables(page: str) -> list[tuple[str, ...]]:
    """Every column table of a docs page, in file order."""
    blocks = re.split(r"\n\s*\n", (DOCS / page).read_text(encoding="utf-8"))
    tables: list[tuple[str, ...]] = []
    for block in blocks:
        if not _COLUMN_TABLE_HEAD.match(block):
            continue
        rows = [
            match.group(1)
            for line in block.splitlines()
            if (match := _COLUMN_TABLE_ROW.match(line))
        ]
        tables.append(tuple(rows))
    return tables


@pytest.mark.parametrize(("name", "schemas", "page"), CONTRACTS, ids=IDS)
def test_docstring_lists_the_declared_columns(
    name: str, schemas: tuple[tuple[str, ...], ...], page: str
) -> None:
    """A docstring may stay silent about columns; it may not restate other ones."""
    import akshare_one

    documented = _docstring_columns(getattr(akshare_one, name))
    assert documented in ((), *schemas), (
        f"{name}'s docstring lists columns that are not its schema: {documented}"
    )


@pytest.mark.parametrize("page", PAGES)
def test_docs_page_documents_exactly_the_declared_columns(page: str) -> None:
    """A page shows its contracts' declared columns, in order, and invents none."""
    expected = PAGES[page]
    documented = _documented_column_tables(page)
    assert len(documented) == len(expected), (
        f"{page} has {len(documented)} column tables for {len(expected)} contracts "
        f"({', '.join(name for name, _ in expected)})"
    )
    for columns, (name, schemas) in zip(documented, expected, strict=True):
        assert columns in schemas, f"{page} documents {name} as {columns}, not as {schemas}"


@pytest.mark.parametrize("columns", ALL_SCHEMAS, ids=lambda c: c[0])
def test_a_schema_declares_no_column_twice(columns: tuple[str, ...]) -> None:
    assert len(set(columns)) == len(columns)


def test_a_source_that_supplies_part_of_the_schema_still_returns_every_column(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing upstream fields come back as NaN, not as a missing column."""

    def fake_fetch_basic_info(self: Any, symbol: str) -> dict[str, Any]:
        return {"rc": 0, "data": {"f57": symbol, "f58": "stub"}}  # price/industry absent

    monkeypatch.setattr(
        "akshare_one.modules.info.eastmoney.EastMoneyClient.fetch_basic_info",
        fake_fetch_basic_info,
    )
    clear("info")

    df = get_basic_info("600000")
    assert tuple(df.columns) == INFO_COLUMNS
    assert df["industry"].isna().all()


def _insider_frame(partial: bool) -> pd.DataFrame:
    """A frame as XueQiu sends it: full, or missing fields the schema promises."""
    if partial:
        return pd.DataFrame({"股票代码": ["SH600000"], "股票名称": ["浦发银行"]})
    return pd.DataFrame(
        {
            "股票代码": ["SH600000"],
            "股票名称": ["浦发银行"],
            "变动人": ["张三"],
            "董监高职务": ["董事"],
            "变动日期": ["2026-01-05"],
            "变动股数": [100],
            "成交均价": [10.0],
            "变动后持股数": [1100],
            "与董监高关系": ["本人"],
        }
    )


@pytest.mark.parametrize("frame", ["empty", "partial", "filled"])
def test_insider_answers_differ_only_in_rows(monkeypatch: pytest.MonkeyPatch, frame: str) -> None:
    """Empty, partial and filled upstream answers all carry the declared columns."""
    monkeypatch.setattr(
        "akshare_one.modules.insider.xueqiu.ak.stock_inner_trade_xq",
        lambda: pd.DataFrame() if frame == "empty" else _insider_frame(partial=frame == "partial"),
    )
    clear("insider")

    df = get_inner_trade_data("600000")
    assert tuple(df.columns) == INSIDER_COLUMNS
    assert df.empty is (frame == "empty")
    if frame == "partial":
        assert df["title"].isna().all()
        assert df["is_board_director"].isna().all()
