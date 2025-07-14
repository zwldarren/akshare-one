# 历史数据

`get_hist_data()` 函数用于获取股票历史行情数据，支持多种时间粒度和复权方式。

## 函数签名

```python
def get_hist_data(symbol, **kwargs) -> pd.DataFrame
```

## 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `symbol` | str | 是 | - | 股票代码(如: "600000") |
| `interval` | str | 否 | "day" | 时间粒度('minute','hour','day','week','month','year') |
| `interval_multiplier` | int | 否 | 1 | 时间间隔倍数 |
| `start_date` | str | 否 | "1970-01-01" | 开始日期(YYYY-MM-DD) |
| `end_date` | str | 否 | "2030-12-31" | 结束日期(YYYY-MM-DD) |
| `adjust` | str | 否 | "none" | 复权类型("none","qfq","hfq") |
| `source` | str | 否 | "eastmoney" | 数据源("eastmoney","eastmoney_direct","sina") |

!!! note "时间间隔说明"
    如果 `interval` 为 'minute'，则 `interval_multiplier` 表示分钟数，如 5 表示 5 分钟线

!!! tip "数据源特性"
    - `eastmoney_direct` 数据源支持港股，如 "00700" 表示腾讯控股
    - `eastmoney_direct` 数据源的小时和分钟级数据只支持当前交易日
    - 不同数据源的数据覆盖范围可能有所差异

## 返回值

返回 `pandas.DataFrame`，包含以下列：

| 列名 | 类型 | 描述 |
|------|------|------|
| `timestamp` | datetime | 时间戳 |
| `open` | float | 开盘价 |
| `high` | float | 最高价 |
| `low` | float | 最低价 |
| `close` | float | 收盘价 |
| `volume` | int | 成交量 |

## 复权类型说明

| 复权类型 | 标识符 | 说明 |
|----------|--------|------|
| 不复权 | `none` | 原始价格，不进行任何调整 |
| 前复权 | `qfq` | 以当前价格为基准向前调整历史价格 |
| 后复权 | `hfq` | 以历史价格为基准向后调整当前价格 |

## 使用示例

### 基础用法

```python
from akshare_one import get_hist_data

# 获取浦发银行日线数据
df = get_hist_data(symbol="600000")
print(df.head())
```

### 获取前复权数据

```python
# 获取前复权日线数据
df = get_hist_data(
    symbol="600000",
    interval="day",
    adjust="qfq",
    start_date="2024-01-01",
    end_date="2024-03-31"
)
print(f"数据条数: {len(df)}")
print(df.head())
```

### 获取分钟级数据

```python
# 获取5分钟线数据（仅当前交易日）
df = get_hist_data(
    symbol="600000",
    interval="minute",
    interval_multiplier=5,
    source="eastmoney_direct"
)
print(df.tail())
```

### 获取港股数据

```python
# 获取腾讯控股港股数据
df = get_hist_data(
    symbol="00700",
    interval="day",
    source="eastmoney_direct",
    start_date="2024-01-01"
)
print(df.head())
```

### 获取周线数据

```python
# 获取周线数据
df = get_hist_data(
    symbol="600000",
    interval="week",
    start_date="2023-01-01",
    end_date="2024-01-01"
)
print(df.head())
```