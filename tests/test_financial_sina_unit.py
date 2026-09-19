"""Offline regression tests for the Sina balance-sheet cleaner.

Sina serves banks a different balance-sheet template with no current/non-current
split. The cleaner used to index ``current_liabilities`` unconditionally, so a
bank symbol raised ``KeyError`` after an otherwise successful fetch. These tests
pin both templates without touching the network.
"""

import numpy as np
import pandas as pd
import pytest

from akshare_one.modules.financial.sina import SinaFinancialReport


@pytest.fixture(autouse=True)
def _disable_cache(monkeypatch):
    monkeypatch.setenv("AKSHARE_ONE_CACHE_ENABLED", "false")


def _bank_frame() -> pd.DataFrame:
    """Shape of the bank template: no 流动资产合计/流动负债合计 rows."""
    return pd.DataFrame(
        {
            "报告日": ["20231231"],
            "币种": ["CNY"],
            "资产总计": [100.0],
            "负债合计": [90.0],
            # 股东权益 is an empty section header in the bank template; the
            # populated subtotal is 归属于母公司股东的权益.
            "股东权益": [np.nan],
            "归属于母公司股东的权益": [10.0],
            "股本": [1.0],
            "资本公积": [2.0],
            "未分配利润": [3.0],
            "少数股东权益": [0.5],
            "短期借款": [5.0],
            "长期借款": [5.0],
            "递延所得税负债": [0.1],
            "递延税款借项": [0.2],
            "客户存款(吸收存款)": [70.0],
            "固定资产净额": [1.0],
            "固定资产净值": [0.9],
            "现金及存放中央银行款项": [20.0],
            "应收账款": [2.0],
            "其他应收款": [1.0],
            "存货": [0.0],
            "商誉": [0.0],
            "长期股权投资": [1.0],
            "交易性金融资产": [5.0],
            "在建工程": [0.0],
            "其他综合收益": [0.0],
            "合同负债": [0.0],
        }
    )


def _non_bank_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "报告日": ["20231231"],
            "币种": ["CNY"],
            "资产总计": [200.0],
            "流动资产合计": [80.0],
            "货币资金": [30.0],
            "存货": [10.0],
            "交易性金融资产": [5.0],
            "应收票据及应收账款": [8.0],
            "非流动资产合计": [120.0],
            "固定资产": [50.0],
            "固定资产净值": [48.0],
            "商誉": [2.0],
            "长期股权投资": [10.0],
            "其他非流动金融资产": [1.0],
            "实收资本(或股本)": [10.0],
            "递延所得税资产": [1.0],
            "负债合计": [100.0],
            "流动负债合计": [40.0],
            "短期借款": [10.0],
            "应付票据及应付账款": [5.0],
            "合同负债": [3.0],
            "吸收存款及同业存放": [0.0],
            "非流动负债合计": [60.0],
            "长期借款": [20.0],
            "递延所得税负债": [2.0],
            "所有者权益(或股东权益)合计": [100.0],
            "未分配利润": [30.0],
            "其他综合收益": [1.0],
            "应收账款": [4.0],
            "预付款项": [2.0],
            "其他应收款": [1.0],
            "在建工程": [3.0],
            "资本公积": [20.0],
            "少数股东权益": [5.0],
        }
    )


def test_bank_balance_sheet_does_not_raise():
    df = SinaFinancialReport("000001")._clean_balance_data(_bank_frame())
    assert df.iloc[0]["total_assets"] == 100.0


def test_bank_balance_sheet_maps_its_template_fields():
    row = SinaFinancialReport("000001")._clean_balance_data(_bank_frame()).iloc[0]
    assert row["shareholders_equity"] == 10.0  # 归属于母公司股东的权益
    assert row["outstanding_shares"] == 1.0  # 股本
    assert row["deposit_liabilities"] == 70.0  # 客户存款(吸收存款)
    assert row["tax_assets"] == 0.2  # 递延税款借项
    assert row["cash_and_equivalents"] == 20.0  # 现金及存放中央银行款项
    assert row["property_plant_and_equipment"] == 1.0  # 固定资产净额
    assert row["fixed_assets_net"] == 0.9  # 固定资产净值


def test_bank_balance_sheet_leaves_unclassified_ratios_nan():
    row = SinaFinancialReport("000001")._clean_balance_data(_bank_frame()).iloc[0]
    # Banks report no current/non-current split, so the ratio is undefined.
    assert np.isnan(row["current_liabilities"])
    assert np.isnan(row["current_ratio"])
    # debt_to_assets still works: (5 + 5) / 100.
    assert row["debt_to_assets"] == pytest.approx(0.1)


def test_non_bank_balance_sheet_ratios_unchanged():
    row = SinaFinancialReport("600519")._clean_balance_data(_non_bank_frame()).iloc[0]
    assert row["current_ratio"] == pytest.approx(2.0)  # 80 / 40
    assert row["debt_to_assets"] == pytest.approx(0.15)  # (10 + 20) / 200
    assert row["property_plant_and_equipment"] == 50.0  # 固定资产, not 固定资产净额


def test_balance_sheet_without_debt_rows_does_not_raise():
    minimal = pd.DataFrame({"报告日": ["20231231"], "资产总计": [10.0]})
    row = SinaFinancialReport("600519")._clean_balance_data(minimal).iloc[0]
    assert np.isnan(row["debt_to_assets"])


def test_bank_debt_is_nan_when_borrowings_are_absent():
    """Recent bank reports have no 短期借款/长期借款; debt must not read as 0."""
    frame = _bank_frame()
    frame["短期借款"] = np.nan
    frame["长期借款"] = np.nan
    row = SinaFinancialReport("000001")._clean_balance_data(frame).iloc[0]
    assert np.isnan(row["debt_to_assets"])
