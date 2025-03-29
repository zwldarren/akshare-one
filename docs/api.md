# Akshare One API 文档

## 核心接口

### `get_hist_data(symbol, interval, **kwargs)`

获取股票历史行情数据

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| symbol | str | 是 | - | 股票代码(如: "600000") |
| interval | str | 是 | - | 时间粒度("day","week","month") |
| interval_multiplier | int | 否 | 1 | 时间间隔乘数 |
| start_date | str | 否 | "1970-01-01" | 开始日期(YYYY-MM-DD) |
| end_date | str | 否 | "2030-12-31" | 结束日期(YYYY-MM-DD) |
| adjust | str | 否 | "none" | 复权类型("none","qfq","hfq") |
| source | str | 否 | "eastmoney" | 数据源(目前仅支持"eastmoney") |

#### 返回值

返回标准化的DataFrame，包含以下列：

- timestamp: 时间戳(UTC时区)
- open: 开盘价
- high: 最高价
- low: 最低价
- close: 收盘价
- volume: 成交量
- is_adjusted: 是否复权

#### 示例

```python
from akshare_one import get_hist_data

# 获取前复权日线数据
df = get_hist_data(
    symbol="600000",
    interval="day",
    adjust="qfq",
    start_date="2024-01-01",
    end_date="2024-03-31"
)
```

### `get_realtime_data(source="eastmoney", symbol=None)`

获取股票实时行情数据

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| source | str | 否 | "eastmoney" | 数据源(目前仅支持"eastmoney") |
| symbol | str | 否 | None | 股票代码(如: "600000")，不传则返回所有股票 |

#### 返回值

返回标准化的DataFrame，包含以下列：

- symbol: 股票代码
- price: 最新价
- change: 涨跌额
- pct_change: 涨跌幅(%)
- timestamp: 时间戳(UTC时区)
- volume: 成交量(手)
- amount: 成交额(元)
- open: 今开
- high: 最高
- low: 最低
- prev_close: 昨收

#### 示例

```python
from akshare_one import get_realtime_data

# 获取所有股票实时数据
df_all = get_realtime_data()

# 获取单只股票实时数据
df_single = get_realtime_data(symbol="600000")
```
