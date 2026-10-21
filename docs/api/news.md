# 新闻数据

`get_news_data()` 函数用于获取个股新闻数据。

## 函数签名

```python
def get_news_data(
    symbol: str,
    source: str = "eastmoney"
) -> pd.DataFrame
```

## 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `symbol` | str | 是 | - | 股票代码 (如: "300059") |
| `source` | str | 否 | "eastmoney" | 数据源 ("eastmoney", "ths") |

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

### 使用同花顺数据源

```python
# 同花顺按个股时间轴返回新闻与研报，研报在 source 列上单独标记
df = get_news_data(symbol="600519", source="ths")
print(df[["title", "publish_time", "source"]].head())
```

!!! warning "同花顺 (`ths`) 数据源说明"
    - `keyword` 列是传入的股票代码，与其它数据源一致
    - `content` 列是上游时间轴给出的摘要，不是新闻全文
    - `source` 列标记条目所属的集合：新闻为 `同花顺`，研报为 `同花顺研报`。
      上游时间轴不提供文章来源，因此该列不是发布媒体，与 `eastmoney` 不同
    - 每个集合只提供一页（最多 60 条），不翻页：一次调用最多返回 60 条新闻与
      60 条研报
