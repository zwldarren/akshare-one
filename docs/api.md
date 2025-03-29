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
