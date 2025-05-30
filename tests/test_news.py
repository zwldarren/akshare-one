import pytest
from akshare_one import get_news_data
from datetime import datetime, timedelta, timezone


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

    def test_invalid_symbol(self):
        """测试无效股票代码"""
        with pytest.raises(Exception):
            get_news_data(symbol="INVALID")

    def test_multiple_pages(self):
        """测试多页新闻数据"""
        df = get_news_data(symbol="300059")
        assert len(df) >= 10  # 至少获取10条新闻
