# 实时数据

`get_realtime_data()` 函数用于获取股票实时行情数据。

## 函数签名

```python
def get_realtime_data(symbol=None, **kwargs) -> pd.DataFrame
```

## 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `symbol` | str | 否 | None | 股票代码(如: "600000")，不传则返回所有股票 |
| `source` | str | 否 | "xueqiu" | 数据源("eastmoney", "eastmoney_direct", "xueqiu") |

!!! warning "重要提示"
    使用 `xueqiu` 数据源时，必须提供 `symbol` 参数

!!! tip "数据源特性"
    - `eastmoney_direct` 数据源支持港股，如 "00700" 表示腾讯控股
    - `eastmoney` 数据源会获取所有股票的实时数据，个股请使用 `eastmoney_direct` 或者 `xueqiu`

## 返回值

返回 `pandas.DataFrame`，包含以下列：

| 列名 | 类型 | 描述 |
|------|------|------|
| `symbol` | str | 股票代码 |
| `price` | float | 最新价 |
| `change` | float | 涨跌额 |
| `pct_change` | float | 涨跌幅(%) |
| `timestamp` | datetime | 时间戳 |
| `volume` | int | 成交量(手) |
| `amount` | float | 成交额(元) |
| `open` | float | 今开 |
| `high` | float | 最高 |
| `low` | float | 最低 |
| `prev_close` | float | 昨收 |

## 使用示例

### 获取所有股票实时数据

```python
from akshare_one import get_realtime_data

# 获取所有股票实时数据（使用东方财富数据源）
df_all = get_realtime_data(source="eastmoney")
print(f"共获取 {len(df_all)} 只股票数据")
print(df_all.head())
```

### 获取单只股票实时数据

```python
# 获取浦发银行实时数据
df_single = get_realtime_data(symbol="600000")
print(df_single)

# 查看具体数据
if not df_single.empty:
    latest = df_single.iloc[0]
    print(f"股票代码: {latest['symbol']}")
    print(f"最新价: {latest['price']}")
    print(f"涨跌幅: {latest['pct_change']:.2f}%")
    print(f"成交量: {latest['volume']} 手")
```

### 获取港股实时数据

```python
# 获取腾讯控股港股实时数据
df_hk = get_realtime_data(
    symbol="00700", 
    source="eastmoney_direct"
)
print(df_hk)
```

### 批量获取多只股票数据

```python
# 定义股票列表
symbols = ["600000", "000001", "000002", "600036", "600519"]

# 批量获取实时数据
realtime_data = []
for symbol in symbols:
    df = get_realtime_data(symbol=symbol, source="eastmoney_direct")
    if not df.empty:
        realtime_data.append(df)

# 合并所有数据
if realtime_data:
    import pandas as pd
    combined_df = pd.concat(realtime_data, ignore_index=True)
    print(combined_df[["symbol", "price", "pct_change"]])
```
