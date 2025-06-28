<div align="center">
  <h1>AKShare One</h1>
  <div>
    <a href="README.md">English</a> | <strong>中文</strong>
  </div>
</div>

**AKShare One** 是用于获取中国A股的数据接口，基于 [AKShare](https://github.com/akfamily/akshare) 开发，目的是简化AKShare的调用，并且统一不同数据源的输入输出格式，使得数据可以更加方便的传递给大语言模型。

## ✨ 项目特色

- 📊 统一不同数据源的股票代码格式
- 🏗️ 标准化返回数据结构
- 🛠️ 简化API参数设计
- ⏱️ 自动处理时间戳和复权数据

## 🚀 核心功能

| 功能 | 接口 |
|------|------|
| 历史数据 | `get_hist_data` |
| 实时行情 | `get_realtime_data` |
| 个股新闻 | `get_news_data` |
| 财务数据 | `get_balance_sheet`/`get_income_statement`/`get_cash_flow` |
| 内部交易 | `get_inner_trade_data` |
| 技术指标 | `get_sma`/`get_ema`/`get_rsi`/`get_macd` |

## 📦 快速安装

```bash
pip install akshare-one
```

## 💻 使用示例

```python
from akshare_one import get_hist_data
from akshare_one.indicators import get_sma

# 获取历史数据
df = get_hist_data(
    symbol="600000",
    interval="day",
    adjust="hfq"
)

# 计算20日简单移动平均
df_sma = get_sma(df, window=20)
```

## 📚 文档

详细API说明请参考 [docs/api.md](docs/api.md)
