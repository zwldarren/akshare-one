# API 概览

AKShare One 提供了一套简洁统一的 API 接口，用于获取中国金融市场的各类数据。所有接口都经过精心设计，具有一致的参数格式和返回结构。

## 🏗️ 设计原则

### 统一的参数格式
- **symbol**: 股票代码，统一使用6位数字格式（如 "600000"）
- **source**: 数据源选择，支持多个数据提供商
- **时间参数**: 统一使用 ISO 格式日期字符串

### 标准化返回格式
所有接口返回 `pandas.DataFrame` 格式，包含：
- 统一的列名规范
- 一致的数据类型

## 📊 数据源支持

| 数据源 | 标识符 | 支持的接口 | 特点 |
|--------|--------|------------|------|
| 东方财富 | `eastmoney` | 历史数据、实时数据、基础信息、财务数据、新闻数据 | 调用AKShare，更新及时 |
| 东方财富直连 | `eastmoney_direct` | 历史数据、实时数据、财务数据 | 支持A股、B股、港股 |
| 新浪财经 | `sina` | 历史数据、财务数据 | 调用AKShare，更新及时 |
| 雪球 | `xueqiu` | 实时数据、内部交易 | 调用AKShare，更新及时 |

## 🔧 核心模块

### 历史数据模块
获取股票的历史行情数据，支持多种时间粒度和复权方式。

```python
from akshare_one import get_hist_data
```

### 实时数据模块
获取股票的实时行情数据，包括价格、成交量等信息。

```python
from akshare_one import get_realtime_data
```

### 基础信息模块
获取股票的基本信息，如公司名称、行业分类、上市时间等。

```python
from akshare_one import get_basic_info
```

### 新闻数据模块
获取与特定股票相关的新闻资讯。

```python
from akshare_one import get_news_data
```

### 财务数据模块
获取上市公司的财务报表数据，包括资产负债表、利润表、现金流量表等。

```python
from akshare_one import (
    get_balance_sheet,
    get_income_statement, 
    get_cash_flow,
    get_financial_metrics
)
```

### 内部交易模块
获取上市公司内部人员的交易数据。

```python
from akshare_one import get_inner_trade_data
```

### 技术指标模块
提供丰富的技术分析指标计算功能。

```python
from akshare_one.indicators import (
    get_sma, get_ema, get_rsi, get_macd, 
    get_bollinger_bands, get_stoch
)
```

## 🚀 快速导航

- **[历史数据](historical.md)** - 获取股票历史行情数据
- **[实时数据](realtime.md)** - 获取股票实时行情数据  
- **[基础信息](basic-info.md)** - 获取股票基础信息
- **[新闻数据](news.md)** - 获取个股新闻数据
- **[财务数据](financial.md)** - 获取财务报表数据
- **[内部交易](insider.md)** - 获取内部交易数据
- **[技术指标](indicators.md)** - 技术分析指标

## 💡 使用建议

- 合理设置时间范围，避免获取过多不必要的数据
- 利用内置缓存机制，避免重复请求相同数据
- 注意访问频率，避免触发接口限流机制
