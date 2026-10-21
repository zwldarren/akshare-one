# 基础信息

`get_basic_info()` 函数用于获取股票基础信息。

## 函数签名

```python
def get_basic_info(
    symbol: str,
    source: str = "eastmoney"
) -> pd.DataFrame
```

## 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `symbol` | str | 是 | - | 股票代码 (如: "600000") |
| `source` | str | 否 | "eastmoney" | 数据源 ("eastmoney", "ths") |

## 返回值

返回 `pandas.DataFrame`，包含以下列：

| 列名 | 类型 | 描述 |
|------|------|------|
| `price` | float | 最新价 |
| `symbol` | str | 股票代码 |
| `name` | str | 股票简称 |
| `total_shares` | float | 总股本 (万股) |
| `float_shares` | float | 流通股 (万股) |
| `total_market_cap` | float | 总市值 (亿元) |
| `float_market_cap` | float | 流通市值 (亿元) |
| `industry` | str | 所属行业 |
| `listing_date` | datetime | 上市日期 |

## 使用示例

### 获取单只股票基础信息

```python
from akshare_one import get_basic_info

# 获取浦发银行基础信息
df = get_basic_info(symbol="600000")
print(df)

# 查看具体信息
if not df.empty:
    info = df.iloc[0]
    print(f"股票名称: {info['name']}")
    print(f"所属行业: {info['industry']}")
    print(f"总市值: {info['total_market_cap']} 元")
```

### 使用同花顺数据源

```python
# 同花顺的基础信息来自实时快照，上市日期来自 F10 公司概况页
df = get_basic_info(symbol="600519", source="ths")
print(df)
```

!!! note "同花顺 (`ths`) 数据源说明"
    - 上游快照不提供所属行业，`industry` 列始终为 `NaN`
    - 上市日期来自 F10 页面；该页读取失败时上市日期为空，其余字段照常返回
