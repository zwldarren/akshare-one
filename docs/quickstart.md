# 快速开始

本指南将帮助您快速安装和使用 AKShare One。

## 安装

### 基础安装
```bash
pip install akshare-one
```

### 完整安装（包含 TA-Lib 技术指标）
```bash
pip install akshare-one[talib]
```

!!! note "TA-Lib 安装说明"
    如需使用 TA-Lib 计算器，请先安装 TA-Lib 库。详细安装说明请参考 [TA-Lib 官方文档](https://ta-lib.org/install/)。

## 基本用法

### 导入模块
```python
from akshare_one import (
    get_hist_data,
    get_realtime_data,
    get_basic_info,
    get_news_data,
    get_balance_sheet,
    get_income_statement,
    get_cash_flow,
    get_financial_metrics,
    get_inner_trade_data
)

from akshare_one.indicators import (
    get_sma, get_ema, get_rsi, get_macd, get_bollinger_bands
)
```

### 获取历史数据
```python
# 获取浦发银行前复权日线数据
df = get_hist_data(
    symbol="600000",
    interval="day",
    adjust="qfq",
    start_date="2024-01-01",
    end_date="2024-03-31"
)
print(df.head())
```

### 获取实时数据
```python
# 获取单只股票实时数据
df = get_realtime_data(symbol="600000")
print(df)
```

### 获取财务数据
```python
# 获取资产负债表
balance_sheet = get_balance_sheet(symbol="600000")

# 获取利润表
income_statement = get_income_statement(symbol="600000")

# 获取现金流量表
cash_flow = get_cash_flow(symbol="600000")
```

### 计算技术指标
```python
# 计算20日简单移动平均
df_sma = get_sma(df, window=20)

# 计算MACD指标
df_macd = get_macd(df)
```

## 配置选项

### 设置缓存
AKShare One 默认启用缓存，您可以通过环境变量配置缓存行为：

```python
import os

# 禁用缓存
os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "False"
```

## 下一步
- 查看完整的 [API 参考](api/overview.md)
- 学习 [示例代码](examples.md)
