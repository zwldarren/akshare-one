# Akshare One API 文档

## 目录

- [核心接口](#核心接口)
  - [`get_hist_data(symbol, **kwargs)`](#get_hist_datasymbol-kwargs)
  - [`get_realtime_data(symbol=None)`](#get_realtime_datasymbolnone)
  - [`get_info(symbol)`](#get_infosymbol)
  - [`get_news_data(symbol)`](#get_news_datasymbol)
  - [`get_balance_sheet(symbol)`](#get_balance_sheetsymbol)
  - [`get_income_statement(symbol)`](#get_income_statementsymbol)
  - [`get_cash_flow(symbol)`](#get_cash_flowsymbol)
  - [`get_inner_trade_data()`](#get_inner_trade_data)
- [技术指标](#技术指标)

# Akshare One API 文档

## 核心接口

### `get_hist_data(symbol, **kwargs)`

获取股票历史行情数据

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| symbol | str | 是 | - | 股票代码(如: "600000") |
| interval | str | 否 | "day" | 时间粒度('minute','hour','day','week','month','year') |
| interval_multiplier | int | 否 | 1 | 时间间隔倍数 |
| start_date | str | 否 | "1970-01-01" | 开始日期(YYYY-MM-DD) |
| end_date | str | 否 | "2030-12-31" | 结束日期(YYYY-MM-DD) |
| adjust | str | 否 | "none" | 复权类型("none","qfq","hfq") |
| source | str | 否 | "eastmoney" | 数据源("eastmoney","eastmoney_direct","sina") |

> 注意: 如果 `interval` 为 'minute'，则 `interval_multiplier` 表示分钟数，如 5 表示 5 分钟线

> eastmoney_direct 数据源支持港股，如 "00700" 表示腾讯控股。此外，小时和分钟级数据只支持当前交易日。

#### 返回值

pd.DataFrame:

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
| symbol | str | 否 | None | 股票代码(如: "600000")，不传则返回所有股票(注意: xueqiu源必须提供此参数) |
| source | str | 否 | "xueqiu" | 数据源("eastmoney", "eastmoney_direct", "xueqiu") |

> eastmoney_direct 数据源支持港股，如 "00700" 表示腾讯控股。

#### 返回值

pd.DataFrame:

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

### `get_info(symbol)`

获取股票基础信息

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| symbol | str | 是 | - | 股票代码(如: "600000") |
| source | str | 否 | "eastmoney" | 数据源(目前仅支持"eastmoney") |

#### 返回值

pd.DataFrame:

- price: 最新价
- symbol: 股票代码
- name: 股票简称
- total_shares: 总股本
- float_shares: 流通股
- total_market_cap: 总市值
- float_market_cap: 流通市值
- industry: 行业
- listing_date: 上市时间

#### 示例

```python
from akshare_one import get_info

# 获取股票基础信息
df = get_info(symbol="600405")
print(df)
```

### `get_news_data(symbol)`

获取个股新闻数据

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| symbol | str | 是 | - | 股票代码(如: "300059") |
| source | str | 否 | "eastmoney" | 数据源(目前仅支持"eastmoney") |

#### 返回值

pd.DataFrame:

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

pd.DataFrame:

- report_date: 报告日期
- currency: 币种
- total_assets: 资产总计
- current_assets: 流动资产合计
- cash_and_equivalents: 货币资金
- inventory: 存货
- current_investments: 交易性金融资产
- trade_and_non_trade_receivables: 应收票据及应收账款
- accounts_receivable: 应收账款
- prepayments: 预付款项
- other_receivables: 其他应收款
- non_current_assets: 非流动资产合计
- property_plant_and_equipment: 固定资产
- fixed_assets_net: 固定资产净值
- construction_in_progress: 在建工程
- goodwill_and_intangible_assets: 商誉
- investments: 长期股权投资
- non_current_investments: 其他非流动金融资产
- outstanding_shares: 实收资本(或股本)
- capital_reserve: 资本公积
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
- current_ratio: 流动比率
- debt_to_assets: 资产负债率

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

pd.DataFrame:

- report_date: 报告日期
- currency: 币种
- revenue: 营业总收入
- operating_revenue: 营业收入
- total_operating_costs: 营业总成本
- cost_of_revenue: 营业成本
- operating_profit: 营业利润
- selling_general_and_administrative_expenses: 销售费用
- operating_expense: 管理费用
- research_and_development: 研发费用
- interest_expense: 利息支出
- ebit: 利润总额
- income_tax_expense: 所得税费用
- net_income: 净利润
- net_income_common_stock: 归属于母公司所有者的净利润
- net_income_non_controlling_interests: 少数股东损益
- earnings_per_share: 基本每股收益
- earnings_per_share_diluted: 稀释每股收益
- investment_income: 投资收益
- fair_value_adjustments: 公允价值变动收益
- asset_impairment_loss: 资产减值损失
- financial_expenses: 财务费用
- taxes_and_surcharges: 营业税金及附加
- other_comprehensive_income: 其他综合收益
- total_comprehensive_income: 综合收益总额

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

pd.DataFrame:

- report_date: 报告日期
- currency: 币种
- net_cash_flow_from_operations: 经营活动产生的现金流量净额
- cash_from_sales: 销售商品、提供劳务收到的现金
- tax_refunds_received: 收到的税费返还
- cash_paid_to_employees: 支付给职工以及为职工支付的现金
- taxes_paid: 支付的各项税费
- total_cash_inflow_from_operations: 经营活动现金流入小计
- total_cash_outflow_from_operations: 经营活动现金流出小计
- capital_expenditure: 购建固定资产、无形资产和其他长期资产支付的现金
- cash_from_investment_recovery: 收回投资所收到的现金
- cash_from_investment_income: 取得投资收益收到的现金
- cash_from_asset_sales: 处置固定资产、无形资产收回的现金
- business_acquisitions_and_disposals: 取得子公司及其他营业单位支付的现金净额
- total_cash_inflow_from_investing: 投资活动现金流入小计
- total_cash_outflow_from_investing: 投资活动现金流出小计
- net_cash_flow_from_investing: 投资活动产生的现金流量净额
- issuance_or_repayment_of_debt_securities: 取得借款收到的现金
- issuance_or_purchase_of_equity_shares: 吸收投资收到的现金
- cash_paid_for_dividends_and_interest: 分配股利、利润或偿付利息所支付的现金
- cash_paid_for_debt_repayment: 偿还债务支付的现金
- total_cash_inflow_from_financing: 筹资活动现金流入小计
- total_cash_outflow_from_financing: 筹资活动现金流出小计
- net_cash_flow_from_financing: 筹资活动产生的现金流量净额
- change_in_cash_and_equivalents: 现金及现金等价物净增加额
- effect_of_exchange_rate_changes: 汇率变动对现金及现金等价物的影响
- beginning_cash_balance: 期初现金及现金等价物余额
- ending_cash_balance: 期末现金及现金等价物余额
- ending_cash: 现金的期末余额
- ending_cash_equivalents: 现金等价物的期末余额

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

pd.DataFrame:

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

## 技术指标

技术指标模块提供常见的技术分析指标计算功能，需要通过`akshare_one.indicators`模块调用：

```python
from akshare_one.indicators import (
    get_sma, get_ema, get_rsi, get_macd, get_bollinger_bands, get_stoch, get_atr,
    get_cci, get_adx, get_willr, get_ad, get_adosc, get_obv, get_mom, get_sar,
    get_tsf, get_apo, get_aroon, get_aroonosc, get_bop, get_cmo, get_dx, get_mfi,
    get_minus_di, get_minus_dm, get_plus_di, get_plus_dm, get_ppo, get_roc,
    get_rocp, get_rocr, get_rocr100, get_trix, get_ultosc
)
```

> Note: 所有技术指标计算函数都支持`talib`和`simple`两种计算方式，`talib`需要额外安装[TA-Lib](https://ta-lib.org/install/)依赖并使用`pip install akshare-one[talib]`安装。

- **简单移动平均线(SMA)**: `get_sma(df, window=20, calculator_type="talib")`
- **指数移动平均线(EMA)**: `get_ema(df, window=20, calculator_type="talib")`
- **相对强弱指数(RSI)**: `get_rsi(df, window=14, calculator_type="talib")`
- **移动平均收敛发散指标(MACD)**: `get_macd(df, fast=12, slow=26, signal=9, calculator_type="talib")`
- **布林带(Bollinger Bands)**: `get_bollinger_bands(df, window=20, std=2, calculator_type="talib")`
- **随机指标(Stochastic Oscillator)**: `get_stoch(df, window=14, smooth_d=3, smooth_k=3, calculator_type="talib")`
- **平均真实波幅(ATR)**: `get_atr(df, window=14, calculator_type="talib")`
- **商品通道指数(CCI)**: `get_cci(df, window=14, calculator_type="talib")`
- **平均方向性指标(ADX)**: `get_adx(df, window=14, calculator_type="talib")`
- **威廉指标(Williams' %R)**: `get_willr(df, window=14, calculator_type="talib")`
- **蔡金A/D线(Chaikin A/D Line)**: `get_ad(df, calculator_type="talib")`
- **蔡金A/D振荡器(Chaikin A/D Oscillator)**: `get_adosc(df, fast_period=3, slow_period=10, calculator_type="talib")`
- **能量潮(On Balance Volume)**: `get_obv(df, calculator_type="talib")`
- **动量指标(Momentum)**: `get_mom(df, window=10, calculator_type="talib")`
- **抛物线转向指标(Parabolic SAR)**: `get_sar(df, acceleration=0.02, maximum=0.2, calculator_type="talib")`
- **时间序列预测(Time Series Forecast)**: `get_tsf(df, window=14, calculator_type="talib")`
- **绝对价格振荡器(Absolute Price Oscillator)**: `get_apo(df, fast_period=12, slow_period=26, ma_type=0, calculator_type="talib")`
- **阿隆指标(Aroon)**: `get_aroon(df, window=14, calculator_type="talib")`
- **阿隆振荡器(Aroon Oscillator)**: `get_aroonosc(df, window=14, calculator_type="talib")`
- **均势指标(Balance of Power)**: `get_bop(df, calculator_type="talib")`
- **钱德动量振荡器(Chande Momentum Oscillator)**: `get_cmo(df, window=14, calculator_type="talib")`
- **动向指标(Directional Movement Index)**: `get_dx(df, window=14, calculator_type="talib")`
- **资金流量指标(Money Flow Index)**: `get_mfi(df, window=14, calculator_type="talib")`
- **负方向指标(-DI)**: `get_minus_di(df, window=14, calculator_type="talib")`
- **负方向运动(-DM)**: `get_minus_dm(df, window=14, calculator_type="talib")`
- **正方向指标(+DI)**: `get_plus_di(df, window=14, calculator_type="talib")`
- **正方向运动(+DM)**: `get_plus_dm(df, window=14, calculator_type="talib")`
- **价格振荡器百分比(Percentage Price Oscillator)**: `get_ppo(df, fast_period=12, slow_period=26, ma_type=0, calculator_type="talib")`
- **变动率(Rate of change)**: `get_roc(df, window=10, calculator_type="talib")`
- **变动率百分比(Rate of change Percentage)**: `get_rocp(df, window=10, calculator_type="talib")`
- **变动率比率(Rate of change ratio)**: `get_rocr(df, window=10, calculator_type="talib")`
- **变动率比率100刻度(Rate of change ratio 100 scale)**: `get_rocr100(df, window=10, calculator_type="talib")`
- **三重指数平滑平均线的1日变动率(TRIX)**: `get_trix(df, window=30, calculator_type="talib")`
- **终极振荡器(Ultimate Oscillator)**: `get_ultosc(df, window1=7, window2=14, window3=28, calculator_type="talib")`

#### 示例

```python
from akshare_one.indicators import get_sma, get_macd

# 计算20日简单移动平均
df_sma = get_sma(df, window=20)

# 计算MACD指标
df_macd = get_macd(df)
```
