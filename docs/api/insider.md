# 内部交易

`get_inner_trade_data()` 函数用于获取雪球内部交易数据。

## 函数签名

```python
def get_inner_trade_data(symbol, **kwargs) -> pd.DataFrame
```

## 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `symbol` | str | 是 | - | 股票代码(如: "600000") |
| `source` | str | 否 | "xueqiu" | 数据源(目前支持"xueqiu") |

## 返回值

返回 `pandas.DataFrame`，包含以下列：

| 列名 | 类型 | 描述 |
|------|------|------|
| `symbol` | str | 股票代码 |
| `issuer` | str | 股票名称 |
| `name` | str | 变动人 |
| `title` | str | 董监高职务 |
| `transaction_date` | datetime | 变动日期 |
| `transaction_shares` | int | 变动股数 |
| `transaction_price_per_share` | float | 成交均价 |
| `shares_owned_after_transaction` | int | 变动后持股数 |
| `relationship` | str | 与董监高关系 |
| `is_board_director` | bool | 是否为董事会成员 |
| `transaction_value` | float | 交易金额(变动股数*成交均价) |
| `shares_owned_before_transaction` | int | 变动前持股数 |

## 使用示例

```python
from akshare_one import get_inner_trade_data

# 获取指定股票内部交易数据
df = get_inner_trade_data(symbol="600000")
print(df[["symbol", "name", "transaction_date", "transaction_value"]].head())
```
