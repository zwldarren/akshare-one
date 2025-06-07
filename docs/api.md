# Akshare One API 文档

## 核心接口

### `get_hist_data(symbol, interval, **kwargs)`

获取股票历史行情数据

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| symbol | str | 是 | - | 股票代码(如: "600000") |
| interval | str | 是 | - | 时间粒度('minute','hour','day','week','month','year') |
| interval_multiplier | int | 否 | 1 | 时间间隔倍数 |
| start_date | str | 否 | "1970-01-01" | 开始日期(YYYY-MM-DD) |
| end_date | str | 否 | "2030-12-31" | 结束日期(YYYY-MM-DD) |
| adjust | str | 否 | "none" | 复权类型("none","qfq","hfq") |
| source | str | 否 | "eastmoney" | 数据源("eastmoney","eastmoney_direct","sina") |

> 注意: 如果 `interval` 为 'minute'，则 `interval_multiplier` 表示分钟数，如 5 表示 5 分钟线

> eastmoney_direct 数据源支持港股，如 "00700" 表示腾讯控股。此外，小时和分钟级数据只支持当前交易日。

#### 返回值

返回标准化的DataFrame，包含以下列：

- timestamp: 时间戳(UTC时区)
- open: 开盘价
- high: 最高价
- low: 最低价
- close: 收盘价
- volume: 成交量

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

### `get_realtime_data(symbol=None)`

获取股票实时行情数据

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| source | str | 否 | "eastmoney" | 数据源("eastmoney", "eastmoney_direct", "xueqiu") |
| symbol | str | 否 | None | 股票代码(如: "600000")，不传则返回所有股票(注意: xueqiu源必须提供此参数) |

> eastmoney_direct 数据源支持港股，如 "00700" 表示腾讯控股。

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

### `get_news_data(symbol)`

获取个股新闻数据

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| symbol | str | 是 | - | 股票代码(如: "300059") |
| source | str | 否 | "eastmoney" | 数据源(目前仅支持"eastmoney") |

#### 返回值

返回标准化的DataFrame，包含以下列：

- keyword: 关键词
- title: 新闻标题
- content: 新闻内容
- publish_time: 发布时间(UTC时区)
- source: 文章来源
- url: 新闻链接

#### 示例

```python
from akshare_one import get_news_data

# 获取个股新闻数据
df = get_news_data(symbol="300059")
print(df[["title", "publish_time", "source"]].head())
```

### `get_balance_sheet(symbol)`

获取资产负债表数据

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| symbol | str | 是 | - | 股票代码(如: "600600") |
| source | str | 否 | "sina" | 数据源(目前支持"sina") |

#### 返回值

返回标准化的DataFrame，包含以下列：

- report_date: 报告日期
- currency: 币种
- total_assets: 资产总计
- current_assets: 流动资产合计
- cash_and_equivalents: 货币资金
- inventory: 存货
- current_investments: 交易性金融资产
- trade_and_non_trade_receivables: 应收票据及应收账款
- non_current_assets: 非流动资产合计
- goodwill_and_intangible_assets: 商誉
- investments: 长期股权投资
- non_current_investments: 其他非流动金融资产
- outstanding_shares: 实收资本(或股本)
- tax_assets: 递延所得税资产
- total_liabilities: 负债合计
- current_liabilities: 流动负债合计
- current_debt: 短期借款
- trade_and_non_trade_payables: 应付票据及应付账款
- deferred_revenue: 合同负债
- deposit_liabilities: 吸收存款及同业存放
- non_current_liabilities: 非流动负债合计
- non_current_debt: 长期借款
- tax_liabilities: 递延所得税负债
- shareholders_equity: 所有者权益(或股东权益)合计
- retained_earnings: 未分配利润
- accumulated_other_comprehensive_income: 其他综合收益
- total_debt: 总债务(短期借款+长期借款)

#### 示例

```python
from akshare_one import get_balance_sheet

# 获取资产负债表数据
df = get_balance_sheet(symbol="600600")
print(df[["report_date", "total_assets", "total_liabilities"]].head())
```

### `get_income_statement(symbol)`

获取利润表数据

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| symbol | str | 是 | - | 股票代码(如: "600600") |
| source | str | 否 | "sina" | 数据源(目前支持"sina") |

#### 返回值

返回标准化的DataFrame，包含以下列：

- report_date: 报告日期
- currency: 币种
- revenue: 营业总收入
- cost_of_revenue: 营业成本
- operating_profit: 营业利润
- operating_expense: 管理费用
- selling_general_and_administrative_expenses: 销售费用
- research_and_development: 研发费用
- interest_expense: 利息支出
- ebit: 利润总额
- income_tax_expense: 所得税费用
- net_income: 净利润
- net_income_common_stock: 归属于母公司所有者的净利润
- net_income_non_controlling_interests: 少数股东损益
- earnings_per_share: 基本每股收益
- earnings_per_share_diluted: 稀释每股收益

#### 示例

```python
from akshare_one import get_income_statement

# 获取利润表数据
df = get_income_statement(symbol="600600")
print(df[["report_date", "revenue", "net_income"]].head())
```

### `get_cash_flow(symbol)`

获取现金流量表数据

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| symbol | str | 是 | - | 股票代码(如: "600600") |
| source | str | 否 | "sina" | 数据源(目前支持"sina") |

#### 返回值

返回标准化的DataFrame，包含以下列：

- report_date: 报告日期
- report_type: 报告类型
- currency: 币种
- net_cash_flow_from_operations: 经营活动产生的现金流量净额
- business_acquisitions_and_disposals: 取得子公司及其他营业单位支付的现金净额
- net_cash_flow_from_investing: 投资活动产生的现金流量净额
- issuance_or_repayment_of_debt_securities: 取得借款收到的现金
- issuance_or_purchase_of_equity_shares: 吸收投资收到的现金
- net_cash_flow_from_financing: 筹资活动产生的现金流量净额
- change_in_cash_and_equivalents: 现金及现金等价物净增加额
- effect_of_exchange_rate_changes: 汇率变动对现金及现金等价物的影响
- ending_cash_balance: 期末现金及现金等价物余额

#### 示例

```python
from akshare_one import get_cash_flow

# 获取现金流量表数据
df = get_cash_flow(symbol="600600")
print(df[["report_date", "net_cash_flow_from_operations", "free_cash_flow"]].head())
```

### `get_inner_trade_data()`

获取雪球内部交易数据

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| symbol | str | 是 | - | 股票代码(如: "600000") |
| source | str | 否 | "xueqiu" | 数据源(目前支持"xueqiu") |

#### 返回值

返回标准化的DataFrame，包含以下列：

- symbol: 股票代码
- issuer: 股票名称
- name: 变动人
- title: 董监高职务
- transaction_date: 变动日期(UTC时区)
- transaction_shares: 变动股数
- transaction_price_per_share: 成交均价
- shares_owned_after_transaction: 变动后持股数
- relationship: 与董监高关系
- is_board_director: 是否为董事会成员
- transaction_value: 交易金额(变动股数*成交均价)
- shares_owned_before_transaction: 变动前持股数

#### 示例

```python
from akshare_one import get_inner_trade_data

# 获取指定股票内部交易数据
df = get_inner_trade_data(symbol="600000")
print(df[["symbol", "name", "transaction_date", "transaction_value"]].head())
```
