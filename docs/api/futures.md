# 期货数据

## 获取期货历史数据

`get_futures_hist_data()` 函数用于获取期货的历史行情数据，支持多种时间粒度。

### 函数签名

```python
def get_futures_hist_data(
    symbol: str,
    contract: str = "main",
    interval: str = "day",
    interval_multiplier: int = 1,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: str = "sina"
) -> pd.DataFrame
```

### 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `symbol` | str | 是 | - | 期货品种代码 (如: "AG" 代表白银) |
| `contract` | str | 否 | "main" | 合约代码 (默认 "main" 为主力合约，也可指定如 "2602") |
| `interval` | str | 否 | "day" | 时间粒度 ("minute", "hour", "day", "week", "month") |
| `interval_multiplier` | int | 否 | 1 | 时间间隔倍数 (如 5 表示 5分钟/5小时/5天) |
| `start_date` | str | 否 | "1970-01-01" | 开始日期 (YYYY-MM-DD) |
| `end_date` | str | 否 | "2030-12-31" | 结束日期 (YYYY-MM-DD) |
| `source` | str | 否 | "sina" | 数据源 (目前仅支持 "sina") |

!!! note "时间间隔说明"
    如果 `interval` 为 'minute' 或 'hour'，`interval_multiplier` 必须大于等于 1。

### 返回值

返回 `pandas.DataFrame`，包含以下列：

| 列名 | 类型 | 描述 |
|------|------|------|
| `timestamp` | datetime | 时间戳 |
| `symbol` | str | 期货品种代码 |
| `contract` | str | 合约代码 |
| `open` | float | 开盘价 |
| `high` | float | 最高价 |
| `low` | float | 最低价 |
| `close` | float | 收盘价 |
| `volume` | int | 成交量 |
| `open_interest` | int | 持仓量 |
| `settlement` | float | 结算价 |

### 使用示例

```python
from akshare_one import get_futures_hist_data

# 获取白银主力合约日线数据
df = get_futures_hist_data(symbol="AG")
print(df.head())

# 获取白银2602合约5分钟线数据
df_5min = get_futures_hist_data(
    symbol="AG",
    contract="2602",
    interval="minute",
    interval_multiplier=5
)
print(df_5min.head())
```

---

## 获取期货实时行情

`get_futures_realtime_data()` 函数用于获取期货的实时行情数据。支持获取单个期货品种、特定合约或所有期货的实时行情。

### 函数签名

```python
def get_futures_realtime_data(
    symbol: str | None = None,
    source: str = "sina"
) -> pd.DataFrame
```

### 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `symbol` | str | 否 | None | 期货代码 (如 "CF" 或 "CF2405")，为 None 时返回所有期货 |
| `source` | str | 否 | "sina" | 数据源 |

### 返回值

返回 `pandas.DataFrame`，包含以下列：

| 列名 | 类型 | 描述 |
|------|------|------|
| `symbol` | str | 期货代码 (包含合约) |
| `contract` | str | 合约代码 |
| `price` | float | 最新价 |
| `change` | float | 涨跌额 |
| `pct_change` | float | 涨跌幅 (%) |
| `timestamp` | datetime | 时间戳 |
| `volume` | int | 成交量 |
| `open_interest` | int | 持仓量 |
| `open` | float | 今开 |
| `high` | float | 最高 |
| `low` | float | 最低 |
| `prev_settlement` | float | 昨结算 |
| `settlement` | float | 最新结算价 |

### 使用示例

```python
from akshare_one import get_futures_realtime_data

# 获取所有期货实时行情
df_all = get_futures_realtime_data()
print(df_all.head())

# 获取棉花 (CF) 所有合约实时行情
df_cf = get_futures_realtime_data(symbol="CF")
print(df_cf)

# 获取特定合约实时行情
df_cf2405 = get_futures_realtime_data(symbol="CF2405")
print(df_cf2405)
```

---

## 获取期货主力合约

`get_futures_main_contracts()` 函数用于获取当前市场上各期货品种的主力合约列表。

### 函数签名

```python
def get_futures_main_contracts(
    source: str = "sina"
) -> pd.DataFrame
```

### 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `source` | str | 否 | "sina" | 数据源 |

### 返回值

返回 `pandas.DataFrame`，包含以下列：

| 列名 | 类型 | 描述 |
|------|------|------|
| `symbol` | str | 期货品种代码 |
| `name` | str | 期货名称 |
| `contract` | str | 主力合约代码 |
| `exchange` | str | 交易所 |

### 使用示例

```python
from akshare_one import get_futures_main_contracts

# 获取主力合约列表
df = get_futures_main_contracts()
print(df.head())
```
