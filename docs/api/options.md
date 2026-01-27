# 期权数据

## 获取期权链

`get_options_chain()` 函数用于获取指定标的的完整期权链数据。

### 函数签名

```python
def get_options_chain(
    underlying_symbol: str,
    source: str = "sina"
) -> pd.DataFrame
```

### 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `underlying_symbol` | str | 是 | - | 标的代码 (如: "510300" 代表 300ETF期权) |
| `source` | str | 否 | "sina" | 数据源 (目前仅支持 "sina") |

### 返回值

返回 `pandas.DataFrame`，包含以下列：

| 列名 | 类型 | 描述 |
|------|------|------|
| `underlying` | str | 标的代码 |
| `symbol` | str | 期权代码 |
| `name` | str | 期权名称 |
| `option_type` | str | 期权类型 (call/put) |
| `strike` | float | 行权价 |
| `expiration` | str | 到期日 |
| `price` | float | 最新价 |
| `change` | float | 涨跌额 |
| `pct_change` | float | 涨跌幅 (%) |
| `volume` | int | 成交量 |
| `open_interest` | int | 持仓量 |
| `implied_volatility` | float | 隐含波动率 |

### 使用示例

```python
from akshare_one import get_options_chain

# 获取300ETF期权链
df = get_options_chain(underlying_symbol="510300")
print(df.head())
```

---

## 获取期权实时行情

`get_options_realtime()` 函数用于获取期权的实时行情数据。支持获取单个期权或指定标的下的所有期权。

### 函数签名

```python
def get_options_realtime(
    symbol: str | None = None,
    underlying_symbol: str | None = None,
    source: str = "sina"
) -> pd.DataFrame
```

### 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `symbol` | str | 否 | None | 期权代码 (如 "10004005") |
| `underlying_symbol` | str | 否 | None | 标的代码 (如 "510300")，用于获取该标的下所有期权 |
| `source` | str | 否 | "sina" | 数据源 |

!!! warning "参数限制"
    `symbol` 和 `underlying_symbol` 必须且只能提供其中一个。

### 返回值

返回 `pandas.DataFrame`，包含以下列：

| 列名 | 类型 | 描述 |
|------|------|------|
| `symbol` | str | 期权代码 |
| `underlying` | str | 标的代码 |
| `price` | float | 最新价 |
| `change` | float | 涨跌额 |
| `pct_change` | float | 涨跌幅 (%) |
| `timestamp` | datetime | 时间戳 |
| `volume` | int | 成交量 |
| `open_interest` | int | 持仓量 |
| `iv` | float | 隐含波动率 |

### 使用示例

```python
from akshare_one import get_options_realtime

# 获取单个期权实时行情
df = get_options_realtime(symbol="10004005")
print(df)

# 获取300ETF所有期权实时行情
df_all = get_options_realtime(underlying_symbol="510300")
print(df_all.head())
```

---

## 获取期权到期日

`get_options_expirations()` 函数用于获取指定标的的可用期权到期日列表。

### 函数签名

```python
def get_options_expirations(
    underlying_symbol: str,
    source: str = "sina"
) -> list[str]
```

### 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `underlying_symbol` | str | 是 | - | 标的代码 |
| `source` | str | 否 | "sina" | 数据源 |

### 返回值

返回 `list[str]`，包含格式为 "YYYY-MM-DD" 的日期字符串列表。

### 使用示例

```python
from akshare_one import get_options_expirations

# 获取300ETF期权到期日
dates = get_options_expirations(underlying_symbol="510300")
print(dates)
# 输出示例: ['2024-02-28', '2024-03-27', ...]
```

---

## 获取期权历史数据

`get_options_hist()` 函数用于获取指定期权的历史行情数据。

### 函数签名

```python
def get_options_hist(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: str = "sina"
) -> pd.DataFrame
```

### 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `symbol` | str | 是 | - | 期权代码 |
| `start_date` | str | 否 | "1970-01-01" | 开始日期 (YYYY-MM-DD) |
| `end_date` | str | 否 | "2030-12-31" | 结束日期 (YYYY-MM-DD) |
| `source` | str | 否 | "sina" | 数据源 |

### 返回值

返回 `pandas.DataFrame`，包含以下列：

| 列名 | 类型 | 描述 |
|------|------|------|
| `timestamp` | datetime | 时间戳 |
| `symbol` | str | 期权代码 |
| `open` | float | 开盘价 |
| `high` | float | 最高价 |
| `low` | float | 最低价 |
| `close` | float | 收盘价 |
| `volume` | int | 成交量 |
| `open_interest` | int | 持仓量 |
| `settlement` | float | 结算价 |

### 使用示例

```python
from akshare_one import get_options_hist

# 获取期权历史数据
df = get_options_hist(
    symbol="10004005",
    start_date="2024-01-01",
    end_date="2024-02-01"
)
print(df.head())
```
