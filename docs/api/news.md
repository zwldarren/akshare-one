# 新闻数据

`get_news_data()` 函数用于获取个股新闻数据。

## 函数签名

```python
def get_news_data(symbol, **kwargs) -> pd.DataFrame
```

## 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `symbol` | str | 是 | - | 股票代码(如: "300059") |
| `source` | str | 否 | "eastmoney" | 数据源(目前仅支持"eastmoney") |

## 返回值

返回 `pandas.DataFrame`，包含以下列：

| 列名 | 类型 | 描述 |
|------|------|------|
| `keyword` | str | 关键词 |
| `title` | str | 新闻标题 |
| `content` | str | 新闻内容 |
| `publish_time` | datetime | 发布时间|
| `source` | str | 文章来源 |
| `url` | str | 新闻链接 |

## 使用示例

```python
from akshare_one import get_news_data

# 获取个股新闻数据
df = get_news_data(symbol="300059")
print(df[["title", "publish_time", "source"]].head())
```