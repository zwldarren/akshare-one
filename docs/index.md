# AKShare One

<div align="center">
  <h2>中国金融市场数据的标准化接口</h2>
  <p>基于 AKShare 构建，提供统一的数据格式和简化的 API</p>
</div>

## ✨ 特性

- 📊 **统一的股票代码格式** - 跨数据源的一致性体验
- 🏗️ **标准化数据结构** - 统一的返回格式，便于数据处理
- 🛠️ **简化的 API 设计** - 减少参数复杂性，提高易用性
- 🔧 **丰富的技术指标** - 内置常用技术分析指标
- 🚀 **高性能缓存** - 利用缓存机制，提升数据获取效率

## 🚀 核心功能

| 功能模块 | 接口函数 | 描述 |
|---------|---------|------|
| 历史数据 | [`get_hist_data()`](api/historical.md) | 获取股票历史行情数据 |
| 实时数据 | [`get_realtime_data()`](api/realtime.md) | 获取股票实时行情数据 |
| 基础信息 | [`get_basic_info()`](api/basic-info.md) | 获取股票基础信息 |
| 新闻数据 | [`get_news_data()`](api/news.md) | 获取个股新闻数据 |
| 财务数据 | [`get_balance_sheet()`](api/financial.md#资产负债表) | 获取资产负债表数据 |
| 财务数据 | [`get_income_statement()`](api/financial.md#利润表) | 获取利润表数据 |
| 财务数据 | [`get_cash_flow()`](api/financial.md#现金流量表) | 获取现金流量表数据 |
| 财务数据 | [`get_financial_metrics()`](api/financial.md#财务关键指标) | 获取财务关键指标 |
| 内部交易 | [`get_inner_trade_data()`](api/insider.md) | 获取内部交易数据 |
| 技术指标 | [indicators 模块](api/indicators.md) | 丰富的技术分析指标 |

## 📦 安装

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

## 💻 快速开始

### 获取历史数据

```python
from akshare_one import get_hist_data

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
from akshare_one import get_realtime_data

# 获取单只股票实时数据
df = get_realtime_data(symbol="600000")
print(df)
```

### 计算技术指标

```python
from akshare_one import get_hist_data
from akshare_one.indicators import get_sma, get_macd

# 获取历史数据
df = get_hist_data(symbol="600000", interval="day")

# 计算20日简单移动平均
df_sma = get_sma(df, window=20)

# 计算MACD指标
df_macd = get_macd(df)
```

## 📚 文档导航

- **[快速开始](quickstart.md)** - 详细的安装和使用指南
- **[API 参考](api/overview.md)** - 完整的 API 文档
- **[示例代码](examples.md)** - 实用的代码示例

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进 AKShare One！

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](https://github.com/zwldarren/akshare-one/blob/main/LICENSE) 文件。

## 🔗 相关链接

- [GitHub 仓库](https://github.com/zwldarren/akshare-one)
- [PyPI 包](https://pypi.org/project/akshare-one/)
- [AKShare 原项目](https://github.com/akfamily/akshare)
- [AKShare One MCP](https://github.com/zwldarren/akshare-one-mcp)
