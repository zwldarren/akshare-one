"""内部交易数据模块

包含上市公司内部交易相关功能
"""

import pandas as pd
from .modules.insider.factory import InsiderDataFactory


def get_inner_trade_data(symbol: str, source: str = "xueqiu") -> "pd.DataFrame":
    """获取雪球内部交易数据

    Args:
        source: 数据源 (目前支持 "xueqiu")
        symbol: 股票代码，如"600000"

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
    provider = InsiderDataFactory.get_provider(source, symbol=symbol)
    return provider.get_inner_trade_data()
