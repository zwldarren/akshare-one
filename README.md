<div align="center">
  <h1>AKShare One</h1>
  <div>
    <a href="README_zh.md">中文</a> | <strong>English</strong>
  </div>
</div>

**AKShare One** is a data interface for obtaining Chinese A-shares, based on [AKShare](https://github.com/akfamily/akshare). It aims to simplify AKShare's usage and unify input/output formats from different data sources, making it easier to pass data to LLM.

## ✨ Features

- 📊 Unified stock code formats across data sources
- 🏗️ Standardized return data structures
- 🛠️ Simplified API parameter design
- ⏱️ Automatic timestamp and adjustment handling

## 🚀 Core Features

| Function | Interface |
|------|------|
| Historical data | `get_hist_data` |
| Real-time quotes | `get_realtime_data` |
| Stock news | `get_news_data` |
| Financial data | `get_balance_sheet`/`get_income_statement`/`get_cash_flow` |
| Internal transactions | `get_inner_trade_data` |
| Basic stock info | `get_basic_info` |
| Financial metrics | `get_financial_metrics` |
| Technical indicators | See [indicators.py](akshare-one/indicators.py) |

## 📦 Quick Installation

```bash
pip install akshare-one
```

## 💻 Usage Example

```python
from akshare_one import get_hist_data
from akshare_one.indicators import get_sma

# Get historical data
df = get_hist_data(
    symbol="600000",
    interval="day",
    adjust="hfq"
)

# Calculate 20-day Simple Moving Average
df_sma = get_sma(df, window=20)
```

## 📚 Documentation

Full API documentation is now available on GitHub Pages:

https://zwldarren.github.io/akshare-one/
