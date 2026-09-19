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
| Futures data | `get_futures_hist_data`/`get_futures_realtime_data` |
| Options data | `get_options_chain`/`get_options_realtime`/`get_options_hist` |
| Internal transactions | `get_inner_trade_data` |
| Basic stock info | `get_basic_info` |
| Financial metrics | `get_financial_metrics` |
| Technical indicators | See [indicators.py](src/akshare_one/indicators.py) |

## 📦 Quick Installation

```bash
pip install akshare-one
```

## 💻 Usage Example

```python
from akshare_one import get_hist_data
from akshare_one.indicators import get_sma

# Get historical data
df = get_hist_data(symbol="600000", interval="day", adjust="hfq")

# Calculate 20-day Simple Moving Average
df_sma = get_sma(df, window=20)
```

## 📚 Documentation

Full API documentation is now available on GitHub Pages:

https://zwldarren.github.io/akshare-one/

## 🧪 Testing

Tests run fully offline by default. Test modules that call live upstream data
providers (EastMoney, Sina, XueQiu, the exchanges) are skipped unless you opt
in, because those endpoints apply aggressive rate limits and a full run can get
your IP temporarily blocked:

```bash
pytest                    # offline unit tests only
pytest --run-network      # include live-provider tests
```

## 🧩 Public interface

The public surface is `akshare_one` and `akshare_one.indicators`. Everything
under `akshare_one.modules` is internal and may change without a deprecation
cycle.

Each domain's output columns are declared in exactly one place,
`akshare_one.modules.<domain>.schema`. Every provider's frame is projected onto
those columns, so a documented column is always present — `NaN` when the
selected source cannot supply it — and always in the documented order.

## ⚠️ Data source notes

- Realtime quotes and basic info fall back across several EastMoney hosts,
  because `push2.eastmoney.com` intermittently returns `502` (notably from
  outside mainland China).
- `xueqiu` realtime quotes need an `xq_a_token` cookie that XueQiu no longer
  hands to anonymous clients, and XueQiu returns `418` once rate-limited.
- `get_options_chain` returns the option contract list with the market-data
  columns left empty; use `get_options_realtime` / `get_options_hist` for
  prices.
- `get_futures_main_contracts()` reflects static exchange snapshots and may be
  slow on the first call (CFFEX); the result is cached for 24 hours.
