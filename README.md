<div align="center">
  <h1>AKShare One</h1>
  <div>
    <strong>English</strong> | <a href="README_zh.md">中文</a>
  </div>
</div>

**AKShare One** is a standardized interface for Chinese financial market data, built as a wrapper around [AKShare](https://github.com/akfamily/akshare) to solve inconsistencies in input/output formats across different data sources.

## ✨ Features

- 📊 Unified stock code formats across data sources
- 🏗️ Standardized return data structures
- 🛠️ Simplified API parameters
- ⏱️ Automatic timestamp and adjustment handling

## 🚀 Core Features

| Feature | Interface |
|---------|-----------|
| Historical data | `get_hist_data` |
| Real-time quotes | `get_realtime_data` |
| Stock news | `get_news_data` |
| Financial data | `get_balance_sheet`/`get_income_statement`/`get_cash_flow` |
| Insider trading | `get_inner_trade_data` |

## 📦 Quick Installation

```bash
pip install akshare-one
```

## 💻 Usage Example

```python
from akshare_one import get_hist_data, get_realtime_data

# Get historical data
df_hist = get_hist_data(
    symbol="600000",
    interval="day",
    adjust="hfq"
)

# Get real-time data
df_realtime = get_realtime_data(symbol="600000")
```

## 📚 Documentation

Detailed API reference: [docs/api.md](docs/api.md)
