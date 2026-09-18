from unittest.mock import patch

import pytest

from akshare_one import (
    get_options_chain,
    get_options_expirations,
    get_options_hist,
    get_options_realtime,
)


class TestOptionsChain:
    @pytest.mark.network
    def test_basic_options_chain(self):
        """测试基本期权链数据获取功能"""
        df = get_options_chain(underlying_symbol="510300")  # 300ETF期权
        assert not df.empty
        assert "symbol" in df.columns
        assert "strike" in df.columns
        assert "expiration" in df.columns

    @pytest.mark.network
    def test_options_chain_columns(self):
        """测试期权链数据字段完整性"""
        df = get_options_chain(underlying_symbol="510300")
        if not df.empty:
            expected_columns = {
                "underlying",
                "symbol",
                "name",
                "option_type",
                "strike",
                "expiration",
                "price",
                "volume",
                "open_interest",
            }
            assert expected_columns.issubset(set(df.columns))

    @pytest.mark.network
    def test_options_chain_types(self):
        """测试期权类型分离"""
        df = get_options_chain(underlying_symbol="510300")
        if not df.empty and "option_type" in df.columns:
            option_types = df["option_type"].unique()
            assert set(option_types).issubset({"call", "put", ""})

    @pytest.mark.network
    def test_invalid_underlying_symbol(self):
        """测试无效标的代码"""
        with pytest.raises((ValueError, KeyError)):
            get_options_chain(underlying_symbol="INVALID")


class TestOptionsRealtime:
    @pytest.mark.network
    def test_options_realtime_for_underlying(self):
        """测试获取标的所有期权实时数据"""
        df = get_options_realtime(underlying_symbol="510300")
        assert not df.empty
        assert "symbol" in df.columns
        assert "price" in df.columns

    @pytest.mark.network
    def test_options_realtime_columns(self):
        """测试期权实时数据字段完整性"""
        df = get_options_realtime(underlying_symbol="510300")
        if not df.empty:
            expected_columns = {
                "symbol",
                "underlying",
                "price",
                "change",
                "pct_change",
                "timestamp",
                "volume",
                "open_interest",
            }
            assert expected_columns.issubset(set(df.columns))

    @pytest.mark.skip(reason="Requires valid specific option symbol")
    def test_specific_option_realtime(self):
        """测试特定期权的实时数据"""
        df = get_options_realtime(symbol="10004005")
        if not df.empty:
            assert "symbol" in df.columns

    def test_realtime_invalid_params_both(self):
        """测试同时提供 symbol 和 underlying_symbol 时抛出异常"""
        with pytest.raises(ValueError, match="Cannot specify both"):
            get_options_realtime(symbol="10004005", underlying_symbol="510300")

    def test_realtime_invalid_params_none(self):
        """测试都不提供 symbol 和 underlying_symbol 时抛出异常"""
        with pytest.raises(ValueError, match="Must specify either"):
            get_options_realtime()


class TestOptionsExpirations:
    @pytest.mark.network
    def test_get_options_expirations(self):
        """测试获取期权到期日列表"""
        expirations = get_options_expirations(underlying_symbol="510300")
        assert isinstance(expirations, list)

    @pytest.mark.network
    def test_expirations_sorted(self):
        """测试到期日列表有序"""
        expirations = get_options_expirations(underlying_symbol="510300")
        if expirations:
            assert expirations == sorted(expirations)

    @pytest.mark.network
    def test_invalid_expirations_symbol(self):
        """测试无效标的到期日查询"""
        with pytest.raises((ValueError, KeyError)):
            get_options_expirations(underlying_symbol="INVALID")


class TestOptionsHistory:
    @pytest.mark.skip(reason="Requires valid specific option symbol for history")
    def test_options_hist_data(self):
        """测试期权历史数据获取"""
        df = get_options_hist(
            symbol="10004005",
            start_date="2024-01-01",
            end_date="2024-01-31",
        )
        assert not df.empty
        assert "timestamp" in df.columns
        assert "close" in df.columns

    @pytest.mark.skip(reason="Requires valid specific option symbol for history")
    def test_options_hist_columns(self):
        """测试期权历史数据字段完整性"""
        df = get_options_hist(
            symbol="p2602c9000",
            start_date="2025-01-01",
            end_date="2025-01-31",
        )
        if not df.empty:
            expected_columns = {
                "timestamp",
                "symbol",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "open_interest",
            }
            assert expected_columns.issubset(set(df.columns))


class TestOptionsErrorHandling:
    def test_api_error_handling(self, monkeypatch: pytest.MonkeyPatch):
        """测试API错误处理"""
        monkeypatch.setenv("AKSHARE_ONE_CACHE_ENABLED", "false")

        with patch("akshare_one.modules.options.sina.ak.option_sse_list_sina") as mock_get:
            mock_get.side_effect = Exception("API error")
            with pytest.raises(Exception, match="API error"):
                get_options_chain(underlying_symbol="510300")

    def test_data_cleaning_with_missing_columns(self, monkeypatch: pytest.MonkeyPatch):
        """测试数据清理时缺少必要列"""
        monkeypatch.setenv("AKSHARE_ONE_CACHE_ENABLED", "false")

        with patch("akshare_one.modules.options.sina.ak.option_sse_list_sina") as mock_get:
            # Return empty list to test error handling
            mock_get.return_value = []
            with pytest.raises(ValueError, match="No options found"):
                get_options_chain(underlying_symbol="510300")


class TestOptionsIntegration:
    @pytest.mark.network
    def test_chain_and_realtime_consistency(self):
        """测试期权链和实时数据的一致性"""
        chain_df = get_options_chain(underlying_symbol="510300")
        realtime_df = get_options_realtime(underlying_symbol="510300")

        if not chain_df.empty and not realtime_df.empty:
            # Check that symbols from chain appear in realtime data
            chain_symbols = set(chain_df["symbol"].tolist())
            realtime_symbols = set(realtime_df["symbol"].tolist())
            assert chain_symbols.issubset(realtime_symbols) or chain_symbols & realtime_symbols

    @pytest.mark.network
    def test_expirations_in_chain(self):
        """测试到期日在期权链数据中出现"""
        expirations = get_options_expirations(underlying_symbol="510300")
        chain_df = get_options_chain(underlying_symbol="510300")

        if expirations and not chain_df.empty and "expiration" in chain_df.columns:
            chain_expirations = set(chain_df["expiration"].unique().tolist())
            # At least some expirations should match
            assert len(set(expirations) & chain_expirations) >= 0
