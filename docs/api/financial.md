# 财务数据

AKShare One 提供多个函数用于获取上市公司财务数据：

1. `get_balance_sheet()` - 获取资产负债表
2. `get_income_statement()` - 获取利润表
3. `get_cash_flow()` - 获取现金流量表
4. `get_financial_metrics()` - 获取财务关键指标

## 通用参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `symbol` | str | 是 | - | 股票代码(如: "600000") |
| `source` | str | 否 | "sina" | 数据源("sina", "eastmoney_direct") |

## 资产负债表 { #资产负债表 }

### 函数签名
```python
def get_balance_sheet(symbol: str, source: Literal["sina"] = "sina") -> pd.DataFrame
```

### 返回值字段
| 字段名 | 描述 |
|--------|------|
| `report_date` | 报告日期 |
| `currency` | 币种 |
| `total_assets` | 资产总计 |
| `current_assets` | 流动资产合计 |
| `cash_and_equivalents` | 货币资金 |
| `inventory` | 存货 |
| `current_investments` | 交易性金融资产 |
| `trade_and_non_trade_receivables` | 应收票据及应收账款 |
| `non_current_assets` | 非流动资产合计 |
| `property_plant_and_equipment` | 固定资产 |
| `goodwill_and_intangible_assets` | 商誉 |
| `investments` | 长期股权投资 |
| `non_current_investments` | 其他非流动金融资产 |
| `outstanding_shares` | 实收资本(或股本) |
| `tax_assets` | 递延所得税资产 |
| `total_liabilities` | 负债合计 |
| `current_liabilities` | 流动负债合计 |
| `current_debt` | 短期借款 |
| `trade_and_non_trade_payables` | 应付票据及应付账款 |
| `deferred_revenue` | 合同负债 |
| `deposit_liabilities` | 吸收存款及同业存放 |
| `non_current_liabilities` | 非流动负债合计 |
| `non_current_debt` | 长期借款 |
| `tax_liabilities` | 递延所得税负债 |
| `shareholders_equity` | 所有者权益(或股东权益)合计 |
| `retained_earnings` | 未分配利润 |
| `accumulated_other_comprehensive_income` | 其他综合收益 |
| `accounts_receivable` | 应收账款 |
| `prepayments` | 预付款项 |
| `other_receivables` | 其他应收款 |
| `fixed_assets_net` | 固定资产净值 |
| `construction_in_progress` | 在建工程 |
| `capital_reserve` | 资本公积 |
| `current_ratio` | 流动比率 |
| `debt_to_assets` | 资产负债率 |
| `minority_interest` | 少数股东权益 |

## 利润表 { #利润表 }

### 函数签名
```python
def get_income_statement(symbol: str, source: Literal["sina"] = "sina") -> pd.DataFrame
```

### 返回值字段
| 字段名 | 描述 |
|--------|------|
| `report_date` | 报告日期 |
| `currency` | 币种 |
| `revenue` | 营业总收入 |
| `operating_revenue` | 营业收入 |
| `total_operating_costs` | 营业总成本 |
| `cost_of_revenue` | 营业成本 |
| `operating_profit` | 营业利润 |
| `selling_general_and_administrative_expenses` | 销售费用 |
| `operating_expense` | 管理费用 |
| `research_and_development` | 研发费用 |
| `interest_expense` | 利息支出 |
| `ebit` | 利润总额 |
| `income_tax_expense` | 所得税费用 |
| `net_income` | 净利润 |
| `net_income_common_stock` | 归属于母公司所有者的净利润 |
| `net_income_non_controlling_interests` | 少数股东损益 |
| `earnings_per_share` | 基本每股收益 |
| `earnings_per_share_diluted` | 稀释每股收益 |
| `investment_income` | 投资收益 |
| `fair_value_adjustments` | 公允价值变动收益 |
| `asset_impairment_loss` | 资产减值损失 |
| `financial_expenses` | 财务费用 |
| `taxes_and_surcharges` | 营业税金及附加 |
| `other_comprehensive_income` | 其他综合收益 |
| `total_comprehensive_income` | 综合收益总额 |

## 现金流量表 { #现金流量表 }

### 函数签名
```python
def get_cash_flow(symbol: str, source: Literal["sina"] = "sina") -> pd.DataFrame
```

