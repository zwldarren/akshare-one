from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from akshare_one import get_news_data


class TestNewsData:
    def test_basic_news_data(self):
        """测试基本新闻数据获取功能"""
        df = get_news_data(symbol="300059")
        assert not df.empty
        required_columns = {
            "keyword",
            "title",
            "content",
            "publish_time",
            "source",
            "url",
        }
        assert required_columns.issubset(df.columns)

        # 验证发布时间格式
        assert isinstance(df.iloc[0]["publish_time"], datetime)

    def test_news_data_time_range(self):
        """测试新闻数据时间范围"""
        df = get_news_data(symbol="300059")
        now = datetime.now(timezone.utc)
        one_year_ago = now - timedelta(days=365)

        # 验证新闻发布时间在合理范围内
        assert all(one_year_ago <= ts <= now for ts in df["publish_time"])

    def test_news_content_quality(self):
        """测试新闻内容质量"""
        df = get_news_data(symbol="300059")
        sample_news = df.iloc[0]

        assert len(sample_news["title"]) > 0
        assert len(sample_news["content"]) > 0
        assert sample_news["url"].startswith("http")

    def test_multiple_pages(self):
        """测试多页新闻数据"""
        df = get_news_data(symbol="300059")
        assert len(df) >= 10  # 至少获取10条新闻

    def test_api_error_handling(self):
        """测试API错误处理"""
        with patch(
            "akshare_one.modules.news.eastmoney.EastMoneyNews.get_news_data"
        ) as mock_get:
            mock_get.side_effect = Exception("API error")
            with pytest.raises(Exception, match="API error"):
                get_news_data(symbol="300059")

    def test_unsupported_source(self):
        """测试不支持的来源"""
        with pytest.raises(ValueError):
            get_news_data(symbol="300059", source="invalid")

    def test_factory_error_handling(self):
        """测试工厂错误处理"""
        with patch(
            "akshare_one.modules.news.factory.NewsDataFactory.get_provider"
        ) as mock_factory:
            mock_factory.side_effect = ValueError("Unsupported source")
            with pytest.raises(ValueError, match="Unsupported source"):
                get_news_data(symbol="300059", source="invalid")
