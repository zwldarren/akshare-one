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
| 期货数据 | `get_futures_hist_data`/`get_futures_realtime_data` |
| 期权数据 | `get_options_chain`/`get_options_realtime`/`get_options_hist` |
| 内部交易 | `get_inner_trade_data` |
| 股票基本信息 | `get_basic_info` |
| 财务指标 | `get_financial_metrics` |
| 技术指标 | 参见 [indicators.py](src/akshare_one/indicators.py) |

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

完整API文档现已迁移至GitHub Pages：

https://zwldarren.github.io/akshare-one/

## 🧪 测试

默认情况下测试完全离线运行。会访问在线数据源（东方财富、新浪、雪球、各交易所）
的测试模块默认跳过，因为这些接口有严格的速率限制，全量运行可能导致 IP 被临时封禁：

```bash
pytest                    # 仅离线单元测试
pytest --run-network      # 包含在线数据源测试
```

## 🧩 公开接口

对外公开的接口只有 `akshare_one` 与 `akshare_one.indicators`。
`akshare_one.modules` 下的内容属于内部实现，可能不经过弃用流程直接变更。

每个领域的输出列只在 `akshare_one.modules.<domain>.schema` 中声明一次。所有
数据源返回的 DataFrame 都会投影到这些列上，因此文档中承诺的列始终存在
——数据源无法提供时为 `NaN`——且顺序与文档一致。

## ⚠️ 数据源说明

- 实时行情与基本信息会在多个东方财富域名间自动重试，因为
  `push2.eastmoney.com` 会间歇性返回 `502`（境外访问时尤其明显）。
- `xueqiu` 实时行情依赖 `xq_a_token` Cookie，而雪球已不再向匿名客户端下发该
  Cookie；触发限流时雪球会返回 `418`。
- `get_options_chain` 只返回期权合约列表，行情字段为空；请使用
  `get_options_realtime` / `get_options_hist` 获取价格。
- `get_futures_main_contracts()` 基于各交易所静态快照，首次调用可能较慢
  （中金所）；结果会缓存 24 小时。