### 返回值字段
| 字段名 | 描述 |
|--------|------|
| `report_date` | 报告日期 |
| `currency` | 币种 |
| `net_cash_flow_from_operations` | 经营活动产生的现金流量净额 |
| `capital_expenditure` | 购建固定资产、无形资产和其他长期资产支付的现金 |
| `business_acquisitions_and_disposals` | 取得子公司及其他营业单位支付的现金净额 |
| `net_cash_flow_from_investing` | 投资活动产生的现金流量净额 |
| `issuance_or_repayment_of_debt_securities` | 取得借款收到的现金 |
| `issuance_or_purchase_of_equity_shares` | 吸收投资收到的现金 |
| `net_cash_flow_from_financing` | 筹资活动产生的现金流量净额 |
| `change_in_cash_and_equivalents` | 现金及现金等价物净增加额 |
| `effect_of_exchange_rate_changes` | 汇率变动对现金及现金等价物的影响 |
| `ending_cash_balance` | 期末现金及现金等价物余额 |
| `cash_from_sales` | 销售商品、提供劳务收到的现金 |
| `tax_refunds_received` | 收到的税费返还 |
| `cash_paid_to_employees` | 支付给职工以及为职工支付的现金 |
| `taxes_paid` | 支付的各项税费 |
| `total_cash_inflow_from_operations` | 经营活动现金流入小计 |
| `total_cash_outflow_from_operations` | 经营活动现金流出小计 |
| `cash_from_investment_recovery` | 收回投资所收到的现金 |
| `cash_from_investment_income` | 取得投资收益收到的现金 |
| `cash_from_asset_sales` | 处置固定资产、无形资产收回的现金 |
| `total_cash_inflow_from_investing` | 投资活动现金流入小计 |
| `total_cash_outflow_from_investing` | 投资活动现金流出小计 |
| `cash_paid_for_dividends_and_interest` | 分配股利、利润或偿付利息所支付的现金 |
| `cash_paid_for_debt_repayment` | 偿还债务支付的现金 |
| `total_cash_inflow_from_financing` | 筹资活动现金流入小计 |
| `total_cash_outflow_from_financing` | 筹资活动现金流出小计 |
| `beginning_cash_balance` | 期初现金及现金等价物余额 |
| `ending_cash` | 现金的期末余额 |
| `ending_cash_equivalents` | 现金等价物的期末余额 |

## 财务关键指标 { #财务关键指标 }

### 函数签名
```python
def get_financial_metrics(symbol: str, source: Literal["eastmoney_direct"] = "eastmoney_direct") -> pd.DataFrame
```

### 返回值字段
| 字段名 | 描述 |
|--------|------|
| `report_date` | 报告日期 |
| `total_assets` | 资产总计 |
| `fixed_assets_net` | 固定资产净值 |
| `cash_and_equivalents` | 货币资金 |
| `accounts_receivable` | 应收账款 |
| `inventory` | 存货 |
| `trade_and_non_trade_payables` | 应付票据及应付账款 |
| `deferred_revenue` | 合同负债 |
| `total_liabilities` | 负债合计 |
| `shareholders_equity` | 所有者权益 |
| `revenue` | 营业总收入 |
| `total_operating_costs` | 营业总成本 |
| `operating_profit` | 营业利润 |
| `net_income_common_stock` | 归属于母公司所有者的净利润 |
| `net_cash_flow_from_operations` | 经营活动产生的现金流量净额 |
| `net_cash_flow_from_investing` | 投资活动产生的现金流量净额 |
| `net_cash_flow_from_financing` | 筹资活动产生的现金流量净额 |
| `change_in_cash_and_equivalents` | 现金及现金等价物净增加额 |

## 使用示例

### 获取资产负债表

```python
from akshare_one import get_balance_sheet

# 获取浦发银行资产负债表
df = get_balance_sheet(symbol="600000")
print(df[["report_date", "total_assets", "total_liabilities", "shareholders_equity"]])
```

### 获取利润表

```python
from akshare_one import get_income_statement

# 获取浦发银行利润表
df = get_income_statement(symbol="600000")
print(df[["report_date", "revenue", "net_income_common_stock"]])
```

### 获取现金流量表

```python
from akshare_one import get_cash_flow

# 获取浦发银行现金流量表
df = get_cash_flow(symbol="600000")
print(df[["report_date", "net_cash_flow_from_operations"]])
```

### 获取财务关键指标

```python
from akshare_one import get_financial_metrics

# 获取浦发银行财务关键指标
df_metrics = get_financial_metrics(symbol="600000")
print(df_metrics.head())
```
