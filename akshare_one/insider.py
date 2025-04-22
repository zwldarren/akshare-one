"""内部交易数据模块

包含上市公司内部交易相关功能
"""

from typing import Optional
import pandas as pd
from .adapters import XueQiuAdapter


def get_inner_trade_data(
    source: str = "xueqiu", symbol: Optional[str] = None
) -> "pd.DataFrame":
    """获取雪球内部交易数据

    Args:
        source: 数据源 (目前支持 "xueqiu")
        symbol: 可选股票代码，如"600000"，不传则返回所有数据

    Returns:
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
    """
    if source == "xueqiu":
        return XueQiuAdapter().get_inner_trade_data(symbol=symbol)
    raise ValueError(f"Unsupported data source: {source}")
