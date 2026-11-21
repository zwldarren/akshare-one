"""akshare drifts by renaming interfaces; these tests pin the bridge.

The failures this guards against are all silent in the default suite, because
the providers import ``akshare`` once and every test that exercises them patches
a *specific* attribute. When akshare drops that attribute the test's patch target
no longer exists, so nothing fails until a user installs a newer akshare — which
is exactly what happened between 1.20.44 and 1.20.65.

Two levels are tested:

* the resolver, against fake modules that look like the akshare releases this
  package supports;
* each provider, against whichever name the *installed* akshare actually has, so
  the suite goes red on the day a rename lands rather than on the day a user
  reports it.
"""

import types

import pandas as pd
import pytest

from akshare_one.modules.compat import (
    RENAMES,
    ak_function,
    available_candidate,
    candidates,
    financial_report_kwargs,
    option_expirations,
)


class TestCandidates:
    @pytest.mark.parametrize(
        ("family", "expected_head", "expected_tail"),
        [
            ("stock_zh_a_hist", "stock_zh_a_hist_em", "stock_zh_a_hist"),
            ("stock_zh_a_daily", "stock_zh_a_hist_sina", "stock_zh_a_daily"),
            ("futures_zh_spot", "futures_zh_contract_realtime_sina", "futures_zh_spot"),
        ],
    )
    def test_newest_name_first(self, family, expected_head, expected_tail):
        names = candidates(family)
        assert names[0] == expected_head
        assert names[-1] == expected_tail

    def test_unknown_name_stands_for_itself(self):
        assert candidates("stock_news_em") == ("stock_news_em",)

    def test_every_family_is_listed_by_its_oldest_name(self):
        """RENAMES is keyed by the name this package's code uses."""
        for key, names in RENAMES.items():
            assert names[-1] == key, "the key must be the oldest name in the family"


class TestAkFunction:
    def test_resolves_to_the_name_this_release_has(self, monkeypatch):
        fake = types.SimpleNamespace(stock_zh_a_hist_em=lambda **_: "new")
        monkeypatch.setattr("akshare_one.modules.compat.ak", fake)
        assert ak_function("stock_zh_a_hist")(symbol="000001") == "new"

    def test_falls_back_to_the_older_names(self, monkeypatch):
        # akshare <= 1.20.63 can only serve the middle name for this family.
        fake = types.SimpleNamespace(stock_zh_a_daily_sina=lambda **_: "middle")
        monkeypatch.setattr("akshare_one.modules.compat.ak", fake)
        assert ak_function("stock_zh_a_daily")(symbol="sh600000") == "middle"

    def test_raises_listing_every_name_tried(self, monkeypatch):
        monkeypatch.setattr("akshare_one.modules.compat.ak", types.SimpleNamespace())
        with pytest.raises(AttributeError) as excinfo:
            ak_function("stock_zh_a_hist")
        message = str(excinfo.value)
        assert "stock_zh_a_hist_em" in message
        assert "stock_zh_a_hist" in message

    def test_available_candidate_reports_what_is_installed(self, monkeypatch):
        monkeypatch.setattr(
            "akshare_one.modules.compat.ak",
            types.SimpleNamespace(futures_zh_min_sina=lambda: None),
        )
        assert available_candidate("futures_zh_minute_sina") == "futures_zh_min_sina"


class TestFinancialReportKwargs:
    def test_new_spelling_uses_symbol_and_indicator(self):
        def new_api(symbol: str = "sh600600", indicator: str = "资产负债表"): ...

        assert financial_report_kwargs(new_api, "sh600000", "利润表") == {
            "symbol": "sh600000",
            "indicator": "利润表",
        }

    def test_old_spelling_uses_stock_and_symbol(self):
        def old_api(stock: str = "sh600600", symbol: str = "资产负债表"): ...

        assert financial_report_kwargs(old_api, "sh600000", "利润表") == {
            "stock": "sh600000",
            "symbol": "利润表",
        }

    def test_unknown_report_is_rejected(self):
        def new_api(symbol: str = "sh600600", indicator: str = "资产负债表"): ...

        with pytest.raises(ValueError, match="Unknown Sina report type"):
            financial_report_kwargs(new_api, "sh600000", "股东权益变动表")


class TestOptionExpirations:
    def test_list_shape_is_passed_through(self):
        assert option_expirations(["202611", "202612"]) == ["202611", "202612"]

    def test_frame_shape_is_unwrapped(self):
        """1.20.65 turned the list into a one-column frame."""
        frame = pd.DataFrame({"到期月份": ["202611", "202612"]})
        assert option_expirations(frame) == ["202611", "202612"]

    def test_empty_frame_becomes_an_empty_list(self):
        assert option_expirations(pd.DataFrame({"到期月份": []})) == []

    def test_non_string_values_are_stringified(self):
        assert option_expirations(pd.DataFrame({"到期月份": [202611]})) == ["202611"]


class TestProvidersResolveAgainstTheInstalledAkshare:
    """The providers must work with whatever akshare is installed right now.

    These do not call the network: they ask the compat layer which name resolves
    and check it is one the provider is willing to use. A rename that lands in a
    future akshare turns the first test red, which is the point.
    """

    @pytest.mark.parametrize("family", sorted(RENAMES))
    def test_every_family_resolves_on_the_installed_akshare(self, family):
        assert available_candidate(family) is not None, (
            f"akshare {_akshare_version()} exposes none of {candidates(family)}; "
            "add the new name to akshare_one.modules.compat.RENAMES"
        )


def _akshare_version() -> str:
    import akshare

    return getattr(akshare, "__version__", "unknown")
